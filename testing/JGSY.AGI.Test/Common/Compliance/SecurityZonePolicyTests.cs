using FluentAssertions;
using JGSY.AGI.Common.Core.Security.Zones;
using JGSY.AGI.Common.Hosting.Security;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;

namespace JGSY.AGI.Test.Common.Compliance;

/// <summary>
/// 安全区域策略测试
/// 合规项：ZONE-001~004, GB/T 36572 四区隔离
/// </summary>
public class SecurityZonePolicyTests
{
    private readonly SecurityZonePolicyService _service;

    public SecurityZonePolicyTests()
    {
        _service = new SecurityZonePolicyService(
            NullLogger<SecurityZonePolicyService>.Instance);
    }

    #region IsAllowed 跨区通信校验

    [Theory]
    [InlineData(SecurityZone.ZoneI_RealtimeControl, SecurityZone.ZoneI_RealtimeControl, true)]
    [InlineData(SecurityZone.ZoneII_NonRealtimeControl, SecurityZone.ZoneII_NonRealtimeControl, true)]
    [InlineData(SecurityZone.ZoneIII_ProductionManagement, SecurityZone.ZoneIII_ProductionManagement, true)]
    [InlineData(SecurityZone.ZoneIV_ExternalServices, SecurityZone.ZoneIV_ExternalServices, true)]
    public void 同区内通信始终允许(SecurityZone source, SecurityZone target, bool expected)
    {
        _service.IsAllowed(source, target).Should().Be(expected);
    }

    [Theory]
    [InlineData(SecurityZone.ZoneI_RealtimeControl, SecurityZone.ZoneII_NonRealtimeControl, true)]
    [InlineData(SecurityZone.ZoneII_NonRealtimeControl, SecurityZone.ZoneI_RealtimeControl, true)]
    [InlineData(SecurityZone.ZoneII_NonRealtimeControl, SecurityZone.ZoneIII_ProductionManagement, true)]
    [InlineData(SecurityZone.ZoneIII_ProductionManagement, SecurityZone.ZoneII_NonRealtimeControl, true)]
    [InlineData(SecurityZone.ZoneIII_ProductionManagement, SecurityZone.ZoneIV_ExternalServices, true)]
    [InlineData(SecurityZone.ZoneIV_ExternalServices, SecurityZone.ZoneIII_ProductionManagement, true)]
    public void 相邻区域通信允许(SecurityZone source, SecurityZone target, bool expected)
    {
        _service.IsAllowed(source, target).Should().Be(expected);
    }

    [Theory]
    [InlineData(SecurityZone.ZoneI_RealtimeControl, SecurityZone.ZoneIII_ProductionManagement)]
    [InlineData(SecurityZone.ZoneI_RealtimeControl, SecurityZone.ZoneIV_ExternalServices)]
    [InlineData(SecurityZone.ZoneII_NonRealtimeControl, SecurityZone.ZoneIV_ExternalServices)]
    public void 跨多区通信被禁止(SecurityZone source, SecurityZone target)
    {
        _service.IsAllowed(source, target).Should().BeFalse(
            $"GB/T 36572: {source} → {target} 跨多区通信应被禁止");
    }

    #endregion

    #region GetAllowedTargets 校验

    [Fact]
    public void ZoneI允许的目标应包含ZoneII()
    {
        var targets = _service.GetAllowedTargets(SecurityZone.ZoneI_RealtimeControl);

        targets.Should().Contain(SecurityZone.ZoneII_NonRealtimeControl, "相邻区 Ⅰ→Ⅱ");
        targets.Should().NotContain(SecurityZone.ZoneIII_ProductionManagement, "跨区 Ⅰ→Ⅲ 应禁止");
        targets.Should().NotContain(SecurityZone.ZoneIV_ExternalServices, "跨区 Ⅰ→Ⅳ 应禁止");
    }

    [Fact]
    public void ZoneIV允许的目标应包含ZoneIII()
    {
        var targets = _service.GetAllowedTargets(SecurityZone.ZoneIV_ExternalServices);

        targets.Should().Contain(SecurityZone.ZoneIII_ProductionManagement, "相邻区 Ⅳ→Ⅲ");
        targets.Should().NotContain(SecurityZone.ZoneI_RealtimeControl, "跨区 Ⅳ→Ⅰ 应禁止");
    }

    #endregion

    #region ValidateTransitAsync 校验

    [Fact]
    public async Task 允许的跨区传输应返回Allowed()
    {
        var result = await _service.ValidateTransitAsync(
            SecurityZone.ZoneI_RealtimeControl,
            SecurityZone.ZoneII_NonRealtimeControl,
            "Telemetry");

        result.Allowed.Should().BeTrue("Ⅰ→Ⅱ 遥测上行应被允许");
    }

    [Fact]
    public async Task 禁止的跨区传输应返回NotAllowed()
    {
        var result = await _service.ValidateTransitAsync(
            SecurityZone.ZoneI_RealtimeControl,
            SecurityZone.ZoneIV_ExternalServices,
            "ControlCommand");

        result.Allowed.Should().BeFalse("Ⅰ→Ⅳ 控制指令应被禁止");
    }

    [Fact]
    public async Task I区到II区应要求签名()
    {
        var result = await _service.ValidateTransitAsync(
            SecurityZone.ZoneII_NonRealtimeControl,
            SecurityZone.ZoneI_RealtimeControl,
            "ControlCommand");

        result.RequiresSignature.Should().BeTrue("Ⅱ→Ⅰ 控制指令下发应要求 SM2 签名");
    }

    [Fact]
    public async Task 跨区传输应标记需要加密()
    {
        // RequiresEncryption 仅当 Ⅰ/Ⅱ→Ⅲ/Ⅳ 时要求加密
        var result = await _service.ValidateTransitAsync(
            SecurityZone.ZoneII_NonRealtimeControl,
            SecurityZone.ZoneIII_ProductionManagement,
            "Telemetry");

        result.RequiresEncryption.Should().BeTrue("Ⅱ→Ⅲ 跨控制区/管理区传输应要求 SM4 加密");
    }

    #endregion

    #region SecurityZoneRegistry 测试

    [Fact]
    public void Ingestion服务应在ZoneI()
    {
        SecurityZoneRegistry.ServiceZones["Ingestion"]
            .Should().Be(SecurityZone.ZoneI_RealtimeControl);
    }

    [Fact]
    public void Device服务应在ZoneI()
    {
        SecurityZoneRegistry.ServiceZones["Device"]
            .Should().Be(SecurityZone.ZoneI_RealtimeControl);
    }

    [Fact]
    public void RuleEngine服务应在ZoneII()
    {
        SecurityZoneRegistry.ServiceZones["RuleEngine"]
            .Should().Be(SecurityZone.ZoneII_NonRealtimeControl);
    }

    [Fact]
    public void Gateway服务应在ZoneIII()
    {
        SecurityZoneRegistry.ServiceZones["Gateway"]
            .Should().Be(SecurityZone.ZoneIII_ProductionManagement);
    }

    [Fact]
    public void Blockchain服务应在ZoneIV()
    {
        SecurityZoneRegistry.ServiceZones["Blockchain"]
            .Should().Be(SecurityZone.ZoneIV_ExternalServices);
    }

    [Fact]
    public void AllowedFlows矩阵应包含所有关键路径()
    {
        SecurityZoneRegistry.AllowedFlows.Should().ContainKey(
            (SecurityZone.ZoneI_RealtimeControl, SecurityZone.ZoneII_NonRealtimeControl),
            "Ⅰ→Ⅱ 遥测上行");

        SecurityZoneRegistry.AllowedFlows.Should().ContainKey(
            (SecurityZone.ZoneII_NonRealtimeControl, SecurityZone.ZoneI_RealtimeControl),
            "Ⅱ→Ⅰ 控制下发");
    }

    [Fact]
    public void IsFlowAllowed应正确判断跨区通信()
    {
        SecurityZoneRegistry.IsFlowAllowed(
            SecurityZone.ZoneI_RealtimeControl,
            SecurityZone.ZoneII_NonRealtimeControl).Should().BeTrue("Ⅰ→Ⅱ 允许");

        SecurityZoneRegistry.IsFlowAllowed(
            SecurityZone.ZoneI_RealtimeControl,
            SecurityZone.ZoneIV_ExternalServices).Should().BeFalse("Ⅰ→Ⅳ 禁止");
    }

    #endregion
}
