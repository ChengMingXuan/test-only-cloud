using FluentAssertions;
using JGSY.AGI.Common.Core.Utils;
using Xunit;

namespace JGSY.AGI.Test.Common
{
    public class SequentialGuidTests
    {
        #region NewId

        [Fact]
        public void NewId_ShouldReturnNonEmptyGuid()
        {
            var guid = SequentialGuid.NewId();
            guid.Should().NotBe(Guid.Empty);
        }

        [Fact]
        public void NewId_ShouldGenerateUniqueIds()
        {
            var guids = Enumerable.Range(0, 100).Select(_ => SequentialGuid.NewId()).ToList();
            guids.Distinct().Should().HaveCount(100);
        }

        [Fact]
        public void NewId_Sequential_ShouldBeOrdered()
        {
            var guid1 = SequentialGuid.NewId();
            Thread.Sleep(2); // Small delay to ensure different timestamps
            var guid2 = SequentialGuid.NewId();

            // UUID v7 should be time-ordered: guid1 < guid2
            string.Compare(guid1.ToString(), guid2.ToString(), StringComparison.Ordinal)
                  .Should().BeLessThan(0);
        }

        #endregion

        #region IsVersion7

        [Fact]
        public void IsVersion7_WithSequentialGuid_ShouldReturnTrue()
        {
            var guid = SequentialGuid.NewId();
            SequentialGuid.IsVersion7(guid).Should().BeTrue();
        }

        [Fact]
        public void IsVersion7_WithRandomGuid_ShouldReturnFalse()
        {
            var guid = Guid.NewGuid(); // v4
            SequentialGuid.IsVersion7(guid).Should().BeFalse();
        }

        [Fact]
        public void IsVersion7_WithEmptyGuid_ShouldReturnFalse()
        {
            SequentialGuid.IsVersion7(Guid.Empty).Should().BeFalse();
        }

        #endregion

        #region NewId with DateTimeOffset

        [Fact]
        public void NewId_WithSpecificTime_ShouldReturnNonEmpty()
        {
            var time = new DateTimeOffset(2025, 6, 15, 12, 0, 0, TimeSpan.Zero);
            var guid = SequentialGuid.NewId(time);

            guid.Should().NotBe(Guid.Empty);
            SequentialGuid.IsVersion7(guid).Should().BeTrue();
        }

        [Fact]
        public void NewId_WithSameTime_ShouldGenerateDifferentIds()
        {
            var time = new DateTimeOffset(2025, 1, 1, 0, 0, 0, TimeSpan.Zero);
            var guid1 = SequentialGuid.NewId(time);
            var guid2 = SequentialGuid.NewId(time);

            // Even with same timestamp, random component should differ
            guid1.Should().NotBe(guid2);
        }

        #endregion

        #region ExtractTimestamp

        [Fact]
        public void ExtractTimestamp_ShouldReturnApproximateCreationTime()
        {
            var beforeCreate = DateTimeOffset.UtcNow;
            var guid = SequentialGuid.NewId();
            var afterCreate = DateTimeOffset.UtcNow;

            var extracted = SequentialGuid.ExtractTimestamp(guid);

            extracted.Should().BeOnOrAfter(beforeCreate.AddMilliseconds(-10));
            extracted.Should().BeOnOrBefore(afterCreate.AddMilliseconds(10));
        }

        [Fact]
        public void ExtractTimestamp_WithSpecificTime_ShouldRoundTrip()
        {
            var originalTime = new DateTimeOffset(2025, 6, 15, 14, 30, 0, TimeSpan.Zero);
            var guid = SequentialGuid.NewId(originalTime);
            var extracted = SequentialGuid.ExtractTimestamp(guid);

            // Should be within 1 second of original time (millisecond precision)
            extracted.Should().BeCloseTo(originalTime, TimeSpan.FromSeconds(1));
        }

        #endregion

        #region Batch generation

        [Fact]
        public void NewId_BatchOf1000_AllShouldBeVersion7()
        {
            var guids = Enumerable.Range(0, 1000).Select(_ => SequentialGuid.NewId()).ToList();

            guids.Should().AllSatisfy(g => SequentialGuid.IsVersion7(g).Should().BeTrue());
        }

        [Fact]
        public void NewId_BatchOf1000_AllShouldBeUnique()
        {
            var guids = Enumerable.Range(0, 1000).Select(_ => SequentialGuid.NewId()).ToList();

            guids.Distinct().Should().HaveCount(1000);
        }

        #endregion
    }
}
