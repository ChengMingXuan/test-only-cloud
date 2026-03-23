using System;
using System.Collections.Generic;
using System.Data.Common;
using System.Threading.Tasks;
using FluentAssertions;
using JGSY.AGI.Common.Core.Data.Dapper;
using JGSY.AGI.Settlement.Data.Repositories;
using JGSY.AGI.Settlement.Entities;
using JGSY.AGI.Settlement.Service;
using Microsoft.Data.Sqlite;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;

namespace JGSY.AGI.Test.Settlement;

/// <summary>
/// BillingService 服务层单元测试（SQLite 内存库 + 仓储 Mock）
/// </summary>
public class BillingServiceTests : IAsyncLifetime
{
    private readonly string _connString = "Data Source=:memory:;Cache=Shared";
    private DbConnection? _anchor;
    private SqliteConnectionFactory? _factory;

    public async Task InitializeAsync()
    {
        _anchor = new SqliteConnection(_connString);
        await _anchor.OpenAsync();
        await CreateSchemaAsync(_anchor);
        _factory = new SqliteConnectionFactory(_connString, _anchor);
    }

    public async Task DisposeAsync()
    {
        if (_anchor != null)
        {
            await _anchor.DisposeAsync();
        }
    }

    [Fact]
    public async Task CreateBillingAsync_ShouldInsertThroughRepository()
    {
        var repo = new Mock<IBillingDetailRepository>();
        var service = new BillingService(repo.Object, _factory!, NullLogger<BillingService>.Instance);
        var billing = new BillingDetail
        {
            Id = Guid.NewGuid(),
            TenantId = Guid.NewGuid(),
            OrderId = Guid.NewGuid(),
            OrderNumber = "NO1",
            UserId = Guid.NewGuid(),
            DeviceId = Guid.NewGuid(),
            ElectricityFee = 10m,
            ServiceFee = 1m,
            ActualAmount = 11m
        };

        var result = await service.CreateBillingAsync(billing);

        repo.Verify(r => r.InsertAsync(billing), Times.Once);
        result.Should().BeSameAs(billing);
    }

    [Fact]
    public async Task GetBillingHistoryAsync_ShouldReturnRepositoryResult()
    {
        var repo = new Mock<IBillingDetailRepository>();
        var billing = new BillingDetail
        {
            Id = Guid.NewGuid(),
            TenantId = Guid.NewGuid(),
            OrderId = Guid.NewGuid(),
            OrderNumber = "NO2",
            UserId = Guid.NewGuid(),
            DeviceId = Guid.NewGuid(),
            ElectricityFee = 8m,
            ServiceFee = 2m,
            ActualAmount = 10m
        };

        repo.Setup(r => r.GetPagedAsync(billing.UserId, null, null, "Charging", 1, 20))
            .ReturnsAsync((new List<BillingDetail> { billing }, 1));

        var service = new BillingService(repo.Object, _factory!, NullLogger<BillingService>.Instance);

        var (items, total) = await service.GetBillingHistoryAsync(billing.UserId, null, null, "Charging", 1, 20);

        total.Should().Be(1);
        items.Should().ContainSingle().Which.OrderId.Should().Be(billing.OrderId);
    }

    [Fact(Skip = "Requires PostgreSQL integration - SQLite Guid mapping issues")]
    public async Task GetMonthlyStatsAsync_ShouldRespectTenantAndDateFilters()
    {
        var repo = new Mock<IBillingDetailRepository>();
        var service = new BillingService(repo.Object, _factory!, NullLogger<BillingService>.Instance);

        var tenantA = Guid.NewGuid();
        var tenantB = Guid.NewGuid();

        await SeedMonthlyStatAsync(new DateTime(2024, 12, 1), "Charging", tenantA, totalAmount: 100m);
        await SeedMonthlyStatAsync(new DateTime(2024, 10, 1), "Charging", tenantA, totalAmount: 50m);
        await SeedMonthlyStatAsync(new DateTime(2024, 12, 1), "Charging", tenantB, totalAmount: 80m);

        var stats = await service.GetMonthlyStatsAsync(tenantA, startMonth: new DateTime(2024, 11, 1), endMonth: null);

        stats.Should().ContainSingle();
        var stat = stats[0];
        stat.month_bucket.Date.Should().Be(new DateTime(2024, 12, 1));
        stat.total_amount.Should().Be(100m);
        stat.BillingType.Should().Be("Charging");
    }

    private static async Task CreateSchemaAsync(DbConnection conn)
    {
        var cmd = conn.CreateCommand();
        cmd.CommandText = @"
CREATE TABLE billing_monthly_stats (
    month_bucket TEXT,
    BillingType TEXT,
    billing_count INTEGER,
    total_amount REAL,
    avg_amount REAL,
    total_energy REAL,
    avg_duration REAL,
    TenantId TEXT
);
";
        await cmd.ExecuteNonQueryAsync();
    }

    private async Task SeedMonthlyStatAsync(DateTime month, string billingType, Guid tenantId, decimal totalAmount)
    {
        var cmd = (SqliteCommand)_anchor!.CreateCommand();
        await using var _ = cmd;
        cmd.CommandText = @"
INSERT INTO billing_monthly_stats (month_bucket, BillingType, billing_count, total_amount, avg_amount, total_energy, avg_duration, TenantId)
VALUES ($month_bucket, $billing_type, $billing_count, $total_amount, $avg_amount, $total_energy, $avg_duration, $tenant_id);
";
        cmd.Parameters.AddWithValue("$month_bucket", month.ToString("O"));
        cmd.Parameters.AddWithValue("$billing_type", billingType);
        cmd.Parameters.AddWithValue("$billing_count", 10);
        cmd.Parameters.AddWithValue("$total_amount", totalAmount);
        cmd.Parameters.AddWithValue("$avg_amount", totalAmount / 10);
        cmd.Parameters.AddWithValue("$total_energy", 42.5m);
        cmd.Parameters.AddWithValue("$avg_duration", 12.5);
        cmd.Parameters.AddWithValue("$tenant_id", tenantId.ToString());
        await cmd.ExecuteNonQueryAsync();
    }

    private sealed class SqliteConnectionFactory : IDbConnectionFactory
    {
        private readonly string _connectionString;
        private readonly DbConnection _anchor;

        public SqliteConnectionFactory(string connectionString, DbConnection anchor)
        {
            _connectionString = connectionString;
            _anchor = anchor;
        }

        public string ConnectionString => _connectionString;

        public DbConnection CreateConnection()
        {
            // 返回 anchor 连接以确保使用同一个共享内存数据库
            if (_anchor.State != System.Data.ConnectionState.Open)
            {
                _anchor.Open();
            }
            return _anchor;
        }
    }
}
