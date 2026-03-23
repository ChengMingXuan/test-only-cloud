using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.ContentPlatform;

/// <summary>
/// 内容平台 CMS 实体与 DTO 单元测试
/// </summary>
public class ContentPlatformEntityTests
{
    #region CmsSite 测试

    [Fact]
    public void CmsSite_ShouldHaveCorrectDefaults()
    {
        var site = new AGI.CMS.Entities.CmsSite();
        site.IsEnabled.Should().BeTrue();
        site.DeleteAt.Should().BeNull();
    }

    [Fact]
    public void CmsSite_ShouldSetAllProperties()
    {
        var tenantId = Guid.NewGuid();
        var site = new AGI.CMS.Entities.CmsSite
        {
            SiteCode = "main-site",
            SiteName = "JGSY 主站",
            Domain = "www.jgsy.com",
            Logo = "/images/logo.png",
            IsEnabled = true,
            SeoTitle = "JGSY 综合能源管理平台",
            TenantId = tenantId
        };

        site.SiteCode.Should().Be("main-site");
        site.SiteName.Should().Be("JGSY 主站");
        site.Domain.Should().Be("www.jgsy.com");
        site.IsEnabled.Should().BeTrue();
        site.TenantId.Should().Be(tenantId);
    }

    #endregion

    #region CmsCompanyInfo 测试

    [Fact]
    public void CmsCompanyInfo_ShouldSetAllProperties()
    {
        var company = new AGI.CMS.Entities.CmsCompanyInfo
        {
            Name = "JGSY",
            FullName = "聚光盛阳新能源科技有限公司",
            FoundedYear = 2020,
            Employees = "200",
            Address = "北京市",
            Phone = "010-12345678",
            Email = "info@jgsy.com"
        };

        company.Name.Should().Be("JGSY");
        company.FoundedYear.Should().Be(2020);
        company.Employees.Should().NotBeNullOrEmpty();
        company.Email.Should().Contain("@");
    }

    #endregion

    #region CmsStats 测试

    [Fact]
    public void CmsStats_ShouldSetProperties()
    {
        var stats = new AGI.CMS.Entities.CmsStats
        {
            StatsKey = "total_stations",
            Value = "1200",
            Icon = "icon-station"
        };

        stats.StatsKey.Should().Be("total_stations");
        stats.Value.Should().Be("1200");
    }

    #endregion

    #region ContentType 枚举测试

    [Fact]
    public void ContentType_ShouldHaveAllExpectedValues()
    {
        Enum.IsDefined(typeof(AGI.CMS.Entities.ContentType), AGI.CMS.Entities.ContentType.Article).Should().BeTrue();
        Enum.IsDefined(typeof(AGI.CMS.Entities.ContentType), AGI.CMS.Entities.ContentType.Image).Should().BeTrue();
        Enum.IsDefined(typeof(AGI.CMS.Entities.ContentType), AGI.CMS.Entities.ContentType.Video).Should().BeTrue();
    }

    [Fact]
    public void ContentStatus_ShouldHaveAllExpectedValues()
    {
        Enum.IsDefined(typeof(AGI.CMS.Entities.ContentStatus), AGI.CMS.Entities.ContentStatus.Draft).Should().BeTrue();
        Enum.IsDefined(typeof(AGI.CMS.Entities.ContentStatus), AGI.CMS.Entities.ContentStatus.Published).Should().BeTrue();
    }

    #endregion
}

/// <summary>
/// CMS DTO 测试
/// </summary>
public class ContentPlatformDtoTests
{
    [Fact]
    public void CreateSiteRequest_ShouldSetProperties()
    {
        var request = new AGI.CMS.Interfaces.CreateSiteRequest
        {
            SiteCode = "test-site",
            SiteName = "测试站点",
            Domain = "test.jgsy.com",
            IsEnabled = true,
            SeoTitle = "测试",
            SeoDescription = "测试站点描述"
        };

        request.SiteCode.Should().Be("test-site");
        request.IsEnabled.Should().BeTrue();
    }

    [Fact]
    public void SiteDto_ShouldHaveCorrectDefaults()
    {
        var dto = new AGI.CMS.Interfaces.SiteDto();
        dto.CategoryCount.Should().Be(0);
        dto.ArticleCount.Should().Be(0);
    }

    [Fact]
    public void CategoryDto_ShouldSupportHierarchy()
    {
        var parent = new AGI.CMS.Interfaces.CategoryDto
        {
            Id = Guid.NewGuid(),
            CategoryName = "新闻",
            Children = new List<AGI.CMS.Interfaces.CategoryDto>
            {
                new() { CategoryName = "公司新闻" },
                new() { CategoryName = "行业动态" }
            }
        };

        parent.Children.Should().HaveCount(2);
        parent.Children[0].CategoryName.Should().Be("公司新闻");
    }
}
