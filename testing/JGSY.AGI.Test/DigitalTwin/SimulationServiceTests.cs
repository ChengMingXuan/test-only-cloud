using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;
using JGSY.AGI.DigitalTwin.Models;
using JGSY.AGI.DigitalTwin.Services;

namespace JGSY.AGI.Test.DigitalTwin;

/// <summary>
/// 仿真服务单元测试（峰值负载、设备故障、容量规划三种场景）
/// </summary>
public class SimulationServiceTests
{
    private readonly Mock<ITwinRepository> _twinRepo;
    private readonly SimulationService _service;

    public SimulationServiceTests()
    {
        _twinRepo = new Mock<ITwinRepository>();
        _service = new SimulationService(
            _twinRepo.Object,
            NullLogger<SimulationService>.Instance);
    }

    private List<ChargingPileTwin> CreateDevices(int count, string stationId, double ratedPower = 120, double currentPower = 60)
    {
        return Enumerable.Range(1, count).Select(i => new ChargingPileTwin
        {
            TwinId = Guid.NewGuid(),
            PhysicalDeviceId = $"DEV-{i:D3}",
            StationId = stationId,
            DeviceModel = "DC-120kW",
            RatedPower = ratedPower,
            CurrentPower = currentPower,
            HealthScore = 90
        }).ToList();
    }

    #region RunSimulationAsync 路由

    [Fact]
    public async Task RunSimulation_UnknownScenario_ReturnsFailure()
    {
        var request = new SimulationRequest
        {
            ScenarioType = "unknown",
            StationId = "station-1"
        };

        var result = await _service.RunSimulationAsync(request);
        result.Success.Should().BeFalse();
        result.Results.Should().ContainKey("error");
    }

    [Fact]
    public async Task RunSimulation_PeakLoad_RoutesToPeakLoadMethod()
    {
        _twinRepo.Setup(r => r.GetByStationIdAsync("station-1"))
            .ReturnsAsync(CreateDevices(5, "station-1"));

        var request = new SimulationRequest
        {
            ScenarioType = "peakload",
            StationId = "station-1",
            Parameters = new Dictionary<string, object>()
        };

        var result = await _service.RunSimulationAsync(request);
        result.Success.Should().BeTrue();
        result.ScenarioType.Should().Be("PeakLoad");
    }

    [Fact]
    public async Task RunSimulation_DeviceFailure_RoutesToDeviceFailureMethod()
    {
        var devices = CreateDevices(3, "station-1");
        _twinRepo.Setup(r => r.GetByStationIdAsync("station-1"))
            .ReturnsAsync(devices);

        var request = new SimulationRequest
        {
            ScenarioType = "devicefailure",
            StationId = "station-1",
            Parameters = new Dictionary<string, object> { ["deviceId"] = devices[0].PhysicalDeviceId }
        };

        var result = await _service.RunSimulationAsync(request);
        result.Success.Should().BeTrue();
        result.ScenarioType.Should().Be("DeviceFailure");
    }

    #endregion

    #region RunPeakLoadSimulationAsync 峰值负载

    [Fact]
    public async Task PeakLoad_NoDevices_ReturnsFailure()
    {
        _twinRepo.Setup(r => r.GetByStationIdAsync("empty-station"))
            .ReturnsAsync(new List<ChargingPileTwin>());

        var result = await _service.RunPeakLoadSimulationAsync("empty-station", new Dictionary<string, object>());
        result.Success.Should().BeFalse();
        result.Results["error"].Should().Be("Station not found or has no devices");
    }

    [Fact]
    public async Task PeakLoad_WithDevices_CalculatesCapacity()
    {
        var devices = CreateDevices(5, "s1", ratedPower: 120, currentPower: 60);
        _twinRepo.Setup(r => r.GetByStationIdAsync("s1")).ReturnsAsync(devices);

        var result = await _service.RunPeakLoadSimulationAsync("s1", new Dictionary<string, object>());
        result.Success.Should().BeTrue();
        result.Results.Should().ContainKey("totalCapacity");
        result.Results.Should().ContainKey("currentLoad");
        result.Results.Should().ContainKey("simulatedPeakLoad");

        // 5台 * 120kW = 600kW 总容量
        Convert.ToDouble(result.Results["totalCapacity"]).Should().Be(600);
        // 5台 * 60kW = 300kW 当前负载
        Convert.ToDouble(result.Results["currentLoad"]).Should().Be(300);
        // 默认 peakMultiplier=1.5, simulatedPeakLoad = 300 * 1.5 = 450
        Convert.ToDouble(result.Results["simulatedPeakLoad"]).Should().Be(450);
    }

    [Fact]
    public async Task PeakLoad_CustomMultiplier_AppliesMultiplier()
    {
        var devices = CreateDevices(4, "s2", ratedPower: 100, currentPower: 50);
        _twinRepo.Setup(r => r.GetByStationIdAsync("s2")).ReturnsAsync(devices);

        var result = await _service.RunPeakLoadSimulationAsync("s2",
            new Dictionary<string, object> { ["peakMultiplier"] = 2.0, ["durationHours"] = 2 });

        result.Success.Should().BeTrue();
        // 4*50=200kW当前，*2=400kW峰值负载
        Convert.ToDouble(result.Results["simulatedPeakLoad"]).Should().Be(400);
    }

    [Fact]
    public async Task PeakLoad_HighLoad_GeneratesRecommendations()
    {
        // 设低容量+高负载：5台10kW=50kW容量，当前40kW (80%利用率)
        var devices = CreateDevices(5, "s3", ratedPower: 10, currentPower: 8);
        _twinRepo.Setup(r => r.GetByStationIdAsync("s3")).ReturnsAsync(devices);

        // peakMultiplier=1.5 → 40*1.5=60 > 50*0.8=40，触发建议
        var result = await _service.RunPeakLoadSimulationAsync("s3", new Dictionary<string, object>());

        result.Success.Should().BeTrue();
        result.Recommendations.Should().NotBeEmpty();
    }

    [Fact]
    public async Task PeakLoad_GeneratesTimeline()
    {
        var devices = CreateDevices(3, "s4");
        _twinRepo.Setup(r => r.GetByStationIdAsync("s4")).ReturnsAsync(devices);

        var result = await _service.RunPeakLoadSimulationAsync("s4",
            new Dictionary<string, object> { ["durationHours"] = 3 });

        result.Timeline.Should().NotBeEmpty();
        result.Timeline.Should().Contain(e => e.EventType == "LoadChange");
    }

    #endregion

    #region RunDeviceFailureSimulationAsync 设备故障

    [Fact]
    public async Task DeviceFailure_DeviceNotFound_ReturnsFailure()
    {
        _twinRepo.Setup(r => r.GetByStationIdAsync("s1"))
            .ReturnsAsync(CreateDevices(3, "s1"));

        var result = await _service.RunDeviceFailureSimulationAsync("s1", "NONEXISTENT");
        result.Success.Should().BeFalse();
        result.Results["error"].Should().Be("Device not found");
    }

    [Fact]
    public async Task DeviceFailure_ValidDevice_CalculatesImpact()
    {
        var devices = CreateDevices(4, "s1", ratedPower: 100, currentPower: 50);
        _twinRepo.Setup(r => r.GetByStationIdAsync("s1")).ReturnsAsync(devices);

        var result = await _service.RunDeviceFailureSimulationAsync("s1", "DEV-001");
        result.Success.Should().BeTrue();
        result.ScenarioType.Should().Be("DeviceFailure");
        result.Results.Should().ContainKey("failedDeviceId");
        result.Results.Should().ContainKey("remainingCapacity");
        result.Results.Should().ContainKey("lostCapacity");

        // 4*100=400 total, DEV-001 故障丢失 100, 剩余 300
        result.Results["failedDeviceId"].Should().Be("DEV-001");
        Convert.ToDouble(result.Results["remainingCapacity"]).Should().Be(300);
        Convert.ToDouble(result.Results["lostCapacity"]).Should().Be(100);
    }

    [Fact]
    public async Task DeviceFailure_GeneratesTimelineAndRecommendations()
    {
        var devices = CreateDevices(3, "s2");
        _twinRepo.Setup(r => r.GetByStationIdAsync("s2")).ReturnsAsync(devices);

        var result = await _service.RunDeviceFailureSimulationAsync("s2", "DEV-001");
        result.Timeline.Should().NotBeEmpty();
        result.Timeline.Should().Contain(e => e.EventType == "DeviceFailure");
        result.Recommendations.Should().NotBeEmpty();
    }

    #endregion

    #region RunCapacityPlanningSimulationAsync 容量规划

    [Fact]
    public async Task CapacityPlanning_NoDevices_ReturnsSuccessWithDefaults()
    {
        // 容量规划即使无设备也会返回 Success=true（使用默认值计算）
        _twinRepo.Setup(r => r.GetByStationIdAsync("empty"))
            .ReturnsAsync(new List<ChargingPileTwin>());

        var result = await _service.RunCapacityPlanningSimulationAsync("empty", 5);
        result.Success.Should().BeTrue();
        result.ScenarioType.Should().Be("CapacityPlanning");
        Convert.ToDouble(result.Results["currentPileCount"]).Should().Be(0);
        Convert.ToDouble(result.Results["additionalPiles"]).Should().Be(5);
    }

    [Fact]
    public async Task CapacityPlanning_AddPiles_CalculatesNewCapacity()
    {
        var devices = CreateDevices(4, "s1", ratedPower: 100);
        _twinRepo.Setup(r => r.GetByStationIdAsync("s1")).ReturnsAsync(devices);

        var result = await _service.RunCapacityPlanningSimulationAsync("s1", 3);
        result.Success.Should().BeTrue();
        result.ScenarioType.Should().Be("CapacityPlanning");
        result.Results.Should().ContainKey("currentCapacity");
        result.Results.Should().ContainKey("newTotalCapacity");
        result.Results.Should().ContainKey("additionalCapacity");

        // 当前 4*100=400kW, 新增 3*100=300kW, 总 700kW
        Convert.ToDouble(result.Results["currentCapacity"]).Should().Be(400);
        Convert.ToDouble(result.Results["additionalCapacity"]).Should().Be(300);
        Convert.ToDouble(result.Results["newTotalCapacity"]).Should().Be(700);
    }

    #endregion
}
