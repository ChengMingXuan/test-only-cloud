using Xunit;
using Moq;
using FluentAssertions;
using Microsoft.AspNetCore.SignalR;
using Microsoft.Extensions.Logging.Abstractions;
using JGSY.AGI.Analytics.Hubs;
using JGSY.AGI.Analytics.Service;
using JGSY.AGI.Analytics.Entities;

namespace JGSY.AGI.Test.Analytics;

/// <summary>
/// RealtimeBehaviorService 单元测试
/// 覆盖：BroadcastEvent / BroadcastEvents / PushSessionUpdate / PushOnlineCountUpdate / 异常吞没
/// </summary>
public class RealtimeBehaviorServiceTests
{
    private readonly Mock<IHubContext<RealtimeBehaviorHub>> _hubContext = new();
    private readonly Mock<IHubClients> _hubClients = new();
    private readonly Mock<IClientProxy> _clientProxy = new();
    private readonly RealtimeBehaviorService _sut;

    private readonly Guid _tenantId = Guid.NewGuid();
    private readonly Guid _userId = Guid.NewGuid();

    public RealtimeBehaviorServiceTests()
    {
        _hubClients.Setup(c => c.Group(It.IsAny<string>())).Returns(_clientProxy.Object);
        _hubContext.Setup(h => h.Clients).Returns(_hubClients.Object);
        _clientProxy.Setup(p => p.SendCoreAsync(It.IsAny<string>(), It.IsAny<object?[]>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        _sut = new RealtimeBehaviorService(
            _hubContext.Object,
            NullLogger<RealtimeBehaviorService>.Instance);
    }

    // ========== BroadcastEventAsync ==========

    [Fact]
    public async Task BroadcastEventAsync_推送到租户组()
    {
        var trackEvent = CreateTrackEvent();

        await _sut.BroadcastEventAsync(trackEvent);

        // 验证推送到 tenant 组
        _hubClients.Verify(c => c.Group($"tenant_{_tenantId}"), Times.AtLeastOnce);
        _clientProxy.Verify(p => p.SendCoreAsync("ReceiveEvent", It.IsAny<object?[]>(), It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task BroadcastEventAsync_有UserId_推送到用户组()
    {
        var trackEvent = CreateTrackEvent(userId: _userId);

        await _sut.BroadcastEventAsync(trackEvent);

        // 租户组 + 用户组 = 至少2次 Group 调用
        _hubClients.Verify(c => c.Group($"user_{_userId}"), Times.Once);
        _clientProxy.Verify(p => p.SendCoreAsync("ReceiveUserEvent", It.IsAny<object?[]>(), It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task BroadcastEventAsync_有PagePath_推送到页面组()
    {
        var pagePath = "/dashboard";
        var trackEvent = CreateTrackEvent(pagePath: pagePath);
        var expectedGroup = $"page_{Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(pagePath))}";

        await _sut.BroadcastEventAsync(trackEvent);

        _hubClients.Verify(c => c.Group(expectedGroup), Times.Once);
        _clientProxy.Verify(p => p.SendCoreAsync("ReceivePageEvent", It.IsAny<object?[]>(), It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task BroadcastEventAsync_无UserId_不推送用户组()
    {
        var trackEvent = CreateTrackEvent(userId: null);

        await _sut.BroadcastEventAsync(trackEvent);

        _clientProxy.Verify(p => p.SendCoreAsync("ReceiveUserEvent", It.IsAny<object?[]>(), It.IsAny<CancellationToken>()), Times.Never);
    }

    [Fact]
    public async Task BroadcastEventAsync_无PagePath_不推送页面组()
    {
        var trackEvent = CreateTrackEvent(pagePath: null);

        await _sut.BroadcastEventAsync(trackEvent);

        _clientProxy.Verify(p => p.SendCoreAsync("ReceivePageEvent", It.IsAny<object?[]>(), It.IsAny<CancellationToken>()), Times.Never);
    }

    [Fact]
    public async Task BroadcastEventAsync_异常不外抛()
    {
        _clientProxy.Setup(p => p.SendCoreAsync(It.IsAny<string>(), It.IsAny<object?[]>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new InvalidOperationException("SignalR连接断开"));

        var act = () => _sut.BroadcastEventAsync(CreateTrackEvent());

        await act.Should().NotThrowAsync(); // 异常被吞没
    }

    // ========== BroadcastEventsAsync ==========

    [Fact]
    public async Task BroadcastEventsAsync_并行广播多个事件()
    {
        var events = new[]
        {
            CreateTrackEvent(eventName: "event1"),
            CreateTrackEvent(eventName: "event2"),
            CreateTrackEvent(eventName: "event3")
        };

        await _sut.BroadcastEventsAsync(events);

        // 每个事件至少推送到租户组
        _clientProxy.Verify(p => p.SendCoreAsync("ReceiveEvent", It.IsAny<object?[]>(), It.IsAny<CancellationToken>()), Times.Exactly(3));
    }

    [Fact]
    public async Task BroadcastEventsAsync_空集合不抛异常()
    {
        await _sut.BroadcastEventsAsync(Array.Empty<TrackEvent>());
    }

    // ========== PushSessionUpdateAsync ==========

    [Fact]
    public async Task PushSessionUpdateAsync_推送到租户组()
    {
        var session = new UserSession
        {
            Id = Guid.NewGuid(),
            TenantId = _tenantId,
            SessionId = "sess-123",
            UserId = _userId,
            StartTime = DateTime.UtcNow.AddMinutes(-10),
            PageViews = 5,
            EventCount = 12,
            EntryPage = "/home",
            ExitPage = "/about"
        };

        await _sut.PushSessionUpdateAsync(session);

        _hubClients.Verify(c => c.Group($"tenant_{_tenantId}"), Times.Once);
        _clientProxy.Verify(p => p.SendCoreAsync("ReceiveSessionUpdate", It.IsAny<object?[]>(), It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task PushSessionUpdateAsync_异常不外抛()
    {
        _clientProxy.Setup(p => p.SendCoreAsync(It.IsAny<string>(), It.IsAny<object?[]>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new Exception("Send失败"));

        var session = new UserSession
        {
            TenantId = _tenantId,
            SessionId = "sess-err"
        };

        var act = () => _sut.PushSessionUpdateAsync(session);
        await act.Should().NotThrowAsync();
    }

    // ========== PushOnlineCountUpdateAsync ==========

    [Fact]
    public async Task PushOnlineCountUpdateAsync_推送在线数到租户()
    {
        await _sut.PushOnlineCountUpdateAsync(_tenantId, 42);

        _hubClients.Verify(c => c.Group($"tenant_{_tenantId}"), Times.Once);
        _clientProxy.Verify(p => p.SendCoreAsync("ReceiveOnlineCountUpdate", It.IsAny<object?[]>(), It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task PushOnlineCountUpdateAsync_异常不外抛()
    {
        _clientProxy.Setup(p => p.SendCoreAsync(It.IsAny<string>(), It.IsAny<object?[]>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new Exception("Hub断开"));

        var act = () => _sut.PushOnlineCountUpdateAsync(_tenantId, 0);
        await act.Should().NotThrowAsync();
    }

    // ========== 辅助方法 ==========

    private TrackEvent CreateTrackEvent(
        Guid? userId = null,
        string? pagePath = null,
        string eventName = "test_click")
    {
        return new TrackEvent
        {
            Id = Guid.NewGuid(),
            TenantId = _tenantId,
            UserId = userId,
            SessionId = "session-123",
            EventType = TrackEventType.Click,
            EventName = eventName,
            PagePath = pagePath,
            EventTime = DateTime.UtcNow,
            ServerTime = DateTime.UtcNow
        };
    }
}
