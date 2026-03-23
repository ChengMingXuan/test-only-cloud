using FluentAssertions;
using JGSY.AGI.DigitalTwin.Models;
using Xunit;

namespace JGSY.AGI.Test.DigitalTwin;

/// <summary>
/// 数字孪生模型单元测试
/// </summary>
public class DigitalTwinModelTests
{
    #region ChargingPileTwin 测试

    [Fact]
    public void ChargingPileTwin_ShouldHaveCorrectDefaults()
    {
        var twin = new ChargingPileTwin();
        twin.CurrentPower.Should().Be(0);
        twin.HealthScore.Should().Be(0);
        twin.UtilizationRate.Should().Be(0);
    }

    [Fact]
    public void ChargingPileTwin_ShouldSetAllProperties()
    {
        var twin = new ChargingPileTwin
        {
            TwinId = Guid.NewGuid(),
            PhysicalDeviceId = "device-001",
            RatedPower = 120.0,
            CurrentPower = 85.5,
            HealthScore = 92.3,
            UtilizationRate = 78.0,
            GunStates = new List<GunTwinState>
            {
                new() { GunNo = 1, Voltage = 380.0, Current = 32.0, Power = 12.16 },
                new() { GunNo = 2, Voltage = 0.0, Current = 0.0, Power = 0.0 }
            }
        };

        twin.TwinId.Should().NotBeEmpty();
        twin.RatedPower.Should().Be(120.0);
        twin.CurrentPower.Should().BeLessThanOrEqualTo(twin.RatedPower);
        twin.HealthScore.Should().BeInRange(0, 100);
        twin.GunStates.Should().HaveCount(2);
        twin.GunStates[0].Power.Should().BePositive();
    }

    [Theory]
    [InlineData(0, 100, 0)]
    [InlineData(50, 100, 50)]
    [InlineData(100, 100, 100)]
    public void ChargingPileTwin_UtilizationRate_ShouldBeValid(double current, double rated, double expected)
    {
        var twin = new ChargingPileTwin
        {
            CurrentPower = current,
            RatedPower = rated,
            UtilizationRate = expected
        };

        twin.UtilizationRate.Should().BeInRange(0, 100);
    }

    #endregion

    #region StationTwin 测试

    [Fact]
    public void StationTwin_ShouldHaveCorrectDefaults()
    {
        var station = new StationTwin();
        station.TotalPileCount.Should().Be(0);
        station.OnlinePileCount.Should().Be(0);
        station.CurrentTotalPower.Should().Be(0);
    }

    [Fact]
    public void StationTwin_ShouldAggregateFromPiles()
    {
        var station = new StationTwin
        {
            TwinId = Guid.NewGuid(),
            StationName = "A站",
            TotalPileCount = 10,
            OnlinePileCount = 8,
            CurrentTotalPower = 500.0,
            OverallHealthScore = 88.5,
            ChargingPiles = new List<ChargingPileTwin>
            {
                new() { TwinId = Guid.NewGuid(), HealthScore = 90 },
                new() { TwinId = Guid.NewGuid(), HealthScore = 87 }
            }
        };

        station.OnlinePileCount.Should().BeLessThanOrEqualTo(station.TotalPileCount);
        station.OverallHealthScore.Should().BeInRange(0, 100);
        station.ChargingPiles.Should().HaveCount(2);
    }

    #endregion

    #region GunTwinState 测试

    [Fact]
    public void GunTwinState_ShouldCalculateCorrectPower()
    {
        var gun = new GunTwinState
        {
            GunNo = 1,
            Voltage = 380.0,
            Current = 32.0,
            Power = 12.16, // kW
            SOC = 65.5
        };

        gun.GunNo.Should().BePositive();
        gun.Power.Should().BePositive();
        gun.SOC.Should().BeInRange(0, 100);
    }

    #endregion

    #region DeviceMessage 测试

    [Fact]
    public void DeviceMessage_ShouldSetAllProperties()
    {
        var msg = new DeviceMessage
        {
            DeviceId = "dev-001",
            MessageType = "telemetry",
            Status = DeviceStatus.Charging,
            Power = 55.3,
            Temperature = 42.1,
            Timestamp = DateTime.UtcNow
        };

        msg.DeviceId.Should().Be("dev-001");
        msg.Status.Should().Be(DeviceStatus.Charging);
        msg.Power.Should().BePositive();
        msg.Temperature.Should().BeInRange(-40, 200);
        msg.Timestamp.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(5));
    }

    #endregion

    #region MaintenanceAlert 测试

    [Fact]
    public void MaintenanceAlert_ShouldHaveProperties()
    {
        var alert = new MaintenanceAlert
        {
            AlertId = Guid.NewGuid(),
            DeviceId = "dev-001",
            Severity = AlertSeverity.Warning,
            Title = "温度过高告警",
            Recommendations = new List<string>
            {
                "检查散热系统",
                "降低输出功率",
                "联系维修人员"
            }
        };

        alert.Severity.Should().Be(AlertSeverity.Warning);
        alert.Recommendations.Should().HaveCountGreaterThan(0);
    }

    #endregion
}
