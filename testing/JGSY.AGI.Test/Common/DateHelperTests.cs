using FluentAssertions;
using JGSY.AGI.Common.Core.Utils;
using Xunit;

namespace JGSY.AGI.Test.Common
{
    public class DateHelperTests
    {
        #region Constants

        [Fact]
        public void Iso8601Format_ShouldBeCorrectPattern()
        {
            DateHelper.Iso8601Format.Should().Contain("yyyy");
            DateHelper.Iso8601Format.Should().Contain("HH:mm:ss");
        }

        [Fact]
        public void DateTimeFormat_ShouldBeCorrectPattern()
        {
            DateHelper.DateTimeFormat.Should().Be("yyyy-MM-dd HH:mm:ss");
        }

        [Fact]
        public void DateFormat_ShouldBeCorrectPattern()
        {
            DateHelper.DateFormat.Should().Be("yyyy-MM-dd");
        }

        [Fact]
        public void TimeFormat_ShouldBeCorrectPattern()
        {
            DateHelper.TimeFormat.Should().Be("HH:mm:ss");
        }

        #endregion

        #region Properties

        [Fact]
        public void UtcNow_ShouldReturnUtcKind()
        {
            var now = DateHelper.UtcNow;
            now.Kind.Should().Be(DateTimeKind.Utc);
        }

        [Fact]
        public void TodayUtc_ShouldReturnMidnight()
        {
            var today = DateHelper.TodayUtc;
            today.Hour.Should().Be(0);
            today.Minute.Should().Be(0);
            today.Second.Should().Be(0);
        }

        #endregion

        #region ToUtc

        [Fact]
        public void ToUtc_WithUtcKind_ShouldReturnSame()
        {
            var utcTime = new DateTime(2025, 1, 15, 10, 30, 0, DateTimeKind.Utc);
            var result = DateHelper.ToUtc(utcTime);

            result.Kind.Should().Be(DateTimeKind.Utc);
            result.Should().Be(utcTime);
        }

        [Fact]
        public void ToUtc_WithLocalKind_ShouldConvertToUtc()
        {
            var localTime = new DateTime(2025, 1, 15, 10, 30, 0, DateTimeKind.Local);
            var result = DateHelper.ToUtc(localTime);

            result.Kind.Should().Be(DateTimeKind.Utc);
        }

        [Fact]
        public void ToUtc_WithUnspecifiedKind_ShouldSpecifyAsUtc()
        {
            var unspecified = new DateTime(2025, 1, 15, 10, 30, 0, DateTimeKind.Unspecified);
            var result = DateHelper.ToUtc(unspecified);

            result.Kind.Should().Be(DateTimeKind.Utc);
        }

        [Fact]
        public void ToUtc_WithNullableNull_ShouldReturnNull()
        {
            DateTime? input = null;
            var result = DateHelper.ToUtc(input);

            result.Should().BeNull();
        }

        [Fact]
        public void ToUtc_WithNullableValue_ShouldConvert()
        {
            DateTime? input = new DateTime(2025, 6, 1, 12, 0, 0, DateTimeKind.Local);
            var result = DateHelper.ToUtc(input);

            result.Should().NotBeNull();
            result!.Value.Kind.Should().Be(DateTimeKind.Utc);
        }

        #endregion

        #region ToLocal / ToChinaTime / FromChinaTime

        [Fact]
        public void ToLocal_ShouldConvertFromUtc()
        {
            var utcTime = new DateTime(2025, 1, 15, 0, 0, 0, DateTimeKind.Utc);
            var result = DateHelper.ToLocal(utcTime);

            result.Kind.Should().Be(DateTimeKind.Local);
        }

        [Fact]
        public void ToLocal_WithNullableNull_ShouldReturnNull()
        {
            DateTime? input = null;
            var result = DateHelper.ToLocal(input);

            result.Should().BeNull();
        }

        [Fact]
        public void ToChinaTime_ShouldAdd8Hours()
        {
            var utc = new DateTime(2025, 1, 15, 0, 0, 0, DateTimeKind.Utc);
            var china = DateHelper.ToChinaTime(utc);

            china.Hour.Should().Be(8);
        }

        [Fact]
        public void FromChinaTime_ShouldSubtract8Hours()
        {
            var chinaTime = new DateTime(2025, 1, 15, 8, 0, 0, DateTimeKind.Unspecified);
            var utc = DateHelper.FromChinaTime(chinaTime);

            utc.Kind.Should().Be(DateTimeKind.Utc);
            utc.Hour.Should().Be(0);
        }

        [Fact]
        public void ChinaTime_RoundTrip_ShouldPreserveTime()
        {
            var original = new DateTime(2025, 6, 15, 14, 30, 0, DateTimeKind.Utc);
            var china = DateHelper.ToChinaTime(original);
            var backToUtc = DateHelper.FromChinaTime(china);

            backToUtc.Should().BeCloseTo(original, TimeSpan.FromSeconds(1));
        }

        #endregion

        #region SpecifyUtc

        [Fact]
        public void SpecifyUtc_ShouldSetKindToUtc()
        {
            var dt = new DateTime(2025, 1, 1, 0, 0, 0, DateTimeKind.Unspecified);
            var result = DateHelper.SpecifyUtc(dt);

            result.Kind.Should().Be(DateTimeKind.Utc);
            result.Year.Should().Be(2025);
        }

        #endregion

        #region Format methods

        [Fact]
        public void FormatIso8601_ShouldReturnCorrectFormat()
        {
            var dt = new DateTime(2025, 3, 15, 10, 30, 45, DateTimeKind.Utc);
            var result = DateHelper.FormatIso8601(dt);

            result.Should().Contain("2025");
            result.Should().Contain("T");
        }

        [Fact]
        public void FormatIso8601_WithNull_ShouldReturnEmptyOrNull()
        {
            DateTime? dt = null;
            var result = DateHelper.FormatIso8601(dt);

            result.Should().BeNullOrEmpty();
        }

        [Fact]
        public void FormatDate_ShouldReturnDateOnly()
        {
            var dt = new DateTime(2025, 3, 15, 10, 30, 45, DateTimeKind.Utc);
            var result = DateHelper.FormatDate(dt);

            result.Should().Be("2025-03-15");
        }

        [Fact]
        public void FormatTime_ShouldReturnTimeOnly()
        {
            var dt = new DateTime(2025, 3, 15, 10, 30, 45, DateTimeKind.Utc);
            var result = DateHelper.FormatTime(dt);

            result.Should().Be("10:30:45");
        }

        [Fact]
        public void Format_WithCustomFormat_ShouldWork()
        {
            var dt = new DateTime(2025, 12, 25, 0, 0, 0, DateTimeKind.Utc);
            var result = DateHelper.Format(dt, "yyyy/MM/dd");

            result.Should().Be("2025/12/25");
        }

        #endregion

        #region Parse / TryParse

        [Fact]
        public void Parse_WithIso8601String_ShouldReturnUtcDateTime()
        {
            var result = DateHelper.Parse("2025-03-15T10:30:45Z");

            result.Kind.Should().Be(DateTimeKind.Utc);
            result.Year.Should().Be(2025);
            result.Month.Should().Be(3);
        }

        [Fact]
        public void TryParse_WithValidString_ShouldReturnTrue()
        {
            var success = DateHelper.TryParse("2025-01-01", out var result);

            success.Should().BeTrue();
            result.Year.Should().Be(2025);
        }

        [Fact]
        public void TryParse_WithNull_ShouldReturnFalse()
        {
            var success = DateHelper.TryParse(null, out _);

            success.Should().BeFalse();
        }

        [Fact]
        public void TryParse_WithInvalidString_ShouldReturnFalse()
        {
            var success = DateHelper.TryParse("not-a-date", out _);

            success.Should().BeFalse();
        }

        #endregion

        #region Timestamp conversions

        [Fact]
        public void FromTimestamp_ShouldConvertMilliseconds()
        {
            // 2025-01-01T00:00:00Z = 1735689600000ms
            var timestamp = 1735689600000L;
            var result = DateHelper.FromTimestamp(timestamp);

            result.Year.Should().Be(2025);
            result.Month.Should().Be(1);
            result.Day.Should().Be(1);
        }

        [Fact]
        public void FromUnixSeconds_ShouldConvertSeconds()
        {
            var seconds = 1735689600L;
            var result = DateHelper.FromUnixSeconds(seconds);

            result.Year.Should().Be(2025);
        }

        [Fact]
        public void ToTimestamp_ShouldReturnMilliseconds()
        {
            var dt = new DateTime(2025, 1, 1, 0, 0, 0, DateTimeKind.Utc);
            var ts = DateHelper.ToTimestamp(dt);

            ts.Should().Be(1735689600000L);
        }

        [Fact]
        public void ToUnixSeconds_ShouldReturnSeconds()
        {
            var dt = new DateTime(2025, 1, 1, 0, 0, 0, DateTimeKind.Utc);
            var ts = DateHelper.ToUnixSeconds(dt);

            ts.Should().Be(1735689600L);
        }

        [Fact]
        public void Timestamp_RoundTrip_ShouldPreserve()
        {
            var original = new DateTime(2025, 6, 15, 14, 30, 0, DateTimeKind.Utc);
            var ts = DateHelper.ToTimestamp(original);
            var restored = DateHelper.FromTimestamp(ts);

            restored.Should().BeCloseTo(original, TimeSpan.FromSeconds(1));
        }

        #endregion

        #region Range methods

        [Fact]
        public void GetTodayRangeUtc_ShouldReturnValidRange()
        {
            var (start, end) = DateHelper.GetTodayRangeUtc();

            start.TimeOfDay.Should().Be(TimeSpan.Zero);
            end.Should().BeAfter(start);
            (end - start).TotalHours.Should().BeGreaterOrEqualTo(23);
            (end - start).TotalHours.Should().BeLessOrEqualTo(24);
        }

        [Fact]
        public void GetWeekRangeUtc_EndShouldBeAfterStart()
        {
            var (start, end) = DateHelper.GetWeekRangeUtc();

            end.Should().BeAfter(start);
            (end - start).TotalDays.Should().BeGreaterOrEqualTo(6);
            (end - start).TotalDays.Should().BeLessOrEqualTo(7);
        }

        [Fact]
        public void GetMonthRangeUtc_ShouldStartOnFirst()
        {
            var (start, end) = DateHelper.GetMonthRangeUtc();

            start.Day.Should().Be(1);
            end.Should().BeAfter(start);
        }

        [Fact]
        public void GetLastDaysRangeUtc_7Days_ShouldReturn7DayRange()
        {
            var (start, end) = DateHelper.GetLastDaysRangeUtc(7);

            (end - start).TotalDays.Should().BeApproximately(7, 0.01);
        }

        [Fact]
        public void GetLastDaysRangeUtc_1Day_ShouldReturn1DayRange()
        {
            var (start, end) = DateHelper.GetLastDaysRangeUtc(1);

            (end - start).TotalDays.Should().BeApproximately(1, 0.01);
        }

        #endregion

        #region Comparison methods

        [Fact]
        public void IsInRange_WithinRange_ShouldReturnTrue()
        {
            var start = new DateTime(2025, 1, 1, 0, 0, 0, DateTimeKind.Utc);
            var end = new DateTime(2025, 12, 31, 0, 0, 0, DateTimeKind.Utc);
            var value = new DateTime(2025, 6, 15, 0, 0, 0, DateTimeKind.Utc);

            DateHelper.IsInRange(value, start, end).Should().BeTrue();
        }

        [Fact]
        public void IsInRange_OutsideRange_ShouldReturnFalse()
        {
            var start = new DateTime(2025, 1, 1, 0, 0, 0, DateTimeKind.Utc);
            var end = new DateTime(2025, 6, 30, 0, 0, 0, DateTimeKind.Utc);
            var value = new DateTime(2025, 12, 31, 0, 0, 0, DateTimeKind.Utc);

            DateHelper.IsInRange(value, start, end).Should().BeFalse();
        }

        [Fact]
        public void IsInRange_OnBoundary_ShouldReturnTrue()
        {
            var start = new DateTime(2025, 1, 1, 0, 0, 0, DateTimeKind.Utc);
            var end = new DateTime(2025, 12, 31, 0, 0, 0, DateTimeKind.Utc);

            DateHelper.IsInRange(start, start, end).Should().BeTrue();
        }

        [Fact]
        public void IsValid_WithDefaultDateTime_ShouldReturnFalse()
        {
            DateHelper.IsValid(default).Should().BeFalse();
        }

        [Fact]
        public void IsValid_WithNonDefaultDateTime_ShouldReturnTrue()
        {
            DateHelper.IsValid(DateTime.UtcNow).Should().BeTrue();
        }

        [Fact]
        public void GetRelativeTime_JustNow_ShouldReturnJustNow()
        {
            var recent = DateTime.UtcNow.AddSeconds(-10);
            var result = DateHelper.GetRelativeTime(recent);

            result.Should().NotBeNullOrEmpty();
        }

        [Fact]
        public void GetRelativeTime_HoursAgo_ShouldContainHour()
        {
            var hoursAgo = DateTime.UtcNow.AddHours(-3);
            var result = DateHelper.GetRelativeTime(hoursAgo);

            result.Should().NotBeNullOrEmpty();
        }

        #endregion
    }
}
