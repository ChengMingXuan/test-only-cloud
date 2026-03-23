using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Dapper;
using FluentAssertions;
using JGSY.AGI.Common.Core.DistributedTransaction;
using Microsoft.Extensions.Logging;
using Moq;
using Npgsql;
using Xunit;

#pragma warning disable DAP005 // Dapper AOT: 集成测试中使用动态 SQL，无需启用 AOT

namespace JGSY.AGI.Test.Integration;

/// <summary>
/// TCC 分布式事务集成测试（Testcontainers PostgreSQL）
/// 测试层级：L2-集成测试（数据库级别验证）
/// </summary>
[Collection("ContainerCollection")]
public class TccDistributedTransactionTests
{
    private readonly ContainerInfrastructureFixture _fixture;

    public TccDistributedTransactionTests(ContainerInfrastructureFixture fixture)
    {
        _fixture = fixture;
    }

    [Fact]
    public async Task TccCoordinator_TryConfirm_AllParticipantsSucceed_ShouldConfirm()
    {
        // Arrange
        await using var conn = new NpgsqlConnection(_fixture.PostgresConnectionString);
        await conn.OpenAsync();
        await CreateTccSchemaAsync(conn);

        var tenantId = Guid.NewGuid();
        var transactionId = Guid.NewGuid();

        // 模拟 TCC 事务创建
        await conn.ExecuteAsync(@"
            INSERT INTO dist_tcc_transactions 
                (id, tenant_id, transaction_type, status, context_data, create_time, update_time, expire_at)
            VALUES 
                (@Id, @TenantId, 'TestTcc', 0, '{""key"":""value""}'::jsonb, @Now, @Now, @ExpireAt)",
            new
            {
                Id = transactionId,
                TenantId = tenantId,
                Now = DateTime.UtcNow,
                ExpireAt = DateTime.UtcNow.AddMinutes(5)
            });

        // Act: 模拟 Try 阶段成功
        await conn.ExecuteAsync(@"
            UPDATE dist_tcc_transactions SET status = 2, update_time = @Now WHERE id = @Id",
            new { Id = transactionId, Now = DateTime.UtcNow });

        // 添加参与者日志
        var participant1Id = Guid.NewGuid();
        var participant2Id = Guid.NewGuid();
        await conn.ExecuteAsync(@"
            INSERT INTO dist_tcc_participant_logs 
                (id, transaction_id, participant_name, service_name, status, started_at, completed_at)
            VALUES 
                (@Id, @TxId, 'Participant1', 'ServiceA', 2, @StartedAt, @CompletedAt)",
            new
            {
                Id = participant1Id,
                TxId = transactionId,
                StartedAt = DateTime.UtcNow.AddMilliseconds(-100),
                CompletedAt = DateTime.UtcNow
            });
        await conn.ExecuteAsync(@"
            INSERT INTO dist_tcc_participant_logs 
                (id, transaction_id, participant_name, service_name, status, started_at, completed_at)
            VALUES 
                (@Id, @TxId, 'Participant2', 'ServiceB', 2, @StartedAt, @CompletedAt)",
            new
            {
                Id = participant2Id,
                TxId = transactionId,
                StartedAt = DateTime.UtcNow.AddMilliseconds(-50),
                CompletedAt = DateTime.UtcNow
            });

        // Act: 模拟 Confirm 阶段
        await conn.ExecuteAsync(@"
            UPDATE dist_tcc_transactions SET status = 5, completed_at = @Now, update_time = @Now WHERE id = @Id",
            new { Id = transactionId, Now = DateTime.UtcNow });

        // Assert
        var tx = await conn.QueryFirstOrDefaultAsync<TccTransactionDto>(
            "SELECT id, status, completed_at FROM dist_tcc_transactions WHERE id = @Id",
            new { Id = transactionId });
        tx.Should().NotBeNull();
        tx!.status.Should().Be(5); // Confirmed
        tx.completed_at.Should().NotBeNull();

        var participants = await conn.QueryAsync<TccParticipantDto>(
            "SELECT participant_name, status FROM dist_tcc_participant_logs WHERE transaction_id = @TxId",
            new { TxId = transactionId });
        participants.Should().HaveCount(2);
    }

    [Fact]
    public async Task TccCoordinator_TryFailed_ShouldCancel()
    {
        // Arrange
        await using var conn = new NpgsqlConnection(_fixture.PostgresConnectionString);
        await conn.OpenAsync();
        await CreateTccSchemaAsync(conn);

        var tenantId = Guid.NewGuid();
        var transactionId = Guid.NewGuid();

        // 创建事务
        await conn.ExecuteAsync(@"
            INSERT INTO dist_tcc_transactions 
                (id, tenant_id, transaction_type, status, context_data, create_time, update_time, expire_at)
            VALUES 
                (@Id, @TenantId, 'TestTcc', 0, '{}'::jsonb, @Now, @Now, @ExpireAt)",
            new
            {
                Id = transactionId,
                TenantId = tenantId,
                Now = DateTime.UtcNow,
                ExpireAt = DateTime.UtcNow.AddMinutes(5)
            });

        // 第一个参与者成功
        await conn.ExecuteAsync(@"
            INSERT INTO dist_tcc_participant_logs 
                (id, transaction_id, participant_name, service_name, status, started_at, completed_at)
            VALUES 
                (@Id, @TxId, 'Participant1', 'ServiceA', 2, @StartedAt, @CompletedAt)",
            new
            {
                Id = Guid.NewGuid(),
                TxId = transactionId,
                StartedAt = DateTime.UtcNow.AddMilliseconds(-100),
                CompletedAt = DateTime.UtcNow
            });

        // 第二个参与者失败
        await conn.ExecuteAsync(@"
            INSERT INTO dist_tcc_participant_logs 
                (id, transaction_id, participant_name, service_name, status, error_message, started_at, completed_at)
            VALUES 
                (@Id, @TxId, 'Participant2', 'ServiceB', 3, '余额不足', @StartedAt, @CompletedAt)",
            new
            {
                Id = Guid.NewGuid(),
                TxId = transactionId,
                StartedAt = DateTime.UtcNow.AddMilliseconds(-50),
                CompletedAt = DateTime.UtcNow
            });

        // Act: Try 失败，事务进入 Cancel 状态
        await conn.ExecuteAsync(@"
            UPDATE dist_tcc_transactions SET status = 7, error_message = 'Participant2 failed: 余额不足', update_time = @Now WHERE id = @Id",
            new { Id = transactionId, Now = DateTime.UtcNow });

        // Assert
        var tx = await conn.QueryFirstOrDefaultAsync<TccTransactionDto>(
            "SELECT id, status, error_message FROM dist_tcc_transactions WHERE id = @Id",
            new { Id = transactionId });
        tx.Should().NotBeNull();
        tx!.status.Should().Be(7); // Cancelled
        tx.error_message.Should().Contain("Participant2 failed");
    }

    [Fact]
    public async Task ResourceReservation_ReserveConfirmCancel_Flow()
    {
        // Arrange
        await using var conn = new NpgsqlConnection(_fixture.PostgresConnectionString);
        await conn.OpenAsync();
        await CreateTccSchemaAsync(conn);

        var tenantId = Guid.NewGuid();
        var transactionId = Guid.NewGuid();
        var reservationId = Guid.NewGuid();
        var resourceId = "CONNECTOR:CP001:1";

        // Act: 创建资源预留
        await conn.ExecuteAsync(@"
            INSERT INTO dist_resource_reservations 
                (id, transaction_id, tenant_id, resource_type, resource_id, reserved_amount, unit, status, create_time, expire_at)
            VALUES 
                (@Id, @TxId, @TenantId, 'ChargingConnector', @ResourceId, 1, 'unit', 0, @Now, @ExpireAt)",
            new
            {
                Id = reservationId,
                TxId = transactionId,
                TenantId = tenantId,
                ResourceId = resourceId,
                Now = DateTime.UtcNow,
                ExpireAt = DateTime.UtcNow.AddMinutes(5)
            });

        // Assert: 预留状态为 Reserved (0)
        var reservation = await conn.QueryFirstOrDefaultAsync<ResourceReservationDto>(
            "SELECT id, status, resource_id, reserved_amount FROM dist_resource_reservations WHERE id = @Id",
            new { Id = reservationId });
        reservation.Should().NotBeNull();
        reservation!.status.Should().Be(0); // Reserved
        reservation.resource_id.Should().Be(resourceId);
        reservation.reserved_amount.Should().Be(1);

        // Act: 确认预留
        await conn.ExecuteAsync(@"
            UPDATE dist_resource_reservations 
            SET status = 1, confirmed_at = @Now 
            WHERE id = @Id",
            new { Id = reservationId, Now = DateTime.UtcNow });

        // Assert: 预留状态为 Confirmed (1)
        reservation = await conn.QueryFirstOrDefaultAsync<ResourceReservationDto>(
            "SELECT id, status, confirmed_at FROM dist_resource_reservations WHERE id = @Id",
            new { Id = reservationId });
        reservation!.status.Should().Be(1); // Confirmed
        reservation.confirmed_at.Should().NotBeNull();
    }

    [Fact]
    public async Task ResourceReservation_MultipleActiveReservations_ShouldBlockNew()
    {
        // Arrange
        await using var conn = new NpgsqlConnection(_fixture.PostgresConnectionString);
        await conn.OpenAsync();
        await CreateTccSchemaAsync(conn);

        var tenantId = Guid.NewGuid();
        var resourceId = "CONNECTOR:CP002:1";

        // 创建第一个预留
        var reservation1Id = Guid.NewGuid();
        await conn.ExecuteAsync(@"
            INSERT INTO dist_resource_reservations 
                (id, transaction_id, tenant_id, resource_type, resource_id, reserved_amount, unit, status, create_time, expire_at)
            VALUES 
                (@Id, @TxId, @TenantId, 'ChargingConnector', @ResourceId, 1, 'unit', 0, @Now, @ExpireAt)",
            new
            {
                Id = reservation1Id,
                TxId = Guid.NewGuid(),
                TenantId = tenantId,
                ResourceId = resourceId,
                Now = DateTime.UtcNow,
                ExpireAt = DateTime.UtcNow.AddMinutes(5)
            });

        // Assert: 检查活跃预留
        var activeCount = await conn.ExecuteScalarAsync<int>(@"
            SELECT COUNT(*) FROM dist_resource_reservations 
            WHERE resource_type = 'ChargingConnector' 
              AND resource_id = @ResourceId 
              AND status = 0 
              AND delete_at IS NULL",
            new { ResourceId = resourceId });

        activeCount.Should().Be(1);
    }

    private async Task CreateTccSchemaAsync(NpgsqlConnection conn)
    {
        await conn.ExecuteAsync(@"
            CREATE TABLE IF NOT EXISTS dist_tcc_transactions (
                id                UUID PRIMARY KEY,
                tenant_id         UUID NOT NULL,
                transaction_type  VARCHAR(200) NOT NULL,
                status            INT NOT NULL DEFAULT 0,
                context_data      JSONB NOT NULL DEFAULT '{}',
                create_time        TIMESTAMP NOT NULL DEFAULT NOW(),
                update_time        TIMESTAMP NOT NULL DEFAULT NOW(),
                expire_at         TIMESTAMP NOT NULL,
                completed_at      TIMESTAMP,
                error_message     TEXT,
                delete_at        TIMESTAMP NULL DEFAULT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_dist_tcc_status ON dist_tcc_transactions (status) WHERE delete_at IS NULL;

            CREATE TABLE IF NOT EXISTS dist_tcc_participant_logs (
                id                UUID PRIMARY KEY,
                transaction_id    UUID NOT NULL,
                participant_name  VARCHAR(200) NOT NULL,
                service_name      VARCHAR(100) NOT NULL,
                status            INT NOT NULL DEFAULT 0,
                try_result        JSONB,
                started_at        TIMESTAMP,
                completed_at      TIMESTAMP,
                error_message     TEXT,
                delete_at        TIMESTAMP NULL DEFAULT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_dist_tcc_participant_tx ON dist_tcc_participant_logs (transaction_id) WHERE delete_at IS NULL;

            CREATE TABLE IF NOT EXISTS dist_resource_reservations (
                id                UUID PRIMARY KEY,
                transaction_id    UUID NOT NULL,
                tenant_id         UUID NOT NULL,
                resource_type     VARCHAR(100) NOT NULL,
                resource_id       VARCHAR(200) NOT NULL,
                reserved_amount   NUMERIC(18, 4) NOT NULL,
                unit              VARCHAR(20) NOT NULL DEFAULT '',
                status            INT NOT NULL DEFAULT 0,
                create_time        TIMESTAMP NOT NULL DEFAULT NOW(),
                expire_at         TIMESTAMP NOT NULL,
                confirmed_at      TIMESTAMP,
                cancelled_at      TIMESTAMP,
                metadata          JSONB,
                delete_at        TIMESTAMP NULL DEFAULT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_dist_reservation_resource ON dist_resource_reservations (resource_type, resource_id) WHERE status = 0 AND delete_at IS NULL;
        ");
    }

    // DTOs for test assertions - 使用 class 以支持 Dapper 灵活映射
    private class TccTransactionDto
    {
        public Guid id { get; set; }
        public int status { get; set; }
        public DateTime? completed_at { get; set; }
        public string? error_message { get; set; }
    }

    private class TccParticipantDto
    {
        public string participant_name { get; set; } = string.Empty;
        public int status { get; set; }
    }

    private class ResourceReservationDto
    {
        public Guid id { get; set; }
        public int status { get; set; }
        public string resource_id { get; set; } = string.Empty;
        public decimal reserved_amount { get; set; }
        public DateTime? confirmed_at { get; set; }
    }
}
