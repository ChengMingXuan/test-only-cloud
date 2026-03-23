using System.Text;
using FluentAssertions;
using JGSY.AGI.Common.Core.Crypto;
using JGSY.AGI.Common.Core.Observability;
using JGSY.AGI.Common.Hosting.Audit;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Moq;
using Xunit;

namespace JGSY.AGI.Test.Common.Compliance;

/// <summary>
/// 本地审计日志服务测试
/// 合规项：DEPLOY-008 / AUDIT-005 / GB/T 36572
/// 覆盖：JSONL 持久化写入、批量写入、查询过滤、归档、SM3 链式哈希防篡改
/// </summary>
public class LocalAuditLogServiceTests : IDisposable
{
    private readonly string _testDir;
    private readonly Mock<ISM3HashService> _sm3Mock;
    private readonly Mock<ILogger<LocalAuditLogService>> _loggerMock;
    private readonly Mock<ILogger<AuditIntegrityService>> _integrityLoggerMock;
    private readonly IAuditIntegrityService _integrityService;
    private readonly LocalAuditLogService _sut;

    public LocalAuditLogServiceTests()
    {
        _testDir = Path.Combine(Path.GetTempPath(), $"audit-test-{Guid.NewGuid():N}");
        _sm3Mock = new Mock<ISM3HashService>();
        _sm3Mock.Setup(s => s.Hash(It.IsAny<byte[]>()))
            .Returns((byte[] data) => System.Security.Cryptography.SHA256.HashData(data));
        _loggerMock = new Mock<ILogger<LocalAuditLogService>>();
        _integrityLoggerMock = new Mock<ILogger<AuditIntegrityService>>();

        _integrityService = new AuditIntegrityService(_sm3Mock.Object, _integrityLoggerMock.Object);

        var options = Options.Create(new LocalAuditOptions
        {
            StoragePath = _testDir,
            RetentionDays = 180,
            MaxEntriesPerFile = 10000,
            EnableChainHash = true,
        });

        _sut = new LocalAuditLogService(_loggerMock.Object, _integrityService, options);
    }

    public void Dispose()
    {
        _sut.Dispose();
        if (Directory.Exists(_testDir))
            Directory.Delete(_testDir, recursive: true);
    }

    #region 写入测试

    [Fact]
    public async Task WriteAsync_写入单条审计日志_文件应包含JSONL记录()
    {
        var entry = CreateEntry("login", "auth:session");

        await _sut.WriteAsync(entry);

        var files = Directory.GetFiles(_testDir, "audit-*.jsonl");
        files.Should().HaveCount(1);
        var content = await File.ReadAllTextAsync(files[0]);
        content.Should().Contain(entry.Action);
        content.Should().Contain(entry.Resource);
    }

    [Fact]
    public async Task WriteAsync_启用链式哈希_应填充ChainHash字段()
    {
        var entry = CreateEntry("update", "device:config");

        await _sut.WriteAsync(entry);

        entry.ChainHash.Should().NotBeNullOrEmpty("启用链式哈希时应自动计算");
    }

    [Fact]
    public async Task WriteAsync_连续写入_链式哈希应形成链()
    {
        var entry1 = CreateEntry("create", "user");
        var entry2 = CreateEntry("update", "user");

        await _sut.WriteAsync(entry1);
        await _sut.WriteAsync(entry2);

        entry1.ChainHash.Should().NotBeNullOrEmpty();
        entry2.ChainHash.Should().NotBeNullOrEmpty();
        entry2.PreviousHash.Should().NotBeNullOrEmpty();
        entry2.PreviousHash.Should().Be(entry1.ChainHash, "第二条日志应引用第一条的哈希");
    }

    [Fact]
    public async Task WriteBatchAsync_批量写入多条_文件应包含所有记录()
    {
        var entries = new List<LocalAuditEntry>
        {
            CreateEntry("create", "device"),
            CreateEntry("update", "device"),
            CreateEntry("delete", "device"),
        };

        await _sut.WriteBatchAsync(entries);

        var files = Directory.GetFiles(_testDir, "audit-*.jsonl");
        files.Should().HaveCount(1);
        var lines = (await File.ReadAllLinesAsync(files[0]))
            .Where(l => !string.IsNullOrWhiteSpace(l)).ToArray();
        lines.Should().HaveCount(3);
    }

    [Fact]
    public async Task WriteBatchAsync_批量写入_每条都有链式哈希()
    {
        var entries = new List<LocalAuditEntry>
        {
            CreateEntry("op1", "res1"),
            CreateEntry("op2", "res2"),
        };

        await _sut.WriteBatchAsync(entries);

        entries.Should().OnlyContain(e => !string.IsNullOrEmpty(e.ChainHash));
    }

    #endregion

    #region 查询测试

    [Fact]
    public async Task QueryAsync_按TenantId过滤_应返回匹配记录()
    {
        var tenantId = Guid.NewGuid();
        var entry1 = CreateEntry("create", "device", tenantId);
        var entry2 = CreateEntry("update", "device", Guid.NewGuid());
        await _sut.WriteAsync(entry1);
        await _sut.WriteAsync(entry2);

        var filter = new AuditQueryFilter { TenantId = tenantId };
        var results = await _sut.QueryAsync(filter);

        results.Should().HaveCount(1);
        results[0].TenantId.Should().Be(tenantId);
    }

    [Fact]
    public async Task QueryAsync_按Action过滤_应返回匹配记录()
    {
        await _sut.WriteAsync(CreateEntry("login", "auth"));
        await _sut.WriteAsync(CreateEntry("logout", "auth"));

        var filter = new AuditQueryFilter { Action = "login" };
        var results = await _sut.QueryAsync(filter);

        results.Should().HaveCount(1);
        results[0].Action.Should().Be("login");
    }

    [Fact]
    public async Task QueryAsync_目录不存在_应返回空列表()
    {
        var tempDir = Path.Combine(Path.GetTempPath(), $"nonexist-{Guid.NewGuid():N}");
        var options = Options.Create(new LocalAuditOptions { StoragePath = tempDir });
        using var sut = new LocalAuditLogService(
            _loggerMock.Object, _integrityService, options);
        // 删除构造函数创建的目录
        if (Directory.Exists(tempDir)) Directory.Delete(tempDir, true);

        var results = await sut.QueryAsync(new AuditQueryFilter());

        results.Should().BeEmpty();
    }

    [Fact]
    public async Task QueryAsync_PageSize限制_应最多返回指定条数()
    {
        for (int i = 0; i < 5; i++)
            await _sut.WriteAsync(CreateEntry($"op-{i}", "resource"));

        var filter = new AuditQueryFilter { PageSize = 3 };
        var results = await _sut.QueryAsync(filter);

        results.Should().HaveCountLessOrEqualTo(3);
    }

    #endregion

    #region 统计测试

    [Fact]
    public async Task GetStatsAsync_写入后_TotalCount应递增()
    {
        await _sut.WriteAsync(CreateEntry("a", "b"));
        await _sut.WriteAsync(CreateEntry("c", "d"));

        var stats = await _sut.GetStatsAsync();

        stats.TotalCount.Should().Be(2);
        stats.RetentionDays.Should().Be(180);
    }

    [Fact]
    public async Task GetStatsAsync_目录为空_存储大小应为0()
    {
        var stats = await _sut.GetStatsAsync();

        stats.TotalCount.Should().Be(0);
        stats.StorageSizeBytes.Should().Be(0);
    }

    #endregion

    #region 归档测试

    [Fact]
    public async Task ArchiveAsync_旧文件应移到归档目录()
    {
        // 创建一个"旧"日志文件
        var oldFile = Path.Combine(_testDir, "audit-2024-01-01.jsonl");
        await File.WriteAllTextAsync(oldFile, "{}");
        File.SetCreationTimeUtc(oldFile, DateTime.UtcNow.AddDays(-200));

        await _sut.ArchiveAsync(DateTimeOffset.UtcNow.AddDays(-100));

        var archiveDir = Path.Combine(_testDir, "archive");
        Directory.Exists(archiveDir).Should().BeTrue();
        File.Exists(Path.Combine(archiveDir, "audit-2024-01-01.jsonl")).Should().BeTrue();
    }

    #endregion

    #region AuditIntegrityService 测试

    [Fact]
    public async Task ComputeChainHash_首条日志_PreviousHash应为null()
    {
        var entry = CreateEntry("first", "entry");

        var hash = await _integrityService.ComputeChainHashAsync(entry);

        hash.Should().NotBeNullOrEmpty();
        entry.PreviousHash.Should().BeNull("首条日志的前一条哈希应为 null");
    }

    [Fact]
    public async Task ComputeChainHash_第二条_PreviousHash应等于首条哈希()
    {
        var entry1 = CreateEntry("first", "entry");
        var entry2 = CreateEntry("second", "entry");

        var hash1 = await _integrityService.ComputeChainHashAsync(entry1);
        var hash2 = await _integrityService.ComputeChainHashAsync(entry2);

        entry2.PreviousHash.Should().Be(hash1);
        hash2.Should().NotBe(hash1, "不同条目的哈希值应不同");
    }

    [Fact]
    public async Task VerifyChainAsync_空范围_应返回Valid()
    {
        var result = await _integrityService.VerifyChainAsync(
            DateTimeOffset.UtcNow.AddDays(-1), DateTimeOffset.UtcNow);

        result.IsValid.Should().BeTrue();
        result.BrokenCount.Should().Be(0);
    }

    [Fact]
    public async Task GetLastValidHashAsync_未写入_应返回null()
    {
        // 创建新的 integrityService 实例以确保空状态
        var svc = new AuditIntegrityService(_sm3Mock.Object, _integrityLoggerMock.Object);

        var hash = await svc.GetLastValidHashAsync();

        hash.Should().BeNull();
    }

    [Fact]
    public async Task GetLastValidHashAsync_写入后_应返回最新哈希()
    {
        var svc = new AuditIntegrityService(_sm3Mock.Object, _integrityLoggerMock.Object);
        var entry = CreateEntry("action", "resource");
        var computed = await svc.ComputeChainHashAsync(entry);

        var lastHash = await svc.GetLastValidHashAsync();

        lastHash.Should().Be(computed);
    }

    #endregion

    #region 配置测试

    [Fact]
    public void LocalAuditOptions_默认值_应符合等保要求()
    {
        var opts = new LocalAuditOptions();

        opts.RetentionDays.Should().BeGreaterOrEqualTo(180, "GB/T 22239 要求审计日志至少保留 6 个月");
        opts.EnableChainHash.Should().BeTrue("默认应启用链式哈希防篡改");
        opts.StoragePath.Should().NotBeNullOrEmpty();
    }

    #endregion

    #region 辅助方法

    private static LocalAuditEntry CreateEntry(string action, string resource, Guid? tenantId = null)
    {
        return new LocalAuditEntry
        {
            Id = Guid.NewGuid(),
            TenantId = tenantId ?? Guid.NewGuid(),
            UserId = "user-001",
            UserName = "测试用户",
            Action = action,
            Resource = resource,
            EventType = "操作",
            Success = true,
            Timestamp = DateTimeOffset.UtcNow,
        };
    }

    #endregion
}
