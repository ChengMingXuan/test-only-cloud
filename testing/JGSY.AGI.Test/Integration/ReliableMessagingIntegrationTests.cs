using System;
using System.Threading;
using System.Threading.Tasks;
using Dapper;
using FluentAssertions;
using JGSY.AGI.Common.Core.DistributedTransaction.ReliableMessaging;
using Npgsql;
using Xunit;

namespace JGSY.AGI.Test.Integration;

/// <summary>
/// 可靠消息（本地消息表 + MQ）集成测试
/// 测试层级：L2-集成测试（数据库级别验证）
/// </summary>
[Collection("ContainerCollection")]
public class ReliableMessagingIntegrationTests
{
    private readonly ContainerInfrastructureFixture _fixture;

    public ReliableMessagingIntegrationTests(ContainerInfrastructureFixture fixture)
    {
        _fixture = fixture;
    }

    [Fact]
    public async Task Outbox_AddMessage_ShouldPersistToPending()
    {
        // Arrange
        await using var conn = new NpgsqlConnection(_fixture.PostgresConnectionString);
        await conn.OpenAsync();
        await CreateReliableMessagingSchemaAsync(conn);

        var tenantId = Guid.NewGuid();
        var messageId = Guid.NewGuid();
        var eventType = "TestEvent";
        var payload = "{\"key\":\"value\"}";

        // Act: 模拟发件箱写入
        await conn.ExecuteAsync(@"
            INSERT INTO dist_outbox_messages 
                (id, tenant_id, event_type, payload, routing_key, exchange, status, retry_count, create_time)
            VALUES 
                (@Id, @TenantId, @EventType, @Payload::jsonb, @RoutingKey, @Exchange, 0, 0, @Now)",
            new
            {
                Id = messageId,
                TenantId = tenantId,
                EventType = eventType,
                Payload = payload,
                RoutingKey = "testevent",
                Exchange = "jgsy.events",
                Now = DateTime.UtcNow
            });

        // Assert
        var status = await conn.ExecuteScalarAsync<int>(
            "SELECT status FROM dist_outbox_messages WHERE id = @Id",
            new { Id = messageId });
        status.Should().Be(0); // Pending
    }

    [Fact]
    public async Task Outbox_MarkAsSent_ShouldUpdateStatus()
    {
        // Arrange
        await using var conn = new NpgsqlConnection(_fixture.PostgresConnectionString);
        await conn.OpenAsync();
        await CreateReliableMessagingSchemaAsync(conn);

        var messageId = Guid.NewGuid();
        await conn.ExecuteAsync(@"
            INSERT INTO dist_outbox_messages 
                (id, tenant_id, event_type, payload, status, create_time)
            VALUES 
                (@Id, @TenantId, 'TestEvent', '{}'::jsonb, 0, @Now)",
            new { Id = messageId, TenantId = Guid.NewGuid(), Now = DateTime.UtcNow });

        // Act: 标记为已发送
        await conn.ExecuteAsync(@"
            UPDATE dist_outbox_messages 
            SET status = 2, processed_at = @Now
            WHERE id = @Id",
            new { Id = messageId, Now = DateTime.UtcNow });

        // Assert
        var result = await conn.QueryFirstAsync<OutboxResultDto>(
            "SELECT status, processed_at FROM dist_outbox_messages WHERE id = @Id",
            new { Id = messageId });
        result.status.Should().Be(2); // Sent
        result.processed_at.Should().NotBeNull();
    }

    [Fact]
    public async Task Inbox_IdempotencyCheck_ShouldRejectDuplicate()
    {
        // Arrange
        await using var conn = new NpgsqlConnection(_fixture.PostgresConnectionString);
        await conn.OpenAsync();
        await CreateReliableMessagingSchemaAsync(conn);

        var messageId = "msg-" + Guid.NewGuid().ToString("N");
        var consumerGroup = "test-consumer";

        // Act: 第一次插入
        var inserted1 = await conn.ExecuteAsync(@"
            INSERT INTO dist_reliable_inbox_messages 
                (message_id, consumer_group, tenant_id, event_type, payload, status, received_at)
            VALUES 
                (@MsgId, @Group, @TenantId, 'TestEvent', '{}'::jsonb, 0, @Now)
            ON CONFLICT (message_id, consumer_group) DO NOTHING",
            new { MsgId = messageId, Group = consumerGroup, TenantId = Guid.NewGuid(), Now = DateTime.UtcNow });

        // Act: 第二次插入（重复）
        var inserted2 = await conn.ExecuteAsync(@"
            INSERT INTO dist_reliable_inbox_messages 
                (message_id, consumer_group, tenant_id, event_type, payload, status, received_at)
            VALUES 
                (@MsgId, @Group, @TenantId, 'TestEvent', '{}'::jsonb, 0, @Now)
            ON CONFLICT (message_id, consumer_group) DO NOTHING",
            new { MsgId = messageId, Group = consumerGroup, TenantId = Guid.NewGuid(), Now = DateTime.UtcNow });

        // Assert
        inserted1.Should().Be(1);
        inserted2.Should().Be(0); // 重复消息被拒绝
    }

    [Fact]
    public async Task DeadLetter_AddAndRequeue_Flow()
    {
        // Arrange
        await using var conn = new NpgsqlConnection(_fixture.PostgresConnectionString);
        await conn.OpenAsync();
        await CreateReliableMessagingSchemaAsync(conn);

        var deadLetterId = Guid.NewGuid();
        var tenantId = Guid.NewGuid();

        // Act: 添加死信
        await conn.ExecuteAsync(@"
            INSERT INTO dist_dead_letter_messages 
                (id, tenant_id, original_message_id, source_table, event_type, payload, error_message, total_retry_count, status, create_time)
            VALUES 
                (@Id, @TenantId, 'orig-123', 'outbox', 'TestEvent', '{}'::jsonb, '处理超时', 5, 0, @Now)",
            new { Id = deadLetterId, TenantId = tenantId, Now = DateTime.UtcNow });

        // Assert: 死信状态为 Pending
        var status = await conn.ExecuteScalarAsync<int>(
            "SELECT status FROM dist_dead_letter_messages WHERE id = @Id",
            new { Id = deadLetterId });
        status.Should().Be(0);

        // Act: 标记为已重试
        await conn.ExecuteAsync(@"
            UPDATE dist_dead_letter_messages 
            SET status = 1, reprocessed_at = @Now, reprocess_result = 'Requeued'
            WHERE id = @Id",
            new { Id = deadLetterId, Now = DateTime.UtcNow });

        // Assert: 死信状态为 Reprocessed
        status = await conn.ExecuteScalarAsync<int>(
            "SELECT status FROM dist_dead_letter_messages WHERE id = @Id",
            new { Id = deadLetterId });
        status.Should().Be(1);
    }

    [Fact]
    public async Task Outbox_RetryWithBackoff_ShouldIncrementRetryCount()
    {
        // Arrange
        await using var conn = new NpgsqlConnection(_fixture.PostgresConnectionString);
        await conn.OpenAsync();
        await CreateReliableMessagingSchemaAsync(conn);

        var messageId = Guid.NewGuid();
        await conn.ExecuteAsync(@"
            INSERT INTO dist_outbox_messages 
                (id, tenant_id, event_type, payload, status, retry_count, create_time)
            VALUES 
                (@Id, @TenantId, 'TestEvent', '{}'::jsonb, 0, 0, @Now)",
            new { Id = messageId, TenantId = Guid.NewGuid(), Now = DateTime.UtcNow });

        // Act: 模拟失败重试（3次）
        for (var i = 1; i <= 3; i++)
        {
            await conn.ExecuteAsync(@"
                UPDATE dist_outbox_messages 
                SET retry_count = retry_count + 1,
                    error_message = @Error,
                    next_retry_at = @NextRetry
                WHERE id = @Id",
                new
                {
                    Id = messageId,
                    Error = $"失败 #{i}",
                    NextRetry = DateTime.UtcNow.AddSeconds(Math.Pow(2, i))
                });
        }

        // Assert
        var result = await conn.QueryFirstAsync<OutboxRetryDto>(
            "SELECT retry_count, error_message FROM dist_outbox_messages WHERE id = @Id",
            new { Id = messageId });
        result.retry_count.Should().Be(3);
        result.error_message.Should().Be("失败 #3");
    }

    private async Task CreateReliableMessagingSchemaAsync(NpgsqlConnection conn)
    {
        await conn.ExecuteAsync(@"
            CREATE TABLE IF NOT EXISTS dist_outbox_messages (
                id                UUID PRIMARY KEY,
                tenant_id         UUID NOT NULL,
                event_type        VARCHAR(200) NOT NULL,
                payload           JSONB NOT NULL,
                routing_key       VARCHAR(200) NOT NULL DEFAULT '',
                exchange          VARCHAR(100) NOT NULL DEFAULT 'jgsy.events',
                status            INT NOT NULL DEFAULT 0,
                retry_count       INT NOT NULL DEFAULT 0,
                create_time        TIMESTAMP NOT NULL DEFAULT NOW(),
                processed_at      TIMESTAMP,
                next_retry_at     TIMESTAMP,
                error_message     TEXT,
                correlation_id    VARCHAR(64),
                trace_id          VARCHAR(64),
                lock_holder       VARCHAR(100),
                lock_until        TIMESTAMP,
                delete_at        TIMESTAMP NULL DEFAULT NULL
            );

            CREATE TABLE IF NOT EXISTS dist_reliable_inbox_messages (
                message_id        VARCHAR(64) NOT NULL,
                consumer_group    VARCHAR(100) NOT NULL DEFAULT '',
                tenant_id         UUID NOT NULL,
                event_type        VARCHAR(200) NOT NULL,
                payload           JSONB NOT NULL,
                status            INT NOT NULL DEFAULT 0,
                retry_count       INT NOT NULL DEFAULT 0,
                received_at       TIMESTAMP NOT NULL DEFAULT NOW(),
                processed_at      TIMESTAMP,
                error_message     TEXT,
                correlation_id    VARCHAR(64),
                trace_id          VARCHAR(64),
                delete_at        TIMESTAMP NULL DEFAULT NULL,
                PRIMARY KEY (message_id, consumer_group)
            );

            CREATE TABLE IF NOT EXISTS dist_dead_letter_messages (
                id                  UUID PRIMARY KEY,
                tenant_id           UUID NOT NULL,
                original_message_id VARCHAR(200) NOT NULL,
                source_table        VARCHAR(20) NOT NULL,
                event_type          VARCHAR(200) NOT NULL,
                payload             JSONB NOT NULL,
                error_message       TEXT NOT NULL,
                total_retry_count   INT NOT NULL DEFAULT 0,
                status              INT NOT NULL DEFAULT 0,
                create_time          TIMESTAMP NOT NULL DEFAULT NOW(),
                reprocessed_at      TIMESTAMP,
                reprocess_result    TEXT,
                delete_at          TIMESTAMP NULL DEFAULT NULL
            );
        ");
    }

    // DTOs
    private class OutboxResultDto
    {
        public int status { get; set; }
        public DateTime? processed_at { get; set; }
    }

    private class OutboxRetryDto
    {
        public int retry_count { get; set; }
        public string? error_message { get; set; }
    }
}
