using System;
using System.Collections.Generic;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;
using JGSY.AGI.User.Business;
using JGSY.AGI.User.Interfaces;

namespace JGSY.AGI.Test.Identity;

/// <summary>
/// 数据脱敏服务单元测试
/// </summary>
public class DataMaskingServiceTests
{
    private readonly DataMaskingService _service;

    public DataMaskingServiceTests()
    {
        _service = new DataMaskingService(NullLogger<DataMaskingService>.Instance);
    }

    #region MaskPhone 手机号脱敏

    [Theory]
    [InlineData("13812345678", "138****5678")]
    [InlineData("15999998888", "159****8888")]
    [InlineData("18600001111", "186****1111")]
    public void MaskPhone_Standard11Digits_ReturnsCorrectMask(string phone, string expected)
    {
        _service.MaskPhone(phone).Should().Be(expected);
    }

    [Fact]
    public void MaskPhone_NullInput_ReturnsEmpty()
    {
        _service.MaskPhone(null).Should().BeEmpty();
    }

    [Fact]
    public void MaskPhone_EmptyInput_ReturnsEmpty()
    {
        _service.MaskPhone("").Should().BeEmpty();
    }

    [Fact]
    public void MaskPhone_ShortInput_ReturnsOriginal()
    {
        _service.MaskPhone("123456").Should().Be("123456");
    }

    [Fact]
    public void MaskPhone_WithDashes_StripsAndMasks()
    {
        // 带连字符的手机号应该先去除再脱敏
        _service.MaskPhone("138-1234-5678").Should().Be("138****5678");
    }

    [Fact]
    public void MaskPhone_WithSpaces_StripsAndMasks()
    {
        _service.MaskPhone("138 1234 5678").Should().Be("138****5678");
    }

    #endregion

    #region MaskEmail 邮箱脱敏

    [Theory]
    [InlineData("username@example.com", "use***@example.com")]
    [InlineData("ab@test.com", "ab@test.com")]
    [InlineData("abc@test.com", "abc@test.com")]
    [InlineData("abcdef@domain.org", "abc***@domain.org")]
    public void MaskEmail_ValidEmail_ReturnsCorrectMask(string email, string expected)
    {
        _service.MaskEmail(email).Should().Be(expected);
    }

    [Fact]
    public void MaskEmail_NullInput_ReturnsEmpty()
    {
        _service.MaskEmail(null).Should().BeEmpty();
    }

    [Fact]
    public void MaskEmail_NoAtSign_ReturnsOriginal()
    {
        _service.MaskEmail("noemailformat").Should().Be("noemailformat");
    }

    #endregion

    #region MaskIdCard 身份证脱敏

    [Fact]
    public void MaskIdCard_18Digits_MasksMiddle8()
    {
        _service.MaskIdCard("110101199001011234").Should().Be("110101********1234");
    }

    [Fact]
    public void MaskIdCard_15Digits_MasksMiddle7()
    {
        _service.MaskIdCard("110101900101123").Should().Be("1101*******1123");
    }

    [Fact]
    public void MaskIdCard_NullInput_ReturnsEmpty()
    {
        _service.MaskIdCard(null).Should().BeEmpty();
    }

    [Fact]
    public void MaskIdCard_EmptyInput_ReturnsEmpty()
    {
        _service.MaskIdCard("").Should().BeEmpty();
    }

    [Fact]
    public void MaskIdCard_WithTrailingSpaces_Trims()
    {
        _service.MaskIdCard("110101199001011234 ").Should().Be("110101********1234");
    }

    [Fact]
    public void MaskIdCard_LowercaseX_ConvertsToUpperCase()
    {
        _service.MaskIdCard("11010119900101123x").Should().Be("110101********123X");
    }

    #endregion

    #region MaskName 姓名脱敏

    [Theory]
    [InlineData("张", "张")]
    [InlineData("张三", "张*")]
    [InlineData("张三明", "张*明")]
    [InlineData("欧阳修之", "欧**之")]
    public void MaskName_VariousLengths_ReturnsCorrectMask(string name, string expected)
    {
        _service.MaskName(name).Should().Be(expected);
    }

    [Fact]
    public void MaskName_NullInput_ReturnsEmpty()
    {
        _service.MaskName(null).Should().BeEmpty();
    }

    [Fact]
    public void MaskName_EmptyInput_ReturnsEmpty()
    {
        _service.MaskName("").Should().BeEmpty();
    }

    [Fact]
    public void MaskName_FiveChars_KeepsFirstAndLast()
    {
        _service.MaskName("司马相如甲").Should().Be("司***甲");
    }

    #endregion

    #region MaskBankCard 银行卡脱敏

    [Fact]
    public void MaskBankCard_16Digits_KeepsFirst4Last4()
    {
        _service.MaskBankCard("6222021234561234").Should().Be("6222********1234");
    }

    [Fact]
    public void MaskBankCard_19Digits_KeepsFirst4Last4()
    {
        _service.MaskBankCard("6222021234567891234").Should().Be("6222***********1234");
    }

    [Fact]
    public void MaskBankCard_NullInput_ReturnsEmpty()
    {
        _service.MaskBankCard(null).Should().BeEmpty();
    }

    [Fact]
    public void MaskBankCard_WithSpaces_StripsAndMasks()
    {
        _service.MaskBankCard("6222 0212 3456 1234").Should().Be("6222********1234");
    }

    [Fact]
    public void MaskBankCard_ShortCard_MasksMiddle()
    {
        _service.MaskBankCard("12345").Should().Be("12*45");
    }

    #endregion

    #region MaskAddress 地址脱敏

    [Fact]
    public void MaskAddress_LongAddress_PreservesFirst10Chars()
    {
        var address = "北京市海淀区中关村大街1号XXX大厦";
        var result = _service.MaskAddress(address);
        result.Should().StartWith("北京市海淀区中关村");
        result.Should().EndWith("******");
    }

    [Fact]
    public void MaskAddress_ShortAddress_ReturnsOriginal()
    {
        _service.MaskAddress("北京市").Should().Be("北京市");
    }

    [Fact]
    public void MaskAddress_NullInput_ReturnsEmpty()
    {
        _service.MaskAddress(null).Should().BeEmpty();
    }

    #endregion

    #region MaskIpAddress IP脱敏

    [Fact]
    public void MaskIpAddress_IPv4_MasksLastTwo()
    {
        _service.MaskIpAddress("192.168.1.100").Should().Be("192.168.*.*");
    }

    [Fact]
    public void MaskIpAddress_NullInput_ReturnsEmpty()
    {
        _service.MaskIpAddress(null).Should().BeEmpty();
    }

    [Fact]
    public void MaskIpAddress_IPv6_MasksAfterFirstColon()
    {
        var result = _service.MaskIpAddress("2001:db8::1");
        result.Should().Be("2001:****");
    }

    #endregion

    #region MaskLicensePlate 车牌号脱敏

    [Fact]
    public void MaskLicensePlate_Standard_KeepsProvinceAndLast()
    {
        _service.MaskLicensePlate("京A12345").Should().Be("京A***5");
    }

    [Fact]
    public void MaskLicensePlate_NullInput_ReturnsEmpty()
    {
        _service.MaskLicensePlate(null).Should().BeEmpty();
    }

    [Fact]
    public void MaskLicensePlate_ShortPlate_ReturnsOriginal()
    {
        _service.MaskLicensePlate("京A1").Should().Be("京A1");
    }

    #endregion

    #region MaskGeneric 通用脱敏

    [Theory]
    [InlineData("1234567890", 3, 4, "123***7890")]
    [InlineData("AB", 3, 3, "**")]
    public void MaskGeneric_VariousParams_ReturnsCorrectMask(string value, int keepStart, int keepEnd, string expected)
    {
        _service.MaskGeneric(value, keepStart, keepEnd).Should().Be(expected);
    }

    [Fact]
    public void MaskGeneric_NullInput_ReturnsEmpty()
    {
        _service.MaskGeneric(null, 3, 3).Should().BeEmpty();
    }

    [Fact]
    public void MaskGeneric_CustomMaskChar_UsesCustomChar()
    {
        _service.MaskGeneric("123456789", 2, 2, '#').Should().Be("12#####89");
    }

    #endregion

    #region MaskByRegex 正则脱敏

    [Fact]
    public void MaskByRegex_ValidPattern_ReplacesByPattern()
    {
        var result = _service.MaskByRegex("test123abc", @"\d+", "***");
        result.Should().Be("test***abc");
    }

    [Fact]
    public void MaskByRegex_NullInput_ReturnsEmpty()
    {
        _service.MaskByRegex(null, @"\d+", "***").Should().BeEmpty();
    }

    [Fact]
    public void MaskByRegex_InvalidPattern_FallsBackToGeneric()
    {
        // 无效的正则表达式应回退到通用脱敏
        var result = _service.MaskByRegex("testvalue", "[invalid", "***");
        result.Should().NotBeNullOrEmpty();
    }

    #endregion

    #region ShouldMask 脱敏判断

    [Fact]
    public void ShouldMask_AdminRole_ReturnsFalse()
    {
        var context = new MaskingContext
        {
            Roles = new List<string> { "Admin" },
            Permissions = new List<string>(),
            CurrentUserId = Guid.NewGuid()
        };

        _service.ShouldMask(context).Should().BeFalse();
    }

    [Fact]
    public void ShouldMask_SuperAdminRole_ReturnsFalse()
    {
        var context = new MaskingContext
        {
            Roles = new List<string> { "SuperAdmin" },
            Permissions = new List<string>(),
            CurrentUserId = Guid.NewGuid()
        };

        _service.ShouldMask(context).Should().BeFalse();
    }

    [Fact]
    public void ShouldMask_HasSensitiveViewPermission_ReturnsFalse()
    {
        var context = new MaskingContext
        {
            Roles = new List<string> { "NormalUser" },
            Permissions = new List<string> { "user:sensitive:view" },
            CurrentUserId = Guid.NewGuid()
        };

        _service.ShouldMask(context).Should().BeFalse();
    }

    [Fact]
    public void ShouldMask_ViewingOwnData_ReturnsFalse()
    {
        var userId = Guid.NewGuid();
        var context = new MaskingContext
        {
            Roles = new List<string> { "NormalUser" },
            Permissions = new List<string>(),
            CurrentUserId = userId,
            TargetUserId = userId
        };

        _service.ShouldMask(context).Should().BeFalse();
    }

    [Fact]
    public void ShouldMask_ExportContext_ReturnsTrue()
    {
        var context = new MaskingContext
        {
            Roles = new List<string> { "NormalUser" },
            Permissions = new List<string>(),
            CurrentUserId = Guid.NewGuid(),
            IsExportContext = true
        };

        _service.ShouldMask(context).Should().BeTrue();
    }

    [Fact]
    public void ShouldMask_NormalUserViewingOthers_ReturnsTrue()
    {
        var context = new MaskingContext
        {
            Roles = new List<string> { "NormalUser" },
            Permissions = new List<string>(),
            CurrentUserId = Guid.NewGuid(),
            TargetUserId = Guid.NewGuid()
        };

        _service.ShouldMask(context).Should().BeTrue();
    }

    #endregion

    #region MaskUserData 用户DTO脱敏

    [Fact]
    public void MaskUserData_NoneLevel_NoMasking()
    {
        var user = new { Id = Guid.NewGuid(), UserName = "testuser", RealName = "张三", Phone = "13812345678", Email = "test@example.com", Avatar = "avatar.png", Status = 1 };

        var result = _service.MaskUserData(user, MaskingLevel.None);

        result.IsMasked.Should().BeFalse();
        result.RealName.Should().Be("张三");
        result.Phone.Should().Be("13812345678");
        result.Email.Should().Be("test@example.com");
    }

    [Fact]
    public void MaskUserData_LightLevel_OnlyMasksIdCard()
    {
        var user = new { Id = Guid.NewGuid(), UserName = "testuser", RealName = "张三", Phone = "13812345678", Email = "test@example.com", IdCard = "110101199001011234", Avatar = "avatar.png", Status = 1 };

        var result = _service.MaskUserData(user, MaskingLevel.Light);

        result.IsMasked.Should().BeTrue();
        result.RealName.Should().Be("张三"); // 轻度不脱敏姓名
        result.Phone.Should().Be("13812345678"); // 轻度不脱敏手机
        result.IdCard.Should().Be("110101********1234"); // 轻度脱敏身份证
    }

    [Fact]
    public void MaskUserData_StandardLevel_MasksNamePhoneEmailIdCard()
    {
        var user = new { Id = Guid.NewGuid(), UserName = "testuser", RealName = "张三明", Phone = "13812345678", Email = "longuser@example.com", IdCard = "110101199001011234", Avatar = "avatar.png", Status = 1, LastLoginIp = "192.168.1.100" };

        var result = _service.MaskUserData(user, MaskingLevel.Standard);

        result.IsMasked.Should().BeTrue();
        result.RealName.Should().Be("张*明");
        result.Phone.Should().Be("138****5678");
        result.Email.Should().Be("lon***@example.com");
        result.IdCard.Should().Be("110101********1234");
        result.LastLoginIp.Should().Be("192.168.*.*");
    }

    [Fact]
    public void MaskUserData_StrictLevel_MasksAllSensitive()
    {
        var user = new { Id = Guid.NewGuid(), UserName = "testuser", RealName = "张三", Phone = "13812345678", Email = "test@example.com", IdCard = "110101199001011234", Address = "北京市海淀区中关村大街1号XXX大厦", Avatar = "avatar.png", Status = 1, LastLoginIp = "10.0.0.1" };

        var result = _service.MaskUserData(user, MaskingLevel.Strict);

        result.IsMasked.Should().BeTrue();
        result.RealName.Should().Be("张*");
        result.Phone.Should().Be("138****5678");
        result.Email.Should().Be("tes***@example.com");
        result.IdCard.Should().Be("110101********1234");
        result.Address.Should().Contain("******");
        result.LastLoginIp.Should().Be("10.0.*.*");
    }

    [Fact]
    public void MaskUserData_PreservesNonSensitiveFields()
    {
        var userId = Guid.NewGuid();
        var user = new { Id = userId, UserName = "testuser", Avatar = "avatar.png", Status = 1 };

        var result = _service.MaskUserData(user, MaskingLevel.Standard);

        result.Id.Should().Be(userId);
        result.UserName.Should().Be("testuser");
        result.Avatar.Should().Be("avatar.png");
        result.Status.Should().Be(1);
    }

    #endregion
}
