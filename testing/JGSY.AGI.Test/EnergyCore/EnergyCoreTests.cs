using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.EnergyCore;

/// <summary>
/// 能源核心模块实体单元测试（VPP / MicroGrid / SEHS / PVESSC）
/// </summary>
public class EnergyCoreEntityTests
{
    #region VPP 虚拟电厂

    [Fact]
    public void VppInfo_ShouldHaveCorrectDefaults()
    {
        var vpp = new AGI.VPP.Entities.VppInfo();
        vpp.DeleteAt.Should().BeNull();
        vpp.CapacityMw.Should().BeNull();
    }

    [Fact]
    public void VppInfo_ShouldSetAllProperties()
    {
        var vpp = new AGI.VPP.Entities.VppInfo
        {
            Name = "华北虚拟电厂",
            Code = "VPP-HB-001",
            Status = 1, // active
            CapacityMw = 50.0m,
            GridDispatchEnabled = true,
            ElecTradeEnabled = true,
            CarbonTradeEnabled = false
        };

        vpp.Name.Should().Be("华北虚拟电厂");
        vpp.Code.Should().StartWith("VPP-");
        vpp.CapacityMw.Should().BeGreaterThan(0);
        vpp.GridDispatchEnabled.Should().BeTrue();
    }

    [Fact]
    public void VppResource_ShouldSetAllProperties()
    {
        var resource = new AGI.VPP.Entities.VppResource
        {
            VppId = Guid.NewGuid(),
            DeviceId = Guid.NewGuid(),
            ResourceType = 1, // storage
            RatedPowerKw = 500.0m,
            AvailablePowerKw = 350.0m,
            Status = 1 // online
        };

        resource.AvailablePowerKw.Should().BeLessThanOrEqualTo(resource.RatedPowerKw.Value);
        resource.ResourceType.Should().Be(1);
    }

    #endregion

    #region MicroGrid 微电网

    [Fact]
    public void MgInfo_ShouldHaveCorrectDefaults()
    {
        var mg = new AGI.MicroGrid.Entities.MgInfo();
        mg.DeleteAt.Should().BeNull();
        mg.RatedCapacityKw.Should().BeNull();
    }

    [Fact]
    public void MgInfo_ShouldSetAllProperties()
    {
        var mg = new AGI.MicroGrid.Entities.MgInfo
        {
            Name = "园区微电网",
            Code = "MG-YQ-001",
            GridType = 1, // AC
            CurrentMode = 1, // grid-connected
            RatedCapacityKw = 200.0m,
            IslandModeEnabled = true,
            VppRegistered = true
        };

        mg.Code.Should().StartWith("MG-");
        mg.GridType.Should().Be(1);
        mg.IslandModeEnabled.Should().BeTrue();
    }

    [Fact]
    public void MgPowerRecord_ShouldTrackPowerFlow()
    {
        var record = new AGI.MicroGrid.Entities.MgPowerRecord
        {
            GridId = Guid.NewGuid(),
            SourcePowerKw = 100.0m,
            LoadPowerKw = 80.0m,
            StoragePowerKw = 15.0m,
            GridExchangeKw = 5.0m,
            FrequencyHz = 50.0m
        };

        record.FrequencyHz.Should().NotBeNull();
        record.FrequencyHz.Value.Should().BeInRange(49.0m, 51.0m);
        record.LoadPowerKw.Should().BeLessThanOrEqualTo(record.SourcePowerKw.Value + record.StoragePowerKw.Value + record.GridExchangeKw.Value);
    }

    #endregion

    #region SEHS 源储荷一体化

    [Fact]
    public void SehsResourceSnapshot_ShouldTrackBalance()
    {
        var snapshot = new AGI.SEHS.Entities.SehsResourceSnapshot
        {
            SourcePowerKw = 200.0m,
            GridPowerKw = 50.0m,
            LoadPowerKw = 180.0m,
            StoragePowerKw = 70.0m,
            StorageSoc = 75.0m,
            PvGenerationKw = 120.0m
        };

        snapshot.StorageSoc.Should().BeInRange(0, 100);
        snapshot.PvGenerationKw.Should().BeLessThanOrEqualTo(snapshot.SourcePowerKw);
    }

    [Fact]
    public void SehsSchedulePlan_ShouldSetAllProperties()
    {
        var plan = new AGI.SEHS.Entities.SehsSchedulePlan
        {
            PlanName = "日前调度计划",
            PlanType = 1, // day-ahead
            PlanDate = new DateTime(2026, 2, 13),
            Objective = 1, // cost-minimize
            TotalCost = 15000.0m,
            GreenRatio = 85.0m,
            Status = 1 // approved
        };

        plan.PlanName.Should().NotBeEmpty();
        plan.GreenRatio.Should().NotBeNull();
        plan.GreenRatio.Value.Should().BeInRange(0, 100);
        plan.Status.Should().Be(1);
    }

    #endregion
}

/// <summary>
/// VPP DTO 测试
/// </summary>
public class EnergyCoreVppDtoTests
{
    [Fact]
    public void CreateVppRequest_ShouldHaveRequiredFields()
    {
        var request = new AGI.VPP.Models.CreateVppRequest
        {
            Name = "测试虚拟电厂",
            Code = "VPP-TEST-001",
            Region = "华北",
            CapacityMw = 100.0m,
            GridDispatchEnabled = true
        };

        request.Name.Should().NotBeEmpty();
        request.Code.Should().NotBeEmpty();
        request.CapacityMw.Should().BePositive();
    }

    [Fact]
    public void VppInfoDto_ShouldSetAllProperties()
    {
        var dto = new AGI.VPP.Models.VppInfoDto
        {
            Id = Guid.NewGuid(),
            Name = "示范虚拟电厂",
            Code = "VPP-SF-001",
            Status = 1 // online
        };

        dto.Id.Should().NotBeEmpty();
        dto.Status.Should().Be(1);
    }
}
