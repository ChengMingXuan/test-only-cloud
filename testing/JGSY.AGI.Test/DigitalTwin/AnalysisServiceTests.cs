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
/// 孪生分析服务单元测试（报告 CRUD + 设备效率计算）
/// </summary>
public class AnalysisServiceTests
{
    private readonly Mock<IAnalysisReportRepository> _reportRepo;
    private readonly Mock<ITelemetryRepository> _telemetryRepo;
    private readonly Mock<ITenantContext> _tenantContext;
    private readonly AnalysisService _service;

    private static readonly Guid TenantId = Guid.NewGuid();

    public AnalysisServiceTests()
    {
        _reportRepo = new Mock<IAnalysisReportRepository>();
        _telemetryRepo = new Mock<ITelemetryRepository>();
        _tenantContext = new Mock<ITenantContext>();
        _tenantContext.Setup(t => t.TenantId).Returns(TenantId);

        _service = new AnalysisService(
            _reportRepo.Object,
            _telemetryRepo.Object,
            _tenantContext.Object,
            new AnalysisTaskChannel(),
            NullLogger<AnalysisService>.Instance);
    }

    #region GetReportsPagedAsync

    [Fact]
    public async Task GetReportsPaged_ReturnsCorrectPaging()
    {
        var reports = new List<AnalysisReport>
        {
            new() { Id = Guid.NewGuid(), Name = "能耗报告" },
            new() { Id = Guid.NewGuid(), Name = "效率报告" }
        };
        _reportRepo.Setup(r => r.GetListAsync(null, null, 1, 10)).ReturnsAsync(reports);
        _reportRepo.Setup(r => r.GetCountAsync(null, null)).ReturnsAsync(2);

        var result = await _service.GetReportsPagedAsync(1, 10);
        result.Items.Should().HaveCount(2);
        result.TotalCount.Should().Be(2);
        result.Page.Should().Be(1);
        result.PageSize.Should().Be(10);
    }

    [Fact]
    public async Task GetReportsPaged_WithFilters_PassesCorrectly()
    {
        _reportRepo.Setup(r => r.GetListAsync("energy", "S1", 2, 5)).ReturnsAsync(new List<AnalysisReport>());
        _reportRepo.Setup(r => r.GetCountAsync("energy", "S1")).ReturnsAsync(0);

        var result = await _service.GetReportsPagedAsync(2, 5, "energy", "S1");
        _reportRepo.Verify(r => r.GetListAsync("energy", "S1", 2, 5), Times.Once);
    }

    #endregion

    #region GetReportByIdAsync

    [Fact]
    public async Task GetReportById_Found_ReturnsReport()
    {
        var id = Guid.NewGuid();
        var report = new AnalysisReport { Id = id, Name = "测试报告" };
        _reportRepo.Setup(r => r.GetByIdAsync(id)).ReturnsAsync(report);

        var result = await _service.GetReportByIdAsync(id);
        result.Should().NotBeNull();
        result!.Id.Should().Be(id);
    }

    [Fact]
    public async Task GetReportById_NotFound_ReturnsNull()
    {
        _reportRepo.Setup(r => r.GetByIdAsync(It.IsAny<Guid>())).ReturnsAsync((AnalysisReport?)null);
        var result = await _service.GetReportByIdAsync(Guid.NewGuid());
        result.Should().BeNull();
    }

    #endregion

    #region CreateReportAsync

    [Fact]
    public async Task CreateReport_SetsCorrectFields()
    {
        var expectedId = Guid.NewGuid();
        _reportRepo.Setup(r => r.InsertAsync(It.IsAny<AnalysisReport>())).ReturnsAsync(expectedId);

        var request = new CreateReportRequest
        {
            ReportType = "energy",
            ReportName = "月度能耗分析",
            StationId = "S1",
            PeriodStart = new DateTime(2024, 1, 1),
            PeriodEnd = new DateTime(2024, 1, 31),
            Parameters = "{\"granularity\":\"daily\"}"
        };

        var result = await _service.CreateReportAsync(request);
        result.Should().Be(expectedId);

        _reportRepo.Verify(r => r.InsertAsync(It.Is<AnalysisReport>(rpt =>
            rpt.ReportType == "energy" &&
            rpt.Name == "月度能耗分析" &&
            rpt.TenantId == TenantId &&
            rpt.Status == (int)AnalysisReportStatus.Pending)), Times.Once);
    }

    #endregion

    #region DeleteReportAsync

    [Fact]
    public async Task DeleteReport_CallsSoftDelete()
    {
        var id = Guid.NewGuid();
        await _service.DeleteReportAsync(id);
        _reportRepo.Verify(r => r.SoftDeleteAsync(id), Times.Once);
    }

    #endregion

    #region GetDeviceEfficiencyAsync

    [Fact]
    public async Task GetDeviceEfficiency_WithData_CalculatesAggregates()
    {
        var start = DateTime.UtcNow.AddDays(-1);
        var end = DateTime.UtcNow;

        var aggregated = new List<AggregatedMetrics>
        {
            new() { BucketTime = start, AvgPower = 50, TotalEnergy = 100, MaxPower = 80 },
            new() { BucketTime = start.AddHours(1), AvgPower = 60, TotalEnergy = 120, MaxPower = 90 },
            new() { BucketTime = start.AddHours(2), AvgPower = 40, TotalEnergy = 80, MaxPower = 70 }
        };
        _telemetryRepo.Setup(r => r.GetAggregatedAsync("D1", "hourly", start, end)).ReturnsAsync(aggregated);

        var healthHistory = new List<HealthScoreHistory>
        {
            new() { HealthScore = 85 },
            new() { HealthScore = 90 },
            new() { HealthScore = 80 }
        };
        _telemetryRepo.Setup(r => r.GetHealthScoreHistoryAsync("D1", It.IsAny<TimeSpan>())).ReturnsAsync(healthHistory);

        var result = await _service.GetDeviceEfficiencyAsync("D1", start, end);
        result.DeviceId.Should().Be("D1");
        result.DataPointCount.Should().Be(3);
        result.TotalEnergy.Should().Be(300);        // 100+120+80
        result.AvgUtilization.Should().Be(50);       // (50+60+40)/3
        result.AvgHealthScore.Should().Be(85);       // (85+90+80)/3
        result.HourlyMetrics.Should().HaveCount(3);
    }

    [Fact]
    public async Task GetDeviceEfficiency_NoData_ReturnsZeros()
    {
        var start = DateTime.UtcNow.AddDays(-1);
        var end = DateTime.UtcNow;

        _telemetryRepo.Setup(r => r.GetAggregatedAsync("D2", "hourly", start, end))
            .ReturnsAsync(new List<AggregatedMetrics>());
        _telemetryRepo.Setup(r => r.GetHealthScoreHistoryAsync("D2", It.IsAny<TimeSpan>()))
            .ReturnsAsync(new List<HealthScoreHistory>());

        var result = await _service.GetDeviceEfficiencyAsync("D2", start, end);
        result.DataPointCount.Should().Be(0);
        result.TotalEnergy.Should().Be(0);
        result.AvgUtilization.Should().Be(0);
        result.AvgHealthScore.Should().Be(0);
    }

    #endregion
}
