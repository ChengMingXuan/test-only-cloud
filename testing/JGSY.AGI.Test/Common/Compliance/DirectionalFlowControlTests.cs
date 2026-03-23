using FluentAssertions;
using JGSY.AGI.Common.Core.Security.Zones;
using JGSY.AGI.Common.Hosting.Security;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;

namespace JGSY.AGI.Test.Common.Compliance;

/// <summary>
/// 数据流方向控制测试
/// 合规项：FLOW-001~003, DEPLOY-003, GB/T 36572
/// 一票否决：云端禁止向本地下发控制指令
/// </summary>
public class DirectionalFlowControlTests
{
    private readonly DirectionalFlowControlService _service;

    public DirectionalFlowControlTests()
    {
        _service = new DirectionalFlowControlService(
            NullLogger<DirectionalFlowControlService>.Instance);
    }

    #region FLOW-001: 遥测数据只上不下

    [Fact]
    public void 遥测数据I到II上行应允许()
    {
        var result = _service.ValidateDirection(
            SecurityZone.ZoneI_RealtimeControl,
            SecurityZone.ZoneII_NonRealtimeControl,
            DataFlowType.Telemetry);

        result.Allowed.Should().BeTrue("FLOW-001: 遥测数据 Ⅰ→Ⅱ 上行应允许");
    }

    [Fact]
    public void 遥测数据III到II下行应禁止()
    {
        var result = _service.ValidateDirection(
            SecurityZone.ZoneIII_ProductionManagement,
            SecurityZone.ZoneII_NonRealtimeControl,
            DataFlowType.Telemetry);

        result.Allowed.Should().BeFalse("FLOW-001: 遥测数据禁止下行 Ⅲ→Ⅱ");
    }

    [Fact]
    public void 遥测数据III到I下行应禁止()
    {
        var result = _service.ValidateDirection(
            SecurityZone.ZoneIII_ProductionManagement,
            SecurityZone.ZoneI_RealtimeControl,
            DataFlowType.Telemetry);

        result.Allowed.Should().BeFalse("FLOW-001: 遥测数据禁止下行 Ⅲ→Ⅰ");
    }

    [Fact]
    public void 遥测数据II到I下行应禁止()
    {
        var result = _service.ValidateDirection(
            SecurityZone.ZoneII_NonRealtimeControl,
            SecurityZone.ZoneI_RealtimeControl,
            DataFlowType.Telemetry);

        result.Allowed.Should().BeFalse("FLOW-001: 遥测数据禁止下行 Ⅱ→Ⅰ");
    }

    #endregion

    #region FLOW-002 / DEPLOY-003: 控制指令本地闭环（一票否决）

    [Fact]
    public void 控制指令II到I本地下发应允许()
    {
        var result = _service.ValidateDirection(
            SecurityZone.ZoneII_NonRealtimeControl,
            SecurityZone.ZoneI_RealtimeControl,
            DataFlowType.ControlCommand);

        result.Allowed.Should().BeTrue("FLOW-003: 控制指令仅允许 Ⅱ→Ⅰ 本地闭环");
    }

    [Fact]
    public void 一票否决_云端III到II控制指令应禁止()
    {
        var result = _service.ValidateDirection(
            SecurityZone.ZoneIII_ProductionManagement,
            SecurityZone.ZoneII_NonRealtimeControl,
            DataFlowType.ControlCommand);

        result.Allowed.Should().BeFalse("一票否决 DEPLOY-003: 云端 Ⅲ→Ⅱ 控制指令禁止");
        result.DenialReason.Should().Contain("一票否决", "拒绝原因应包含一票否决标识");
    }

    [Fact]
    public void 一票否决_云端III到I控制指令应禁止()
    {
        var result = _service.ValidateDirection(
            SecurityZone.ZoneIII_ProductionManagement,
            SecurityZone.ZoneI_RealtimeControl,
            DataFlowType.ControlCommand);

        result.Allowed.Should().BeFalse("一票否决 DEPLOY-003: 云端 Ⅲ→Ⅰ 控制指令禁止");
    }

    [Fact]
    public void 一票否决_外部IV到III控制指令应禁止()
    {
        var result = _service.ValidateDirection(
            SecurityZone.ZoneIV_ExternalServices,
            SecurityZone.ZoneIII_ProductionManagement,
            DataFlowType.ControlCommand);

        result.Allowed.Should().BeFalse("一票否决: 外部 Ⅳ→Ⅲ 控制指令禁止");
    }

    [Fact]
    public void 一票否决_外部IV到I控制指令应禁止()
    {
        var result = _service.ValidateDirection(
            SecurityZone.ZoneIV_ExternalServices,
            SecurityZone.ZoneI_RealtimeControl,
            DataFlowType.ControlCommand);

        result.Allowed.Should().BeFalse("一票否决: 外部 Ⅳ→Ⅰ 控制指令禁止");
    }

    #endregion

    #region 策略下发方向控制

    [Fact]
    public void 策略下发III到II应允许()
    {
        var result = _service.ValidateDirection(
            SecurityZone.ZoneIII_ProductionManagement,
            SecurityZone.ZoneII_NonRealtimeControl,
            DataFlowType.StrategyDispatch);

        result.Allowed.Should().BeTrue("策略下发 Ⅲ→Ⅱ 应允许");
    }

    [Fact]
    public void 策略下发从错误方向应禁止()
    {
        var result = _service.ValidateDirection(
            SecurityZone.ZoneII_NonRealtimeControl,
            SecurityZone.ZoneIII_ProductionManagement,
            DataFlowType.StrategyDispatch);

        result.Allowed.Should().BeFalse("策略下发仅允许 Ⅲ→Ⅱ");
    }

    #endregion

    #region 同区通信

    [Theory]
    [InlineData(SecurityZone.ZoneI_RealtimeControl)]
    [InlineData(SecurityZone.ZoneII_NonRealtimeControl)]
    [InlineData(SecurityZone.ZoneIII_ProductionManagement)]
    [InlineData(SecurityZone.ZoneIV_ExternalServices)]
    public void 同区内通信始终允许(SecurityZone zone)
    {
        var result = _service.ValidateDirection(zone, zone, DataFlowType.ControlCommand);

        result.Allowed.Should().BeTrue($"同区 {zone} 内通信应始终允许");
    }

    #endregion

    #region LogFlowEventAsync

    [Fact]
    public async Task 记录流事件不应抛出异常()
    {
        var flowEvent = new FlowEvent(
            "TestSource", "TestTarget",
            SecurityZone.ZoneI_RealtimeControl,
            SecurityZone.ZoneII_NonRealtimeControl,
            DataFlowType.Telemetry,
            1024, true,
            DateTimeOffset.UtcNow);

        var act = () => _service.LogFlowEventAsync(flowEvent);
        await act.Should().NotThrowAsync("记录流事件应正常完成");
    }

    #endregion

    #region GetFlowStatsAsync

    [Fact]
    public async Task 获取流统计应返回空列表()
    {
        var stats = await _service.GetFlowStatsAsync(
            DateTimeOffset.UtcNow.AddHours(-1),
            DateTimeOffset.UtcNow);

        stats.Should().NotBeNull();
        stats.Should().BeEmpty("初始状态下统计应为空");
    }

    #endregion
}
