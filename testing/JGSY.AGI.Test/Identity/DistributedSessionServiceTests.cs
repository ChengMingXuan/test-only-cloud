using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using Moq;
using Xunit;
using JGSY.AGI.Auth.Business;
using JGSY.AGI.Auth.Interfaces;
using JGSY.AGI.Common.Core.Exceptions;
using JGSY.AGI.Common.Core.Interfaces;

namespace JGSY.AGI.Test.Identity;

/// <summary>
/// 分布式会话服务单元测试（纯缓存实现，无数据库依赖）
/// 注意：该服务内部有 GetSessionAsync→DestroySessionAsync→GetSessionAsync 的调用链，
/// mock 时需避免无限递归（expired 会话的 Destroy 再次 Get 必须返回 null）
/// </summary>
public class DistributedSessionServiceTests
{
    private readonly Mock<ICacheManager> _cacheMock;
    private readonly DistributedSessionOptions _options;
    private readonly DistributedSessionService _service;

    public DistributedSessionServiceTests()
    {
        _cacheMock = new Mock<ICacheManager>();
        _options = new DistributedSessionOptions
        {
            DefaultTimeoutMinutes = 30,
            SlidingWindowMinutes = 10,
            MaxSessionsPerUser = 0, // 默认不限制，需要时覆盖
            KickOldestOnLimit = true
        };

        _service = new DistributedSessionService(
            _cacheMock.Object,
            Options.Create(_options),
            NullLogger<DistributedSessionService>.Instance);
    }

    #region CreateSessionAsync

    [Fact]
    public async Task CreateSessionAsync_NoLimit_ReturnsSession()
    {
        // Arrange：MaxSessionsPerUser=0 表示不限制
        var userId = Guid.NewGuid();
        var tenantId = Guid.NewGuid();

        _cacheMock.Setup(c => c.GetAsync<List<string>>(
                It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((List<string>?)null);

        _cacheMock.Setup(c => c.SetAsync(
                It.IsAny<string>(), It.IsAny<DistributedSession>(),
                It.IsAny<TimeSpan>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        _cacheMock.Setup(c => c.SetAsync(
                It.IsAny<string>(), It.IsAny<List<string>>(),
                It.IsAny<TimeSpan>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        var request = new CreateSessionRequest
        {
            UserId = userId,
            TenantId = tenantId,
            Username = "testuser"
        };

        // Act
        var result = await _service.CreateSessionAsync(request);

        // Assert
        result.Should().NotBeNull();
        result.UserId.Should().Be(userId);
        result.TenantId.Should().Be(tenantId);
        result.Username.Should().Be("testuser");
        result.SessionId.Should().NotBeNullOrEmpty();
        result.ExpiresAt.Should().BeAfter(DateTime.UtcNow);
    }

    [Fact]
    public async Task CreateSessionAsync_WithTimeout_UsesCustomTimeout()
    {
        // Arrange
        var userId = Guid.NewGuid();
        _cacheMock.Setup(c => c.GetAsync<List<string>>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((List<string>?)null);
        _cacheMock.Setup(c => c.SetAsync(It.IsAny<string>(), It.IsAny<DistributedSession>(), It.IsAny<TimeSpan>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);
        _cacheMock.Setup(c => c.SetAsync(It.IsAny<string>(), It.IsAny<List<string>>(), It.IsAny<TimeSpan>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        var request = new CreateSessionRequest
        {
            UserId = userId,
            TenantId = Guid.NewGuid(),
            Username = "user",
            Timeout = TimeSpan.FromHours(2)
        };

        // Act
        var result = await _service.CreateSessionAsync(request);

        // Assert
        result.ExpiresAt.Should().BeCloseTo(DateTime.UtcNow.AddHours(2), TimeSpan.FromSeconds(5));
    }

    [Fact]
    public async Task CreateSessionAsync_WithInitialData_StoresData()
    {
        // Arrange
        _cacheMock.Setup(c => c.GetAsync<List<string>>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((List<string>?)null);
        _cacheMock.Setup(c => c.SetAsync(It.IsAny<string>(), It.IsAny<DistributedSession>(), It.IsAny<TimeSpan>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);
        _cacheMock.Setup(c => c.SetAsync(It.IsAny<string>(), It.IsAny<List<string>>(), It.IsAny<TimeSpan>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        var request = new CreateSessionRequest
        {
            UserId = Guid.NewGuid(),
            TenantId = Guid.NewGuid(),
            Username = "user",
            InitialData = new Dictionary<string, string> { ["theme"] = "dark" }
        };

        // Act
        var result = await _service.CreateSessionAsync(request);

        // Assert
        result.Data.Should().ContainKey("theme");
        result.Data["theme"].Should().Be("dark");
    }

    #endregion

    #region GetSessionAsync

    [Fact]
    public async Task GetSessionAsync_NotFound_ReturnsNull()
    {
        // Arrange
        _cacheMock.Setup(c => c.GetAsync<DistributedSession>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((DistributedSession?)null);

        // Act
        var result = await _service.GetSessionAsync("nonexistent-session");

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task GetSessionAsync_Expired_DestroysAndReturnsNull()
    {
        // Arrange: 第一次调用返回过期会话，第二次（DestroySessionAsync 内部 GetSession）返回 null 以中断递归
        var callCount = 0;
        _cacheMock.Setup(c => c.GetAsync<DistributedSession>(
                It.Is<string>(k => k.StartsWith("session:")),
                It.IsAny<CancellationToken>()))
            .ReturnsAsync(() =>
            {
                callCount++;
                if (callCount == 1)
                {
                    return new DistributedSession
                    {
                        SessionId = "expired-session",
                        UserId = Guid.NewGuid(),
                        ExpiresAt = DateTime.UtcNow.AddMinutes(-10) // 已过期
                    };
                }
                return null; // 第二次返回 null，中断 Destroy→Get 递归
            });

        _cacheMock.Setup(c => c.RemoveAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.GetSessionAsync("expired-session");

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task GetSessionAsync_Valid_ReturnsSession()
    {
        // Arrange
        var session = new DistributedSession
        {
            SessionId = "valid-session",
            UserId = Guid.NewGuid(),
            ExpiresAt = DateTime.UtcNow.AddHours(1)
        };
        _cacheMock.Setup(c => c.GetAsync<DistributedSession>(
                It.Is<string>(k => k.Contains("valid-session")),
                It.IsAny<CancellationToken>()))
            .ReturnsAsync(session);

        // Act
        var result = await _service.GetSessionAsync("valid-session");

        // Assert
        result.Should().NotBeNull();
        result!.SessionId.Should().Be("valid-session");
    }

    #endregion

    #region DestroySessionAsync

    [Fact]
    public async Task DestroySessionAsync_NotFound_ReturnsFalse()
    {
        // Arrange
        _cacheMock.Setup(c => c.GetAsync<DistributedSession>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((DistributedSession?)null);

        // Act
        var result = await _service.DestroySessionAsync("nonexistent");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task DestroySessionAsync_Valid_RemovesCacheAndReturnsTrue()
    {
        // Arrange
        var session = new DistributedSession
        {
            SessionId = "to-destroy",
            UserId = Guid.NewGuid(),
            ExpiresAt = DateTime.UtcNow.AddHours(1)
        };
        _cacheMock.Setup(c => c.GetAsync<DistributedSession>(
                It.Is<string>(k => k.Contains("to-destroy")),
                It.IsAny<CancellationToken>()))
            .ReturnsAsync(session);
        _cacheMock.Setup(c => c.RemoveAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);
        _cacheMock.Setup(c => c.GetAsync<List<string>>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<string> { "to-destroy" });
        _cacheMock.Setup(c => c.SetAsync(It.IsAny<string>(), It.IsAny<List<string>>(), It.IsAny<TimeSpan>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.DestroySessionAsync("to-destroy");

        // Assert
        result.Should().BeTrue();
        _cacheMock.Verify(c => c.RemoveAsync(
            It.Is<string>(k => k.Contains("to-destroy")),
            It.IsAny<CancellationToken>()), Times.AtLeastOnce);
    }

    #endregion

    #region RefreshSessionAsync

    [Fact]
    public async Task RefreshSessionAsync_NotFound_ReturnsFalse()
    {
        // Arrange
        _cacheMock.Setup(c => c.GetAsync<DistributedSession>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((DistributedSession?)null);

        // Act
        var result = await _service.RefreshSessionAsync("nonexistent");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task RefreshSessionAsync_Valid_ReturnsTrue()
    {
        // Arrange：会话仍在有效期内
        var session = new DistributedSession
        {
            SessionId = "active-session",
            UserId = Guid.NewGuid(),
            ExpiresAt = DateTime.UtcNow.AddMinutes(20), // 剩余 20 分钟
            LastActiveAt = DateTime.UtcNow.AddMinutes(-5)
        };
        _cacheMock.Setup(c => c.GetAsync<DistributedSession>(
                It.Is<string>(k => k.Contains("active-session")),
                It.IsAny<CancellationToken>()))
            .ReturnsAsync(session);
        _cacheMock.Setup(c => c.SetAsync(It.IsAny<string>(), It.IsAny<DistributedSession>(), It.IsAny<TimeSpan>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.RefreshSessionAsync("active-session");

        // Assert
        result.Should().BeTrue();
    }

    #endregion

    #region SetSessionDataAsync

    [Fact]
    public async Task SetSessionDataAsync_SessionNotFound_ThrowsBusinessException()
    {
        // Arrange
        _cacheMock.Setup(c => c.GetAsync<DistributedSession>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((DistributedSession?)null);

        // Act & Assert
        await _service.Invoking(s => s.SetSessionDataAsync("nonexistent", "key", "value"))
            .Should().ThrowAsync<BusinessException>()
            .WithMessage("*不存在*");
    }

    #endregion

    #region GetUserSessionCountAsync

    [Fact]
    public async Task GetUserSessionCountAsync_NoSessions_ReturnsZero()
    {
        // Arrange
        _cacheMock.Setup(c => c.GetAsync<List<string>>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((List<string>?)null);

        // Act
        var result = await _service.GetUserSessionCountAsync(Guid.NewGuid());

        // Assert
        result.Should().Be(0);
    }

    #endregion

    #region DistributedSession 实体

    [Fact]
    public void DistributedSession_IsExpired_FutureDate_ReturnsFalse()
    {
        var session = new DistributedSession
        {
            ExpiresAt = DateTime.UtcNow.AddHours(1)
        };
        session.IsExpired.Should().BeFalse();
    }

    [Fact]
    public void DistributedSession_IsExpired_PastDate_ReturnsTrue()
    {
        var session = new DistributedSession
        {
            ExpiresAt = DateTime.UtcNow.AddMinutes(-1)
        };
        session.IsExpired.Should().BeTrue();
    }

    #endregion

    #region DistributedSessionOptions 默认值

    [Fact]
    public void DistributedSessionOptions_DefaultValues()
    {
        var opts = new DistributedSessionOptions();
        opts.DefaultTimeoutMinutes.Should().Be(30);
        opts.SlidingWindowMinutes.Should().Be(10);
        opts.MaxSessionsPerUser.Should().Be(5);
        opts.KickOldestOnLimit.Should().BeTrue();
        opts.MaxSessionLifetimeDays.Should().Be(30);
    }

    #endregion
}
