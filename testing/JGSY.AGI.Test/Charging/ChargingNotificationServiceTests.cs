using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;
using JGSY.AGI.Common.Core.Service;
using JGSY.AGI.Charging.Entities;
using JGSY.AGI.Charging.Service;

namespace JGSY.AGI.Test.Charging;

/// <summary>
/// 充电通知服务单元测试（通知委托 + 异常降级）
/// </summary>
public class ChargingNotificationServiceTests
{
    private readonly Mock<INotificationService> _notificationService;
    private readonly ChargingNotificationService _service;

    private static readonly Guid TestUserId = Guid.NewGuid();
    private static readonly Guid TestTenantId = Guid.NewGuid();

    public ChargingNotificationServiceTests()
    {
        _notificationService = new Mock<INotificationService>();
        _service = new ChargingNotificationService(
            _notificationService.Object,
            NullLogger<ChargingNotificationService>.Instance);
    }

    private ChargingReservation CreateReservation() => new()
    {
        UserId = TestUserId,
        TenantId = TestTenantId,
        ReservationNo = "RSV20250101001",
        StationName = "测试充电站",
        PileCode = "DC-001",
        PortNumber = 1,
        StartTime = DateTime.Now.AddHours(1),
        EndTime = DateTime.Now.AddHours(2)
    };

    private ChargingOrder CreateOrder() => new()
    {
        UserId = TestUserId,
        TenantId = TestTenantId,
        OrderNumber = "ORD20250101001",
        PileCode = "DC-001",
        StartTime = DateTime.Now.AddHours(-1),
        EndTime = DateTime.Now,
        ConsumePower = 35.5m,
        Price = 52.75m
    };

    #region SendReservationReminderAsync 预约提醒

    [Fact]
    public async Task SendReservationReminder_Success_ReturnsTrue()
    {
        _notificationService.Setup(n => n.SendAsync(It.IsAny<SendNotificationRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new SendNotificationResponse { Success = true });

        var result = await _service.SendReservationReminderAsync(CreateReservation());
        result.Should().BeTrue();
    }

    [Fact]
    public async Task SendReservationReminder_Failure_ReturnsFalse()
    {
        _notificationService.Setup(n => n.SendAsync(It.IsAny<SendNotificationRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new SendNotificationResponse { Success = false });

        var result = await _service.SendReservationReminderAsync(CreateReservation());
        result.Should().BeFalse();
    }

    [Fact]
    public async Task SendReservationReminder_Exception_ReturnsFalse()
    {
        _notificationService.Setup(n => n.SendAsync(It.IsAny<SendNotificationRequest>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new Exception("网络超时"));

        var result = await _service.SendReservationReminderAsync(CreateReservation());
        result.Should().BeFalse();
    }

    [Fact]
    public async Task SendReservationReminder_SetsCorrectTemplateId()
    {
        SendNotificationRequest? captured = null;
        _notificationService.Setup(n => n.SendAsync(It.IsAny<SendNotificationRequest>(), It.IsAny<CancellationToken>()))
            .Callback<SendNotificationRequest, CancellationToken>((req, _) => captured = req)
            .ReturnsAsync(new SendNotificationResponse { Success = true });

        await _service.SendReservationReminderAsync(CreateReservation());

        captured.Should().NotBeNull();
        captured!.TemplateId.Should().Be("RESERVATION_REMINDER");
        captured.UserId.Should().Be(TestUserId);
        captured.TenantId.Should().Be(TestTenantId);
    }

    #endregion

    #region SendReservationConfirmedAsync 预约确认

    [Fact]
    public async Task SendReservationConfirmed_Success_ReturnsTrue()
    {
        _notificationService.Setup(n => n.SendAsync(It.IsAny<SendNotificationRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new SendNotificationResponse { Success = true });

        var result = await _service.SendReservationConfirmedAsync(CreateReservation());
        result.Should().BeTrue();
    }

    [Fact]
    public async Task SendReservationConfirmed_Exception_ReturnsFalse()
    {
        _notificationService.Setup(n => n.SendAsync(It.IsAny<SendNotificationRequest>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new InvalidOperationException("服务不可用"));

        var result = await _service.SendReservationConfirmedAsync(CreateReservation());
        result.Should().BeFalse();
    }

    #endregion

    #region SendReservationCancelledAsync 预约取消

    [Fact]
    public async Task SendReservationCancelled_IncludesReason()
    {
        SendNotificationRequest? captured = null;
        _notificationService.Setup(n => n.SendAsync(It.IsAny<SendNotificationRequest>(), It.IsAny<CancellationToken>()))
            .Callback<SendNotificationRequest, CancellationToken>((req, _) => captured = req)
            .ReturnsAsync(new SendNotificationResponse { Success = true });

        await _service.SendReservationCancelledAsync(CreateReservation(), "用户主动取消");

        captured!.TemplateId.Should().Be("RESERVATION_CANCELLED");
        captured.TemplateParams.Should().ContainKey("reason");
        captured.TemplateParams!["reason"].Should().Be("用户主动取消");
    }

    #endregion

    #region SendReservationExpiredAsync 预约过期

    [Fact]
    public async Task SendReservationExpired_SetsCorrectTemplate()
    {
        SendNotificationRequest? captured = null;
        _notificationService.Setup(n => n.SendAsync(It.IsAny<SendNotificationRequest>(), It.IsAny<CancellationToken>()))
            .Callback<SendNotificationRequest, CancellationToken>((req, _) => captured = req)
            .ReturnsAsync(new SendNotificationResponse { Success = true });

        await _service.SendReservationExpiredAsync(CreateReservation());

        captured!.TemplateId.Should().Be("RESERVATION_EXPIRED");
    }

    #endregion

    #region SendChargingStartedAsync 充电开始

    [Fact]
    public async Task SendChargingStarted_DelegatesToSpecificMethod()
    {
        _notificationService.Setup(n => n.SendChargingStartedAsync(
                TestUserId, TestTenantId, "DC-001", It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new SendNotificationResponse { Success = true });

        var result = await _service.SendChargingStartedAsync(CreateOrder());
        result.Should().BeTrue();
        _notificationService.Verify(n => n.SendChargingStartedAsync(
            TestUserId, TestTenantId, "DC-001", It.IsAny<string>(), It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task SendChargingStarted_Exception_ReturnsFalse()
    {
        _notificationService.Setup(n => n.SendChargingStartedAsync(
                It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<string>(), It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new Exception("发送失败"));

        var result = await _service.SendChargingStartedAsync(CreateOrder());
        result.Should().BeFalse();
    }

    #endregion

    #region SendChargingCompletedAsync 充电完成

    [Fact]
    public async Task SendChargingCompleted_CalculatesDuration()
    {
        var order = CreateOrder();
        order.StartTime = new DateTime(2025, 1, 6, 10, 0, 0);
        order.EndTime = new DateTime(2025, 1, 6, 11, 30, 0);

        _notificationService.Setup(n => n.SendChargingCompletedAsync(
                TestUserId, TestTenantId, "DC-001",
                90m, // 90分钟
                35.5m, // 电量
                52.75m, // 金额
                It.IsAny<CancellationToken>()))
            .ReturnsAsync(new SendNotificationResponse { Success = true });

        var result = await _service.SendChargingCompletedAsync(order);
        result.Should().BeTrue();
    }

    [Fact]
    public async Task SendChargingCompleted_NullTimes_DurationIsZero()
    {
        var order = CreateOrder();
        order.StartTime = null;
        order.EndTime = null;

        _notificationService.Setup(n => n.SendChargingCompletedAsync(
                It.IsAny<Guid>(), It.IsAny<Guid>(), It.IsAny<string>(),
                0m, // 无法计算时长
                It.IsAny<decimal>(), It.IsAny<decimal>(),
                It.IsAny<CancellationToken>()))
            .ReturnsAsync(new SendNotificationResponse { Success = true });

        var result = await _service.SendChargingCompletedAsync(order);
        result.Should().BeTrue();
    }

    #endregion

    #region SendChargingErrorAsync 充电异常

    [Fact]
    public async Task SendChargingError_PassesErrorMessage()
    {
        _notificationService.Setup(n => n.SendChargingErrorAsync(
                TestUserId, TestTenantId, "DC-001", "过温保护", It.IsAny<CancellationToken>()))
            .ReturnsAsync(new SendNotificationResponse { Success = true });

        var result = await _service.SendChargingErrorAsync(CreateOrder(), "过温保护");
        result.Should().BeTrue();
        _notificationService.Verify(n => n.SendChargingErrorAsync(
            TestUserId, TestTenantId, "DC-001", "过温保护", It.IsAny<CancellationToken>()), Times.Once);
    }

    #endregion

    #region SendRefundSuccessAsync 退款成功

    [Fact]
    public async Task SendRefundSuccess_SetsCorrectTemplate()
    {
        SendNotificationRequest? captured = null;
        _notificationService.Setup(n => n.SendAsync(It.IsAny<SendNotificationRequest>(), It.IsAny<CancellationToken>()))
            .Callback<SendNotificationRequest, CancellationToken>((req, _) => captured = req)
            .ReturnsAsync(new SendNotificationResponse { Success = true });

        var result = await _service.SendRefundSuccessAsync(TestUserId, TestTenantId, "ORD001", 100.50m);
        result.Should().BeTrue();
        captured!.TemplateId.Should().Be("REFUND_SUCCESS");
        captured.TemplateParams!["amount"].Should().Be("100.50");
    }

    #endregion

    #region SendLowBalanceAlertAsync 低余额提醒

    [Fact]
    public async Task SendLowBalanceAlert_SetsCorrectTemplate()
    {
        SendNotificationRequest? captured = null;
        _notificationService.Setup(n => n.SendAsync(It.IsAny<SendNotificationRequest>(), It.IsAny<CancellationToken>()))
            .Callback<SendNotificationRequest, CancellationToken>((req, _) => captured = req)
            .ReturnsAsync(new SendNotificationResponse { Success = true });

        var result = await _service.SendLowBalanceAlertAsync(TestUserId, TestTenantId, 5.00m);
        result.Should().BeTrue();
        captured!.TemplateId.Should().Be("LOW_BALANCE_ALERT");
        captured.TemplateParams!["balance"].Should().Be("5.00");
    }

    [Fact]
    public async Task SendLowBalanceAlert_Exception_ReturnsFalse()
    {
        _notificationService.Setup(n => n.SendAsync(It.IsAny<SendNotificationRequest>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new Exception("Redis连接失败"));

        var result = await _service.SendLowBalanceAlertAsync(TestUserId, TestTenantId, 5.00m);
        result.Should().BeFalse();
    }

    #endregion
}
