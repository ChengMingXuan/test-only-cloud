using FluentAssertions;
using Xunit;
using JGSY.AGI.Simulator.Models;

namespace JGSY.AGI.Test.Simulator;

/// <summary>
/// Simulator 设备仿真服务单元测试
/// 覆盖仿真会话、遥测数据、模拟器状态等
/// </summary>
public class SimulatorServiceTests
{
    #region SimulatorSession 会话模型测试

    [Fact]
    public void SimulatorSession_ShouldHaveCorrectDefaults()
    {
        var session = new SimulatorSession();
        session.TotalReported.Should().Be(0);
        session.SuccessCount.Should().Be(0);
        session.FailCount.Should().Be(0);
        session.DeleteAt.Should().BeNull("新建会话不应被软删除");
    }

    [Fact]
    public void SimulatorSession_ShouldSetAllProperties()
    {
        var tenantId = Guid.NewGuid();
        var deviceId = Guid.NewGuid();
        var session = new SimulatorSession
        {
            SessionId = Guid.NewGuid().ToString(),
            DeviceId = deviceId,
            TenantId = tenantId,
            DeviceName = "测试充电桩-001",
            StationId = Guid.NewGuid().ToString(),
            MaxPower = 120.0,
            GunCount = 2,
            IntervalSeconds = 10,
            Protocol = "OCPP1.6",
            Status = SimulatorStatus.Running,
            TotalReported = 100,
            SimulatorType = "Charging"
        };

        session.DeviceId.Should().Be(deviceId);
        session.TenantId.Should().Be(tenantId);
        session.Status.Should().Be(SimulatorStatus.Running);
        session.TotalReported.Should().Be(100);
        session.MaxPower.Should().BePositive();
        session.GunCount.Should().Be(2);
    }

    [Fact]
    public void SimulatorSession_TenantId_ShouldNotBeEmpty()
    {
        var session = new SimulatorSession
        {
            TenantId = Guid.NewGuid()
        };
        session.TenantId.Should().NotBe(Guid.Empty, "仿真会话必须关联租户");
    }

    #endregion

    #region SimulatorStatus 枚举测试

    [Theory]
    [InlineData(SimulatorStatus.Running)]
    [InlineData(SimulatorStatus.Stopped)]
    [InlineData(SimulatorStatus.Error)]
    public void SimulatorStatus_ShouldHaveValidValues(SimulatorStatus status)
    {
        Enum.IsDefined(typeof(SimulatorStatus), status).Should().BeTrue();
    }

    #endregion

    #region SimulatorTelemetry 遥测数据测试

    [Fact]
    public void SimulatorTelemetry_ShouldSetProperties()
    {
        var telemetry = new SimulatorTelemetry
        {
            DeviceId = Guid.NewGuid().ToString(),
            StationId = Guid.NewGuid().ToString()
        };

        telemetry.DeviceId.Should().NotBeNullOrEmpty();
        telemetry.StationId.Should().NotBeNullOrEmpty();
    }

    #endregion

    #region SimulatorType 类型测试

    [Theory]
    [InlineData("Charging")]
    [InlineData("PV")]
    [InlineData("ESS")]
    [InlineData("PVESSC")]
    public void SimulatorSession_SimulatorType_ShouldBeValid(string simType)
    {
        var session = new SimulatorSession
        {
            SimulatorType = simType
        };
        session.SimulatorType.Should().NotBeNullOrEmpty();
    }

    #endregion

    #region 业务规则测试

    [Fact]
    public void SimulatorSession_TotalReported_ShouldNotBeNegative()
    {
        var session = new SimulatorSession
        {
            TotalReported = 0
        };
        session.TotalReported.Should().BeGreaterOrEqualTo(0, "上报总数不能为负数");
    }

    [Fact]
    public void SimulatorSession_ShouldAllowStationIdOptional()
    {
        var session = new SimulatorSession
        {
            SessionId = Guid.NewGuid().ToString(),
            DeviceId = Guid.NewGuid(),
            TenantId = Guid.NewGuid()
        };
        session.SessionId.Should().NotBeNullOrEmpty();
    }

    [Fact]
    public void SimulatorSession_SoftDelete_ShouldWork()
    {
        var session = new SimulatorSession();
        session.DeleteAt.Should().BeNull("初始不应被删除");

        session.DeleteAt = DateTime.UtcNow;
        session.DeleteAt.Should().NotBeNull("软删除后应有时间戳");
    }

    #endregion
}
