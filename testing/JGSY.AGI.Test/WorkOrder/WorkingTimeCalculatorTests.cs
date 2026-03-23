using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;
using JGSY.AGI.WorkOrder.Service;

namespace JGSY.AGI.Test.WorkOrder;

/// <summary>
/// 工作时间计算服务单元测试
/// </summary>
public class WorkingTimeCalculatorTests
{
    private readonly Mock<IHolidayService> _holidayService;
    private readonly WorkingTimeCalculator _calculator;

    public WorkingTimeCalculatorTests()
    {
        _holidayService = new Mock<IHolidayService>();
        // 默认：非节假日
        _holidayService.Setup(h => h.IsHolidayAsync(It.IsAny<DateTime>()))
            .ReturnsAsync(false);

        _calculator = new WorkingTimeCalculator(
            NullLogger<WorkingTimeCalculator>.Instance,
            _holidayService.Object);
    }

    #region IsWorkingTime 工作时间判断

    [Theory]
    [InlineData(2025, 1, 6, 9, 0)] // 周一 9:00
    [InlineData(2025, 1, 6, 12, 0)] // 周一 12:00
    [InlineData(2025, 1, 6, 18, 0)] // 周一 18:00
    [InlineData(2025, 1, 7, 10, 30)] // 周二 10:30
    [InlineData(2025, 1, 10, 15, 0)] // 周五 15:00
    public void IsWorkingTime_WorkdayWithinHours_ReturnsTrue(int y, int m, int d, int h, int min)
    {
        _calculator.IsWorkingTime(new DateTime(y, m, d, h, min, 0)).Should().BeTrue();
    }

    [Theory]
    [InlineData(2025, 1, 4, 10, 0)] // 周六
    [InlineData(2025, 1, 5, 10, 0)] // 周日
    [InlineData(2025, 1, 6, 8, 59)] // 周一 工作时间前
    [InlineData(2025, 1, 6, 18, 1)] // 周一 工作时间后
    [InlineData(2025, 1, 6, 0, 0)]  // 周一 午夜
    public void IsWorkingTime_NonWorkingTime_ReturnsFalse(int y, int m, int d, int h, int min)
    {
        _calculator.IsWorkingTime(new DateTime(y, m, d, h, min, 0)).Should().BeFalse();
    }

    #endregion

    #region IsWorkingDayAsync 工作日判断

    [Fact]
    public async Task IsWorkingDayAsync_WeekdayNotHoliday_ReturnsTrue()
    {
        // 2025-01-06 是周一
        var result = await _calculator.IsWorkingDayAsync(new DateTime(2025, 1, 6));
        result.Should().BeTrue();
    }

    [Fact]
    public async Task IsWorkingDayAsync_Weekend_ReturnsFalse()
    {
        // 2025-01-04 是周六
        var result = await _calculator.IsWorkingDayAsync(new DateTime(2025, 1, 4));
        result.Should().BeFalse();
    }

    [Fact]
    public async Task IsWorkingDayAsync_WeekdayButHoliday_ReturnsFalse()
    {
        // 设置 2025-01-06 为节假日
        _holidayService.Setup(h => h.IsHolidayAsync(new DateTime(2025, 1, 6)))
            .ReturnsAsync(true);

        var result = await _calculator.IsWorkingDayAsync(new DateTime(2025, 1, 6));
        result.Should().BeFalse();
    }

    #endregion

    #region CalculateWorkingMinutesAsync 工作时长计算

    [Fact]
    public async Task CalculateWorkingMinutesAsync_StartAfterEnd_ReturnsZero()
    {
        var result = await _calculator.CalculateWorkingMinutesAsync(
            new DateTime(2025, 1, 7, 10, 0, 0),
            new DateTime(2025, 1, 6, 10, 0, 0));
        result.Should().Be(0);
    }

    [Fact]
    public async Task CalculateWorkingMinutesAsync_SameTime_ReturnsZero()
    {
        var t = new DateTime(2025, 1, 6, 10, 0, 0);
        var result = await _calculator.CalculateWorkingMinutesAsync(t, t);
        result.Should().Be(0);
    }

    [Fact]
    public async Task CalculateWorkingMinutesAsync_SameDayWorkingHours_ReturnsCorrectMinutes()
    {
        // 周一 10:00 - 12:00 = 120分钟
        var result = await _calculator.CalculateWorkingMinutesAsync(
            new DateTime(2025, 1, 6, 10, 0, 0),
            new DateTime(2025, 1, 6, 12, 0, 0));
        result.Should().Be(120);
    }

    [Fact]
    public async Task CalculateWorkingMinutesAsync_SameDayStartBeforeWorkHours_ClampsToStart()
    {
        // 周一 7:00 - 12:00 → 实际计算 9:00 - 12:00 = 180分钟
        var result = await _calculator.CalculateWorkingMinutesAsync(
            new DateTime(2025, 1, 6, 7, 0, 0),
            new DateTime(2025, 1, 6, 12, 0, 0));
        result.Should().Be(180);
    }

    [Fact]
    public async Task CalculateWorkingMinutesAsync_SameDayEndAfterWorkHours_ClampsToEnd()
    {
        // 周一 10:00 - 22:00 → 实际计算 10:00 - 18:00 = 480分钟
        var result = await _calculator.CalculateWorkingMinutesAsync(
            new DateTime(2025, 1, 6, 10, 0, 0),
            new DateTime(2025, 1, 6, 22, 0, 0));
        result.Should().Be(480);
    }

    [Fact]
    public async Task CalculateWorkingMinutesAsync_FullWorkDay_Returns540Minutes()
    {
        // 周一 9:00 - 18:00 = 540分钟（9小时）
        var result = await _calculator.CalculateWorkingMinutesAsync(
            new DateTime(2025, 1, 6, 9, 0, 0),
            new DateTime(2025, 1, 6, 18, 0, 0));
        result.Should().Be(540);
    }

    [Fact]
    public async Task CalculateWorkingMinutesAsync_CrossWeekend_SkipsWeekendDays()
    {
        // 周五 10:00 到 周一 12:00
        // 周五：10:00 - 18:00 = 480分
        // 周六 + 周日 = 0
        // 周一：9:00 - 12:00 = 180分
        // 合计 = 660分
        var result = await _calculator.CalculateWorkingMinutesAsync(
            new DateTime(2025, 1, 3, 10, 0, 0),  // 周五
            new DateTime(2025, 1, 6, 12, 0, 0));  // 周一
        result.Should().Be(660);
    }

    [Fact]
    public async Task CalculateWorkingMinutesAsync_EntirelyOnWeekend_ReturnsZero()
    {
        // 周六到周日
        var result = await _calculator.CalculateWorkingMinutesAsync(
            new DateTime(2025, 1, 4, 10, 0, 0),
            new DateTime(2025, 1, 5, 17, 0, 0));
        result.Should().Be(0);
    }

    [Fact]
    public async Task CalculateWorkingMinutesAsync_HolidaySkipped()
    {
        // 设置周二为节假日
        _holidayService.Setup(h => h.IsHolidayAsync(new DateTime(2025, 1, 7)))
            .ReturnsAsync(true);

        // 周一 10:00 到 周三 12:00
        // 周一：10:00 - 18:00 = 480分
        // 周二：节假日 = 0
        // 周三：9:00 - 12:00 = 180分
        // 合计 = 660分
        var result = await _calculator.CalculateWorkingMinutesAsync(
            new DateTime(2025, 1, 6, 10, 0, 0),
            new DateTime(2025, 1, 8, 12, 0, 0));
        result.Should().Be(660);
    }

    [Fact]
    public async Task CalculateWorkingMinutesAsync_TwoFullWorkDays_Returns1080Minutes()
    {
        // 周一 9:00 到 周二 18:00 = 2 * 540 = 1080分钟
        var result = await _calculator.CalculateWorkingMinutesAsync(
            new DateTime(2025, 1, 6, 9, 0, 0),
            new DateTime(2025, 1, 7, 18, 0, 0));
        result.Should().Be(1080);
    }

    #endregion

    #region GetNextWorkingTime 获取下一个工作时间

    [Fact]
    public void GetNextWorkingTime_AlreadyWorkingTime_ReturnsSame()
    {
        // 周一 10:00 已经是工作时间
        var input = new DateTime(2025, 1, 6, 10, 0, 0);
        _calculator.GetNextWorkingTime(input).Should().Be(input);
    }

    [Fact]
    public void GetNextWorkingTime_BeforeWorkHours_ReturnsToday9AM()
    {
        // 周一 7:00 → 周一 9:00
        var result = _calculator.GetNextWorkingTime(new DateTime(2025, 1, 6, 7, 0, 0));
        result.Should().Be(new DateTime(2025, 1, 6, 9, 0, 0));
    }

    [Fact]
    public void GetNextWorkingTime_AfterWorkHours_ReturnsNextDay9AM()
    {
        // 周一 19:00 → 周二 9:00
        var result = _calculator.GetNextWorkingTime(new DateTime(2025, 1, 6, 19, 0, 0));
        result.Should().Be(new DateTime(2025, 1, 7, 9, 0, 0));
    }

    [Fact]
    public void GetNextWorkingTime_FridayEvening_SkipsWeekend()
    {
        // 周五 19:00 → 周六 9:00（因 IsWorkingTime 不查数据库中的节假日，只查星期几）
        // 但注意 IsWorkingTime 只检查星期几，不检查 IsHoliday（isHoliday是async方法）
        // GetNextWorkingTime 调用 IsWorkingTime（非async），周六返回false → 跳到周日 9:00 也false → 跳到周一 9:00 true
        var result = _calculator.GetNextWorkingTime(new DateTime(2025, 1, 3, 19, 0, 0));
        result.Should().Be(new DateTime(2025, 1, 6, 9, 0, 0));
    }

    [Fact]
    public void GetNextWorkingTime_Saturday_SkipsToMonday()
    {
        // 周六 10:00 → 周一 9:00
        var result = _calculator.GetNextWorkingTime(new DateTime(2025, 1, 4, 10, 0, 0));
        result.Should().Be(new DateTime(2025, 1, 6, 9, 0, 0));
    }

    #endregion
}
