using System;
using System.Collections.Generic;
using System.Data.Common;
using System.Threading.Tasks;
using FluentAssertions;
using JGSY.AGI.Charging.Data;
using JGSY.AGI.Charging.Entities;
using JGSY.AGI.Charging.Service;
using JGSY.AGI.Common.Core.Data.Dapper;
using JGSY.AGI.Common.Core.Interfaces;
using Microsoft.Data.Sqlite;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;

namespace JGSY.AGI.Test.Charging;

/// <summary>
/// 服务层费用计算单元测试（使用内存 SQLite + 假分片连接工厂）
/// </summary>
public class ChargingOrderServiceServiceTests : IAsyncLifetime
{
    private readonly string _connString = "Data Source=:memory:;Cache=Shared";
    private DbConnection? _anchor;
    private SqliteShardedConnectionFactory? _factory;

    public async Task InitializeAsync()
    {
        _anchor = new SqliteConnection(_connString);
        await _anchor.OpenAsync();
        await CreateSchemaAsync(_anchor);
        _factory = new SqliteShardedConnectionFactory(_connString, _anchor);
    }

    public async Task DisposeAsync()
    {
        if (_anchor != null)
        {
            await _anchor.DisposeAsync();
        }
    }

    [Fact(Skip = "Requires PostgreSQL integration - SQLite Guid mapping issues")]
    public async Task CalculateOrderFee_ShouldUseKwhPricing_WhenChargeType3002()
    {
        var orderId = Guid.NewGuid();
        var tenantId = Guid.NewGuid();
        await SeedOrderAsync(orderId, tenantId, consumePower: 10m, orderType: "3002");
        await SeedCustomPriceAsync(pileId: null, priceId: Guid.NewGuid(), chargeType: "3002", price: 2.0m);

        var mockTenantContext = new Mock<ITenantContext>();
        mockTenantContext.Setup(t => t.TenantId).Returns(tenantId);
        var service = new ChargingOrderService(_factory!, NullLogger<ChargingOrderService>.Instance, new ServiceCollection().BuildServiceProvider(), mockTenantContext.Object);

        var result = await service.CalculateOrderFeeAsync(orderId, tenantId);

        result.ElectricFee.Should().Be(20m);
        result.TotalAmount.Should().Be(20m);
        result.ActualAmount.Should().Be(20m);
        result.ChargeType.Should().Be("3002");
    }

    [Fact(Skip = "Requires PostgreSQL integration - SQLite Guid mapping issues")]
    public async Task CalculateOrderFee_ShouldApplyTieredHours_WhenChargeType3001()
    {
        var orderId = Guid.NewGuid();
        var tenantId = Guid.NewGuid();
        await SeedOrderAsync(orderId, tenantId, consumePower: 0m, orderType: "3001", start: DateTime.UtcNow.AddHours(-4), end: DateTime.UtcNow);
        await SeedCustomPriceAsync(pileId: null, priceId: Guid.NewGuid(), chargeType: "3001", price: 1.5m, hours: 1.5m, granterNum: "2", granterPrice: "3");

        var mockTenantContext2 = new Mock<ITenantContext>();
        mockTenantContext2.Setup(t => t.TenantId).Returns(tenantId);
        var service = new ChargingOrderService(_factory!, NullLogger<ChargingOrderService>.Instance, new ServiceCollection().BuildServiceProvider(), mockTenantContext2.Object);

        var result = await service.CalculateOrderFeeAsync(orderId, tenantId);

        // 前2小时按1.5，后2小时按3.0 => 2*1.5 + 2*3 = 9
        result.ElectricFee.Should().Be(9m);
        result.TotalAmount.Should().Be(9m);
        result.ActualAmount.Should().Be(9m);
        result.ChargeType.Should().Be("3001");
    }

    private async Task CreateSchemaAsync(DbConnection conn)
    {
        var cmd = conn.CreateCommand();
        cmd.CommandText = @"
CREATE TABLE charging_order (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT false,
    user_id TEXT,
    order_number TEXT,
    order_state TEXT,
    charge_status TEXT,
    is_fee TEXT,
    pile_id TEXT,
    port_id TEXT,
    station_id TEXT,
    start_time TEXT,
    end_time TEXT,
    hour TEXT,
    price REAL,
    mobile TEXT,
    card_no TEXT,
    order_type TEXT,
    device_type INTEGER,
    order_source INTEGER,
    consume_power REAL,
    custom_price_id TEXT,
    delete_at INTEGER DEFAULT 0,
    create_time TEXT,
    update_time TEXT
);
CREATE TABLE charging_custom_price (
    price_id TEXT PRIMARY KEY,
    pile_id TEXT,
    charge_type TEXT,
    price REAL,
    hours REAL,
    granter_num TEXT,
    granter_price TEXT,
    delete_at INTEGER DEFAULT 0
);
";
        await cmd.ExecuteNonQueryAsync();
    }

    private async Task SeedOrderAsync(Guid orderId, Guid tenantId, decimal consumePower, string orderType, DateTime? start = null, DateTime? end = null)
    {
        var cmd = (SqliteCommand)_anchor!.CreateCommand();
        await using var _ = cmd;
        cmd.CommandText = @"
INSERT INTO charging_order (id, tenant_id, order_number, order_state, charge_status, is_fee, pile_id, port_id, station_id, start_time, end_time, hour, price, mobile, card_no, order_type, device_type, order_source, consume_power, custom_price_id, create_time, update_time)
VALUES ($id, $tenant_id, $order_number, '1', '9001', '2001', false, false, false, $start_time, $end_time, '1', false, false, false, $order_type, 2, 2, $consume_power, false, $create_time, $update_time);
";
        cmd.Parameters.AddWithValue("$id", orderId.ToString());
        cmd.Parameters.AddWithValue("$tenant_id", tenantId.ToString());
        cmd.Parameters.AddWithValue("$order_number", $"CHG{DateTime.UtcNow.Ticks}");
        cmd.Parameters.AddWithValue("$start_time", (start ?? DateTime.UtcNow.AddHours(-1)).ToString("O"));
        cmd.Parameters.AddWithValue("$end_time", (end ?? DateTime.UtcNow).ToString("O"));
        cmd.Parameters.AddWithValue("$order_type", orderType);
        cmd.Parameters.AddWithValue("$consume_power", consumePower);
        cmd.Parameters.AddWithValue("$create_time", DateTime.UtcNow.ToString("O"));
        cmd.Parameters.AddWithValue("$update_time", DateTime.UtcNow.ToString("O"));
        await cmd.ExecuteNonQueryAsync();
    }

    private async Task SeedCustomPriceAsync(Guid? pileId, Guid priceId, string chargeType, decimal price, decimal? hours = null, string? granterNum = null, string? granterPrice = null)
    {
        var cmd = (SqliteCommand)_anchor!.CreateCommand();
        await using var _ = cmd;
        cmd.CommandText = @"
INSERT INTO charging_custom_price (price_id, pile_id, charge_type, price, hours, granter_num, granter_price, delete_at)
VALUES ($price_id, $pile_id, $charge_type, $price, $hours, $granter_num, $granter_price, 0);
";
        cmd.Parameters.AddWithValue("$price_id", priceId.ToString());
        cmd.Parameters.AddWithValue("$pile_id", (object?)pileId?.ToString() ?? DBNull.Value);
        cmd.Parameters.AddWithValue("$charge_type", chargeType);
        cmd.Parameters.AddWithValue("$price", price);
        cmd.Parameters.AddWithValue("$hours", (object?)hours ?? DBNull.Value);
        cmd.Parameters.AddWithValue("$granter_num", (object?)granterNum ?? DBNull.Value);
        cmd.Parameters.AddWithValue("$granter_price", (object?)granterPrice ?? DBNull.Value);
        await cmd.ExecuteNonQueryAsync();
    }

    private sealed class SqliteShardedConnectionFactory : IShardedConnectionFactory
    {
        private readonly string _connectionString;
        private readonly DbConnection _anchor;

        public SqliteShardedConnectionFactory(string connectionString, DbConnection anchor)
        {
            _connectionString = connectionString;
            _anchor = anchor;
        }

        public DbConnection CreateReadConnection(Guid tenantId)
        {
            // 返回 anchor 连接以确保使用同一个共享内存数据库
            if (_anchor.State != System.Data.ConnectionState.Open)
                _anchor.Open();
            return _anchor;
        }

        public DbConnection CreateWriteConnection(Guid tenantId) => CreateReadConnection(tenantId);
        public DbConnection CreateConnectionForShard(int shardIndex, bool isRead = false) => CreateReadConnection(Guid.Empty);
        public int GetShardIndex(Guid tenantId) => 0;
        public IEnumerable<(int ShardIndex, DbConnection Connection)> GetAllShardConnections(bool isRead = true)
            => new (int, DbConnection)[] { (0, _anchor) };
    }
}
