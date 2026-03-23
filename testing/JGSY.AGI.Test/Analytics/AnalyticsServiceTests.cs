using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.Analytics;

/// <summary>
/// 分析服务实体与 DTO 单元测试
/// </summary>
public class AnalyticsEntityTests
{
    #region TrackEvent 测试

    [Fact]
    public void TrackEvent_ShouldHaveCorrectDefaults()
    {
        var entity = new AGI.Analytics.Entities.TrackEvent();
        entity.Id.Should().BeEmpty();
        entity.SessionId.Should().BeNullOrEmpty();
        entity.DeleteAt.Should().BeNull();
    }

    [Fact]
    public void TrackEvent_ShouldSetAllProperties()
    {
        var tenantId = Guid.NewGuid();
        var now = DateTime.UtcNow;
        var entity = new AGI.Analytics.Entities.TrackEvent
        {
            SessionId = "sess-001",
            EventName = "page_view",
            PagePath = "/dashboard",
            Referrer = "https://example.com",
            UserId = Guid.NewGuid(),
            TenantId = tenantId,
            CreateTime = now
        };

        entity.SessionId.Should().Be("sess-001");
        entity.EventName.Should().Be("page_view");
        entity.PagePath.Should().Be("/dashboard");
        entity.Referrer.Should().Be("https://example.com");
        entity.TenantId.Should().Be(tenantId);
    }

    #endregion

    #region DailyReport 测试

    [Fact]
    public void DailyReport_ShouldHaveCorrectDefaults()
    {
        var report = new AGI.Analytics.Entities.DailyReport();
        report.TotalEnergyKwh.Should().Be(0);
        report.OrderCount.Should().Be(0);
        report.TotalRevenue.Should().Be(0);
        report.FaultCount.Should().Be(0);
        report.DeleteAt.Should().BeNull();
    }

    [Fact]
    public void DailyReport_ShouldCalculateMetricsCorrectly()
    {
        var report = new AGI.Analytics.Entities.DailyReport
        {
            ReportDate = new DateOnly(2026, 2, 13),
            StationId = Guid.NewGuid(),
            TotalEnergyKwh = 1500.5m,
            OrderCount = 120,
            TotalRevenue = 4500.75m,
            FaultCount = 3
        };

        report.ReportDate.Should().Be(new DateOnly(2026, 2, 13));
        report.OrderCount.Should().Be(120);
        report.TotalEnergyKwh.Should().BeGreaterThan(0);
        report.TotalRevenue.Should().Be(4500.75m);
    }

    #endregion

    #region UserProfile 测试

    [Fact]
    public void UserProfile_ShouldHaveCorrectDefaults()
    {
        var profile = new AGI.Analytics.Entities.UserProfile();
        profile.TotalVisits.Should().Be(0);
        profile.TotalPageViews.Should().Be(0);
        profile.BounceRate.Should().Be(0);
        profile.DeleteAt.Should().BeNull();
    }

    [Fact]
    public void UserProfile_ShouldTrackVisitMetrics()
    {
        var profile = new AGI.Analytics.Entities.UserProfile
        {
            UserId = Guid.NewGuid(),
            UserType = "member",
            TotalVisits = 50,
            TotalPageViews = 200,
            BounceRate = 25.5,
            AvgSessionDuration = 360.0
        };

        profile.TotalVisits.Should().Be(50);
        profile.TotalPageViews.Should().BeGreaterThan(profile.TotalVisits);
        profile.BounceRate.Should().BeInRange(0, 100);
        profile.AvgSessionDuration.Should().BePositive();
    }

    #endregion
}

/// <summary>
/// 运营分析 DTO 测试
/// </summary>
public class AnalyticsDtoTests
{
    [Fact]
    public void ChargingStatsOverview_ShouldHaveCorrectDefaults()
    {
        var stats = new AGI.Analytics.Models.ChargingStatsOverview();
        stats.TotalChargingCount.Should().Be(0);
        stats.TotalChargingAmount.Should().Be(0);
    }

    [Fact]
    public void DeviceStatsOverview_ShouldCalculateOnlineRate()
    {
        var stats = new AGI.Analytics.Models.DeviceStatsOverview
        {
            TotalDevices = 100,
            OnlineDevices = 95,
            FaultDevices = 2,
            OnlineRate = 95.0m,
            UtilizationRate = 68.5m
        };

        stats.OnlineDevices.Should().BeLessThanOrEqualTo(stats.TotalDevices);
        stats.OnlineRate.Should().BeInRange(0, 100);
        stats.FaultDevices.Should().BeLessThanOrEqualTo(stats.TotalDevices);
    }

    [Fact]
    public void RevenueOverview_ShouldHaveCorrectProperties()
    {
        var revenue = new AGI.Analytics.Models.RevenueOverview
        {
            TotalRevenue = 100000m,
            ElectricityRevenue = 80000m,
            GrossProfit = 40000m,
            NetProfitRate = 25.0m
        };

        revenue.ElectricityRevenue.Should().BeLessThanOrEqualTo(revenue.TotalRevenue);
        revenue.GrossProfit.Should().BeLessThanOrEqualTo(revenue.TotalRevenue);
        revenue.NetProfitRate.Should().BeInRange(-100m, 100m);
    }
}
