using FluentAssertions;
using JGSY.AGI.User.Entities;
using JGSY.AGI.Auth.Entities;
using Xunit;
using UserEntity = JGSY.AGI.User.Entities.User;
using UserTypeEnum = JGSY.AGI.User.Entities.UserType;
using GenderEnum = JGSY.AGI.User.Entities.Gender;

namespace JGSY.AGI.Test.Identity;

/// <summary>
/// 用户模块实体测试
/// </summary>
public class UserEntityTests
{
    [Fact]
    public void User_ShouldHaveCorrectDefaults()
    {
        var user = new UserEntity();
        user.DeleteAt.Should().BeNull();
        user.Status.Should().Be((int)UserStatus.Active);
    }

    [Fact]
    public void User_ShouldSetAllProperties()
    {
        var user = new UserEntity
        {
            UserName = "zhangsan",
            RealName = "张三",
            Email = "zhangsan@jgsy.com",
            Phone = "13800138000",
            Status = (int)UserStatus.Active,
            UserType = (int)UserTypeEnum.Normal,
            Gender = (int)GenderEnum.Male,
            Avatar = "https://cdn.jgsy.com/avatar/default.png"
        };

        user.UserName.Should().Be("zhangsan");
        user.Email.Should().Contain("@");
        user.Status.Should().Be((int)UserStatus.Active);
        user.Gender.Should().Be((int)GenderEnum.Male);
    }

    [Theory]
    [InlineData(UserStatus.Active)]
    [InlineData(UserStatus.Disabled)]
    [InlineData(UserStatus.Locked)]
    [InlineData(UserStatus.Deleted)]
    public void UserStatus_ShouldHaveDefinedValues(UserStatus status)
    {
        Enum.IsDefined(typeof(UserStatus), status).Should().BeTrue();
    }

    [Theory]
    [InlineData(UserTypeEnum.Normal)]
    [InlineData(UserTypeEnum.SystemAdmin)]
    [InlineData(UserTypeEnum.TenantAdmin)]
    public void UserType_ShouldHaveDefinedValues(UserTypeEnum userType)
    {
        Enum.IsDefined(typeof(UserTypeEnum), userType).Should().BeTrue();
    }
}

/// <summary>
/// 部门实体测试
/// </summary>
public class DepartmentEntityTests
{
    [Fact]
    public void Department_ShouldHaveCorrectDefaults()
    {
        var dept = new Department();
        dept.DeleteAt.Should().BeNull();
        dept.Status.Should().Be((int)DepartmentStatus.Active);
    }

    [Fact]
    public void Department_ShouldSupportHierarchy()
    {
        var parent = new Department
        {
            DepartmentName = "运营中心",
            DepartmentCode = "OPS",
            Status = (int)DepartmentStatus.Active,
            SortOrder = 1
        };
        var child = new Department
        {
            DepartmentName = "华东运营部",
            DepartmentCode = "OPS-HD",
            ParentId = parent.Id,
            Status = (int)DepartmentStatus.Active,
            SortOrder = 1
        };

        child.ParentId.Should().Be(parent.Id);
        child.DepartmentName.Should().Contain("华东");
    }
}

/// <summary>
/// 用户 DTO 测试
/// </summary>
public class UserDtoTests
{
    [Fact]
    public void UserCreateRequest_ShouldSetRequiredFields()
    {
        var request = new UserCreateRequest
        {
            UserName = "newuser",
            Password = "P@ssw0rd123",
            RealName = "新用户",
            Email = "new@jgsy.com",
            Phone = "13900139000"
        };

        request.UserName.Should().NotBeEmpty();
        request.Password.Should().NotBeEmpty();
        request.Email.Should().Contain("@");
    }

    [Fact]
    public void UserDto_ShouldMapFromUser()
    {
        var dto = new UserDto
        {
            Id = Guid.NewGuid(),
            UserName = "testuser",
            RealName = "测试用户",
            Email = "test@jgsy.com",
            Phone = "13800000001"
        };

        dto.Id.Should().NotBeEmpty();
        dto.UserName.Should().Be("testuser");
    }

    [Fact]
    public void ChangePasswordRequest_ShouldHaveFields()
    {
        var req = new ChangePasswordRequest
        {
            OldPassword = "oldpass",
            NewPassword = "NewP@ss1",
            ConfirmPassword = "NewP@ss1"
        };

        req.NewPassword.Should().Be(req.ConfirmPassword);
    }
}

/// <summary>
/// 认证模块实体测试
/// </summary>
public class AuthEntityTests
{
    [Fact]
    public void RefreshToken_ShouldHaveCorrectDefaults()
    {
        var token = new RefreshToken();
        token.DeleteAt.Should().BeNull();
        token.IsRevoked.Should().BeFalse();
    }

    [Fact]
    public void RefreshToken_Expiry_ShouldBeInFuture()
    {
        var token = new RefreshToken
        {
            Token = Guid.NewGuid().ToString("N"),
            ExpiresAt = DateTime.UtcNow.AddDays(7),
            IsRevoked = false
        };

        token.ExpiresAt.Should().BeAfter(DateTime.UtcNow);
        token.IsRevoked.Should().BeFalse();
    }

    [Fact]
    public void LoginLog_ShouldSetAllProperties()
    {
        var log = new LoginLog
        {
            LoginType = (int)LoginType.Password,
            LoginResult = (int)global::JGSY.AGI.Auth.Entities.LoginResult.Success,
            ClientIp = "192.168.1.100",
            UserAgent = "Mozilla/5.0",
            DeviceType = "Web"
        };

        log.LoginResult.Should().Be((int)global::JGSY.AGI.Auth.Entities.LoginResult.Success);
        log.ClientIp.Should().NotBeEmpty();
    }

    [Theory]
    [InlineData(LoginType.Password)]
    [InlineData(LoginType.SMS)]
    [InlineData(LoginType.WeChat)]
    [InlineData(LoginType.QQ)]
    [InlineData(LoginType.SSO)]
    public void LoginType_ShouldHaveAllValues(LoginType type)
    {
        Enum.IsDefined(typeof(LoginType), type).Should().BeTrue();
    }

    [Fact]
    public void TokenBlacklist_ShouldSetRevocationType()
    {
        var blacklist = new TokenBlacklist
        {
            JwtId = Guid.NewGuid().ToString(),
            RevocationType = (int)TokenRevocationType.Logout,
            TokenExpiresAt = DateTime.UtcNow.AddHours(1)
        };

        blacklist.RevocationType.Should().Be((int)TokenRevocationType.Logout);
    }

    [Theory]
    [InlineData(MfaType.Totp)]
    [InlineData(MfaType.Email)]
    [InlineData(MfaType.Sms)]
    public void MfaType_ShouldHaveDefinedValues(MfaType mfaType)
    {
        Enum.IsDefined(typeof(MfaType), mfaType).Should().BeTrue();
    }
}

/// <summary>
/// 用户标签测试
/// </summary>
public class UserTagTests
{
    [Fact]
    public void UserTag_ShouldSetAllProperties()
    {
        var tag = new UserTag
        {
            Name = "VIP客户",
            TagType = (int)TagType.System,
            Color = (int)TagColor.Default,
            IsEnabled = true
        };

        tag.Name.Should().Be("VIP客户");
        tag.IsEnabled.Should().BeTrue();
    }

    [Fact]
    public void UserTagMapping_ShouldLinkUserAndTag()
    {
        var userId = Guid.NewGuid();
        var tagId = Guid.NewGuid();
        var mapping = new UserTagMapping
        {
            UserId = userId,
            TagId = tagId,
            Source = (int)TagSource.Manual
        };

        mapping.UserId.Should().Be(userId);
        mapping.TagId.Should().Be(tagId);
        mapping.Source.Should().Be((int)TagSource.Manual);
    }
}
