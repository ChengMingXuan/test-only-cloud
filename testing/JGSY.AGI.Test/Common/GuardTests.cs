using FluentAssertions;
using JGSY.AGI.Common.Core.Utils;
using Xunit;

namespace JGSY.AGI.Test.Common
{
    public class GuardTests
    {
        #region NotNull

        [Fact]
        public void NotNull_WithNonNullObject_ShouldNotThrow()
        {
            var action = () => Guard.NotNull(new object(), "param");
            action.Should().NotThrow();
        }

        [Fact]
        public void NotNull_WithNull_ShouldThrowArgumentNullException()
        {
            var action = () => Guard.NotNull(null!, "myParam");
            action.Should().Throw<ArgumentNullException>()
                  .WithParameterName("myParam");
        }

        [Fact]
        public void NotNull_WithString_ShouldNotThrow()
        {
            var action = () => Guard.NotNull("hello", "param");
            action.Should().NotThrow();
        }

        [Fact]
        public void NotNull_WithEmptyString_ShouldNotThrow()
        {
            // Empty string is not null
            var action = () => Guard.NotNull(string.Empty, "param");
            action.Should().NotThrow();
        }

        #endregion

        #region NotNullOrEmpty

        [Fact]
        public void NotNullOrEmpty_WithValidString_ShouldNotThrow()
        {
            var action = () => Guard.NotNullOrEmpty("hello", "param");
            action.Should().NotThrow();
        }

        [Fact]
        public void NotNullOrEmpty_WithNull_ShouldThrowArgumentException()
        {
            var action = () => Guard.NotNullOrEmpty(null!, "myParam");
            action.Should().Throw<ArgumentException>()
                  .WithParameterName("myParam");
        }

        [Fact]
        public void NotNullOrEmpty_WithEmptyString_ShouldThrowArgumentException()
        {
            var action = () => Guard.NotNullOrEmpty(string.Empty, "myParam");
            action.Should().Throw<ArgumentException>()
                  .WithParameterName("myParam");
        }

        [Fact]
        public void NotNullOrEmpty_ExceptionMessage_ShouldContainParamName()
        {
            var action = () => Guard.NotNullOrEmpty("", "userName");
            action.Should().Throw<ArgumentException>()
                  .WithMessage("*userName*");
        }

        [Fact]
        public void NotNullOrEmpty_WithWhitespace_ShouldNotThrow()
        {
            // whitespace is not empty per string.IsNullOrEmpty
            var action = () => Guard.NotNullOrEmpty("  ", "param");
            action.Should().NotThrow();
        }

        #endregion

        #region GreaterThanZero

        [Fact]
        public void GreaterThanZero_WithPositiveValue_ShouldNotThrow()
        {
            var action = () => Guard.GreaterThanZero(1, "param");
            action.Should().NotThrow();
        }

        [Fact]
        public void GreaterThanZero_WithLargeValue_ShouldNotThrow()
        {
            var action = () => Guard.GreaterThanZero(int.MaxValue, "param");
            action.Should().NotThrow();
        }

        [Fact]
        public void GreaterThanZero_WithZero_ShouldThrowArgumentOutOfRangeException()
        {
            var action = () => Guard.GreaterThanZero(0, "count");
            action.Should().Throw<ArgumentOutOfRangeException>()
                  .WithParameterName("count");
        }

        [Fact]
        public void GreaterThanZero_WithNegative_ShouldThrowArgumentOutOfRangeException()
        {
            var action = () => Guard.GreaterThanZero(-5, "count");
            action.Should().Throw<ArgumentOutOfRangeException>()
                  .WithParameterName("count");
        }

        [Fact]
        public void GreaterThanZero_ExceptionMessage_ShouldContainHint()
        {
            var action = () => Guard.GreaterThanZero(0, "pageSize");
            action.Should().Throw<ArgumentOutOfRangeException>()
                  .WithMessage("*大于0*");
        }

        #endregion
    }
}
