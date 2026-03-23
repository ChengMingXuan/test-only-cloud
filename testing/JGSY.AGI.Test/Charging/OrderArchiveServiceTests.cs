using System;
using System.Collections.Generic;
using System.Data.Common;
using System.Threading.Tasks;
using FluentAssertions;
using JGSY.AGI.Charging.Data;
using JGSY.AGI.Charging.Service;
using JGSY.AGI.Common.Core.Data.Dapper;
using Microsoft.Data.Sqlite;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;

namespace JGSY.AGI.Test.Charging;

/// <summary>
/// OrderArchiveService 单元测试（多分片归档逻辑）
/// </summary>
public class OrderArchiveServiceTests : IAsyncLifetime
{
    private readonly string _connString = "Data Source=:memory:;Cache=Shared";
    private DbConnection? _anchor;
    private MultiShardConnectionFactory? _factory;

    public async Task InitializeAsync()
    {
        _anchor = new SqliteConnection(_connString);
        await _anchor.OpenAsync();
        await CreateSchemaAsync(_anchor);
        _factory = new MultiShardConnectionFactory(_connString, _anchor);
    }

    public async Task DisposeAsync()
    {
        if (_anchor != null)
        {
            await _anchor.DisposeAsync();
        }
    }

    [Fact]
    public async Task ArchiveOldOrdersAsync_ShouldSoftDeleteCompletedOrders()
    {
        var tenantId = Guid.NewGuid();

        // 种子数据：一个旧的已完成订单和一个新的订单
        await SeedOrderAsync(Guid.NewGuid(), tenantId, orderState: "5", endTime: DateTime.UtcNow.AddDays(-60));
        await SeedOrderAsync(Guid.NewGuid(), tenantId, orderState: "5", endTime: DateTime.UtcNow.AddDays(-10));
        await SeedOrderAsync(Guid.NewGuid(), tenantId, orderState: "1", endTime: null);

        var service = new OrderArchiveService(_factory!, NullLogger<OrderArchiveService>.Instance);

        var result = await service.ArchiveOldOrdersAsync(archiveDays: 30);

        // 只有一个分片（索引0），应该归档1条记录
        result.Should().ContainKey(0);
        result[0].Should().Be(1);
    }

    [Fact(Skip = "Requires PostgreSQL integration - SQLite Guid mapping issues")]
    public async Task RestoreOrderFromArchiveAsync_ShouldRestoreDeletedOrder()
    {
        var tenantId = Guid.NewGuid();
        var orderId = Guid.NewGuid();
        var orderNumber = "RESTORE001";

        // 种子数据：一个已软删除的订单
        await SeedOrderAsync(orderId, tenantId, orderState: "5", endTime: DateTime.UtcNow.AddDays(-60), DeleteAt: DateTime.UtcNow, orderNumber: orderNumber);

        var service = new OrderArchiveService(_factory!, NullLogger<OrderArchiveService>.Instance);

        var restored = await service.RestoreOrderFromArchiveAsync(orderNumber, tenantId);

        restored.Should().NotBeNull();
        restored!.OrderNumber.Should().Be(orderNumber);
        restored.DeleteAt.Should().BeNull();
    }

    [Fact]
    public async Task RestoreOrderFromArchiveAsync_ShouldReturnNull_WhenNotFound()
    {
        var service = new OrderArchiveService(_factory!, NullLogger<OrderArchiveService>.Instance);

        var restored = await service.RestoreOrderFromArchiveAsync("NONEXISTENT", Guid.NewGuid());

        restored.Should().BeNull();
    }

    private static async Task CreateSchemaAsync(DbConnection conn)
    {
        var cmd = conn.CreateCommand();
        cmd.CommandText = @"
CREATE TABLE charging_order (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
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
    consume_power REAL,
    order_type TEXT,
    delete_at TEXT DEFAULT NULL,
    create_time TEXT,
    update_time TEXT
);
";
        await cmd.ExecuteNonQueryAsync();
    }

    private async Task SeedOrderAsync(Guid id, Guid tenantId, string orderState, DateTime? endTime, DateTime? DeleteAt = (DateTime?)null, string? orderNumber = null)
    {
        var cmd = (SqliteCommand)_anchor!.CreateCommand();
        await using var _ = cmd;
        cmd.CommandText = @"
INSERT INTO charging_order 
    (id, tenant_id, order_number, order_state, charge_status, is_fee, start_time, end_time, order_type, delete_at, create_time, update_time)
VALUES 
    ($id, $tenant_id, $order_number, $order_state, '9003', '2001', $start_time, $end_time, '3001', $delete_at, $now, $now);
";
        cmd.Parameters.AddWithValue("$id", id.ToString());
        cmd.Parameters.AddWithValue("$tenant_id", tenantId.ToString());
        cmd.Parameters.AddWithValue("$order_number", orderNumber ?? $"ORD{DateTime.UtcNow.Ticks}");
        cmd.Parameters.AddWithValue("$order_state", orderState);
        cmd.Parameters.AddWithValue("$start_time", DateTime.UtcNow.AddDays(-70).ToString("O"));
        cmd.Parameters.AddWithValue("$end_time", (object?)endTime?.ToString("O") ?? DBNull.Value);
        cmd.Parameters.AddWithValue("$delete_at", DeleteAt != null ? (object)DeleteAt.Value.ToString("O") : DBNull.Value);
        cmd.Parameters.AddWithValue("$now", DateTime.UtcNow.ToString("O"));
        await cmd.ExecuteNonQueryAsync();
    }

    /// <summary>
    /// 模拟多分片连接工厂（实际只有一个分片）
    /// </summary>
    private sealed class MultiShardConnectionFactory : IShardedConnectionFactory
    {
        private readonly string _connectionString;
        private readonly DbConnection _anchor;

        public MultiShardConnectionFactory(string connectionString, DbConnection anchor)
        {
            _connectionString = connectionString;
            _anchor = anchor;
        }

        public DbConnection CreateReadConnection(Guid tenantId)
        {
            if (_anchor.State != System.Data.ConnectionState.Open)
                _anchor.Open();
            return _anchor;
        }

        public DbConnection CreateWriteConnection(Guid tenantId) => CreateReadConnection(tenantId);
        public DbConnection CreateConnectionForShard(int shardIndex, bool isRead = false) => CreateReadConnection(Guid.Empty);
        public int GetShardIndex(Guid tenantId) => 0;

        public IEnumerable<(int ShardIndex, DbConnection Connection)> GetAllShardConnections(bool isRead = true)
        {
            yield return (0, _anchor);
        }
    }
}
