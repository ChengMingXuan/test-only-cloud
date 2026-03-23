using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;
using JGSY.AGI.Common.Core.Interfaces;
using JGSY.AGI.Common.Core.ServiceClients;
using JGSY.AGI.DigitalTwin.Data.Repositories;
using JGSY.AGI.DigitalTwin.Models;
using JGSY.AGI.DigitalTwin.Services;

namespace JGSY.AGI.Test.DigitalTwin;

/// <summary>
/// 总览驾驶舱服务单元测试（KPI 计算 + Station 跨服务调用降级 + 告警统计）
/// </summary>
public class OverviewServiceTests
{
    private readonly Mock<IStationTwinRepository> _stationRepo;
    private readonly Mock<IChargingPileTwinRepository> _pileTwinRepo;
    private readonly Mock<IAlertRepository> _alertRepo;
    private readonly Mock<ITenantContext> _tenantContext;
    private readonly Mock<IServiceTransport> _serviceTransport;
    private readonly OverviewService _service;

    private static readonly Guid TenantId = Guid.NewGuid();

    public OverviewServiceTests()
    {
        _stationRepo = new Mock<IStationTwinRepository>();
        _pileTwinRepo = new Mock<IChargingPileTwinRepository>();
        _alertRepo = new Mock<IAlertRepository>();
        _tenantContext = new Mock<ITenantContext>();
        _serviceTransport = new Mock<IServiceTransport>();

        _tenantContext.Setup(t => t.TenantId).Returns(TenantId);

        _service = new OverviewService(
            _stationRepo.Object,
            _pileTwinRepo.Object,
            _alertRepo.Object,
            _tenantContext.Object,
            _serviceTransport.Object,
            NullLogger<OverviewService>.Instance);
    }

    #region GetKpiAsync

    [Fact]
    public async Task GetKpi_WithDevices_CalculatesAllMetrics()
    {
        // Arrange: Station 服务返回 2 个场站
        SetupStationServiceReturns(2);

        var devices = new List<ChargingPileTwin>
        {
            new() { PhysicalDeviceId = "D1", Status = DeviceStatus.Charging, CurrentPower = 60, TotalEnergy = 1000, HealthScore = 90, UtilizationRate = 80 },
            new() { PhysicalDeviceId = "D2", Status = DeviceStatus.Idle, CurrentPower = 0, TotalEnergy = 500, HealthScore = 70, UtilizationRate = 40 },
            new() { PhysicalDeviceId = "D3", Status = DeviceStatus.Offline, CurrentPower = 0, TotalEnergy = 200, HealthScore = 50, UtilizationRate = 0 },
            new() { PhysicalDeviceId = "D4", Status = DeviceStatus.Fault, CurrentPower = 0, TotalEnergy = 100, HealthScore = 30, UtilizationRate = 0 }
        };
        _pileTwinRepo.Setup(r => r.GetAllAsync(TenantId)).ReturnsAsync(devices);

        var alerts = new List<MaintenanceAlert>
        {
            new() { AlertId = Guid.NewGuid(), Severity = AlertSeverity.Warning },
            new() { AlertId = Guid.NewGuid(), Severity = AlertSeverity.Critical }
        };
        _alertRepo.Setup(r => r.GetActiveAsync(TenantId)).ReturnsAsync(alerts);

        // Act
        var kpi = await _service.GetKpiAsync();

        // Assert
        kpi.TotalStations.Should().Be(2);
        kpi.TotalDevices.Should().Be(4);
        kpi.OnlineDevices.Should().Be(3);   // Charging + Idle + Fault (非 Offline)
        kpi.OfflineDevices.Should().Be(1);
        kpi.FaultDevices.Should().Be(1);
        kpi.TotalPower.Should().Be(60);
        kpi.TotalEnergy.Should().Be(1800);
        kpi.AvgHealthScore.Should().Be(60);  // (90+70+50+30)/4
        kpi.AvgUtilization.Should().Be(30);  // (80+40+0+0)/4
        kpi.ActiveAlerts.Should().Be(2);
    }

    [Fact]
    public async Task GetKpi_NoDevices_ReturnsZeroAverages()
    {
        SetupStationServiceReturns(0);
        _pileTwinRepo.Setup(r => r.GetAllAsync(TenantId)).ReturnsAsync(new List<ChargingPileTwin>());
        _alertRepo.Setup(r => r.GetActiveAsync(TenantId)).ReturnsAsync(new List<MaintenanceAlert>());

        var kpi = await _service.GetKpiAsync();
        kpi.TotalDevices.Should().Be(0);
        kpi.AvgHealthScore.Should().Be(0);
        kpi.AvgUtilization.Should().Be(0);
    }

    [Fact]
    public async Task GetKpi_StationServiceFailure_FallsBackToLocalData()
    {
        // Station 服务调用失败
        _serviceTransport.Setup(t => t.PostAsync<InternalStationListResponse>(
                It.IsAny<string>(), It.IsAny<string>(), It.IsAny<object?>(), It.IsAny<ServiceCallOptions?>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new Exception("Station 服务不可用"));

        // 本地有 3 个 StationTwin
        var localStations = new List<StationTwin>
        {
            new() { PhysicalStationId = "S1" },
            new() { PhysicalStationId = "S2" },
            new() { PhysicalStationId = "S3" }
        };
        _stationRepo.Setup(r => r.GetAllAsync(TenantId)).ReturnsAsync(localStations);
        _pileTwinRepo.Setup(r => r.GetAllAsync(TenantId)).ReturnsAsync(new List<ChargingPileTwin>());
        _alertRepo.Setup(r => r.GetActiveAsync(TenantId)).ReturnsAsync(new List<MaintenanceAlert>());

        var kpi = await _service.GetKpiAsync();
        kpi.TotalStations.Should().Be(3); // 降级使用本地数据
    }

    #endregion

    #region GetAlertStatisticsAsync

    [Fact]
    public async Task GetAlertStatistics_CalculatesSeverityCounts()
    {
        var alerts = new List<MaintenanceAlert>
        {
            new() { Severity = AlertSeverity.Info, Status = AlertStatus.Active, CreateTime = DateTime.UtcNow },
            new() { Severity = AlertSeverity.Warning, Status = AlertStatus.Active, CreateTime = DateTime.UtcNow },
            new() { Severity = AlertSeverity.Warning, Status = AlertStatus.Acknowledged, CreateTime = DateTime.UtcNow },
            new() { Severity = AlertSeverity.Critical, Status = AlertStatus.Active, CreateTime = DateTime.UtcNow.AddDays(-1) },
            new() { Severity = AlertSeverity.Emergency, Status = AlertStatus.Active, CreateTime = DateTime.UtcNow }
        };
        _alertRepo.Setup(r => r.GetActiveAsync(TenantId)).ReturnsAsync(alerts);

        var stats = await _service.GetAlertStatisticsAsync();
        stats.Total.Should().Be(5);
        stats.InfoCount.Should().Be(1);
        stats.WarningCount.Should().Be(2);
        stats.CriticalCount.Should().Be(1);
        stats.EmergencyCount.Should().Be(1);
        stats.UnacknowledgedCount.Should().Be(4); // Active 状态
        stats.TodayCount.Should().Be(4);           // 除了 AddDays(-1) 那个
    }

    [Fact]
    public async Task GetAlertStatistics_Empty_AllZeros()
    {
        _alertRepo.Setup(r => r.GetActiveAsync(TenantId)).ReturnsAsync(new List<MaintenanceAlert>());
        var stats = await _service.GetAlertStatisticsAsync();
        stats.Total.Should().Be(0);
        stats.UnacknowledgedCount.Should().Be(0);
    }

    #endregion

    #region Helper

    /// <summary>
    /// 模拟 Station 服务返回指定数量场站
    /// </summary>
    private void SetupStationServiceReturns(int count)
    {
        var items = Enumerable.Range(1, count).Select(i => new InternalStationItem
        {
            StationId = Guid.NewGuid(),
            Name = $"场站{i}"
        }).ToList();

        var response = new InternalStationListResponse { Stations = items };

        _serviceTransport.Setup(t => t.PostAsync<InternalStationListResponse>(
                It.IsAny<string>(), It.IsAny<string>(), It.IsAny<object?>(), It.IsAny<ServiceCallOptions?>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(response);
    }

    #endregion
}
