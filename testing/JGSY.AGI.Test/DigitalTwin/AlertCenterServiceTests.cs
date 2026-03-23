using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;
using JGSY.AGI.Common.Core.Interfaces;
using JGSY.AGI.DigitalTwin.Data.Repositories;
using JGSY.AGI.DigitalTwin.Models;
using JGSY.AGI.DigitalTwin.Services;

namespace JGSY.AGI.Test.DigitalTwin;

/// <summary>
/// 告警中心服务单元测试（告警管理 + 规则管理 + 统计）
/// </summary>
public class AlertCenterServiceTests
{
    private readonly Mock<IAlertRepository> _alertRepo;
    private readonly Mock<IAlertRuleRepository> _alertRuleRepo;
    private readonly Mock<ITenantContext> _tenantContext;
    private readonly AlertCenterService _service;

    private static readonly Guid TenantId = Guid.NewGuid();

    public AlertCenterServiceTests()
    {
        _alertRepo = new Mock<IAlertRepository>();
        _alertRuleRepo = new Mock<IAlertRuleRepository>();
        _tenantContext = new Mock<ITenantContext>();
        _tenantContext.Setup(t => t.TenantId).Returns(TenantId);

        _service = new AlertCenterService(
            _alertRepo.Object,
            _alertRuleRepo.Object,
            _tenantContext.Object,
            NullLogger<AlertCenterService>.Instance);
    }

    #region GetAlertsPagedAsync 告警分页

    [Fact]
    public async Task GetAlertsPaged_ReturnsPagedResult()
    {
        var alerts = new List<MaintenanceAlert>
        {
            new() { AlertId = Guid.NewGuid(), DeviceId = "DEV-001", Severity = AlertSeverity.Warning, Status = AlertStatus.Active },
            new() { AlertId = Guid.NewGuid(), DeviceId = "DEV-002", Severity = AlertSeverity.Critical, Status = AlertStatus.Active }
        };
        _alertRepo.Setup(r => r.GetPagedAsync(TenantId, 1, 10, null, null, null))
            .ReturnsAsync(alerts);
        _alertRepo.Setup(r => r.GetCountAsync(TenantId, null, null, null))
            .ReturnsAsync(2);

        var result = await _service.GetAlertsPagedAsync(1, 10);
        result.Items.Should().HaveCount(2);
        result.TotalCount.Should().Be(2);
        result.Page.Should().Be(1);
        result.PageSize.Should().Be(10);
    }

    [Fact]
    public async Task GetAlertsPaged_WithSeverityFilter_PassesToRepo()
    {
        _alertRepo.Setup(r => r.GetPagedAsync(TenantId, 1, 20, "Critical", null, null))
            .ReturnsAsync(new List<MaintenanceAlert>());
        _alertRepo.Setup(r => r.GetCountAsync(TenantId, "Critical", null, null))
            .ReturnsAsync(0);

        var result = await _service.GetAlertsPagedAsync(1, 20, severity: "Critical");
        result.Items.Should().BeEmpty();
        _alertRepo.Verify(r => r.GetPagedAsync(TenantId, 1, 20, "Critical", null, null), Times.Once);
    }

    [Fact]
    public async Task GetAlertsPaged_WithStatusFilter_ParsesEnum()
    {
        _alertRepo.Setup(r => r.GetPagedAsync(TenantId, 1, 10, null, null, (int)AlertStatus.Resolved))
            .ReturnsAsync(new List<MaintenanceAlert>());
        _alertRepo.Setup(r => r.GetCountAsync(TenantId, null, null, (int)AlertStatus.Resolved))
            .ReturnsAsync(0);

        await _service.GetAlertsPagedAsync(1, 10, status: "Resolved");
        _alertRepo.Verify(r => r.GetPagedAsync(TenantId, 1, 10, null, null, (int)AlertStatus.Resolved), Times.Once);
    }

    #endregion

    #region GetAlertByIdAsync

    [Fact]
    public async Task GetAlertById_Found_ReturnsAlert()
    {
        var alertId = Guid.NewGuid();
        var alert = new MaintenanceAlert { AlertId = alertId, DeviceId = "DEV-001" };
        _alertRepo.Setup(r => r.GetByIdAsync(alertId)).ReturnsAsync(alert);

        var result = await _service.GetAlertByIdAsync(alertId);
        result.Should().NotBeNull();
        result!.AlertId.Should().Be(alertId);
    }

    [Fact]
    public async Task GetAlertById_NotFound_ReturnsNull()
    {
        _alertRepo.Setup(r => r.GetByIdAsync(It.IsAny<Guid>())).ReturnsAsync((MaintenanceAlert?)null);

        var result = await _service.GetAlertByIdAsync(Guid.NewGuid());
        result.Should().BeNull();
    }

    #endregion

    #region AcknowledgeAlertAsync / ResolveAlertAsync

    [Fact]
    public async Task AcknowledgeAlert_DelegatesToRepo()
    {
        var alertId = Guid.NewGuid();
        await _service.AcknowledgeAlertAsync(alertId, "admin");
        _alertRepo.Verify(r => r.AcknowledgeAsync(alertId, "admin"), Times.Once);
    }

    [Fact]
    public async Task ResolveAlert_DelegatesToRepo()
    {
        var alertId = Guid.NewGuid();
        await _service.ResolveAlertAsync(alertId);
        _alertRepo.Verify(r => r.ResolveAsync(alertId), Times.Once);
    }

    #endregion

    #region 告警规则 CRUD

    [Fact]
    public async Task GetRulesPaged_ReturnsPagedResult()
    {
        var rules = new List<AlertRule>
        {
            new() { Id = Guid.NewGuid(), Name = "温度过高", IsEnabled = true }
        };
        _alertRuleRepo.Setup(r => r.GetListAsync(null, null, 1, 10)).ReturnsAsync(rules);
        _alertRuleRepo.Setup(r => r.GetCountAsync(null, null)).ReturnsAsync(1);

        var result = await _service.GetRulesPagedAsync(1, 10);
        result.Items.Should().HaveCount(1);
        result.TotalCount.Should().Be(1);
    }

    [Fact]
    public async Task CreateRule_ReturnsNewId()
    {
        var newId = Guid.NewGuid();
        _alertRuleRepo.Setup(r => r.InsertAsync(It.IsAny<AlertRule>())).ReturnsAsync(newId);

        var rule = new AlertRule { Name = "新规则" };
        var result = await _service.CreateRuleAsync(rule);
        result.Should().Be(newId);
    }

    [Fact]
    public async Task UpdateRule_DelegatesToRepo()
    {
        var rule = new AlertRule { Id = Guid.NewGuid(), Name = "更新后" };
        await _service.UpdateRuleAsync(rule);
        _alertRuleRepo.Verify(r => r.UpdateAsync(rule), Times.Once);
    }

    [Fact]
    public async Task DeleteRule_CallsSoftDelete()
    {
        var ruleId = Guid.NewGuid();
        await _service.DeleteRuleAsync(ruleId);
        _alertRuleRepo.Verify(r => r.SoftDeleteAsync(ruleId), Times.Once);
    }

    [Fact]
    public async Task ToggleRule_DelegatesToRepo()
    {
        var ruleId = Guid.NewGuid();
        await _service.ToggleRuleAsync(ruleId, false);
        _alertRuleRepo.Verify(r => r.ToggleEnabledAsync(ruleId, false), Times.Once);
    }

    #endregion

    #region GetStatisticsAsync 统计

    [Fact]
    public async Task GetStatistics_CalculatesCorrectly()
    {
        var alerts = new List<MaintenanceAlert>
        {
            new() { Severity = AlertSeverity.Info, Status = AlertStatus.Active, CreateTime = DateTime.UtcNow },
            new() { Severity = AlertSeverity.Warning, Status = AlertStatus.Active, CreateTime = DateTime.UtcNow },
            new() { Severity = AlertSeverity.Critical, Status = AlertStatus.Acknowledged, CreateTime = DateTime.UtcNow.AddDays(-1) },
            new() { Severity = AlertSeverity.Emergency, Status = AlertStatus.Resolved, CreateTime = DateTime.UtcNow },
            new() { Severity = AlertSeverity.Warning, Status = AlertStatus.Active, CreateTime = DateTime.UtcNow }
        };
        _alertRepo.Setup(r => r.GetAllNonDeletedAsync(TenantId)).ReturnsAsync(alerts);

        var stats = await _service.GetStatisticsAsync();
        stats.Total.Should().Be(5);
        stats.InfoCount.Should().Be(1);
        stats.WarningCount.Should().Be(2);
        stats.CriticalCount.Should().Be(1);
        stats.EmergencyCount.Should().Be(1);
        stats.UnacknowledgedCount.Should().Be(3); // Active 状态的有3个
        stats.TodayCount.Should().Be(4);     // 除了 AddDays(-1) 那个，其余4个是今天
    }

    [Fact]
    public async Task GetStatistics_EmptyAlerts_ReturnsZeros()
    {
        _alertRepo.Setup(r => r.GetAllNonDeletedAsync(TenantId))
            .ReturnsAsync(new List<MaintenanceAlert>());

        var stats = await _service.GetStatisticsAsync();
        stats.Total.Should().Be(0);
        stats.InfoCount.Should().Be(0);
        stats.UnacknowledgedCount.Should().Be(0);
    }

    #endregion
}
