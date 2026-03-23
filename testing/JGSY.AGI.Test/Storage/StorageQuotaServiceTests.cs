using Xunit;
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using JGSY.AGI.Common.Core.Interfaces;
using JGSY.AGI.Storage.Business;
using JGSY.AGI.Storage.Data.Repositories;
using JGSY.AGI.Storage.Entities;
using JGSY.AGI.Storage.Interfaces;

namespace JGSY.AGI.Test.Storage;

/// <summary>StorageQuotaService 单元测试</summary>
public class StorageQuotaServiceTests
{
    private readonly Mock<IStorageQuotaRepository> _repoMock = new();
    private readonly Mock<ITenantContext> _tenantMock = new();
    private readonly StorageQuotaService _sut;

    public StorageQuotaServiceTests()
    {
        _sut = new StorageQuotaService(
            _repoMock.Object,
            _tenantMock.Object,
            NullLogger<StorageQuotaService>.Instance);
    }

    // ========== GetQuotaAsync ==========

    [Fact]
    public async Task GetQuotaAsync_委托仓储返回结果()
    {
        var tenantId = Guid.NewGuid();
        var quota = new StorageQuota { Id = Guid.NewGuid(), TenantId = tenantId, TotalQuota = 1024 };
        _repoMock.Setup(r => r.GetByTenantIdAsync(tenantId)).ReturnsAsync(quota);

        var result = await _sut.GetQuotaAsync(tenantId);

        result.Should().BeSameAs(quota);
    }

    [Fact]
    public async Task GetQuotaAsync_不存在返回Null()
    {
        _repoMock.Setup(r => r.GetByTenantIdAsync(It.IsAny<Guid>())).ReturnsAsync((StorageQuota?)null);

        var result = await _sut.GetQuotaAsync(Guid.NewGuid());

        result.Should().BeNull();
    }

    // ========== SetQuotaAsync ==========

    [Fact]
    public async Task SetQuotaAsync_不存在时创建新配额()
    {
        var tenantId = Guid.NewGuid();
        _repoMock.Setup(r => r.GetByTenantIdAsync(tenantId)).ReturnsAsync((StorageQuota?)null);

        var request = new SetQuotaRequest
        {
            TenantId = tenantId,
            TotalQuota = 10737418240, // 10GB
            FileCountLimit = 1000,
            MaxFileSize = 104857600, // 100MB
            AllowedExtensions = ".jpg,.png,.pdf",
            WarningThreshold = 85
        };

        var result = await _sut.SetQuotaAsync(request);

        result.TenantId.Should().Be(tenantId);
        result.TotalQuota.Should().Be(10737418240);
        result.FileCountLimit.Should().Be(1000);
        result.MaxFileSize.Should().Be(104857600);
        result.AllowedExtensions.Should().Be(".jpg,.png,.pdf");
        result.WarningThreshold.Should().Be(85);
        result.UsedSpace.Should().Be(0);
        result.FileCount.Should().Be(0);
        result.IsEnabled.Should().BeTrue();
        result.Id.Should().NotBeEmpty();

        _repoMock.Verify(r => r.UpsertAsync(It.Is<StorageQuota>(q => q.TenantId == tenantId)), Times.Once);
    }

    [Fact]
    public async Task SetQuotaAsync_已存在时更新字段()
    {
        var tenantId = Guid.NewGuid();
        var existing = new StorageQuota
        {
            Id = Guid.NewGuid(),
            TenantId = tenantId,
            TotalQuota = 5000,
            UsedSpace = 2000,
            FileCount = 50,
            IsEnabled = true
        };
        _repoMock.Setup(r => r.GetByTenantIdAsync(tenantId)).ReturnsAsync(existing);

        var request = new SetQuotaRequest
        {
            TenantId = tenantId,
            TotalQuota = 20000,
            FileCountLimit = 500,
            MaxFileSize = 2048,
            WarningThreshold = 90
        };

        var result = await _sut.SetQuotaAsync(request);

        // 更新的字段
        result.TotalQuota.Should().Be(20000);
        result.FileCountLimit.Should().Be(500);
        result.MaxFileSize.Should().Be(2048);
        result.WarningThreshold.Should().Be(90);
        // 保留原有的已用空间和文件数
        result.UsedSpace.Should().Be(2000);
        result.FileCount.Should().Be(50);

        _repoMock.Verify(r => r.UpsertAsync(existing), Times.Once);
    }

    // ========== CheckQuotaAsync ==========

    [Fact]
    public async Task CheckQuotaAsync_无配额时允许上传()
    {
        var tenantId = Guid.NewGuid();
        _repoMock.Setup(r => r.GetByTenantIdAsync(tenantId)).ReturnsAsync((StorageQuota?)null);

        var result = await _sut.CheckQuotaAsync(tenantId, 1024);

        result.IsAllowed.Should().BeTrue();
        result.AvailableSpace.Should().Be(long.MaxValue);
        result.AvailableFileCount.Should().Be(int.MaxValue);
    }

    [Fact]
    public async Task CheckQuotaAsync_配额禁用时允许上传()
    {
        var tenantId = Guid.NewGuid();
        var quota = new StorageQuota { TenantId = tenantId, IsEnabled = false };
        _repoMock.Setup(r => r.GetByTenantIdAsync(tenantId)).ReturnsAsync(quota);

        var result = await _sut.CheckQuotaAsync(tenantId, 1024);

        result.IsAllowed.Should().BeTrue();
        result.AvailableSpace.Should().Be(long.MaxValue);
    }

    [Fact]
    public async Task CheckQuotaAsync_超出单文件大小限制时拒绝()
    {
        var tenantId = Guid.NewGuid();
        var quota = new StorageQuota
        {
            TenantId = tenantId,
            IsEnabled = true,
            MaxFileSize = 1024, // 1KB
            TotalQuota = 1048576,
            UsedSpace = 0
        };
        _repoMock.Setup(r => r.GetByTenantIdAsync(tenantId)).ReturnsAsync(quota);

        var result = await _sut.CheckQuotaAsync(tenantId, 2048); // 2KB > 1KB

        result.IsAllowed.Should().BeFalse();
        result.Reason.Should().Contain("文件大小超出限制");
    }

    [Fact]
    public async Task CheckQuotaAsync_总空间不足时拒绝()
    {
        var tenantId = Guid.NewGuid();
        var quota = new StorageQuota
        {
            TenantId = tenantId,
            IsEnabled = true,
            TotalQuota = 10000,
            UsedSpace = 9500  // 只剩500
        };
        _repoMock.Setup(r => r.GetByTenantIdAsync(tenantId)).ReturnsAsync(quota);

        var result = await _sut.CheckQuotaAsync(tenantId, 1000); // 需要1000 > 500

        result.IsAllowed.Should().BeFalse();
        result.Reason.Should().Contain("存储空间不足");
        result.AvailableSpace.Should().Be(500);
    }

    [Fact]
    public async Task CheckQuotaAsync_文件数量达上限时拒绝()
    {
        var tenantId = Guid.NewGuid();
        var quota = new StorageQuota
        {
            TenantId = tenantId,
            IsEnabled = true,
            TotalQuota = 100000,
            UsedSpace = 0,
            FileCountLimit = 100,
            FileCount = 100  // 已满
        };
        _repoMock.Setup(r => r.GetByTenantIdAsync(tenantId)).ReturnsAsync(quota);

        var result = await _sut.CheckQuotaAsync(tenantId, 100);

        result.IsAllowed.Should().BeFalse();
        result.Reason.Should().Contain("文件数量已达上限");
        result.AvailableFileCount.Should().Be(0);
    }

    [Fact]
    public async Task CheckQuotaAsync_允许上传且触发预警()
    {
        var tenantId = Guid.NewGuid();
        var quota = new StorageQuota
        {
            TenantId = tenantId,
            IsEnabled = true,
            TotalQuota = 10000,
            UsedSpace = 7500,
            FileCount = 5,
            FileCountLimit = 100,
            WarningThreshold = 80  // 80%
        };
        _repoMock.Setup(r => r.GetByTenantIdAsync(tenantId)).ReturnsAsync(quota);

        // 上传500字节后使用率 = (7500+500)/10000 = 80%，达到阈值
        var result = await _sut.CheckQuotaAsync(tenantId, 500);

        result.IsAllowed.Should().BeTrue();
        result.IsWarning.Should().BeTrue();
        result.AvailableSpace.Should().Be(2000); // 10000-7500-500
        result.AvailableFileCount.Should().Be(94); // 100 - 5 - 1
    }

    [Fact]
    public async Task CheckQuotaAsync_允许上传且无预警()
    {
        var tenantId = Guid.NewGuid();
        var quota = new StorageQuota
        {
            TenantId = tenantId,
            IsEnabled = true,
            TotalQuota = 100000,
            UsedSpace = 1000,
            FileCount = 2,
            WarningThreshold = 80
        };
        _repoMock.Setup(r => r.GetByTenantIdAsync(tenantId)).ReturnsAsync(quota);

        // 上传100字节后使用率 = (1000+100)/100000 = 1.1%，远未达阈值
        var result = await _sut.CheckQuotaAsync(tenantId, 100);

        result.IsAllowed.Should().BeTrue();
        result.IsWarning.Should().BeFalse();
    }

    [Fact]
    public async Task CheckQuotaAsync_无文件数量限制时AvailableFileCount为MaxValue()
    {
        var tenantId = Guid.NewGuid();
        var quota = new StorageQuota
        {
            TenantId = tenantId,
            IsEnabled = true,
            TotalQuota = 100000,
            UsedSpace = 0,
            FileCountLimit = null,
            WarningThreshold = 80
        };
        _repoMock.Setup(r => r.GetByTenantIdAsync(tenantId)).ReturnsAsync(quota);

        var result = await _sut.CheckQuotaAsync(tenantId, 100);

        result.IsAllowed.Should().BeTrue();
        result.AvailableFileCount.Should().Be(int.MaxValue);
    }

    // ========== UpdateUsedSpaceAsync ==========

    [Fact]
    public async Task UpdateUsedSpaceAsync_委托仓储()
    {
        var tenantId = Guid.NewGuid();

        await _sut.UpdateUsedSpaceAsync(tenantId, 1024, 1);

        _repoMock.Verify(r => r.UpdateUsedSpaceAsync(tenantId, 1024, 1), Times.Once);
    }

    // ========== RecalculateUsedSpaceAsync ==========

    [Fact]
    public async Task RecalculateUsedSpaceAsync_委托仓储()
    {
        var tenantId = Guid.NewGuid();
        _repoMock.Setup(r => r.RecalculateUsedSpaceAsync(tenantId)).ReturnsAsync((5000L, 10));

        await _sut.RecalculateUsedSpaceAsync(tenantId);

        _repoMock.Verify(r => r.RecalculateUsedSpaceAsync(tenantId), Times.Once);
    }
}
