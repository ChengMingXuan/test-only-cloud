using Xunit;
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using JGSY.AGI.PVESSC.Business;
using JGSY.AGI.PVESSC.Interfaces;
using JGSY.AGI.PVESSC.Entities;
using JGSY.AGI.PVESSC.Models;
using JGSY.AGI.Common.Core.Interfaces;

namespace JGSY.AGI.Test.PVESSC;

/// <summary>
/// V2G 服务单元测试
/// 覆盖: 配置管理、放电授权、停止放电、结算计算、收入统计
/// </summary>
public class V2gServiceTests
{
    private readonly Mock<IV2gConfigRepository> _configRepo = new();
    private readonly Mock<IV2gSessionRepository> _sessionRepo = new();
    private readonly Mock<IV2gSettlementRepository> _settlementRepo = new();
    private readonly Mock<ITenantContext> _ctx = new();
    private readonly V2gService _service;

    private readonly Guid _tenantId = Guid.NewGuid();

    public V2gServiceTests()
    {
        _ctx.Setup(c => c.TenantId).Returns(_tenantId);
        _service = new V2gService(_configRepo.Object, _sessionRepo.Object, _settlementRepo.Object, _ctx.Object);
    }

    #region 配置管理

    [Fact]
    public async Task GetConfigListAsync_ReturnsMappedDtos()
    {
        // Arrange
        var siteId = Guid.NewGuid();
        var configs = new List<PvesscV2gConfig>
        {
            new() { Id = Guid.NewGuid(), SiteId = siteId, ChargerId = "CG-001", V2gCapable = true, MaxDischargeKw = 50, MinSocPercent = 20, DischargePriceYuan = 0.8m, Priority = 1, IsActive = true },
            new() { Id = Guid.NewGuid(), SiteId = siteId, ChargerId = "CG-002", V2gCapable = false, MaxDischargeKw = 30, MinSocPercent = 30, DischargePriceYuan = 0.6m, Priority = 2, IsActive = false }
        };
        _configRepo.Setup(r => r.GetListAsync(_tenantId, siteId)).ReturnsAsync(configs);

        // Act
        var result = (await _service.GetConfigListAsync(siteId)).ToList();

        // Assert
        result.Should().HaveCount(2);
        result[0].ChargerId.Should().Be("CG-001");
        result[0].V2gCapable.Should().BeTrue();
        result[0].MaxDischargeKw.Should().Be(50);
        result[0].DischargePriceYuan.Should().Be(0.8m);
        result[1].IsActive.Should().BeFalse();
    }

    [Fact]
    public async Task UpdateConfigAsync_ExistingConfig_UpdatesAndReturnsTrue()
    {
        // Arrange
        var siteId = Guid.NewGuid();
        var existing = new PvesscV2gConfig { Id = Guid.NewGuid(), SiteId = siteId, ChargerId = "CG-001", MaxDischargeKw = 30 };
        _configRepo.Setup(r => r.GetByChargerIdAsync(_tenantId, siteId, "CG-001")).ReturnsAsync(existing);
        _configRepo.Setup(r => r.UpdateAsync(It.IsAny<PvesscV2gConfig>())).ReturnsAsync(true);

        var request = new UpdateV2gConfigRequest { V2gCapable = true, MaxDischargeKw = 60, MinSocPercent = 15, DischargePriceYuan = 1.2m, Priority = 5, IsActive = true };

        // Act
        var result = await _service.UpdateConfigAsync(siteId, "CG-001", request);

        // Assert
        result.Should().BeTrue();
        existing.MaxDischargeKw.Should().Be(60);
        existing.MinSocPercent.Should().Be(15);
        existing.DischargePriceYuan.Should().Be(1.2m);
        _configRepo.Verify(r => r.UpdateAsync(existing), Times.Once);
    }

    [Fact]
    public async Task UpdateConfigAsync_NewConfig_InsertsAndReturnsTrue()
    {
        // Arrange
        var siteId = Guid.NewGuid();
        _configRepo.Setup(r => r.GetByChargerIdAsync(_tenantId, siteId, "CG-NEW")).ReturnsAsync((PvesscV2gConfig?)null);

        var request = new UpdateV2gConfigRequest { V2gCapable = true, MaxDischargeKw = 50, MinSocPercent = 20, DischargePriceYuan = 0.8m, Priority = 1, IsActive = true };

        // Act
        var result = await _service.UpdateConfigAsync(siteId, "CG-NEW", request);

        // Assert
        result.Should().BeTrue();
        _configRepo.Verify(r => r.InsertAsync(It.Is<PvesscV2gConfig>(c =>
            c.SiteId == siteId &&
            c.ChargerId == "CG-NEW" &&
            c.TenantId == _tenantId &&
            c.MaxDischargeKw == 50)), Times.Once);
    }

    #endregion

    #region 会话管理

    [Fact]
    public async Task GetSessionsAsync_ReturnsMappedTupleWithTotal()
    {
        // Arrange
        var siteId = Guid.NewGuid();
        var sessions = new List<PvesscV2gSession>
        {
            new() { Id = Guid.NewGuid(), SiteId = siteId, ChargerId = "CG-001", VehicleVin = "VIN001", Status = 1, SocStart = 80 }
        };
        _sessionRepo.Setup(r => r.GetListAsync(_tenantId, siteId, 1, 10, It.IsAny<short?>())).ReturnsAsync(sessions);
        _sessionRepo.Setup(r => r.GetCountAsync(_tenantId, siteId, It.IsAny<short?>())).ReturnsAsync(5);

        // Act
        var (items, total) = await _service.GetSessionsAsync(siteId, 1, 10);

        // Assert
        items.Should().HaveCount(1);
        items.First().VehicleVin.Should().Be("VIN001");
        total.Should().Be(5);
    }

    [Fact]
    public async Task GetSessionByIdAsync_Exists_ReturnsMappedDto()
    {
        // Arrange
        var sessionId = Guid.NewGuid();
        var session = new PvesscV2gSession { Id = sessionId, ChargerId = "CG-001", VehicleVin = "VIN123", Status = 2, DischargePowerKw = 50 };
        _sessionRepo.Setup(r => r.GetByIdAsync(sessionId, _tenantId)).ReturnsAsync(session);

        // Act
        var result = await _service.GetSessionByIdAsync(sessionId);

        // Assert
        result.Should().NotBeNull();
        result!.VehicleVin.Should().Be("VIN123");
        result.Status.Should().Be(2);
    }

    [Fact]
    public async Task GetSessionByIdAsync_NotFound_ReturnsNull()
    {
        // Arrange
        _sessionRepo.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), _tenantId)).ReturnsAsync((PvesscV2gSession?)null);

        // Act
        var result = await _service.GetSessionByIdAsync(Guid.NewGuid());

        // Assert
        result.Should().BeNull();
    }

    #endregion

    #region 放电授权

    [Fact]
    public async Task AuthorizeDischargeAsync_WithConfig_UsesPriceFromConfig()
    {
        // Arrange
        var siteId = Guid.NewGuid();
        var config = new PvesscV2gConfig { DischargePriceYuan = 1.5m };
        _configRepo.Setup(r => r.GetByChargerIdAsync(_tenantId, siteId, "CG-001")).ReturnsAsync(config);

        var request = new AuthorizeV2gRequest { ChargerId = "CG-001", VehicleVin = "VIN100", SocStart = 90, SocFloor = 20, DischargePowerKw = 50 };

        // Act
        var sessionId = await _service.AuthorizeDischargeAsync(siteId, request);

        // Assert
        sessionId.Should().NotBeEmpty();
        _sessionRepo.Verify(r => r.InsertAsync(It.Is<PvesscV2gSession>(s =>
            s.PriceYuanPerKwh == 1.5m &&
            s.Status == 1 &&
            s.OwnerAuthorized == true &&
            s.SocStart == 90 &&
            s.SocFloor == 20 &&
            s.VehicleVin == "VIN100" &&
            s.TenantId == _tenantId)), Times.Once);
    }

    [Fact]
    public async Task AuthorizeDischargeAsync_NoConfig_UsesPriceZero()
    {
        // Arrange
        var siteId = Guid.NewGuid();
        _configRepo.Setup(r => r.GetByChargerIdAsync(_tenantId, siteId, "CG-NEW")).ReturnsAsync((PvesscV2gConfig?)null);

        var request = new AuthorizeV2gRequest { ChargerId = "CG-NEW", VehicleVin = "VIN200", SocStart = 80, SocFloor = 30, DischargePowerKw = 40 };

        // Act
        var sessionId = await _service.AuthorizeDischargeAsync(siteId, request);

        // Assert
        sessionId.Should().NotBeEmpty();
        _sessionRepo.Verify(r => r.InsertAsync(It.Is<PvesscV2gSession>(s =>
            s.PriceYuanPerKwh == 0m &&
            s.DischargePowerKw == 40)), Times.Once);
    }

    #endregion

    #region 停止放电

    [Fact]
    public async Task StopDischargeAsync_ActiveSession_NoReason_CompletesWithStatus2()
    {
        // Arrange
        var sessionId = Guid.NewGuid();
        var session = new PvesscV2gSession { Id = sessionId, Status = 1 };
        _sessionRepo.Setup(r => r.GetByIdAsync(sessionId, _tenantId)).ReturnsAsync(session);
        _sessionRepo.Setup(r => r.UpdateAsync(It.IsAny<PvesscV2gSession>())).ReturnsAsync(true);

        // Act
        var result = await _service.StopDischargeAsync(sessionId, null);

        // Assert
        result.Should().BeTrue();
        session.Status.Should().Be(2); // 已完成
        session.EndTime.Should().NotBeNull();
    }

    [Fact]
    public async Task StopDischargeAsync_ActiveSession_WithReason_AbortsWithStatus3()
    {
        // Arrange
        var sessionId = Guid.NewGuid();
        var session = new PvesscV2gSession { Id = sessionId, Status = 1 };
        _sessionRepo.Setup(r => r.GetByIdAsync(sessionId, _tenantId)).ReturnsAsync(session);
        _sessionRepo.Setup(r => r.UpdateAsync(It.IsAny<PvesscV2gSession>())).ReturnsAsync(true);

        // Act
        var result = await _service.StopDischargeAsync(sessionId, "SOC过低");

        // Assert
        result.Should().BeTrue();
        session.Status.Should().Be(3); // 已中止
        session.AbortReason.Should().Be("SOC过低");
    }

    [Fact]
    public async Task StopDischargeAsync_NotFound_ReturnsFalse()
    {
        // Arrange
        _sessionRepo.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), _tenantId)).ReturnsAsync((PvesscV2gSession?)null);

        // Act
        var result = await _service.StopDischargeAsync(Guid.NewGuid(), null);

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task StopDischargeAsync_NotActive_ReturnsFalse()
    {
        // Arrange
        var sessionId = Guid.NewGuid();
        var session = new PvesscV2gSession { Id = sessionId, Status = 2 }; // 已完成
        _sessionRepo.Setup(r => r.GetByIdAsync(sessionId, _tenantId)).ReturnsAsync(session);

        // Act
        var result = await _service.StopDischargeAsync(sessionId, null);

        // Assert
        result.Should().BeFalse();
    }

    #endregion

    #region 结算

    [Fact]
    public async Task GetSettlementsAsync_ReturnsMappedTuple()
    {
        // Arrange
        var siteId = Guid.NewGuid();
        var items = new List<PvesscV2gSettlement>
        {
            new() { Id = Guid.NewGuid(), SessionId = Guid.NewGuid(), VehicleVin = "VIN001", DischargeKwh = 100, GrossRevenue = 80, NetRevenue = 75, Status = 1 }
        };
        _settlementRepo.Setup(r => r.GetListAsync(_tenantId, siteId, 1, 10)).ReturnsAsync(items);
        _settlementRepo.Setup(r => r.GetCountAsync(_tenantId, siteId)).ReturnsAsync(3);

        // Act
        var (result, total) = await _service.GetSettlementsAsync(siteId, 1, 10);

        // Assert
        result.Should().HaveCount(1);
        result.First().DischargeKwh.Should().Be(100);
        total.Should().Be(3);
    }

    [Fact]
    public async Task SettleSessionAsync_CompletedSession_CalculatesRevenue()
    {
        // Arrange
        var sessionId = Guid.NewGuid();
        var siteId = Guid.NewGuid();
        var session = new PvesscV2gSession
        {
            Id = sessionId,
            TenantId = _tenantId,
            SiteId = siteId,
            VehicleVin = "VIN001",
            DischargeEnergyKwh = 100,
            PriceYuanPerKwh = 1.0m,
            Status = 2 // 已完成
        };
        _sessionRepo.Setup(r => r.GetByIdAsync(sessionId, _tenantId)).ReturnsAsync(session);

        // Act
        var result = await _service.SettleSessionAsync(sessionId);

        // Assert
        result.Should().BeTrue();

        // 验证结算计算: gross = 100 * 1.0 = 100, batteryCost = 100 * 0.05 = 5, net = 95
        // ownerRevenue = 95 * 70% = 66.5, platformRevenue = 95 - 66.5 = 28.5
        _settlementRepo.Verify(r => r.InsertAsync(It.Is<PvesscV2gSettlement>(s =>
            s.DischargeKwh == 100 &&
            s.GrossRevenue == 100m &&
            s.BatteryCost == 5m &&
            s.NetRevenue == 95m &&
            s.OwnerSharePercent == 70m &&
            s.OwnerRevenue == 66.5m &&
            s.PlatformRevenue == 28.5m &&
            s.Status == 1 &&
            s.TenantId == _tenantId)), Times.Once);
    }

    [Fact]
    public async Task SettleSessionAsync_SessionNotFound_ReturnsFalse()
    {
        // Arrange
        _sessionRepo.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), _tenantId)).ReturnsAsync((PvesscV2gSession?)null);

        // Act
        var result = await _service.SettleSessionAsync(Guid.NewGuid());

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task SettleSessionAsync_SessionNotCompleted_ReturnsFalse()
    {
        // Arrange
        var session = new PvesscV2gSession { Id = Guid.NewGuid(), Status = 1 }; // 放电中
        _sessionRepo.Setup(r => r.GetByIdAsync(session.Id, _tenantId)).ReturnsAsync(session);

        // Act
        var result = await _service.SettleSessionAsync(session.Id);

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task SettleSessionAsync_AbortedSession_StillSettles()
    {
        // Arrange — status=3(中止) ≥ 2, 也可结算
        var session = new PvesscV2gSession
        {
            Id = Guid.NewGuid(),
            TenantId = _tenantId,
            SiteId = Guid.NewGuid(),
            VehicleVin = "VIN002",
            DischargeEnergyKwh = 50,
            PriceYuanPerKwh = 0.8m,
            Status = 3 // 已中止
        };
        _sessionRepo.Setup(r => r.GetByIdAsync(session.Id, _tenantId)).ReturnsAsync(session);

        // Act
        var result = await _service.SettleSessionAsync(session.Id);

        // Assert
        result.Should().BeTrue();
        _settlementRepo.Verify(r => r.InsertAsync(It.Is<PvesscV2gSettlement>(s =>
            s.GrossRevenue == 40m && // 50 * 0.8 = 40
            s.BatteryCost == 2.5m)), Times.Once); // 50 * 0.05 = 2.5
    }

    #endregion

    #region 收入统计

    [Fact]
    public async Task GetRevenueAsync_ReturnsAggregatedDto()
    {
        // Arrange
        var siteId = Guid.NewGuid();
        _settlementRepo.Setup(r => r.GetTotalRevenueAsync(_tenantId, siteId)).ReturnsAsync(15000m);
        _sessionRepo.Setup(r => r.GetCountAsync(_tenantId, siteId, It.IsAny<short?>())).ReturnsAsync(100);
        _sessionRepo.Setup(r => r.GetCountAsync(_tenantId, siteId, (short?)1)).ReturnsAsync(5);

        // Act
        var result = await _service.GetRevenueAsync(siteId);

        // Assert
        result.TotalRevenue.Should().Be(15000m);
    }

    #endregion
}
