using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.Orchestrator;

/// <summary>
/// Orchestrator 跨域调度仲裁服务单元测试
/// 覆盖调度策略、执行日志、动态配置等实体
/// </summary>
public class OrchestratorServiceTests
{
    #region OrchDispatchStrategy 调度策略实体测试

    [Fact]
    public void OrchDispatchStrategy_ShouldHaveCorrectDefaults()
    {
        var strategy = new AGI.Orchestrator.Entities.OrchDispatchStrategy();
        strategy.DeleteAt.Should().BeNull("新建策略不应被软删除");
        strategy.Id.Should().Be(Guid.Empty);
    }

    [Fact]
    public void OrchDispatchStrategy_ShouldSetAllProperties()
    {
        var tenantId = Guid.NewGuid();
        var strategy = new AGI.Orchestrator.Entities.OrchDispatchStrategy
        {
            Id = Guid.NewGuid(),
            TenantId = tenantId,
            StrategyName = "峰谷调度策略",
            PriorityOrder = "1",
            IsDefault = true
        };

        strategy.StrategyName.Should().Be("峰谷调度策略");
        strategy.PriorityOrder.Should().Be("1");
        strategy.IsDefault.Should().BeTrue();
        strategy.TenantId.Should().Be(tenantId);
    }

    [Theory]
    [InlineData("1")]
    [InlineData("5")]
    [InlineData("10")]
    public void OrchDispatchStrategy_PriorityOrder_ShouldBeValid(string priority)
    {
        var strategy = new AGI.Orchestrator.Entities.OrchDispatchStrategy
        {
            PriorityOrder = priority
        };
        strategy.PriorityOrder.Should().NotBeNullOrEmpty("优先级顺序不应为空");
    }

    #endregion

    #region OrchDispatchLog 调度日志实体测试

    [Fact]
    public void OrchDispatchLog_ShouldSetProperties()
    {
        var log = new AGI.Orchestrator.Entities.OrchDispatchLog
        {
            Id = Guid.NewGuid(),
            StrategyId = Guid.NewGuid(),
            DispatchTime = DateTime.UtcNow,
            TotalPowerKw = 1500.0m,
            ExecutionResult = "success"
        };

        log.TotalPowerKw.Should().BePositive();
        log.ExecutionResult.Should().Be("success");
        log.DispatchTime.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(5));
    }

    [Fact]
    public void OrchDispatchLog_ShouldHaveCorrectDefaults()
    {
        var log = new AGI.Orchestrator.Entities.OrchDispatchLog();
        log.DeleteAt.Should().BeNull("新建调度日志不应被软删除");
    }

    #endregion

    #region OrchDynamicConfig 动态配置实体测试

    [Fact]
    public void OrchDynamicConfig_ShouldSetProperties()
    {
        var config = new AGI.SEHS.Entities.OrchDynamicConfig
        {
            Id = Guid.NewGuid(),
            ConfigKey = "dispatch.max_power_kw",
            ConfigValue = "5000",
            ConfigGroup = "dispatch",
            Version = 1,
            IsEncrypted = false
        };

        config.ConfigKey.Should().Contain("dispatch");
        config.ConfigValue.Should().NotBeNullOrEmpty();
        config.IsEncrypted.Should().BeFalse();
        config.Version.Should().Be(1);
    }

    [Fact]
    public void OrchDynamicConfig_TenantId_ShouldNotBeEmpty()
    {
        var config = new AGI.SEHS.Entities.OrchDynamicConfig
        {
            TenantId = Guid.NewGuid(),
            ConfigKey = "test.key",
            ConfigValue = "test_value"
        };
        config.TenantId.Should().NotBe(Guid.Empty, "动态配置必须关联租户");
    }

    [Theory]
    [InlineData("dispatch.max_power_kw", "5000")]
    [InlineData("dispatch.min_interval_s", "60")]
    [InlineData("dispatch.retry_count", "3")]
    public void OrchDynamicConfig_KeyValue_ShouldBeValid(string key, string value)
    {
        var config = new AGI.SEHS.Entities.OrchDynamicConfig
        {
            ConfigKey = key,
            ConfigValue = value
        };
        config.ConfigKey.Should().NotBeNullOrEmpty();
        config.ConfigValue.Should().NotBeNullOrEmpty();
    }

    #endregion
}
