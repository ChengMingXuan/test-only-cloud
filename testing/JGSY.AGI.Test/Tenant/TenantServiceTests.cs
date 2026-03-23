using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;
using JGSY.AGI.Common.Core.Data.Dapper;
using JGSY.AGI.Common.Core.Exceptions;
using JGSY.AGI.Common.Core.Interfaces;
using JGSY.AGI.Tenant.Business;
using JGSY.AGI.Tenant.Data;
using JGSY.AGI.Tenant.Entities;
using JGSY.AGI.Tenant.Interfaces;
using TenantEntity = JGSY.AGI.Tenant.Entities.Tenant;

namespace JGSY.AGI.Test.Tenant;

/// <summary>
/// 租户服务单元测试
/// </summary>
public class TenantServiceTests
{
    private readonly Mock<ITenantRepository> _repoMock;
    private readonly Mock<ICacheManager> _cacheMock;
    private readonly TenantService _service;

    public TenantServiceTests()
    {
        _repoMock = new Mock<ITenantRepository>();
        _cacheMock = new Mock<ICacheManager>();

        // TenantDbContext 需要 IDbConnectionFactory，此处传入 mock
        var connFactoryMock = new Mock<IDbConnectionFactory>();
        var dbContext = new TenantDbContext(connFactoryMock.Object);

        _service = new TenantService(
            _repoMock.Object,
            dbContext,
            _cacheMock.Object,
            NullLogger<TenantService>.Instance);
    }

    #region CreateTenantAsync

    [Fact]
    public async Task CreateTenantAsync_DuplicateName_ThrowsConflictException()
    {
        // Arrange
        _repoMock.Setup(r => r.ExistsByNameAsync("已存在租户", It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var request = new TenantCreateRequest
        {
            TenantName = "已存在租户",
            TenantDomain = "new.domain.com",
            TenantCode = "NEW001"
        };

        // Act & Assert
        await _service.Invoking(s => s.CreateTenantAsync(request, Guid.NewGuid()))
            .Should().ThrowAsync<ConflictException>()
            .WithMessage("*已存在*");
    }

    [Fact]
    public async Task CreateTenantAsync_DuplicateDomain_ThrowsConflictException()
    {
        // Arrange
        _repoMock.Setup(r => r.ExistsByNameAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(false);
        _repoMock.Setup(r => r.ExistsByDomainAsync("existing.domain.com", It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var request = new TenantCreateRequest
        {
            TenantName = "新租户",
            TenantDomain = "existing.domain.com",
            TenantCode = "NEW001"
        };

        // Act & Assert
        await _service.Invoking(s => s.CreateTenantAsync(request, Guid.NewGuid()))
            .Should().ThrowAsync<ConflictException>()
            .WithMessage("*域名*已存在*");
    }

    [Fact]
    public async Task CreateTenantAsync_DuplicateCode_ThrowsConflictException()
    {
        // Arrange
        _repoMock.Setup(r => r.ExistsByNameAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(false);
        _repoMock.Setup(r => r.ExistsByDomainAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(false);
        _repoMock.Setup(r => r.ExistsByCodeAsync("EXIST01", It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var request = new TenantCreateRequest
        {
            TenantName = "新租户",
            TenantDomain = "new.domain.com",
            TenantCode = "EXIST01"
        };

        // Act & Assert
        await _service.Invoking(s => s.CreateTenantAsync(request, Guid.NewGuid()))
            .Should().ThrowAsync<ConflictException>()
            .WithMessage("*代码*已存在*");
    }

    #endregion

    #region GetTenantByIdAsync

    [Fact]
    public async Task GetTenantByIdAsync_CacheHit_ReturnsCachedTenant()
    {
        // Arrange
        var tenantId = Guid.NewGuid();
        var cachedDto = new TenantDto { Id = tenantId, Name = "缓存租户" };
        _cacheMock.Setup(c => c.GetAsync<TenantDto>($"tenant:{tenantId}", It.IsAny<CancellationToken>()))
            .ReturnsAsync(cachedDto);

        // Act
        var result = await _service.GetTenantByIdAsync(tenantId);

        // Assert
        result.Should().NotBeNull();
        result!.Name.Should().Be("缓存租户");
        // 不应该访问仓储
        _repoMock.Verify(r => r.GetByIdWithQuotaAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()), Times.Never);
    }

    [Fact]
    public async Task GetTenantByIdAsync_CacheMiss_QueriesRepoAndCaches()
    {
        // Arrange
        var tenantId = Guid.NewGuid();
        _cacheMock.Setup(c => c.GetAsync<TenantDto>($"tenant:{tenantId}", It.IsAny<CancellationToken>()))
            .ReturnsAsync((TenantDto?)null);

        var tenant = new TenantEntity
        {
            Id = tenantId,
            TenantId = tenantId,
            TenantName = "测试租户",
            TenantDomain = "test.com",
            TenantCode = "TEST01",
            Status = (int)TenantStatus.Active,
            IsolationMode = (int)IsolationMode.Logical,
            CreateTime = DateTime.UtcNow,
            UpdateTime = DateTime.UtcNow
        };
        _repoMock.Setup(r => r.GetByIdWithQuotaAsync(tenantId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(tenant);

        // Act
        var result = await _service.GetTenantByIdAsync(tenantId);

        // Assert
        result.Should().NotBeNull();
        result!.Name.Should().Be("测试租户");

        // 应写入缓存
        _cacheMock.Verify(c => c.SetAsync(
            $"tenant:{tenantId}",
            It.Is<TenantDto>(d => d.Name == "测试租户"),
            TimeSpan.FromHours(1),
            It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task GetTenantByIdAsync_NotFound_ReturnsNull()
    {
        // Arrange
        var tenantId = Guid.NewGuid();
        _cacheMock.Setup(c => c.GetAsync<TenantDto>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((TenantDto?)null);
        _repoMock.Setup(r => r.GetByIdWithQuotaAsync(tenantId, It.IsAny<CancellationToken>()))
            .ReturnsAsync((TenantEntity?)null);

        // Act
        var result = await _service.GetTenantByIdAsync(tenantId);

        // Assert
        result.Should().BeNull();
    }

    #endregion

    #region GetTenantByDomainAsync

    [Fact]
    public async Task GetTenantByDomainAsync_CacheHit_ReturnsCached()
    {
        // Arrange
        var cachedDto = new TenantDto { Domain = "test.com" };
        _cacheMock.Setup(c => c.GetAsync<TenantDto>("tenant:domain:test.com", It.IsAny<CancellationToken>()))
            .ReturnsAsync(cachedDto);

        // Act
        var result = await _service.GetTenantByDomainAsync("test.com");

        // Assert
        result.Should().NotBeNull();
        result!.Domain.Should().Be("test.com");
    }

    [Fact]
    public async Task GetTenantByDomainAsync_NotFound_ReturnsNull()
    {
        // Arrange
        _cacheMock.Setup(c => c.GetAsync<TenantDto>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((TenantDto?)null);
        _repoMock.Setup(r => r.GetByDomainAsync("unknown.com", It.IsAny<CancellationToken>()))
            .ReturnsAsync((TenantEntity?)null);

        // Act
        var result = await _service.GetTenantByDomainAsync("unknown.com");

        // Assert
        result.Should().BeNull();
    }

    #endregion

    #region GetStatisticsAsync

    [Fact]
    public async Task GetStatisticsAsync_DelegatesToRepository()
    {
        // Arrange
        var expected = new TenantStatistics { TotalCount = 50, ActiveCount = 40 };
        _repoMock.Setup(r => r.GetStatisticsAsync(It.IsAny<CancellationToken>()))
            .ReturnsAsync(expected);

        // Act
        var result = await _service.GetStatisticsAsync();

        // Assert
        result.TotalCount.Should().Be(50);
        result.ActiveCount.Should().Be(40);
    }

    #endregion

    #region GetActiveTenantsAsync

    [Fact]
    public async Task GetActiveTenantsAsync_ReturnsActiveTenantDtos()
    {
        // Arrange
        var tenants = new List<TenantEntity>
        {
            CreateTestTenant("租户A", "a.com", "A001"),
            CreateTestTenant("租户B", "b.com", "B001")
        };
        _repoMock.Setup(r => r.GetActiveTenantsAsync(It.IsAny<CancellationToken>()))
            .ReturnsAsync(tenants);

        // Act
        var result = await _service.GetActiveTenantsAsync();

        // Assert
        result.Should().HaveCount(2);
    }

    #endregion

    #region GetExpiringTenantsAsync

    [Fact]
    public async Task GetExpiringTenantsAsync_ReturnsTenantsSoonExpiring()
    {
        // Arrange
        var tenants = new List<TenantEntity>
        {
            CreateTestTenant("将过期租户", "expire.com", "EXP01")
        };
        _repoMock.Setup(r => r.GetExpiringTenantsAsync(30, It.IsAny<CancellationToken>()))
            .ReturnsAsync(tenants);

        // Act
        var result = await _service.GetExpiringTenantsAsync(30);

        // Assert
        result.Should().HaveCount(1);
    }

    #endregion

    #region BatchUpdateStatusAsync

    [Fact]
    public async Task BatchUpdateStatusAsync_DelegatesToRepoAndClearsCache()
    {
        // Arrange
        var tenantIds = new List<Guid> { Guid.NewGuid(), Guid.NewGuid() };
        var operatorId = Guid.NewGuid();
        _repoMock.Setup(r => r.UpdateStatusBatchAsync(tenantIds, TenantStatus.Suspended, It.IsAny<CancellationToken>()))
            .ReturnsAsync(2);

        _cacheMock.Setup(c => c.RemoveAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.BatchUpdateStatusAsync(tenantIds, TenantStatus.Suspended, operatorId);

        // Assert
        result.Should().Be(2);
    }

    #endregion

    #region GetTenantConnectionStringAsync

    [Fact]
    public async Task GetTenantConnectionStringAsync_NotFound_ThrowsNotFoundException()
    {
        // Arrange
        var tenantId = Guid.NewGuid();
        _repoMock.Setup(r => r.GetByIdAsync(tenantId, It.IsAny<CancellationToken>()))
            .ReturnsAsync((TenantEntity?)null);

        // Act & Assert
        await _service.Invoking(s => s.GetTenantConnectionStringAsync(tenantId))
            .Should().ThrowAsync<NotFoundException>();
    }

    [Fact]
    public async Task GetTenantConnectionStringAsync_LogicalMode_ReturnsDefaultString()
    {
        // Arrange
        var tenantId = Guid.NewGuid();
        var tenant = CreateTestTenant("测试", "test.com", "T001");
        tenant.IsolationMode = (int)IsolationMode.Logical;
        _repoMock.Setup(r => r.GetByIdAsync(tenantId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(tenant);

        // Act
        var result = await _service.GetTenantConnectionStringAsync(tenantId);

        // Assert
        result.Should().Be("默认连接字符串");
    }

    #endregion

    #region RenewTenantAsync

    [Fact]
    public async Task RenewTenantAsync_NotFound_ThrowsNotFoundException()
    {
        // Arrange
        var tenantId = Guid.NewGuid();
        _repoMock.Setup(r => r.GetByIdAsync(tenantId, It.IsAny<CancellationToken>()))
            .ReturnsAsync((TenantEntity?)null);

        // Act & Assert
        await _service.Invoking(s => s.RenewTenantAsync(tenantId, DateTime.UtcNow.AddYears(1), Guid.NewGuid()))
            .Should().ThrowAsync<NotFoundException>();
    }

    [Fact]
    public async Task RenewTenantAsync_ExpiredTenant_ResetsToActive()
    {
        // Arrange
        var tenantId = Guid.NewGuid();
        var tenant = CreateTestTenant("过期租户", "expired.com", "EXP01");
        tenant.Status = (int)TenantStatus.Expired;
        _repoMock.Setup(r => r.GetByIdAsync(tenantId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(tenant);
        _repoMock.Setup(r => r.UpdateAsync(It.IsAny<TenantEntity>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);
        _cacheMock.Setup(c => c.RemoveAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        var newExpire = DateTime.UtcNow.AddYears(1);

        // Act
        var result = await _service.RenewTenantAsync(tenantId, newExpire, Guid.NewGuid());

        // Assert
        result.Should().BeTrue();
        tenant.Status.Should().Be((int)TenantStatus.Active);
        tenant.ExpireTime.Should().Be(newExpire);
    }

    [Fact]
    public async Task RenewTenantAsync_ActiveTenant_UpdatesExpireTime()
    {
        // Arrange
        var tenantId = Guid.NewGuid();
        var tenant = CreateTestTenant("活跃租户", "active.com", "ACT01");
        _repoMock.Setup(r => r.GetByIdAsync(tenantId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(tenant);
        _repoMock.Setup(r => r.UpdateAsync(It.IsAny<TenantEntity>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);
        _cacheMock.Setup(c => c.RemoveAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        var newExpire = DateTime.UtcNow.AddMonths(6);

        // Act
        var result = await _service.RenewTenantAsync(tenantId, newExpire, Guid.NewGuid());

        // Assert
        result.Should().BeTrue();
        tenant.Status.Should().Be((int)TenantStatus.Active); // 保持活跃
        tenant.ExpireTime.Should().Be(newExpire);
    }

    #endregion

    #region 辅助方法

    private static TenantEntity CreateTestTenant(string name, string domain, string code)
    {
        var id = Guid.NewGuid();
        return new TenantEntity
        {
            Id = id,
            TenantId = id,
            TenantName = name,
            TenantDomain = domain,
            TenantCode = code,
            Status = (int)TenantStatus.Active,
            IsolationMode = (int)IsolationMode.Logical,
            CreateTime = DateTime.UtcNow,
            UpdateTime = DateTime.UtcNow
        };
    }

    #endregion
}
