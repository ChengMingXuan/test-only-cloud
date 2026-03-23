using Xunit;
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using JGSY.AGI.MicroGrid.Business;
using JGSY.AGI.MicroGrid.Interfaces;
using JGSY.AGI.MicroGrid.Entities;
using JGSY.AGI.MicroGrid.Models;
using JGSY.AGI.Common.Core.Interfaces;
using JGSY.AGI.Common.Core.ServiceClients;

namespace JGSY.AGI.Test.MicroGrid;

/// <summary>
/// 微电网保护规则服务单元测试
/// 覆盖: CRUD、启停、保护检测触发（频率/电压/过流/过充/过放/逆功率 6 种）、动作执行（告警/切岛/跳闸/限电）
/// </summary>
public class MgProtectionRuleServiceTests
{
    private readonly Mock<IMgProtectionRuleRepository> _ruleRepo = new();
    private readonly Mock<IMgAlertRecordRepository> _alertRepo = new();
    private readonly Mock<IMgModeService> _modeService = new();
    private readonly Mock<IServiceTransport> _transport = new();
    private readonly Mock<ITenantContext> _ctx = new();
    private readonly MgProtectionRuleService _service;

    private readonly Guid _tenantId = Guid.NewGuid();

    public MgProtectionRuleServiceTests()
    {
        _ctx.Setup(c => c.TenantId).Returns(_tenantId);
        _service = new MgProtectionRuleService(
            _ruleRepo.Object, _alertRepo.Object, _modeService.Object,
            _transport.Object, _ctx.Object, NullLogger<MgProtectionRuleService>.Instance);
    }

    #region 查询

    [Fact]
    public async Task GetByIdAsync_Found_ReturnsMappedDto()
    {
        // Arrange
        var id = Guid.NewGuid();
        var gridId = Guid.NewGuid();
        var entity = new MgProtectionRule
        {
            Id = id, GridId = gridId, RuleName = "频率保护规则",
            ProtectionType = 1, ThresholdValue = 49.5m,
            ComparisonOperator = 2, ActionType = 1, Priority = 1, IsActive = true
        };
        _ruleRepo.Setup(r => r.GetByIdAsync(id, _tenantId)).ReturnsAsync(entity);

        // Act
        var result = await _service.GetByIdAsync(id);

        // Assert
        result.Should().NotBeNull();
        result!.RuleName.Should().Be("频率保护规则");
        result.ProtectionType.Should().Be(1);
        result.ThresholdValue.Should().Be(49.5m);
        result.IsActive.Should().BeTrue();
    }

    [Fact]
    public async Task GetByIdAsync_NotFound_ReturnsNull()
    {
        // Arrange
        _ruleRepo.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), _tenantId)).ReturnsAsync((MgProtectionRule?)null);

        // Act
        var result = await _service.GetByIdAsync(Guid.NewGuid());

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task GetListAsync_ReturnsMappedTuple()
    {
        // Arrange
        var gridId = Guid.NewGuid();
        var rules = new List<MgProtectionRule>
        {
            new() { Id = Guid.NewGuid(), GridId = gridId, RuleName = "R1", ProtectionType = 1, ActionType = 1 },
            new() { Id = Guid.NewGuid(), GridId = gridId, RuleName = "R2", ProtectionType = 2, ActionType = 2 }
        };
        _ruleRepo.Setup(r => r.GetListAsync(_tenantId, gridId, It.IsAny<short?>(), It.IsAny<bool?>(), 1, 20)).ReturnsAsync(rules);
        _ruleRepo.Setup(r => r.GetCountAsync(_tenantId, gridId, It.IsAny<short?>(), It.IsAny<bool?>())).ReturnsAsync(10);

        // Act
        var (items, total) = await _service.GetListAsync(gridId, null, null, 1, 20);

        // Assert
        items.Should().HaveCount(2);
        total.Should().Be(10);
    }

    #endregion

    #region 创建

    [Fact]
    public async Task CreateAsync_ReturnsNewId()
    {
        // Arrange
        var request = new CreateProtectionRuleRequest
        {
            GridId = Guid.NewGuid(),
            RuleName = "过流保护",
            ProtectionType = 3,
            ThresholdValue = 100m,
            ComparisonOperator = 1, // 大于
            ActionType = 1, // 告警
            Priority = 1,
            IsActive = true,
            Description = "电流超过 100A 时告警"
        };

        // Act
        var result = await _service.CreateAsync(request);

        // Assert
        result.Should().NotBeEmpty();
        _ruleRepo.Verify(r => r.InsertAsync(It.Is<MgProtectionRule>(e =>
            e.RuleName == "过流保护" &&
            e.ProtectionType == 3 &&
            e.ThresholdValue == 100m &&
            e.TenantId == _tenantId)), Times.Once);
    }

    #endregion

    #region 更新

    [Fact]
    public async Task UpdateAsync_Found_UpdatesAndReturnsTrue()
    {
        // Arrange
        var id = Guid.NewGuid();
        var entity = new MgProtectionRule { Id = id, RuleName = "旧名", ProtectionType = 1 };
        _ruleRepo.Setup(r => r.GetByIdAsync(id, _tenantId)).ReturnsAsync(entity);
        _ruleRepo.Setup(r => r.UpdateAsync(It.IsAny<MgProtectionRule>())).ReturnsAsync(true);

        var request = new UpdateProtectionRuleRequest
        {
            RuleName = "新名", ProtectionType = 2, ThresholdValue = 220m,
            ComparisonOperator = 1, ActionType = 2, Priority = 2, IsActive = true, Description = "更新描述"
        };

        // Act
        var result = await _service.UpdateAsync(id, request);

        // Assert
        result.Should().BeTrue();
        entity.RuleName.Should().Be("新名");
        entity.ProtectionType.Should().Be(2);
        entity.ThresholdValue.Should().Be(220m);
    }

    [Fact]
    public async Task UpdateAsync_NotFound_ReturnsFalse()
    {
        // Arrange
        _ruleRepo.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), _tenantId)).ReturnsAsync((MgProtectionRule?)null);

        // Act
        var result = await _service.UpdateAsync(Guid.NewGuid(), new UpdateProtectionRuleRequest());

        // Assert
        result.Should().BeFalse();
    }

    #endregion

    #region 删除 + 启停

    [Fact]
    public async Task DeleteAsync_DelegatesToRepo()
    {
        // Arrange
        var id = Guid.NewGuid();
        _ruleRepo.Setup(r => r.DeleteAsync(id, _tenantId)).ReturnsAsync(true);

        // Act
        var result = await _service.DeleteAsync(id);

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public async Task ToggleActiveAsync_DelegatesToRepo()
    {
        // Arrange
        var id = Guid.NewGuid();
        _ruleRepo.Setup(r => r.ToggleActiveAsync(id, _tenantId, false)).ReturnsAsync(true);

        // Act
        var result = await _service.ToggleActiveAsync(id, false);

        // Assert
        result.Should().BeTrue();
        _ruleRepo.Verify(r => r.ToggleActiveAsync(id, _tenantId, false), Times.Once);
    }

    #endregion

    #region 保护检测 — CheckProtectionAsync

    [Fact]
    public async Task CheckProtectionAsync_FrequencyRule_GreaterThan_Triggers()
    {
        // Arrange — 频率保护: 频率 > 50.5Hz 时告警
        var gridId = Guid.NewGuid();
        var rule = new MgProtectionRule
        {
            Id = Guid.NewGuid(), GridId = gridId, ProtectionType = 1, // 频率
            ThresholdValue = 50.5m, ComparisonOperator = 1, // 大于
            ActionType = 1 // 告警
        };
        _ruleRepo.Setup(r => r.GetActiveRulesAsync(_tenantId, gridId)).ReturnsAsync(new[] { rule });

        var request = new MgProtectionCheckRequest { FrequencyHz = 51.0m }; // 超出阈值

        // Act
        var results = await _service.CheckProtectionAsync(gridId, request);

        // Assert
        results.Should().HaveCount(1);
        results[0].ActionExecuted.Should().BeTrue(); // 告警动作成功
        results[0].CurrentValue.Should().Be(51.0m);
        results[0].ThresholdValue.Should().Be(50.5m);
        results[0].Message.Should().Contain("频率");
        _alertRepo.Verify(r => r.InsertAsync(It.IsAny<MgAlertRecord>()), Times.Once);
    }

    [Fact]
    public async Task CheckProtectionAsync_VoltageRule_LessThan_Triggers()
    {
        // Arrange — 电压保护: 电压 < 190V 时切岛
        var gridId = Guid.NewGuid();
        var rule = new MgProtectionRule
        {
            Id = Guid.NewGuid(), GridId = gridId, ProtectionType = 2, // 电压
            ThresholdValue = 190m, ComparisonOperator = 2, // 小于
            ActionType = 2 // 切换孤岛
        };
        _ruleRepo.Setup(r => r.GetActiveRulesAsync(_tenantId, gridId)).ReturnsAsync(new[] { rule });
        _modeService.Setup(s => s.SwitchModeAsync(gridId, It.Is<SwitchModeRequest>(r => r.TargetMode == 3))).ReturnsAsync(true);

        var request = new MgProtectionCheckRequest { VoltageV = 180m }; // 低于阈值

        // Act
        var results = await _service.CheckProtectionAsync(gridId, request);

        // Assert
        results.Should().HaveCount(1);
        results[0].ActionExecuted.Should().BeTrue(); // 切岛执行成功
        results[0].Message.Should().Contain("电压");
        _modeService.Verify(s => s.SwitchModeAsync(gridId, It.IsAny<SwitchModeRequest>()), Times.Once);
    }

    [Fact]
    public async Task CheckProtectionAsync_OvercurrentRule_NotTriggered_NoResults()
    {
        // Arrange — 过流保护: 电流 > 100A, 但当前只有 80A
        var gridId = Guid.NewGuid();
        var rule = new MgProtectionRule
        {
            Id = Guid.NewGuid(), GridId = gridId, ProtectionType = 3,
            ThresholdValue = 100m, ComparisonOperator = 1, ActionType = 3
        };
        _ruleRepo.Setup(r => r.GetActiveRulesAsync(_tenantId, gridId)).ReturnsAsync(new[] { rule });

        var request = new MgProtectionCheckRequest { CurrentA = 80m }; // 未超出

        // Act
        var results = await _service.CheckProtectionAsync(gridId, request);

        // Assert
        results.Should().BeEmpty();
    }

    [Fact]
    public async Task CheckProtectionAsync_OverchargeSOC_GreaterThan_Triggers()
    {
        // Arrange — 过充保护: SOC > 95% 时跳闸
        var gridId = Guid.NewGuid();
        var rule = new MgProtectionRule
        {
            Id = Guid.NewGuid(), GridId = gridId, ProtectionType = 4, // 过充
            ThresholdValue = 95m, ComparisonOperator = 1, // SOC > 95
            ActionType = 3 // 跳闸 — 安全保护: 设备网关未就绪, 返回 false
        };
        _ruleRepo.Setup(r => r.GetActiveRulesAsync(_tenantId, gridId)).ReturnsAsync(new[] { rule });

        var request = new MgProtectionCheckRequest { SocPercent = 98m };

        // Act
        var results = await _service.CheckProtectionAsync(gridId, request);

        // Assert
        results.Should().HaveCount(1);
        results[0].ActionExecuted.Should().BeFalse(); // 跳闸设备网关未就绪 → false
        results[0].Message.Should().Contain("SOC(过充)");
    }

    [Fact]
    public async Task CheckProtectionAsync_OverDischargeSOC_LessThan_Triggers()
    {
        // Arrange — 过放保护: SOC < 10% 时告警
        var gridId = Guid.NewGuid();
        var rule = new MgProtectionRule
        {
            Id = Guid.NewGuid(), GridId = gridId, ProtectionType = 5, // 过放
            ThresholdValue = 10m, ComparisonOperator = 2, // SOC < 10
            ActionType = 1 // 告警
        };
        _ruleRepo.Setup(r => r.GetActiveRulesAsync(_tenantId, gridId)).ReturnsAsync(new[] { rule });

        var request = new MgProtectionCheckRequest { SocPercent = 5m };

        // Act
        var results = await _service.CheckProtectionAsync(gridId, request);

        // Assert
        results.Should().HaveCount(1);
        results[0].ActionExecuted.Should().BeTrue(); // 告警可执行
        results[0].Message.Should().Contain("SOC(过放)");
    }

    [Fact]
    public async Task CheckProtectionAsync_ReversePower_GreaterThan_Triggers_LimitAction()
    {
        // Arrange — 逆功率保护: 功率 > 50kW 时限电
        var gridId = Guid.NewGuid();
        var rule = new MgProtectionRule
        {
            Id = Guid.NewGuid(), GridId = gridId, ProtectionType = 6, // 逆功率
            ThresholdValue = 50m, ComparisonOperator = 1,
            ActionType = 4 // 限电 — 设备网关未就绪
        };
        _ruleRepo.Setup(r => r.GetActiveRulesAsync(_tenantId, gridId)).ReturnsAsync(new[] { rule });

        var request = new MgProtectionCheckRequest { PowerKw = 60m };

        // Act
        var results = await _service.CheckProtectionAsync(gridId, request);

        // Assert
        results.Should().HaveCount(1);
        results[0].ActionExecuted.Should().BeFalse(); // 限电设备网关未就绪
    }

    [Fact]
    public async Task CheckProtectionAsync_MultipleRules_OnlyTriggeredOnesReturned()
    {
        // Arrange — 2 条规则，只有 1 条触发
        var gridId = Guid.NewGuid();
        var rule1 = new MgProtectionRule
        {
            Id = Guid.NewGuid(), GridId = gridId, ProtectionType = 1,
            ThresholdValue = 50.5m, ComparisonOperator = 1, ActionType = 1
        };
        var rule2 = new MgProtectionRule
        {
            Id = Guid.NewGuid(), GridId = gridId, ProtectionType = 2,
            ThresholdValue = 190m, ComparisonOperator = 2, ActionType = 1
        };
        _ruleRepo.Setup(r => r.GetActiveRulesAsync(_tenantId, gridId)).ReturnsAsync(new[] { rule1, rule2 });

        var request = new MgProtectionCheckRequest { FrequencyHz = 50.8m, VoltageV = 220m }; // 频率触发，电压正常

        // Act
        var results = await _service.CheckProtectionAsync(gridId, request);

        // Assert
        results.Should().HaveCount(1);
        results[0].ProtectionType.Should().Be(1); // 只有频率规则触发
    }

    [Fact]
    public async Task CheckProtectionAsync_NoValueForRuleType_SkipsRule()
    {
        // Arrange — 规则是频率保护，但请求中没有频率值
        var gridId = Guid.NewGuid();
        var rule = new MgProtectionRule
        {
            Id = Guid.NewGuid(), GridId = gridId, ProtectionType = 1,
            ThresholdValue = 49.5m, ComparisonOperator = 2, ActionType = 1
        };
        _ruleRepo.Setup(r => r.GetActiveRulesAsync(_tenantId, gridId)).ReturnsAsync(new[] { rule });

        var request = new MgProtectionCheckRequest { VoltageV = 220m }; // 没有 FrequencyHz

        // Act
        var results = await _service.CheckProtectionAsync(gridId, request);

        // Assert
        results.Should().BeEmpty(); // 没有对应值 → 跳过
    }

    [Fact]
    public async Task CheckProtectionAsync_NoThreshold_DoesNotTrigger()
    {
        // Arrange — 阈值为 null
        var gridId = Guid.NewGuid();
        var rule = new MgProtectionRule
        {
            Id = Guid.NewGuid(), GridId = gridId, ProtectionType = 1,
            ThresholdValue = null, ComparisonOperator = 1, ActionType = 1
        };
        _ruleRepo.Setup(r => r.GetActiveRulesAsync(_tenantId, gridId)).ReturnsAsync(new[] { rule });

        var request = new MgProtectionCheckRequest { FrequencyHz = 55m };

        // Act
        var results = await _service.CheckProtectionAsync(gridId, request);

        // Assert
        results.Should().BeEmpty();
    }

    [Fact]
    public async Task CheckProtectionAsync_EqualOperator_Triggers()
    {
        // Arrange — 等于操作符
        var gridId = Guid.NewGuid();
        var rule = new MgProtectionRule
        {
            Id = Guid.NewGuid(), GridId = gridId, ProtectionType = 3,
            ThresholdValue = 50m, ComparisonOperator = 3, // 等于
            ActionType = 1
        };
        _ruleRepo.Setup(r => r.GetActiveRulesAsync(_tenantId, gridId)).ReturnsAsync(new[] { rule });

        var request = new MgProtectionCheckRequest { CurrentA = 50m }; // 恰好等于

        // Act
        var results = await _service.CheckProtectionAsync(gridId, request);

        // Assert
        results.Should().HaveCount(1);
    }

    #endregion
}
