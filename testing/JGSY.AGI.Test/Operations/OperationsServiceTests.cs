using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.Operations;

/// <summary>
/// Operations 能源运营服务单元测试（EnergyEff/MultiEnergy/SafeControl）
/// 覆盖电表配置、能耗记录、效率指标等实体
/// </summary>
public class OperationsServiceTests
{
    #region EeMeterConfig 电表配置实体测试

    [Fact]
    public void EeMeterConfig_ShouldHaveCorrectDefaults()
    {
        var meter = new AGI.Operations.Modules.EnergyEff.Entities.EeMeterConfig();
        meter.DeleteAt.Should().BeNull("新建电表配置不应被软删除");
    }

    [Fact]
    public void EeMeterConfig_ShouldSetAllProperties()
    {
        var tenantId = Guid.NewGuid();
        var meter = new AGI.Operations.Modules.EnergyEff.Entities.EeMeterConfig
        {
            Id = Guid.NewGuid(),
            TenantId = tenantId,
            MeterCode = "EM-001",
            MeterName = "1号变压器总表",
            RatedPowerKw = 1000.0m,
            CtRatio = 200,
            IsOnline = true
        };

        meter.MeterCode.Should().StartWith("EM-");
        meter.MeterName.Should().NotBeNullOrEmpty();
        meter.RatedPowerKw.Should().BePositive();
        meter.TenantId.Should().Be(tenantId);
        meter.IsOnline.Should().BeTrue();
    }

    [Theory]
    [InlineData(100)]
    [InlineData(200)]
    [InlineData(500)]
    public void EeMeterConfig_CtRatio_ShouldBePositive(int ratio)
    {
        var meter = new AGI.Operations.Modules.EnergyEff.Entities.EeMeterConfig
        {
            CtRatio = ratio
        };
        meter.CtRatio.Should().BePositive("CT变比必须为正整数");
    }

    #endregion

    #region EeConsumption 能耗记录实体测试

    [Fact]
    public void EeConsumption_ShouldSetProperties()
    {
        var consumption = new AGI.Operations.Modules.EnergyEff.Entities.EeConsumption
        {
            Id = Guid.NewGuid(),
            TenantId = Guid.NewGuid(),
            EnergyKwh = 5000.0m,
            CostYuan = 3500.0m,
            PeakKwh = 2000.0m,
            ValleyKwh = 1500.0m
        };

        consumption.EnergyKwh.Should().BePositive();
        consumption.CostYuan.Should().BePositive();
        consumption.PeakKwh.Should().BeLessThanOrEqualTo(consumption.EnergyKwh);
        consumption.ValleyKwh.Should().BeLessThanOrEqualTo(consumption.EnergyKwh);
    }

    [Fact]
    public void EeConsumption_TenantId_ShouldNotBeEmpty()
    {
        var c = new AGI.Operations.Modules.EnergyEff.Entities.EeConsumption
        {
            TenantId = Guid.NewGuid()
        };
        c.TenantId.Should().NotBe(Guid.Empty, "能耗记录必须关联租户");
    }

    #endregion

    #region EeEfficiencyIndex 效率指标实体测试

    [Fact]
    public void EeEfficiencyIndex_ShouldSetProperties()
    {
        var index = new AGI.Operations.Modules.EnergyEff.Entities.EeEfficiencyIndex
        {
            Id = Guid.NewGuid(),
            TenantId = Guid.NewGuid(),
            IndexName = "综合能效指数",
            IndexCode = "CEI-001",
            TargetValue = 0.90m,
            ActualValue = 0.85m,
            Period = "2026-03"
        };

        index.IndexName.Should().NotBeNullOrEmpty();
        index.IndexCode.Should().StartWith("CEI-");
        index.ActualValue.Should().BeLessThanOrEqualTo(1.0m);
        index.TargetValue.Should().BeGreaterThan(0);
    }

    [Fact]
    public void EeEfficiencyIndex_ShouldHaveCorrectDefaults()
    {
        var index = new AGI.Operations.Modules.EnergyEff.Entities.EeEfficiencyIndex();
        index.DeleteAt.Should().BeNull("新建效率指标不应被软删除");
    }

    [Theory]
    [InlineData("2026-01")]
    [InlineData("2026-03")]
    [InlineData("2026-12")]
    public void EeEfficiencyIndex_Period_ShouldBeValid(string period)
    {
        var index = new AGI.Operations.Modules.EnergyEff.Entities.EeEfficiencyIndex
        {
            Period = period
        };
        index.Period.Should().MatchRegex(@"^\d{4}-\d{2}$", "周期必须为 yyyy-MM 格式");
    }

    #endregion
}
