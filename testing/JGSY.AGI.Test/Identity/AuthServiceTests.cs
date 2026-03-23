using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;
using JGSY.AGI.Auth.Business;
using JGSY.AGI.Auth.Entities;
using JGSY.AGI.Auth.Interfaces;
using JGSY.AGI.Common.Core.Data.Dapper;
using JGSY.AGI.Common.Core.Interfaces;

namespace JGSY.AGI.Test.Identity;

/// <summary>
/// 认证服务单元测试
/// </summary>
public class AuthServiceTests
{
    private readonly Mock<IDbConnectionFactory> _connFactoryMock;
    private readonly Mock<IJwtTokenService> _jwtMock;
    private readonly Mock<ITenantContext> _tenantContextMock;
    private readonly Mock<ICacheManager> _cacheMock;
    private readonly Mock<IServiceScopeFactory> _scopeFactoryMock;
    private readonly Mock<IMfaService> _mfaServiceMock;
    private readonly AuthService _service;
    private readonly Guid _tenantId = Guid.NewGuid();

    public AuthServiceTests()
    {
        _connFactoryMock = new Mock<IDbConnectionFactory>();
        _jwtMock = new Mock<IJwtTokenService>();
        _tenantContextMock = new Mock<ITenantContext>();
        _cacheMock = new Mock<ICacheManager>();
        _scopeFactoryMock = new Mock<IServiceScopeFactory>();
        _mfaServiceMock = new Mock<IMfaService>();

        _tenantContextMock.Setup(t => t.TenantId).Returns(_tenantId);

        var configData = new Dictionary<string, string?>
        {
            ["Mfa:Enabled"] = "false",
        };
        var configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(configData)
            .Build();

        _service = new AuthService(
            _connFactoryMock.Object,
            _jwtMock.Object,
            _tenantContextMock.Object,
            _cacheMock.Object,
            _scopeFactoryMock.Object,
            configuration,
            _mfaServiceMock.Object,
            NullLogger<AuthService>.Instance);
    }

    #region LoginAsync

    [Fact]
    public async Task LoginAsync_ValidateUserDelegateNotSet_ReturnsServiceConfigError()
    {
        // Arrange - 不设置 ValidateUserAsync 委托
        var request = new LoginRequest { Username = "admin", Password = "123456" };

        // Act
        var result = await _service.LoginAsync(request);

        // Assert
        result.Success.Should().BeFalse();
        result.Result.Should().Be(LoginResult.Failed);
        result.Message.Should().Contain("服务配置错误");
    }

    [Fact]
    public async Task LoginAsync_UserNotFound_ReturnsUserNotFound()
    {
        // Arrange
        _service.ValidateUserAsync = (_, _, _, _) => Task.FromResult<UserValidationResult?>(null);
        var request = new LoginRequest { Username = "nonexistent", Password = "123456" };

        // Act
        var result = await _service.LoginAsync(request);

        // Assert
        result.Success.Should().BeFalse();
        result.Result.Should().Be(LoginResult.UserNotFound);
        result.Message.Should().Contain("用户名或密码错误");
    }

    [Fact]
    public async Task LoginAsync_WrongPassword_ReturnsWrongPassword()
    {
        // Arrange
        _service.ValidateUserAsync = (_, _, _, _) => Task.FromResult<UserValidationResult?>(
            new UserValidationResult
            {
                UserId = Guid.NewGuid(),
                TenantId = _tenantId,
                IsPasswordValid = false,
                IsActive = true,
                Username = "testuser"
            });
        var request = new LoginRequest { Username = "testuser", Password = "wrongpass" };

        // Act
        var result = await _service.LoginAsync(request);

        // Assert
        result.Success.Should().BeFalse();
        result.Result.Should().Be(LoginResult.WrongPassword);
    }

    [Fact]
    public async Task LoginAsync_AccountDisabled_ReturnsAccountDisabled()
    {
        // Arrange
        _service.ValidateUserAsync = (_, _, _, _) => Task.FromResult<UserValidationResult?>(
            new UserValidationResult
            {
                UserId = Guid.NewGuid(),
                TenantId = _tenantId,
                IsPasswordValid = true,
                IsActive = false,
                Username = "disableduser"
            });
        var request = new LoginRequest { Username = "disableduser", Password = "123456" };

        // Act
        var result = await _service.LoginAsync(request);

        // Assert
        result.Success.Should().BeFalse();
        result.Result.Should().Be(LoginResult.AccountDisabled);
        result.Message.Should().Contain("禁用");
    }

    [Fact]
    public async Task LoginAsync_ValidCredentials_ReturnsSuccessWithToken()
    {
        // Arrange
        var userId = Guid.NewGuid();
        var tokenResult = new TokenResult
        {
            AccessToken = "access-token-123",
            RefreshToken = "refresh-token-456",
            AccessTokenExpires = DateTime.UtcNow.AddMinutes(30),
            RefreshTokenExpires = DateTime.UtcNow.AddDays(7)
        };

        _service.ValidateUserAsync = (_, _, _, _) => Task.FromResult<UserValidationResult?>(
            new UserValidationResult
            {
                UserId = userId,
                TenantId = _tenantId,
                IsPasswordValid = true,
                IsActive = true,
                Username = "admin",
                RealName = "管理员",
                Roles = new List<string> { "Admin" },
                Permissions = new List<string> { "dashboard:view" }
            });

        _jwtMock.Setup(j => j.GenerateTokenPairAsync(
                userId, _tenantId, "admin",
                It.IsAny<IEnumerable<string>?>(),
                It.IsAny<IEnumerable<string>?>(),
                It.IsAny<string?>(), It.IsAny<string?>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(tokenResult);

        var request = new LoginRequest { Username = "admin", Password = "123456", DeviceId = "dev1" };

        // Act
        var result = await _service.LoginAsync(request);

        // Assert
        result.Success.Should().BeTrue();
        result.Result.Should().Be(LoginResult.Success);
        result.AccessToken.Should().Be("access-token-123");
        result.RefreshToken.Should().Be("refresh-token-456");
        result.User.Should().NotBeNull();
        result.User!.Username.Should().Be("admin");
        result.User.UserId.Should().Be(userId);
        result.User.TenantId.Should().Be(_tenantId);
        result.User.Roles.Should().Contain("Admin");
    }

    [Fact]
    public async Task LoginAsync_SuccessfulLogin_GeneratesTokenPair()
    {
        // Arrange
        var userId = Guid.NewGuid();
        _service.ValidateUserAsync = (_, _, _, _) => Task.FromResult<UserValidationResult?>(
            new UserValidationResult { UserId = userId, TenantId = _tenantId, IsPasswordValid = true, IsActive = true, Username = "user1" });

        _jwtMock.Setup(j => j.GenerateTokenPairAsync(
                It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<string>(),
                It.IsAny<IEnumerable<string>?>(), It.IsAny<IEnumerable<string>?>(),
                It.IsAny<string?>(), It.IsAny<string?>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new TokenResult { AccessToken = "at", RefreshToken = "rt", AccessTokenExpires = DateTime.UtcNow.AddMinutes(30) });

        // Act
        await _service.LoginAsync(new LoginRequest { Username = "user1", Password = "pass" });

        // Assert
        _jwtMock.Verify(j => j.GenerateTokenPairAsync(
            userId, _tenantId, "user1",
            It.IsAny<IEnumerable<string>?>(),
            It.IsAny<IEnumerable<string>?>(),
            It.IsAny<string?>(), It.IsAny<string?>(), It.IsAny<CancellationToken>()), Times.Once);
    }

    #endregion

    #region LogoutAsync

    [Fact]
    public async Task LogoutAsync_ValidToken_CallsRevokeAndReturnsTrue()
    {
        // Arrange
        _jwtMock.Setup(j => j.RevokeTokenAsync("refresh-token", TokenRevocationType.Logout, It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        // Act
        var result = await _service.LogoutAsync("refresh-token");

        // Assert
        result.Should().BeTrue();
        _jwtMock.Verify(j => j.RevokeTokenAsync("refresh-token", TokenRevocationType.Logout, It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task LogoutAsync_InvalidToken_ReturnsFalse()
    {
        // Arrange
        _jwtMock.Setup(j => j.RevokeTokenAsync("bad-token", TokenRevocationType.Logout, It.IsAny<CancellationToken>()))
            .ReturnsAsync(false);

        // Act
        var result = await _service.LogoutAsync("bad-token");

        // Assert
        result.Should().BeFalse();
    }

    #endregion

    #region RefreshTokenAsync

    [Fact]
    public async Task RefreshTokenAsync_ValidToken_ReturnsNewTokenResult()
    {
        // Arrange
        var expected = new TokenResult { AccessToken = "new-at", RefreshToken = "new-rt" };
        _jwtMock.Setup(j => j.RefreshTokenAsync("old-rt", null, It.IsAny<CancellationToken>()))
            .ReturnsAsync(expected);

        // Act
        var result = await _service.RefreshTokenAsync("old-rt");

        // Assert
        result.Should().NotBeNull();
        result!.AccessToken.Should().Be("new-at");
    }

    [Fact]
    public async Task RefreshTokenAsync_ExpiredToken_ReturnsNull()
    {
        // Arrange
        _jwtMock.Setup(j => j.RefreshTokenAsync("expired-rt", null, It.IsAny<CancellationToken>()))
            .ReturnsAsync((TokenResult?)null);

        // Act
        var result = await _service.RefreshTokenAsync("expired-rt");

        // Assert
        result.Should().BeNull();
    }

    #endregion

    #region LogoutAllDevicesAsync

    [Fact]
    public async Task LogoutAllDevicesAsync_CallsRevokeAllUserTokens()
    {
        // Arrange
        var userId = Guid.NewGuid();

        // Act
        await _service.LogoutAllDevicesAsync(userId);

        // Assert
        _jwtMock.Verify(j => j.RevokeAllUserTokensAsync(userId, TokenRevocationType.PasswordChanged, It.IsAny<CancellationToken>()), Times.Once);
    }

    #endregion

    #region GetCurrentUserAsync

    [Fact]
    public async Task GetCurrentUserAsync_InvalidToken_ReturnsNull()
    {
        // Arrange
        _jwtMock.Setup(j => j.ParseToken("invalid-token")).Returns((TokenClaims?)null);

        // Act
        var result = await _service.GetCurrentUserAsync("invalid-token");

        // Assert
        result.Should().BeNull();
    }

    #endregion
}
