using FluentAssertions;
using JGSY.AGI.Common.Core.Interfaces;
using Xunit;

namespace JGSY.AGI.Test.Common
{
    // PagedResult<T> is defined in JGSY.AGI.Common.Abstractions/Interfaces/IRepository.cs
    public class PagedResultTests
    {
        [Fact]
        public void TotalPages_ShouldCalculateCorrectly()
        {
            var result = new PagedResult<string>
            {
                TotalCount = 100,
                PageSize = 10
            };

            result.TotalPages.Should().Be(10);
        }

        [Fact]
        public void TotalPages_WithRemainder_ShouldRoundUp()
        {
            var result = new PagedResult<string>
            {
                TotalCount = 101,
                PageSize = 10
            };

            result.TotalPages.Should().Be(11);
        }

        [Fact]
        public void TotalPages_WithExactMultiple_ShouldNotRoundUp()
        {
            var result = new PagedResult<string>
            {
                TotalCount = 50,
                PageSize = 10
            };

            result.TotalPages.Should().Be(5);
        }

        [Fact]
        public void TotalPages_ZeroTotalCount_ShouldReturnZero()
        {
            var result = new PagedResult<string>
            {
                TotalCount = 0,
                PageSize = 10
            };

            result.TotalPages.Should().Be(0);
        }

        [Fact]
        public void TotalPages_SingleItem_ShouldReturnOne()
        {
            var result = new PagedResult<string>
            {
                TotalCount = 1,
                PageSize = 10
            };

            result.TotalPages.Should().Be(1);
        }

        [Fact]
        public void HasPreviousPage_OnFirstPage_ShouldBeFalse()
        {
            var result = new PagedResult<string>
            {
                Page = 1
            };

            result.HasPreviousPage.Should().BeFalse();
        }

        [Fact]
        public void HasPreviousPage_OnSecondPage_ShouldBeTrue()
        {
            var result = new PagedResult<string>
            {
                Page = 2
            };

            result.HasPreviousPage.Should().BeTrue();
        }

        [Fact]
        public void HasNextPage_OnLastPage_ShouldBeFalse()
        {
            var result = new PagedResult<string>
            {
                TotalCount = 30,
                PageSize = 10,
                Page = 3
            };

            result.HasNextPage.Should().BeFalse();
        }

        [Fact]
        public void HasNextPage_NotOnLastPage_ShouldBeTrue()
        {
            var result = new PagedResult<string>
            {
                TotalCount = 30,
                PageSize = 10,
                Page = 2
            };

            result.HasNextPage.Should().BeTrue();
        }

        [Fact]
        public void HasNextPage_OnFirstPageOfMany_ShouldBeTrue()
        {
            var result = new PagedResult<string>
            {
                TotalCount = 100,
                PageSize = 10,
                Page = 1
            };

            result.HasNextPage.Should().BeTrue();
        }

        [Fact]
        public void Total_ShouldBeSynonymForTotalCount()
        {
            var result = new PagedResult<string>
            {
                TotalCount = 42
            };

            result.Total.Should().Be(42);
        }

        [Fact]
        public void Total_Setter_ShouldUpdateTotalCount()
        {
            var result = new PagedResult<string>();
            result.Total = 99;

            result.TotalCount.Should().Be(99);
        }

        [Fact]
        public void PageIndex_ShouldBeSynonymForPage()
        {
            var result = new PagedResult<string>
            {
                Page = 5
            };

            result.PageIndex.Should().Be(5);
        }

        [Fact]
        public void PageIndex_Setter_ShouldUpdatePage()
        {
            var result = new PagedResult<string>();
            result.PageIndex = 7;

            result.Page.Should().Be(7);
        }

        [Fact]
        public void Items_DefaultShouldBeEmptyList()
        {
            var result = new PagedResult<string>();

            result.Items.Should().NotBeNull();
            result.Items.Should().BeEmpty();
        }

        [Fact]
        public void Items_ShouldPreserveAddedItems()
        {
            var result = new PagedResult<string>();
            result.Items.Add("item1");
            result.Items.Add("item2");

            result.Items.Should().HaveCount(2);
            result.Items.Should().Contain("item1");
        }

        [Theory]
        [InlineData(0, 10, 0)]
        [InlineData(1, 10, 1)]
        [InlineData(10, 10, 1)]
        [InlineData(11, 10, 2)]
        [InlineData(20, 10, 2)]
        [InlineData(21, 10, 3)]
        [InlineData(100, 25, 4)]
        [InlineData(101, 25, 5)]
        public void TotalPages_VariousInputs_ShouldCalculateCorrectly(int totalCount, int pageSize, int expectedPages)
        {
            var result = new PagedResult<string>
            {
                TotalCount = totalCount,
                PageSize = pageSize
            };

            result.TotalPages.Should().Be(expectedPages);
        }
    }
}
