using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;
using JGSY.AGI.DigitalTwin.Models;
using JGSY.AGI.DigitalTwin.Services;

namespace JGSY.AGI.Test.DigitalTwin;

/// <summary>
/// 预测性维护服务单元测试（AI 健康评估 + 寿命预测 + 异常检测）
/// </summary>
public class PredictiveMaintenanceServiceTests
{
    private readonly Mock<ITwinRepository> _twinRepo;
    private readonly Mock<IIotCloudAiClient> _aiClient;
    private readonly Mock<IAlertService> _alertService;
    private readonly PredictiveMaintenanceService _service;

    public PredictiveMaintenanceServiceTests()
    {
        _twinRepo = new Mock<ITwinRepository>();
        _aiClient = new Mock<IIotCloudAiClient>();
        _alertService = new Mock<IAlertService>();

        _service = new PredictiveMaintenanceService(
            _twinRepo.Object,
            _aiClient.Object,
            _alertService.Object,
            NullLogger<PredictiveMaintenanceService>.Instance);
    }

    #region PredictMaintenanceAsync

    [Fact]
    public async Task PredictMaintenance_DeviceNotFound_ReturnsUnknownRisk()
    {
        _twinRepo.Setup(r => r.GetByDeviceIdAsync("MISSING")).ReturnsAsync((ChargingPileTwin?)null);

        var result = await _service.PredictMaintenanceAsync("MISSING");
        result.DeviceId.Should().Be("MISSING");
        result.HealthScore.Should().Be(0);
        result.RiskLevel.Should().Be("Unknown");
        result.Recommendations.Should().Contain("设备未找到");
    }

    [Fact]
    public async Task PredictMaintenance_HealthyDevice_ReturnsLowRisk()
    {
        var twin = new ChargingPileTwin { PhysicalDeviceId = "D1", DeviceModel = "120kW" };
        _twinRepo.Setup(r => r.GetByDeviceIdAsync("D1")).ReturnsAsync(twin);

        _aiClient.Setup(c => c.AssessHealthAsync("D1", It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DeviceHealthResult { DeviceId = "D1", HealthScore = 85, HealthLevel = "Good" });
        _aiClient.Setup(c => c.PredictRemainingLifeAsync("D1", It.IsAny<CancellationToken>()))
            .ReturnsAsync(new RemainingLifeResult { DeviceId = "D1", RemainingDays = 500 });
        _aiClient.Setup(c => c.GetMaintenanceRecommendationAsync("D1", It.IsAny<CancellationToken>()))
            .ReturnsAsync(new MaintenanceRecommendationResult
            {
                Tasks = new List<MaintenanceTask>
                {
                    new() { Description = "定期清洁散热系统" },
                    new() { Description = "检查接线端子" }
                }
            });

        var result = await _service.PredictMaintenanceAsync("D1");
        result.HealthScore.Should().Be(85);
        result.RemainingDays.Should().Be(500);
        result.RiskLevel.Should().Be("Low");  // Good → Low
        result.Recommendations.Should().HaveCount(2);

        // 健康设备不应触发告警
        _alertService.Verify(s => s.SendAlertAsync(It.IsAny<MaintenanceAlert>()), Times.Never);
    }

    [Fact]
    public async Task PredictMaintenance_CriticalDevice_TriggersAlert()
    {
        var twin = new ChargingPileTwin { PhysicalDeviceId = "D2", DeviceModel = "60kW" };
        _twinRepo.Setup(r => r.GetByDeviceIdAsync("D2")).ReturnsAsync(twin);

        _aiClient.Setup(c => c.AssessHealthAsync("D2", It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DeviceHealthResult { DeviceId = "D2", HealthScore = 35, HealthLevel = "Poor" });
        _aiClient.Setup(c => c.PredictRemainingLifeAsync("D2", It.IsAny<CancellationToken>()))
            .ReturnsAsync(new RemainingLifeResult { DeviceId = "D2", RemainingDays = 20 });
        _aiClient.Setup(c => c.GetMaintenanceRecommendationAsync("D2", It.IsAny<CancellationToken>()))
            .ReturnsAsync(new MaintenanceRecommendationResult { Tasks = new List<MaintenanceTask>() });

        var result = await _service.PredictMaintenanceAsync("D2");
        result.HealthScore.Should().Be(35);
        result.RiskLevel.Should().Be("High");  // Poor → High

        // 健康分 < 40 应触发 Critical 告警
        _alertService.Verify(s => s.SendAlertAsync(It.Is<MaintenanceAlert>(a =>
            a.Severity == AlertSeverity.Critical && a.DeviceId == "D2")), Times.Once);
    }

    [Fact]
    public async Task PredictMaintenance_LowHealthScore_TriggersWarningAlert()
    {
        var twin = new ChargingPileTwin { PhysicalDeviceId = "D3", DeviceModel = "90kW" };
        _twinRepo.Setup(r => r.GetByDeviceIdAsync("D3")).ReturnsAsync(twin);

        // 健康分 50 (< 60 但 >= 40) → Warning
        _aiClient.Setup(c => c.AssessHealthAsync("D3", It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DeviceHealthResult { DeviceId = "D3", HealthScore = 50, HealthLevel = "Fair" });
        _aiClient.Setup(c => c.PredictRemainingLifeAsync("D3", It.IsAny<CancellationToken>()))
            .ReturnsAsync(new RemainingLifeResult { DeviceId = "D3", RemainingDays = 60 });
        _aiClient.Setup(c => c.GetMaintenanceRecommendationAsync("D3", It.IsAny<CancellationToken>()))
            .ReturnsAsync(new MaintenanceRecommendationResult { Tasks = new List<MaintenanceTask>() });

        await _service.PredictMaintenanceAsync("D3");

        _alertService.Verify(s => s.SendAlertAsync(It.Is<MaintenanceAlert>(a =>
            a.Severity == AlertSeverity.Warning)), Times.Once);
    }

    [Fact]
    public async Task PredictMaintenance_NullAiResults_UsesDefaults()
    {
        var twin = new ChargingPileTwin { PhysicalDeviceId = "D4" };
        _twinRepo.Setup(r => r.GetByDeviceIdAsync("D4")).ReturnsAsync(twin);

        // AI 服务返回 null
        _aiClient.Setup(c => c.AssessHealthAsync("D4", It.IsAny<CancellationToken>()))
            .ReturnsAsync((DeviceHealthResult?)null);
        _aiClient.Setup(c => c.PredictRemainingLifeAsync("D4", It.IsAny<CancellationToken>()))
            .ReturnsAsync((RemainingLifeResult?)null);
        _aiClient.Setup(c => c.GetMaintenanceRecommendationAsync("D4", It.IsAny<CancellationToken>()))
            .ReturnsAsync((MaintenanceRecommendationResult?)null);

        var result = await _service.PredictMaintenanceAsync("D4");
        result.HealthScore.Should().Be(50);       // 默认值
        result.RemainingDays.Should().Be(365);     // 默认值
        result.RiskLevel.Should().Be("Unknown");   // null → Unknown
        result.Recommendations.Should().BeEmpty();
    }

    [Theory]
    [InlineData("excellent", "Low")]
    [InlineData("good", "Low")]
    [InlineData("fair", "Medium")]
    [InlineData("poor", "High")]
    [InlineData("critical", "Critical")]
    [InlineData(null, "Unknown")]
    public async Task PredictMaintenance_MapsHealthLevelCorrectly(string? healthLevel, string expectedRisk)
    {
        var twin = new ChargingPileTwin { PhysicalDeviceId = "DX" };
        _twinRepo.Setup(r => r.GetByDeviceIdAsync("DX")).ReturnsAsync(twin);

        _aiClient.Setup(c => c.AssessHealthAsync("DX", It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DeviceHealthResult { HealthScore = 80, HealthLevel = healthLevel! });
        _aiClient.Setup(c => c.PredictRemainingLifeAsync("DX", It.IsAny<CancellationToken>()))
            .ReturnsAsync(new RemainingLifeResult { RemainingDays = 999 });
        _aiClient.Setup(c => c.GetMaintenanceRecommendationAsync("DX", It.IsAny<CancellationToken>()))
            .ReturnsAsync(new MaintenanceRecommendationResult { Tasks = new List<MaintenanceTask>() });

        var result = await _service.PredictMaintenanceAsync("DX");
        result.RiskLevel.Should().Be(expectedRisk);
    }

    #endregion

    #region DetectAnomaliesAsync

    [Fact]
    public async Task DetectAnomalies_InsufficientData_ReturnsEmpty()
    {
        // 少于 24 个数据点
        var telemetry = Enumerable.Range(0, 10).Select(i => new DeviceTelemetry
        {
            Time = DateTime.UtcNow.AddHours(-i),
            Power = 50,
            Voltage = 380,
            Current = 100,
            Temperature = 45
        }).ToList();

        _twinRepo.Setup(r => r.GetTelemetryHistoryAsync("D1", It.IsAny<DateTime>(), It.IsAny<DateTime>(), "hourly"))
            .ReturnsAsync(telemetry);

        var results = await _service.DetectAnomaliesAsync("D1");
        results.Should().BeEmpty();
    }

    [Fact]
    public async Task DetectAnomalies_WithAnomalies_ReturnsOnlyAnomalous()
    {
        // 足够的数据点
        var telemetry = Enumerable.Range(0, 48).Select(i => new DeviceTelemetry
        {
            Time = DateTime.UtcNow.AddHours(-i),
            Power = 50 + i,
            Voltage = 380,
            Current = 100,
            Temperature = 45
        }).ToList();

        _twinRepo.Setup(r => r.GetTelemetryHistoryAsync("D1", It.IsAny<DateTime>(), It.IsAny<DateTime>(), "hourly"))
            .ReturnsAsync(telemetry);

        // AI 检测到异常
        _aiClient.Setup(c => c.DetectAnomaliesAsync(It.IsAny<List<DeviceDataPoint>>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new AnomalyDetectionResult
            {
                DeviceId = "D1",
                IsAnomaly = true,
                AnomalyScore = 0.85,
                AnomalyType = "PowerSpike"
            });

        var results = await _service.DetectAnomaliesAsync("D1");
        results.Should().HaveCount(1);
        results[0].IsAnomaly.Should().BeTrue();
        results[0].DeviceId.Should().Be("D1");
    }

    [Fact]
    public async Task DetectAnomalies_NoAnomalyDetected_ReturnsEmpty()
    {
        var telemetry = Enumerable.Range(0, 48).Select(i => new DeviceTelemetry
        {
            Time = DateTime.UtcNow.AddHours(-i),
            Power = 50,
            Voltage = 380,
            Current = 100,
            Temperature = 45
        }).ToList();

        _twinRepo.Setup(r => r.GetTelemetryHistoryAsync("D1", It.IsAny<DateTime>(), It.IsAny<DateTime>(), "hourly"))
            .ReturnsAsync(telemetry);

        _aiClient.Setup(c => c.DetectAnomaliesAsync(It.IsAny<List<DeviceDataPoint>>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new AnomalyDetectionResult { IsAnomaly = false, AnomalyScore = 0.1 });

        var results = await _service.DetectAnomaliesAsync("D1");
        results.Should().BeEmpty(); // IsAnomaly=false 被过滤
    }

    [Fact]
    public async Task DetectAnomalies_AiReturnsNull_ReturnsEmpty()
    {
        var telemetry = Enumerable.Range(0, 48).Select(i => new DeviceTelemetry
        {
            Time = DateTime.UtcNow.AddHours(-i),
            Power = 50
        }).ToList();

        _twinRepo.Setup(r => r.GetTelemetryHistoryAsync("D1", It.IsAny<DateTime>(), It.IsAny<DateTime>(), "hourly"))
            .ReturnsAsync(telemetry);

        _aiClient.Setup(c => c.DetectAnomaliesAsync(It.IsAny<List<DeviceDataPoint>>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((AnomalyDetectionResult?)null);

        var results = await _service.DetectAnomaliesAsync("D1");
        results.Should().BeEmpty();
    }

    #endregion
}
