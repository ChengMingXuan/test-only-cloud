using Xunit;
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using JGSY.AGI.Station.Service;
using JGSY.AGI.Station.Data.Repositories;
using JGSY.AGI.Station.Entities;
using JGSY.AGI.Common.Core.Enums;
using JGSY.AGI.Common.Core.Exceptions;

namespace JGSY.AGI.Test.Station;

/// <summary>
/// 场站活动服务单元测试
/// </summary>
public class StationActivityServiceTests
{
    private readonly Mock<IActivityRepository> _activityRepo = new();
    private readonly StationActivityService _service;

    public StationActivityServiceTests()
    {
        _service = new StationActivityService(
            _activityRepo.Object,
            NullLogger<StationActivityService>.Instance);
    }

    #region 创建活动

    [Fact]
    public async Task CreateActivityAsync_ActiveTimeRange_SetsActiveStatus()
    {
        // Arrange
        var activity = new StationActivity
        {
            ActivityName = "充电优惠",
            StartTime = DateTime.UtcNow.AddHours(-1),
            EndTime = DateTime.UtcNow.AddDays(7),
            Status = (int)ActivityStatus.Draft
        };

        // Act
        var result = await _service.CreateActivityAsync(activity);

        // Assert
        result.Status.Should().Be((int)ActivityStatus.Active);
        _activityRepo.Verify(r => r.InsertActivityAsync(activity), Times.Once);
    }

    [Fact]
    public async Task CreateActivityAsync_EndedTimeRange_SetsEndedStatus()
    {
        // Arrange
        var activity = new StationActivity
        {
            ActivityName = "过期活动",
            StartTime = DateTime.UtcNow.AddDays(-7),
            EndTime = DateTime.UtcNow.AddHours(-1),
            Status = (int)ActivityStatus.Draft
        };

        // Act
        var result = await _service.CreateActivityAsync(activity);

        // Assert
        result.Status.Should().Be((int)ActivityStatus.Ended);
    }

    [Fact]
    public async Task CreateActivityAsync_FutureTimeRange_KeepsOriginalStatus()
    {
        // Arrange
        var activity = new StationActivity
        {
            ActivityName = "未来活动",
            StartTime = DateTime.UtcNow.AddDays(1),
            EndTime = DateTime.UtcNow.AddDays(7),
            Status = (int)ActivityStatus.Draft
        };

        // Act
        var result = await _service.CreateActivityAsync(activity);

        // Assert - 不满足任何条件，保持原始状态
        result.Status.Should().Be((int)ActivityStatus.Draft);
    }

    #endregion

    #region 查询活动

    [Fact]
    public async Task GetActivitiesAsync_DelegatesToRepo()
    {
        // Arrange
        var items = new List<StationActivity> { new() { ActivityName = "A" } };
        _activityRepo.Setup(r => r.GetActivitiesAsync(ActivityStatus.Active, null, null, 1, 10))
            .ReturnsAsync((items, 1));

        // Act
        var (activities, total) = await _service.GetActivitiesAsync(ActivityStatus.Active, pageSize: 10);

        // Assert
        activities.Should().HaveCount(1);
        total.Should().Be(1);
    }

    [Fact]
    public async Task GetActiveActivitiesAsync_DelegatesToRepo()
    {
        // Arrange
        var stationId = Guid.NewGuid();
        var items = new List<StationActivity> { new() { ActivityName = "B" } };
        _activityRepo.Setup(r => r.GetActiveActivitiesAsync(stationId, "All")).ReturnsAsync(items);

        // Act
        var result = await _service.GetActiveActivitiesAsync(stationId);

        // Assert
        result.Should().HaveCount(1);
    }

    #endregion

    #region 参与活动

    [Fact]
    public async Task ParticipateActivityAsync_ActivityNotFound_ReturnsFail()
    {
        // Arrange
        var activityId = Guid.NewGuid();
        _activityRepo.Setup(r => r.GetActivityByIdAsync(activityId)).ReturnsAsync((StationActivity?)null);

        // Act
        var (success, message, discount) = await _service.ParticipateActivityAsync(activityId, "user1");

        // Assert
        success.Should().BeFalse();
        message.Should().Contain("活动不存在");
        discount.Should().Be(0);
    }

    [Fact]
    public async Task ParticipateActivityAsync_NotActive_ReturnsFail()
    {
        // Arrange
        var activityId = Guid.NewGuid();
        var activity = new StationActivity
        {
            ActivityId = activityId,
            Status = (int)ActivityStatus.Ended,
            StartTime = DateTime.UtcNow.AddDays(-7),
            EndTime = DateTime.UtcNow.AddDays(7)
        };
        _activityRepo.Setup(r => r.GetActivityByIdAsync(activityId)).ReturnsAsync(activity);

        // Act
        var (success, message, _) = await _service.ParticipateActivityAsync(activityId, "user1");

        // Assert
        success.Should().BeFalse();
        message.Should().Contain("未开始或已结束");
    }

    [Fact]
    public async Task ParticipateActivityAsync_OutsideTimeRange_ReturnsFail()
    {
        // Arrange
        var activityId = Guid.NewGuid();
        var activity = new StationActivity
        {
            ActivityId = activityId,
            Status = (int)ActivityStatus.Active,
            StartTime = DateTime.UtcNow.AddDays(1), // 未来才开始
            EndTime = DateTime.UtcNow.AddDays(7)
        };
        _activityRepo.Setup(r => r.GetActivityByIdAsync(activityId)).ReturnsAsync(activity);

        // Act
        var (success, message, _) = await _service.ParticipateActivityAsync(activityId, "user1");

        // Assert
        success.Should().BeFalse();
        message.Should().Contain("不在活动时间范围内");
    }

    [Fact]
    public async Task ParticipateActivityAsync_TotalLimitReached_ReturnsFail()
    {
        // Arrange
        var activityId = Guid.NewGuid();
        var activity = new StationActivity
        {
            ActivityId = activityId,
            Status = (int)ActivityStatus.Active,
            StartTime = DateTime.UtcNow.AddHours(-1),
            EndTime = DateTime.UtcNow.AddDays(7),
            TotalLimit = 100,
            CurrentCount = 100
        };
        _activityRepo.Setup(r => r.GetActivityByIdAsync(activityId)).ReturnsAsync(activity);

        // Act
        var (success, message, _) = await _service.ParticipateActivityAsync(activityId, "user1");

        // Assert
        success.Should().BeFalse();
        message.Should().Contain("名额已满");
    }

    [Fact]
    public async Task ParticipateActivityAsync_DailyLimitReached_ReturnsFail()
    {
        // Arrange
        var activityId = Guid.NewGuid();
        var activity = new StationActivity
        {
            ActivityId = activityId,
            Status = (int)ActivityStatus.Active,
            StartTime = DateTime.UtcNow.AddHours(-1),
            EndTime = DateTime.UtcNow.AddDays(7),
            DailyLimit = 3
        };
        _activityRepo.Setup(r => r.GetActivityByIdAsync(activityId)).ReturnsAsync(activity);
        _activityRepo.Setup(r => r.CountUserDailyParticipationsAsync(activityId, "user1")).ReturnsAsync(3);

        // Act
        var (success, message, _) = await _service.ParticipateActivityAsync(activityId, "user1");

        // Assert
        success.Should().BeFalse();
        message.Should().Contain("每日参与上限");
    }

    [Fact]
    public async Task ParticipateActivityAsync_WithDiscountRate_ReturnsDiscountAmount()
    {
        // Arrange
        var activityId = Guid.NewGuid();
        var activity = new StationActivity
        {
            ActivityId = activityId,
            ActivityName = "七折优惠",
            Status = (int)ActivityStatus.Active,
            StartTime = DateTime.UtcNow.AddHours(-1),
            EndTime = DateTime.UtcNow.AddDays(7),
            DiscountRate = 0.7m,
            DiscountAmount = null
        };
        _activityRepo.Setup(r => r.GetActivityByIdAsync(activityId)).ReturnsAsync(activity);

        // Act
        var (success, message, discount) = await _service.ParticipateActivityAsync(activityId, "user1");

        // Assert
        success.Should().BeTrue();
        message.Should().Contain("参与成功");
        discount.Should().Be(0.7m);
        _activityRepo.Verify(r => r.InsertParticipationAsync(It.IsAny<ActivityParticipation>()), Times.Once);
        _activityRepo.Verify(r => r.IncrementActivityCountAsync(activityId), Times.Once);
    }

    [Fact]
    public async Task ParticipateActivityAsync_WithDiscountAmount_ReturnsFixedDiscount()
    {
        // Arrange
        var activityId = Guid.NewGuid();
        var activity = new StationActivity
        {
            ActivityId = activityId,
            ActivityName = "满减优惠",
            Status = (int)ActivityStatus.Active,
            StartTime = DateTime.UtcNow.AddHours(-1),
            EndTime = DateTime.UtcNow.AddDays(7),
            DiscountRate = null,
            DiscountAmount = 10m
        };
        _activityRepo.Setup(r => r.GetActivityByIdAsync(activityId)).ReturnsAsync(activity);

        // Act
        var (success, _, discount) = await _service.ParticipateActivityAsync(activityId, "user1");

        // Assert
        success.Should().BeTrue();
        discount.Should().Be(10m);
    }

    #endregion

    #region 优惠券生成

    [Fact]
    public async Task GenerateCouponsAsync_CreatesCorrectCount()
    {
        // Arrange & Act
        var result = await _service.GenerateCouponsAsync(
            Guid.NewGuid(), "满减券", "FixedAmount", 10m, 5,
            DateTime.UtcNow, DateTime.UtcNow.AddDays(30), 50m);

        // Assert
        result.Should().HaveCount(5);
        result.Should().OnlyContain(c => c.CouponType == "FixedAmount");
        result.Should().OnlyContain(c => c.DiscountValue == 10m);
        result.Should().OnlyContain(c => c.MinAmount == 50m);
        result.Should().OnlyContain(c => c.Status == (int)CouponStatus.Unused);
        result.Should().OnlyContain(c => c.CouponCode.StartsWith("CPN"));

        _activityRepo.Verify(r => r.InsertCouponsAsync(It.Is<List<Coupon>>(l => l.Count == 5)), Times.Once);
    }

    #endregion

    #region 发放优惠券

    [Fact]
    public async Task IssueCouponToUserAsync_CouponNull_ReturnsNull()
    {
        // Arrange
        var couponId = Guid.NewGuid();
        _activityRepo.Setup(r => r.GetCouponByIdAsync(couponId)).ReturnsAsync((Coupon?)null);

        // Act
        var result = await _service.IssueCouponToUserAsync(couponId, "user1");

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task IssueCouponToUserAsync_AlreadyAssigned_ReturnsNull()
    {
        // Arrange
        var couponId = Guid.NewGuid();
        var coupon = new Coupon { CouponId = couponId, UserId = "otherUser" };
        _activityRepo.Setup(r => r.GetCouponByIdAsync(couponId)).ReturnsAsync(coupon);

        // Act
        var result = await _service.IssueCouponToUserAsync(couponId, "user1");

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task IssueCouponToUserAsync_Success_SetsUserId()
    {
        // Arrange
        var couponId = Guid.NewGuid();
        var coupon = new Coupon { CouponId = couponId, UserId = null };
        _activityRepo.Setup(r => r.GetCouponByIdAsync(couponId)).ReturnsAsync(coupon);

        // Act
        var result = await _service.IssueCouponToUserAsync(couponId, "user1");

        // Assert
        result.Should().NotBeNull();
        result!.UserId.Should().Be("user1");
        _activityRepo.Verify(r => r.UpdateCouponAsync(coupon), Times.Once);
    }

    #endregion

    #region 使用优惠券

    [Fact]
    public async Task UseCouponAsync_CouponNull_ReturnsFail()
    {
        // Arrange
        _activityRepo.Setup(r => r.GetCouponByCodeAsync("INVALID")).ReturnsAsync((Coupon?)null);

        // Act
        var (success, message, _) = await _service.UseCouponAsync("INVALID", "user1", "O001", 100m);

        // Assert
        success.Should().BeFalse();
        message.Should().Contain("不存在");
    }

    [Fact]
    public async Task UseCouponAsync_WrongUser_ReturnsFail()
    {
        // Arrange
        var coupon = CreateValidCoupon("CPN001");
        coupon.UserId = "otherUser";
        _activityRepo.Setup(r => r.GetCouponByCodeAsync("CPN001")).ReturnsAsync(coupon);

        // Act
        var (success, message, _) = await _service.UseCouponAsync("CPN001", "user1", "O001", 100m);

        // Assert
        success.Should().BeFalse();
        message.Should().Contain("不属于当前用户");
    }

    [Fact]
    public async Task UseCouponAsync_AlreadyUsed_ReturnsFail()
    {
        // Arrange
        var coupon = CreateValidCoupon("CPN002");
        coupon.Status = (int)CouponStatus.Used;
        _activityRepo.Setup(r => r.GetCouponByCodeAsync("CPN002")).ReturnsAsync(coupon);

        // Act
        var (success, message, _) = await _service.UseCouponAsync("CPN002", "user1", "O001", 100m);

        // Assert
        success.Should().BeFalse();
        message.Should().Contain("已使用或已过期");
    }

    [Fact]
    public async Task UseCouponAsync_Expired_ReturnsFail()
    {
        // Arrange
        var coupon = CreateValidCoupon("CPN003");
        coupon.ValidTo = DateTime.UtcNow.AddDays(-1); // 已过期
        _activityRepo.Setup(r => r.GetCouponByCodeAsync("CPN003")).ReturnsAsync(coupon);

        // Act
        var (success, message, _) = await _service.UseCouponAsync("CPN003", "user1", "O001", 100m);

        // Assert
        success.Should().BeFalse();
        message.Should().Contain("有效期");
    }

    [Fact]
    public async Task UseCouponAsync_BelowMinAmount_ReturnsFail()
    {
        // Arrange
        var coupon = CreateValidCoupon("CPN004");
        coupon.MinAmount = 200m;
        _activityRepo.Setup(r => r.GetCouponByCodeAsync("CPN004")).ReturnsAsync(coupon);

        // Act
        var (success, message, _) = await _service.UseCouponAsync("CPN004", "user1", "O001", 150m);

        // Assert
        success.Should().BeFalse();
        message.Should().Contain("200");
    }

    [Fact]
    public async Task UseCouponAsync_FixedAmount_ReturnsCorrectDiscount()
    {
        // Arrange
        var coupon = CreateValidCoupon("CPN005");
        coupon.CouponType = "FixedAmount";
        coupon.DiscountValue = 20m;
        _activityRepo.Setup(r => r.GetCouponByCodeAsync("CPN005")).ReturnsAsync(coupon);

        // Act
        var (success, _, discount) = await _service.UseCouponAsync("CPN005", "user1", "O001", 100m);

        // Assert
        success.Should().BeTrue();
        discount.Should().Be(20m);
        _activityRepo.Verify(r => r.UpdateCouponAsync(It.Is<Coupon>(
            c => c.Status == (int)CouponStatus.Used && c.UsedOrderNo == "O001")), Times.Once);
    }

    [Fact]
    public async Task UseCouponAsync_Percentage_CalculatesDiscount()
    {
        // Arrange
        var coupon = CreateValidCoupon("CPN006");
        coupon.CouponType = "Percentage";
        coupon.DiscountValue = 10m; // 10%
        _activityRepo.Setup(r => r.GetCouponByCodeAsync("CPN006")).ReturnsAsync(coupon);

        // Act
        var (success, _, discount) = await _service.UseCouponAsync("CPN006", "user1", "O001", 200m);

        // Assert
        success.Should().BeTrue();
        discount.Should().Be(20m); // 200 * (10/100) = 20
    }

    [Fact]
    public async Task UseCouponAsync_FullDiscount_ReturnsDiscountValue()
    {
        // Arrange
        var coupon = CreateValidCoupon("CPN007");
        coupon.CouponType = "FullDiscount";
        coupon.DiscountValue = 50m;
        coupon.MinAmount = 100m;
        _activityRepo.Setup(r => r.GetCouponByCodeAsync("CPN007")).ReturnsAsync(coupon);

        // Act
        var (success, _, discount) = await _service.UseCouponAsync("CPN007", "user1", "O001", 150m);

        // Assert
        success.Should().BeTrue();
        discount.Should().Be(50m);
    }

    [Fact]
    public async Task UseCouponAsync_MaxDiscountCap_LimitsDiscount()
    {
        // Arrange
        var coupon = CreateValidCoupon("CPN008");
        coupon.CouponType = "Percentage";
        coupon.DiscountValue = 50m; // 50%
        coupon.MaxDiscount = 30m;
        _activityRepo.Setup(r => r.GetCouponByCodeAsync("CPN008")).ReturnsAsync(coupon);

        // Act
        var (success, _, discount) = await _service.UseCouponAsync("CPN008", "user1", "O001", 200m);

        // Assert
        success.Should().BeTrue();
        discount.Should().Be(30m); // 200*50%=100, 但 MaxDiscount=30
    }

    #endregion

    #region 用户优惠券查询

    [Fact]
    public async Task GetUserCouponsAsync_DelegatesToRepo()
    {
        // Arrange
        var coupons = new List<Coupon> { new() { CouponName = "券A" } };
        _activityRepo.Setup(r => r.GetUserCouponsAsync("user1", CouponStatus.Unused)).ReturnsAsync(coupons);

        // Act
        var result = await _service.GetUserCouponsAsync("user1", CouponStatus.Unused);

        // Assert
        result.Should().HaveCount(1);
    }

    #endregion

    #region 活动统计

    [Fact]
    public async Task GetActivityStatisticsAsync_ActivityNull_ThrowsBusinessException()
    {
        // Arrange
        var activityId = Guid.NewGuid();
        _activityRepo.Setup(r => r.GetActivityByIdAsync(activityId)).ReturnsAsync((StationActivity?)null);

        // Act & Assert
        var act = () => _service.GetActivityStatisticsAsync(activityId);
        await act.Should().ThrowAsync<BusinessException>().WithMessage("*活动不存在*");
    }

    [Fact]
    public async Task GetActivityStatisticsAsync_WithParticipations_CalculatesCorrectly()
    {
        // Arrange
        var activityId = Guid.NewGuid();
        var activity = new StationActivity { ActivityId = activityId, ActivityName = "测试活动" };
        var participations = new List<ActivityParticipation>
        {
            new() { UserId = "user1", DiscountAmount = 10m },
            new() { UserId = "user1", DiscountAmount = 20m },
            new() { UserId = "user2", DiscountAmount = 15m },
            new() { UserId = "user3", DiscountAmount = 25m }
        };
        _activityRepo.Setup(r => r.GetActivityByIdAsync(activityId)).ReturnsAsync(activity);
        _activityRepo.Setup(r => r.GetParticipationsByActivityAsync(activityId)).ReturnsAsync(participations);

        // Act
        var result = await _service.GetActivityStatisticsAsync(activityId);

        // Assert
        result.ActivityId.Should().Be(activityId);
        result.ActivityName.Should().Be("测试活动");
        result.TotalParticipations.Should().Be(4);
        result.UniqueUsers.Should().Be(3); // user1, user2, user3
        result.TotalDiscountAmount.Should().Be(70m); // 10+20+15+25
        result.AverageDiscountAmount.Should().Be(17.5m); // 70/4
    }

    [Fact]
    public async Task GetActivityStatisticsAsync_NoParticipations_ReturnsZeros()
    {
        // Arrange
        var activityId = Guid.NewGuid();
        var activity = new StationActivity { ActivityId = activityId, ActivityName = "空活动" };
        _activityRepo.Setup(r => r.GetActivityByIdAsync(activityId)).ReturnsAsync(activity);
        _activityRepo.Setup(r => r.GetParticipationsByActivityAsync(activityId)).ReturnsAsync(new List<ActivityParticipation>());

        // Act
        var result = await _service.GetActivityStatisticsAsync(activityId);

        // Assert
        result.TotalParticipations.Should().Be(0);
        result.UniqueUsers.Should().Be(0);
        result.TotalDiscountAmount.Should().Be(0);
        result.AverageDiscountAmount.Should().Be(0); // 0/0 会被 0 : 0 处理
    }

    #endregion

    #region 辅助方法

    private static Coupon CreateValidCoupon(string code)
    {
        return new Coupon
        {
            CouponCode = code,
            CouponName = "测试券",
            CouponType = "FixedAmount",
            DiscountValue = 10m,
            UserId = "user1",
            ValidFrom = DateTime.UtcNow.AddDays(-1),
            ValidTo = DateTime.UtcNow.AddDays(30),
            Status = (int)CouponStatus.Unused,
            MinAmount = null,
            MaxDiscount = null
        };
    }

    #endregion
}
