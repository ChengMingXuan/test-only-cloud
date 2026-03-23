using FluentAssertions;
using JGSY.AGI.Common.Core.Utils;
using Xunit;

namespace JGSY.AGI.Test.Common
{
    public class ValidateHelperTests
    {
        #region IsEmail

        [Theory]
        [InlineData("test@example.com", true)]
        [InlineData("user.name@domain.co", true)]
        [InlineData("user-name@domain.com", true)]
        [InlineData("user_name@domain.com", true)]
        [InlineData("user@sub.domain.com", true)]
        [InlineData("user@domain.info", true)]
        [InlineData("invalid", false)]
        [InlineData("@domain.com", false)]
        [InlineData("user@", false)]
        [InlineData("user@.com", false)]
        [InlineData("", false)]
        [InlineData("user@domain", false)]
        public void IsEmail_ShouldValidateCorrectly(string email, bool expected)
        {
            ValidateHelper.IsEmail(email).Should().Be(expected);
        }

        #endregion

        #region IsPhone

        [Theory]
        [InlineData("13800138000", true)]
        [InlineData("15912345678", true)]
        [InlineData("18612345678", true)]
        [InlineData("19912345678", true)]
        [InlineData("17612345678", true)]
        [InlineData("14512345678", true)]
        [InlineData("12345678901", false)]  // doesn't start with 1[3-9]
        [InlineData("1380013800", false)]   // too short (10 digits)
        [InlineData("138001380001", false)] // too long (12 digits)
        [InlineData("23800138000", false)]  // doesn't start with 1
        [InlineData("10800138000", false)]  // second digit is 0
        [InlineData("1380013800a", false)]  // contains letter
        [InlineData("", false)]
        public void IsPhone_ShouldValidateCorrectly(string phone, bool expected)
        {
            ValidateHelper.IsPhone(phone).Should().Be(expected);
        }

        #endregion
    }

    public class RegexHelperTests
    {
        #region IsMatch

        [Fact]
        public void IsMatch_WithMatchingPattern_ShouldReturnTrue()
        {
            RegexHelper.IsMatch("hello123", @"\d+").Should().BeTrue();
        }

        [Fact]
        public void IsMatch_WithNonMatchingPattern_ShouldReturnFalse()
        {
            RegexHelper.IsMatch("hello", @"^\d+$").Should().BeFalse();
        }

        [Fact]
        public void IsMatch_EmailPattern_ShouldWork()
        {
            RegexHelper.IsMatch("test@example.com", @"^[\w-\.]+@[\w-]+\.[\w-]{2,4}$").Should().BeTrue();
        }

        #endregion

        #region Replace

        [Fact]
        public void Replace_ShouldReplaceMatchedPattern()
        {
            var result = RegexHelper.Replace("hello 123 world 456", @"\d+", "NUM");
            result.Should().Be("hello NUM world NUM");
        }

        [Fact]
        public void Replace_WithNoMatch_ShouldReturnOriginal()
        {
            var result = RegexHelper.Replace("hello world", @"\d+", "NUM");
            result.Should().Be("hello world");
        }

        [Fact]
        public void Replace_EmptyReplacement_ShouldRemoveMatches()
        {
            var result = RegexHelper.Replace("a1b2c3", @"\d", "");
            result.Should().Be("abc");
        }

        #endregion
    }

    public class RetryHelperTests
    {
        #region Successful on first attempt

        [Fact]
        public async Task RetryAsync_SuccessOnFirstAttempt_ShouldReturnImmediately()
        {
            var callCount = 0;
            var result = await RetryHelper.RetryAsync(async () =>
            {
                callCount++;
                return await Task.FromResult("success");
            }, maxAttempts: 3, delayMs: 10);

            result.Should().Be("success");
            callCount.Should().Be(1);
        }

        #endregion

        #region Retry on failure then success

        [Fact]
        public async Task RetryAsync_FailThenSucceed_ShouldRetry()
        {
            var callCount = 0;
            var result = await RetryHelper.RetryAsync(async () =>
            {
                callCount++;
                if (callCount < 3)
                    throw new Exception("transient error");
                return await Task.FromResult("success");
            }, maxAttempts: 3, delayMs: 10);

            result.Should().Be("success");
            callCount.Should().Be(3);
        }

        #endregion

        #region All attempts fail

        [Fact]
        public async Task RetryAsync_AllAttemptsFail_ShouldThrowLastException()
        {
            var callCount = 0;
            var action = () => RetryHelper.RetryAsync(async () =>
            {
                callCount++;
                await Task.CompletedTask;
                throw new Exception("persistent error");
#pragma warning disable CS0162
                return "unreachable";
#pragma warning restore CS0162
            }, maxAttempts: 3, delayMs: 10);

            await action.Should().ThrowAsync<Exception>()
                        .WithMessage("*persistent*");
            callCount.Should().Be(3);
        }

        #endregion

        #region Single attempt

        [Fact]
        public async Task RetryAsync_SingleAttempt_Success_ShouldWork()
        {
            var result = await RetryHelper.RetryAsync(
                async () => await Task.FromResult(42),
                maxAttempts: 1, delayMs: 10);

            result.Should().Be(42);
        }

        [Fact]
        public async Task RetryAsync_SingleAttempt_Failure_ShouldThrow()
        {
            var action = () => RetryHelper.RetryAsync<int>(async () =>
            {
                await Task.CompletedTask;
                throw new Exception("fail");
            }, maxAttempts: 1, delayMs: 10);

            await action.Should().ThrowAsync<Exception>();
        }

        #endregion
    }

    public class TimeHelperTests
    {
        [Fact]
        public void GetTimestamp_ShouldReturnPositiveValue()
        {
            var ts = TimeHelper.GetTimestamp();
            ts.Should().BeGreaterThan(0);
        }

        [Fact]
        public void GetTimestamp_ShouldBeRecentMilliseconds()
        {
            var ts = TimeHelper.GetTimestamp();
            var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();

            ts.Should().BeCloseTo(now, 1000); // within 1 second
        }

        [Fact]
        public void FromTimestamp_ShouldConvertCorrectly()
        {
            var nowMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            var dt = TimeHelper.FromTimestamp(nowMs);

            dt.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(2));
        }

        [Fact]
        public void FromTimestamp_KnownValue_ShouldReturn2025()
        {
            // 2025-01-01T00:00:00Z
            var dt = TimeHelper.FromTimestamp(1735689600000L);
            dt.Year.Should().Be(2025);
            dt.Month.Should().Be(1);
            dt.Day.Should().Be(1);
        }
    }

    public class DateTimeHelperTests
    {
        [Fact]
        public void ToUtcString_ShouldReturnCorrectFormat()
        {
            var dt = new DateTime(2025, 3, 15, 10, 30, 0, DateTimeKind.Utc);
            var result = DateTimeHelper.ToUtcString(dt);

            result.Should().Be("2025-03-15T10:30:00Z");
        }

        [Fact]
        public void ParseUtc_ShouldReturnUtcDateTime()
        {
            var result = DateTimeHelper.ParseUtc("2025-03-15T10:30:00Z");

            result.Kind.Should().Be(DateTimeKind.Utc);
            result.Year.Should().Be(2025);
            result.Month.Should().Be(3);
            result.Hour.Should().Be(10);
        }

        [Fact]
        public void RoundTrip_ShouldPreserveTime()
        {
            var original = new DateTime(2025, 6, 15, 14, 30, 0, DateTimeKind.Utc);
            var str = DateTimeHelper.ToUtcString(original);
            var restored = DateTimeHelper.ParseUtc(str);

            restored.Should().BeCloseTo(original, TimeSpan.FromSeconds(1));
        }
    }
}
