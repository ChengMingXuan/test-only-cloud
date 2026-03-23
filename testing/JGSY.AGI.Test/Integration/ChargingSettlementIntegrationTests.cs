using System;
using System.Linq;
using System.Threading.Tasks;
using Dapper;
using FluentAssertions;
using Npgsql;
using Xunit;

#pragma warning disable DAP005 // Dapper AOT: 集成测试中使用动态 SQL，无需启用 AOT

namespace JGSY.AGI.Test.Integration;

/// <summary>
/// Charging → Settlement 跨服务集成测试（Testcontainers PostgreSQL）
/// 测试层级：L2-集成测试（数据库级别验证）
/// </summary>
[Collection("ContainerCollection")]
public class ChargingSettlementIntegrationTests
{
    private readonly ContainerInfrastructureFixture _fixture;

    public ChargingSettlementIntegrationTests(ContainerInfrastructureFixture fixture)
    {
        _fixture = fixture;
    }

    [Fact]
    public async Task ChargingOrder_ToSettlementBilling_IntegrationFlow()
    {
        // Arrange: 创建测试所需的表结构
        await using var conn = new NpgsqlConnection(_fixture.PostgresConnectionString);
        await conn.OpenAsync();

        await CreateChargingSchemaAsync(conn);
        await CreateSettlementSchemaAsync(conn);

        var tenantId = Guid.NewGuid();
        var userId = Guid.NewGuid();
        var orderId = Guid.NewGuid();
        var orderNumber = $"TC{DateTime.UtcNow:yyyyMMddHHmmssfff}";

        // Act 1: 插入充电订单
        await conn.ExecuteAsync(@"
            INSERT INTO charging_order 
                (id, tenant_id, user_id, order_number, order_state, charge_status, is_fee, pile_id, port_id, station_id, start_time, end_time, consume_power, order_type, create_time, update_time, delete_at)
            VALUES 
                (@Id, @TenantId, @UserId, @OrderNumber, '5', '9003', '2001', @PileId, @PortId, @StationId, @StartTime, @EndTime, @ConsumePower, '3002', @Now, @Now, NULL)",
            new
            {
                Id = orderId,
                TenantId = tenantId,
                UserId = userId,
                OrderNumber = orderNumber,
                PileId = Guid.NewGuid(),
                PortId = Guid.NewGuid(),
                StationId = Guid.NewGuid(),
                StartTime = DateTime.UtcNow.AddHours(-2),
                EndTime = DateTime.UtcNow,
                ConsumePower = 25.5m,
                Now = DateTime.UtcNow
            });

        // Act 2: 模拟结算服务创建账单明细
        var billingId = Guid.NewGuid();
        await conn.ExecuteAsync(@"
            INSERT INTO settlement_billing_detail
                (id, tenant_id, order_id, order_number, user_id, device_id, billing_type, billing_time, energy_consumed, duration_minutes, electricity_fee, service_fee, actual_amount, settlement_status, create_time, update_time, delete_at)
            VALUES 
                (@Id, @TenantId, @OrderId, @OrderNumber, @UserId, @DeviceId, 'Charging', @BillingTime, @EnergyConsumed, @DurationMinutes, @ElectricityFee, @ServiceFee, @ActualAmount, 'Pending', @Now, @Now, NULL)",
            new
            {
                Id = billingId,
                TenantId = tenantId,
                OrderId = orderId,
                OrderNumber = orderNumber,
                UserId = userId,
                DeviceId = Guid.NewGuid(),
                BillingTime = DateTime.UtcNow,
                EnergyConsumed = 25.5m,
                DurationMinutes = 120,
                ElectricityFee = 51.0m,
                ServiceFee = 5.1m,
                ActualAmount = 56.1m,
                Now = DateTime.UtcNow
            });

        // Assert 1: 验证充电订单
        var order = await conn.QueryFirstOrDefaultAsync<ChargingOrderDto>(
            "SELECT order_number, order_state, consume_power FROM charging_order WHERE id = @Id", new { Id = orderId });
        order.Should().NotBeNull();
        order!.order_number.Should().Be(orderNumber);
        order.order_state.Should().Be("5"); // 已完成
        order.consume_power.Should().Be(25.5m);

        // Assert 2: 验证账单明细
        var billing = await conn.QueryFirstOrDefaultAsync<BillingDetailDto>(
            "SELECT order_id, billing_type, actual_amount, settlement_status FROM settlement_billing_detail WHERE id = @Id", new { Id = billingId });
        billing.Should().NotBeNull();
        billing!.order_id.Should().Be(orderId);
        billing.billing_type.Should().Be("Charging");
        billing.actual_amount.Should().Be(56.1m);
        billing.settlement_status.Should().Be("Pending");

        // Act 3: 模拟结算完成
        await conn.ExecuteAsync(
            "UPDATE settlement_billing_detail SET settlement_status = 'Settled', update_time = @Now WHERE id = @Id",
            new { Id = billingId, Now = DateTime.UtcNow });

        // Assert 3: 验证结算状态更新
        var settledStatus = await conn.ExecuteScalarAsync<string>(
            "SELECT settlement_status FROM settlement_billing_detail WHERE id = @Id", new { Id = billingId });
        settledStatus.Should().Be("Settled");
    }

    [Fact]
    public async Task MultiTenantIsolation_ShouldPreventCrossAccess()
    {
        await using var conn = new NpgsqlConnection(_fixture.PostgresConnectionString);
        await conn.OpenAsync();

        await CreateChargingSchemaAsync(conn);

        var tenantA = Guid.NewGuid();
        var tenantB = Guid.NewGuid();
        var orderA = Guid.NewGuid();
        var orderB = Guid.NewGuid();

        // 为两个租户各创建一个订单
        await conn.ExecuteAsync(@"
            INSERT INTO charging_order (id, tenant_id, user_id, order_number, order_state, charge_status, is_fee, start_time, order_type, create_time, update_time, delete_at)
            VALUES (@Id, @TenantId, @UserId, @OrderNumber, '1', '9001', '2001', @Now, '3001', @Now, @Now, NULL)",
            new { Id = orderA, TenantId = tenantA, UserId = Guid.NewGuid(), OrderNumber = "TA001", Now = DateTime.UtcNow });

        await conn.ExecuteAsync(@"
            INSERT INTO charging_order (id, tenant_id, user_id, order_number, order_state, charge_status, is_fee, start_time, order_type, create_time, update_time, delete_at)
            VALUES (@Id, @TenantId, @UserId, @OrderNumber, '1', '9001', '2001', @Now, '3001', @Now, @Now, NULL)",
            new { Id = orderB, TenantId = tenantB, UserId = Guid.NewGuid(), OrderNumber = "TB001", Now = DateTime.UtcNow });

        // 租户 A 查询只应看到自己的订单
        var ordersForTenantA = (await conn.QueryAsync<ChargingOrderDto>(
            "SELECT order_number, order_state, consume_power FROM charging_order WHERE tenant_id = @TenantId AND delete_at IS NULL",
            new { TenantId = tenantA })).ToList();

        ordersForTenantA.Should().ContainSingle();
        ordersForTenantA.First().order_number.Should().Be("TA001");
    }

    [Fact]
    public async Task SoftDelete_ShouldExcludeFromQueries()
    {
        await using var conn = new NpgsqlConnection(_fixture.PostgresConnectionString);
        await conn.OpenAsync();

        await CreateChargingSchemaAsync(conn);

        var tenantId = Guid.NewGuid();
        var activeOrder = Guid.NewGuid();
        var deletedOrder = Guid.NewGuid();

        await conn.ExecuteAsync(@"
            INSERT INTO charging_order (id, tenant_id, user_id, order_number, order_state, charge_status, is_fee, start_time, order_type, create_time, update_time, delete_at)
            VALUES (@Id, @TenantId, @UserId, @OrderNumber, '1', '9001', '2001', @Now, '3001', @Now, @Now, NULL)",
            new { Id = activeOrder, TenantId = tenantId, UserId = Guid.NewGuid(), OrderNumber = "ACTIVE001", Now = DateTime.UtcNow });

        await conn.ExecuteAsync(@"
            INSERT INTO charging_order (id, tenant_id, user_id, order_number, order_state, charge_status, is_fee, start_time, order_type, create_time, update_time, delete_at)
            VALUES (@Id, @TenantId, @UserId, @OrderNumber, '1', '9001', '2001', @Now, '3001', @Now, @Now, @DeletedAt)",
            new { Id = deletedOrder, TenantId = tenantId, UserId = Guid.NewGuid(), OrderNumber = "DELETED001", Now = DateTime.UtcNow, DeletedAt = DateTime.UtcNow });

        var activeOrders = (await conn.QueryAsync<ChargingOrderDto>(
            "SELECT order_number, order_state, consume_power FROM charging_order WHERE tenant_id = @TenantId AND delete_at IS NULL",
            new { TenantId = tenantId })).ToList();

        activeOrders.Should().ContainSingle();
        activeOrders.First().order_number.Should().Be("ACTIVE001");
    }

    private static async Task CreateChargingSchemaAsync(NpgsqlConnection conn)
    {
        await conn.ExecuteAsync(@"
            CREATE TABLE IF NOT EXISTS charging_order (
                id UUID PRIMARY KEY,
                tenant_id UUID NOT NULL,
                user_id UUID,
                order_number VARCHAR(50),
                order_state VARCHAR(10),
                charge_status VARCHAR(10),
                is_fee VARCHAR(10),
                pile_id UUID,
                port_id UUID,
                station_id UUID,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                consume_power DECIMAL(10,2),
                order_type VARCHAR(10),
                create_time TIMESTAMP,
                update_time TIMESTAMP,
                delete_at TIMESTAMP NULL DEFAULT NULL
            )");
    }

    private static async Task CreateSettlementSchemaAsync(NpgsqlConnection conn)
    {
        await conn.ExecuteAsync(@"
            CREATE TABLE IF NOT EXISTS settlement_billing_detail (
                id UUID PRIMARY KEY,
                tenant_id UUID NOT NULL,
                order_id UUID,
                order_number VARCHAR(50),
                user_id UUID,
                device_id UUID,
                billing_type VARCHAR(50),
                billing_time TIMESTAMP,
                energy_consumed DECIMAL(10,2),
                duration_minutes INT,
                electricity_fee DECIMAL(10,2),
                service_fee DECIMAL(10,2),
                actual_amount DECIMAL(10,2),
                settlement_status VARCHAR(20),
                create_time TIMESTAMP,
                update_time TIMESTAMP,
                delete_at TIMESTAMP NULL DEFAULT NULL
            )");
    }

    #region DTOs for Dapper AOT compatibility

    private class ChargingOrderDto
    {
        public string order_number { get; set; } = string.Empty;
        public string order_state { get; set; } = string.Empty;
        public decimal consume_power { get; set; }
    }

    private class BillingDetailDto
    {
        public Guid order_id { get; set; }
        public string billing_type { get; set; } = string.Empty;
        public decimal actual_amount { get; set; }
        public string settlement_status { get; set; } = string.Empty;
    }

    #endregion
}
