using FluentAssertions;
using JGSY.AGI.Common.Core.Interfaces;
using JGSY.AGI.Common.Core.Service;
using Microsoft.AspNetCore.Http;
using Moq;
using System.Security.Claims;
using Xunit;

namespace JGSY.AGI.Test.Common;

/// <summary>
/// ICurrentUser 和 CurrentUser 实现的单元测试
/// </summary>
public class CurrentUserTests
{
    private readonly Mock<IHttpContextAccessor> _httpContextAccessorMock;
    private readonly ICurrentUser _currentUser;

    public CurrentUserTests()
    {
        _httpContextAccessorMock = new Mock<IHttpContextAccessor>();
        _currentUser = new CurrentUser(_httpContextAccessorMock.Object);
    }

    private void SetupUser(params Claim[] claims)
    {
        var identity = new ClaimsIdentity(claims, "TestAuth");
        var principal = new ClaimsPrincipal(identity);
        var httpContext = new DefaultHttpContext { User = principal };
        _httpContextAccessorMock.Setup(x => x.HttpContext).Returns(httpContext);
    }

    private void SetupAnonymousUser()
    {
        var httpContext = new DefaultHttpContext();
        _httpContextAccessorMock.Setup(x => x.HttpContext).Returns(httpContext);
    }

    #region UserId 测试

    [Fact]
    public void UserId_从sub_claim获取_返回正确的Guid()
    {
        // Arrange
        var expectedUserId = Guid.NewGuid();
        SetupUser(new Claim("sub", expectedUserId.ToString()));

        // Act
        var result = _currentUser.UserId;

        // Assert
        result.Should().Be(expectedUserId);
    }

    [Fact]
    public void UserId_从NameIdentifier_claim获取_返回正确的Guid()
    {
        // Arrange
        var expectedUserId = Guid.NewGuid();
        SetupUser(new Claim(ClaimTypes.NameIdentifier, expectedUserId.ToString()));

        // Act
        var result = _currentUser.UserId;

        // Assert
        result.Should().Be(expectedUserId);
    }

    [Fact]
    public void UserId_从userId_claim获取_返回正确的Guid()
    {
        // Arrange
        var expectedUserId = Guid.NewGuid();
        SetupUser(new Claim("userId", expectedUserId.ToString()));

        // Act
        var result = _currentUser.UserId;

        // Assert
        result.Should().Be(expectedUserId);
    }

    [Fact]
    public void UserId_未认证用户_返回Empty()
    {
        // Arrange
        SetupAnonymousUser();

        // Act
        var result = _currentUser.UserId;

        // Assert
        result.Should().Be(Guid.Empty);
    }

    [Fact]
    public void UserIdOrNull_未认证用户_返回null()
    {
        // Arrange
        SetupAnonymousUser();

        // Act
        var result = _currentUser.UserIdOrNull;

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public void UserIdOrNull_已认证用户_返回UserId()
    {
        // Arrange
        var expectedUserId = Guid.NewGuid();
        SetupUser(new Claim("sub", expectedUserId.ToString()));

        // Act
        var result = _currentUser.UserIdOrNull;

        // Assert
        result.Should().Be(expectedUserId);
    }

    #endregion

    #region TenantId 测试

    [Fact]
    public void TenantId_从tenant_id_claim获取_返回正确的Guid()
    {
        // Arrange
        var expectedTenantId = Guid.NewGuid();
        SetupUser(new Claim("tenant_id", expectedTenantId.ToString()));

        // Act
        var result = _currentUser.TenantId;

        // Assert
        result.Should().Be(expectedTenantId);
    }

    [Fact]
    public void TenantId_从tenantId_claim获取_返回正确的Guid()
    {
        // Arrange
        var expectedTenantId = Guid.NewGuid();
        SetupUser(new Claim("tenantId", expectedTenantId.ToString()));

        // Act
        var result = _currentUser.TenantId;

        // Assert
        result.Should().Be(expectedTenantId);
    }

    [Fact]
    public void TenantId_已认证但无租户信息_返回系统管理员租户ID()
    {
        // Arrange
        SetupUser(new Claim("sub", Guid.NewGuid().ToString()));

        // Act
        var result = _currentUser.TenantId;

        // Assert
        result.Should().Be(CurrentUser.SystemAdminTenantId);
    }

    [Fact]
    public void TenantId_未认证用户_返回Empty()
    {
        // Arrange
        SetupAnonymousUser();

        // Act
        var result = _currentUser.TenantId;

        // Assert
        result.Should().Be(Guid.Empty);
    }

    #endregion

    #region UserName 和 DisplayName 测试

    [Fact]
    public void UserName_从name_claim获取_返回正确的值()
    {
        // Arrange
        SetupUser(new Claim("name", "testuser"));

        // Act
        var result = _currentUser.UserName;

        // Assert
        result.Should().Be("testuser");
    }

    [Fact]
    public void UserName_从preferred_username_claim获取_返回正确的值()
    {
        // Arrange
        SetupUser(new Claim("preferred_username", "preferred_user"));

        // Act
        var result = _currentUser.UserName;

        // Assert
        result.Should().Be("preferred_user");
    }

    [Fact]
    public void DisplayName_从display_name_claim获取_返回正确的值()
    {
        // Arrange
        SetupUser(new Claim("display_name", "显示名称"));

        // Act
        var result = _currentUser.DisplayName;

        // Assert
        result.Should().Be("显示名称");
    }

    [Fact]
    public void DisplayName_无display_name时使用UserName_返回UserName()
    {
        // Arrange
        SetupUser(new Claim("name", "testuser"));

        // Act
        var result = _currentUser.DisplayName;

        // Assert
        result.Should().Be("testuser");
    }

    #endregion

    #region Email 和 PhoneNumber 测试

    [Fact]
    public void Email_从email_claim获取_返回正确的值()
    {
        // Arrange
        SetupUser(new Claim("email", "test@example.com"));

        // Act
        var result = _currentUser.Email;

        // Assert
        result.Should().Be("test@example.com");
    }

    [Fact]
    public void PhoneNumber_从phone_number_claim获取_返回正确的值()
    {
        // Arrange
        SetupUser(new Claim("phone_number", "13800138000"));

        // Act
        var result = _currentUser.PhoneNumber;

        // Assert
        result.Should().Be("13800138000");
    }

    #endregion

    #region Roles 测试

    [Fact]
    public void Roles_有多个角色_返回所有角色()
    {
        // Arrange
        SetupUser(
            new Claim(ClaimTypes.Role, "Admin"),
            new Claim(ClaimTypes.Role, "User"),
            new Claim(ClaimTypes.Role, "Manager")
        );

        // Act
        var result = _currentUser.Roles;

        // Assert
        result.Should().HaveCount(3);
        result.Should().Contain("Admin");
        result.Should().Contain("User");
        result.Should().Contain("Manager");
    }

    [Fact]
    public void IsInRole_存在该角色_返回true()
    {
        // Arrange
        SetupUser(new Claim(ClaimTypes.Role, "Admin"));

        // Act
        var result = _currentUser.IsInRole("Admin");

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public void IsInRole_不存在该角色_返回false()
    {
        // Arrange
        SetupUser(new Claim(ClaimTypes.Role, "User"));

        // Act
        var result = _currentUser.IsInRole("Admin");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public void IsInAnyRole_存在任一角色_返回true()
    {
        // Arrange
        SetupUser(new Claim(ClaimTypes.Role, "User"));

        // Act
        var result = _currentUser.IsInAnyRole("Admin", "User", "Manager");

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public void IsInAllRoles_存在所有角色_返回true()
    {
        // Arrange
        SetupUser(
            new Claim(ClaimTypes.Role, "Admin"),
            new Claim(ClaimTypes.Role, "User")
        );

        // Act
        var result = _currentUser.IsInAllRoles("Admin", "User");

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public void IsInAllRoles_缺少某个角色_返回false()
    {
        // Arrange
        SetupUser(new Claim(ClaimTypes.Role, "Admin"));

        // Act
        var result = _currentUser.IsInAllRoles("Admin", "User");

        // Assert
        result.Should().BeFalse();
    }

    #endregion

    #region IsAuthenticated 测试

    [Fact]
    public void IsAuthenticated_已认证用户_返回true()
    {
        // Arrange
        SetupUser(new Claim("sub", Guid.NewGuid().ToString()));

        // Act
        var result = _currentUser.IsAuthenticated;

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public void IsAuthenticated_未认证用户_返回false()
    {
        // Arrange
        SetupAnonymousUser();

        // Act
        var result = _currentUser.IsAuthenticated;

        // Assert
        result.Should().BeFalse();
    }

    #endregion

    #region IsSystemAdmin 和 IsTenantAdmin 测试

    [Fact]
    public void IsSystemAdmin_有SystemAdmin角色_返回true()
    {
        // Arrange
        SetupUser(new Claim(ClaimTypes.Role, CurrentUser.SystemAdminRole));

        // Act
        var result = _currentUser.IsSystemAdmin;

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public void IsSystemAdmin_属于系统管理员租户_返回true()
    {
        // Arrange
        SetupUser(
            new Claim("sub", Guid.NewGuid().ToString()),
            new Claim("tenant_id", CurrentUser.SystemAdminTenantId.ToString())
        );

        // Act
        var result = _currentUser.IsSystemAdmin;

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public void IsTenantAdmin_有TenantAdmin角色_返回true()
    {
        // Arrange
        SetupUser(new Claim(ClaimTypes.Role, CurrentUser.TenantAdminRole));

        // Act
        var result = _currentUser.IsTenantAdmin;

        // Assert
        result.Should().BeTrue();
    }

    #endregion

    #region Require 方法测试

    [Fact]
    public void RequireUserId_已认证用户_返回UserId()
    {
        // Arrange
        var expectedUserId = Guid.NewGuid();
        SetupUser(new Claim("sub", expectedUserId.ToString()));

        // Act
        var result = _currentUser.RequireUserId();

        // Assert
        result.Should().Be(expectedUserId);
    }

    [Fact]
    public void RequireUserId_未认证用户_抛出异常()
    {
        // Arrange
        SetupAnonymousUser();

        // Act
        var act = () => _currentUser.RequireUserId();

        // Assert
        act.Should().Throw<UnauthorizedAccessException>()
           .WithMessage("*用户身份*登录*");
    }

    [Fact]
    public void RequireTenantId_有租户上下文_返回TenantId()
    {
        // Arrange
        var expectedTenantId = Guid.NewGuid();
        SetupUser(new Claim("tenant_id", expectedTenantId.ToString()));

        // Act
        var result = _currentUser.RequireTenantId();

        // Assert
        result.Should().Be(expectedTenantId);
    }

    [Fact]
    public void RequireTenantId_无租户上下文_抛出异常()
    {
        // Arrange
        SetupAnonymousUser();

        // Act
        var act = () => _currentUser.RequireTenantId();

        // Assert
        act.Should().Throw<UnauthorizedAccessException>()
           .WithMessage("*租户上下文*登录*");
    }

    #endregion

    #region GetClaimValue 测试

    [Fact]
    public void GetClaimValue_存在的Claim_返回值()
    {
        // Arrange
        SetupUser(new Claim("custom_claim", "custom_value"));

        // Act
        var result = _currentUser.GetClaimValue("custom_claim");

        // Assert
        result.Should().Be("custom_value");
    }

    [Fact]
    public void GetClaimValue_不存在的Claim_返回null()
    {
        // Arrange
        SetupUser(new Claim("other_claim", "value"));

        // Act
        var result = _currentUser.GetClaimValue("non_existent");

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public void GetClaimValues_多个相同类型的Claim_返回所有值()
    {
        // Arrange
        SetupUser(
            new Claim("permission", "read"),
            new Claim("permission", "write"),
            new Claim("permission", "delete")
        );

        // Act
        var result = _currentUser.GetClaimValues("permission");

        // Assert
        result.Should().HaveCount(3);
        result.Should().Contain("read");
        result.Should().Contain("write");
        result.Should().Contain("delete");
    }

    #endregion
}
