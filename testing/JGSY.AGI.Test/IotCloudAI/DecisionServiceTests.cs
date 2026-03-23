using Xunit;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using JGSY.AGI.IotCloudAI.Core.Services;
using JGSY.AGI.IotCloudAI.Models;

namespace JGSY.AGI.Test.IotCloudAI;

/// <summary>DecisionService 单元测试</summary>
public class DecisionServiceTests
{
    private readonly DecisionService _sut;

    public DecisionServiceTests()
    {
        _sut = new DecisionService(NullLogger<DecisionService>.Instance);
    }

    // ========== GenerateStrategyAsync ==========

    [Fact]
    public async Task GenerateStrategyAsync_高风险生成紧急响应策略()
    {
        var awareness = new SituationAwareness
        {
            EntityId = "device-001",
            OverallStatus = "Critical",
            RiskLevel = 0.85
        };

        var result = await _sut.GenerateStrategyAsync(awareness);

        result.Status.Should().Be("Success");
        result.Priority.Should().Be("Critical");
        result.RecommendedActions.Should().HaveCount(1);
        result.RecommendedActions[0].ActionType.Should().Be("Emergency");
        result.RecommendedActions[0].Urgency.Should().Be("Immediate");
        result.RecommendedActions[0].ExpectedBenefit.Should().Be(0.9m);
        result.Confidence.Should().BeGreaterOrEqualTo(0.85);
    }

    [Fact]
    public async Task GenerateStrategyAsync_中等风险生成预防性策略()
    {
        var awareness = new SituationAwareness
        {
            EntityId = "device-002",
            OverallStatus = "Warning",
            RiskLevel = 0.55
        };

        var result = await _sut.GenerateStrategyAsync(awareness);

        result.Priority.Should().Be("High");
        result.RecommendedActions.Should().HaveCount(1);
        result.RecommendedActions[0].ActionType.Should().Be("Preventive");
        result.RecommendedActions[0].Urgency.Should().Be("Soon");
    }

    [Fact]
    public async Task GenerateStrategyAsync_低风险生成监控策略()
    {
        var awareness = new SituationAwareness
        {
            EntityId = "device-003",
            OverallStatus = "Normal",
            RiskLevel = 0.2
        };

        var result = await _sut.GenerateStrategyAsync(awareness);

        result.Priority.Should().Be("Normal");
        result.RecommendedActions.Should().HaveCount(1);
        result.RecommendedActions[0].ActionType.Should().Be("Monitoring");
        result.RecommendedActions[0].Urgency.Should().Be("Scheduled");
        result.RecommendedActions[0].Risk.Should().Be(0.05);
    }

    [Fact]
    public async Task GenerateStrategyAsync_边界值0_7应为高风险()
    {
        var awareness = new SituationAwareness
        {
            EntityId = "device-004",
            RiskLevel = 0.7 // 边界：<=0.7 不是 Critical
        };

        var result = await _sut.GenerateStrategyAsync(awareness);

        // 0.7 不 > 0.7，所以进入 > 0.4 分支
        result.Priority.Should().Be("High");
    }

    [Fact]
    public async Task GenerateStrategyAsync_边界值0_4应为常规()
    {
        var awareness = new SituationAwareness
        {
            EntityId = "device-005",
            RiskLevel = 0.4 // 边界：<=0.4 不是 High
        };

        var result = await _sut.GenerateStrategyAsync(awareness);

        result.Priority.Should().Be("Normal");
    }

    // ========== EvaluateOptionsAsync ==========

    [Fact]
    public async Task EvaluateOptionsAsync_按评分排序并选中最优()
    {
        var options = new List<DecisionOption>
        {
            new() { OptionId = "A", Description = "方案A", ExpectedBenefit = 0.8m, Risk = 0.1 },
            new() { OptionId = "B", Description = "方案B", ExpectedBenefit = 0.5m, Risk = 0.3 },
            new() { OptionId = "C", Description = "方案C", ExpectedBenefit = 0.9m, Risk = 0.05 }
        };

        var result = await _sut.EvaluateOptionsAsync(options);

        result.Status.Should().Be("Success");
        result.EvaluatedOptions.Should().HaveCount(3);
        result.Confidence.Should().Be(0.8);

        // 验证评分公式：Score = ExpectedBenefit × 0.6 + (1 - Risk) × 0.4
        // C: 0.9*0.6+(1-0.05)*0.4 = 0.54+0.38 = 0.92
        // A: 0.8*0.6+(1-0.1)*0.4  = 0.48+0.36 = 0.84
        // B: 0.5*0.6+(1-0.3)*0.4  = 0.30+0.28 = 0.58
        result.EvaluatedOptions[0].OptionId.Should().Be("C");
        result.EvaluatedOptions[0].Score.Should().Be(0.92m);
        result.EvaluatedOptions[0].Selected.Should().BeTrue();

        result.EvaluatedOptions[1].OptionId.Should().Be("A");
        result.EvaluatedOptions[1].Score.Should().Be(0.84m);
        result.EvaluatedOptions[1].Selected.Should().BeFalse();

        result.EvaluatedOptions[2].OptionId.Should().Be("B");
        result.EvaluatedOptions[2].Score.Should().Be(0.58m);
        result.EvaluatedOptions[2].Selected.Should().BeFalse();
    }

    [Fact]
    public async Task EvaluateOptionsAsync_空选项列表返回成功()
    {
        var result = await _sut.EvaluateOptionsAsync(new List<DecisionOption>());

        result.Status.Should().Be("Success");
        result.EvaluatedOptions.Should().BeEmpty();
        result.Confidence.Should().Be(0.8);
    }

    [Fact]
    public async Task EvaluateOptionsAsync_单选项自动选中()
    {
        var options = new List<DecisionOption>
        {
            new() { OptionId = "only", Description = "唯一方案", ExpectedBenefit = 0.6m, Risk = 0.2 }
        };

        var result = await _sut.EvaluateOptionsAsync(options);

        result.EvaluatedOptions.Should().HaveCount(1);
        result.EvaluatedOptions[0].Selected.Should().BeTrue();
        result.EvaluatedOptions[0].ExpectedBenefit.Should().Be(0.6m);
        result.EvaluatedOptions[0].Risk.Should().Be(0.2);
    }

    // ========== OptimizeDecisionAsync ==========

    [Fact]
    public async Task OptimizeDecisionAsync_置信度增加0_05且不超过1()
    {
        var decision = new DecisionResult
        {
            DecisionId = "original",
            Confidence = 0.8,
            RecommendedActions = new List<RecommendedAction>()
        };

        var result = await _sut.OptimizeDecisionAsync(decision);

        result.Confidence.Should().BeApproximately(0.85, 0.0001);
        result.DecisionId.Should().NotBe("original"); // 新ID
    }

    [Fact]
    public async Task OptimizeDecisionAsync_置信度上限为1()
    {
        var decision = new DecisionResult
        {
            DecisionId = "high-conf",
            Confidence = 0.98,
            RecommendedActions = new List<RecommendedAction>()
        };

        var result = await _sut.OptimizeDecisionAsync(decision);

        result.Confidence.Should().Be(1.0);
    }

    [Fact]
    public async Task OptimizeDecisionAsync_有评估选项时重排推荐动作()
    {
        var bestOptionId = "match-option";
        var decision = new DecisionResult
        {
            Confidence = 0.7,
            EvaluatedOptions = new List<EvaluatedOption>
            {
                new() { OptionId = bestOptionId, Score = 0.9m, Selected = true }
            },
            RecommendedActions = new List<RecommendedAction>
            {
                new() { ActionId = "other", ExpectedBenefit = 0.5m },
                new() { ActionId = bestOptionId, ExpectedBenefit = 0.8m }
            }
        };

        var result = await _sut.OptimizeDecisionAsync(decision);

        // 匹配 bestOption 的 action 应排在第一位
        result.RecommendedActions[0].ActionId.Should().Be(bestOptionId);
    }

    // ========== DecideAsync ==========

    [Fact]
    public async Task DecideAsync_完整链路成功执行()
    {
        var awareness = new SituationAwareness
        {
            EntityId = "device-010",
            OverallStatus = "Warning",
            RiskLevel = 0.6
        };

        var result = await _sut.DecideAsync(awareness);

        result.Status.Should().Be("Success");
        result.RecommendedActions.Should().NotBeEmpty();
        result.Priority.Should().NotBeNullOrEmpty();
        result.Confidence.Should().BeGreaterThan(0);
        result.DecisionTimeMs.Should().BeGreaterOrEqualTo(0);
        result.EvaluatedOptions.Should().NotBeEmpty();
        result.Errors.Should().BeEmpty();
    }

    [Fact]
    public async Task DecideAsync_低风险场景有动作和评估选项()
    {
        var awareness = new SituationAwareness
        {
            EntityId = "device-011",
            RiskLevel = 0.1
        };

        var result = await _sut.DecideAsync(awareness);

        result.Status.Should().Be("Success");
        result.Priority.Should().Be("Normal");
        result.RecommendedActions.Should().HaveCount(1);
        result.EvaluatedOptions.Should().HaveCount(1);
        result.EvaluatedOptions[0].Selected.Should().BeTrue();
    }
}
