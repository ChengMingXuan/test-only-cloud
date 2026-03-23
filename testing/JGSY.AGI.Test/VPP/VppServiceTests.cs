using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.VPP;

/// <summary>
/// VPP 虚拟电厂服务单元测试
/// 覆盖实体默认值、属性赋值、业务规则验证
/// </summary>
public class VppServiceTests
{
    #region VppInfo 实体测试

    [Fact]
    public void VppInfo_ShouldHaveCorrectDefaults()
    {
        var vpp = new AGI.VPP.Entities.VppInfo();
        vpp.DeleteAt.Should().BeNull("新建实体不应被软删除");
        vpp.Id.Should().Be(Guid.Empty);
        vpp.CapacityMw.Should().BeNull();
    }

    [Fact]
    public void VppInfo_ShouldSetAllProperties()
    {
        var tenantId = Guid.NewGuid();
        var vpp = new AGI.VPP.Entities.VppInfo
        {
            Id = Guid.NewGuid(),
            TenantId = tenantId,
            Name = "华北虚拟电厂",
            Code = "VPP-HB-001",
            Status = 1,
            CapacityMw = 50.0m,
            GridDispatchEnabled = true,
            ElecTradeEnabled = true,
            CarbonTradeEnabled = false
        };

        vpp.Name.Should().Be("华北虚拟电厂");
        vpp.Code.Should().StartWith("VPP-");
        vpp.TenantId.Should().Be(tenantId);
        vpp.CapacityMw.Should().BeGreaterThan(0);
        vpp.GridDispatchEnabled.Should().BeTrue();
        vpp.CarbonTradeEnabled.Should().BeFalse();
    }

    [Fact]
    public void VppInfo_TenantId_ShouldNotBeEmpty()
    {
        var vpp = new AGI.VPP.Entities.VppInfo
        {
            TenantId = Guid.NewGuid()
        };
        vpp.TenantId.Should().NotBe(Guid.Empty, "租户ID不能为空");
    }

    #endregion

    #region VppResource 实体测试

    [Fact]
    public void VppResource_ShouldSetAllProperties()
    {
        var resource = new AGI.VPP.Entities.VppResource
        {
            Id = Guid.NewGuid(),
            VppId = Guid.NewGuid(),
            DeviceId = Guid.NewGuid(),
            ResourceType = 1,
            RatedPowerKw = 500.0m,
            AvailablePowerKw = 350.0m,
            Status = 1
        };

        resource.AvailablePowerKw.Should().BeLessThanOrEqualTo(resource.RatedPowerKw.Value,
            "可用功率不应超过额定功率");
        resource.ResourceType.Should().Be(1);
        resource.VppId.Should().NotBe(Guid.Empty);
    }

    [Fact]
    public void VppResource_ShouldHaveCorrectDefaults()
    {
        var resource = new AGI.VPP.Entities.VppResource();
        resource.DeleteAt.Should().BeNull("新建资源不应被软删除");
    }

    #endregion

    #region VppDispatchRecord 实体测试

    [Fact]
    public void VppDispatchRecord_ShouldSetProperties()
    {
        var record = new AGI.VPP.Entities.VppDispatchRecord
        {
            Id = Guid.NewGuid(),
            VppId = Guid.NewGuid(),
            InstructionType = 1, // peak_shaving
            RequiredPowerKw = 200.0m,
            Status = 0 // pending
        };

        record.InstructionType.Should().Be((short)1);
        record.RequiredPowerKw.Should().BePositive();
        record.Status.Should().Be((short)0);
    }

    [Theory]
    [InlineData((short)1)] // 削峰填谷
    [InlineData((short)2)] // 调频
    [InlineData((short)3)] // 需求响应
    [InlineData((short)4)] // 紧急调度
    public void VppDispatchRecord_InstructionType_ShouldBeValid(short instructionType)
    {
        var record = new AGI.VPP.Entities.VppDispatchRecord
        {
            InstructionType = instructionType
        };
        record.InstructionType.Should().BeGreaterThan((short)0);
    }

    #endregion
}
