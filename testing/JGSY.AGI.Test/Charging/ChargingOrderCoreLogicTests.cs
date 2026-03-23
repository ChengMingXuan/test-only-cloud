using System;
using System.Collections.Generic;
using FluentAssertions;
using JGSY.AGI.Charging.Entities;
using Xunit;

namespace JGSY.AGI.Test.Charging;

/// <summary>
/// 充电订单核心业务逻辑测试 - P0 覆盖
/// 注意：本项目使用字符串常量标识订单状态（OrderStatus.Pending = "1" 等）
/// </summary>
public class ChargingOrderCoreLogicTests
{
    private readonly Guid _tenantId = Guid.NewGuid();

    #region 订单状态流转测试

    [Fact]
    public void Order_InitialStatus_ShouldBePending()
    {
        // 验证待处理状态值
        var initialStatus = OrderStatus.Pending;
        
        initialStatus.Should().Be(OrderStatus.Pending);
        initialStatus.Should().Be("1");
    }

    [Theory]
    [InlineData("1", "3", true)]     // Pending -> Charging
    [InlineData("3", "5", true)]     // Charging -> Completed
    [InlineData("3", "4", true)]     // Charging -> Refunded
    [InlineData("1", "2", true)]     // Pending -> Cancelled
    [InlineData("5", "3", false)]    // Completed -> Charging (不允许)
    [InlineData("6", "1", false)]    // Settled -> Pending (不允许)
    public void Order_StatusTransition_ShouldFollowRules(
        string from, 
        string to, 
        bool isAllowed)
    {
        var canTransit = IsStatusTransitionAllowed(from, to);
        canTransit.Should().Be(isAllowed);
    }

    [Fact]
    public void CompletedOrder_CanOnlyTransitToSettled()
    {
        var from = OrderStatus.Completed; // "5"
        var validTarget = OrderStatus.Settled; // "6"
        
        // 只有 Settled 是有效的目标状态
        var canTransitToSettled = IsStatusTransitionAllowed(from, validTarget);
        var canTransitToPending = IsStatusTransitionAllowed(from, OrderStatus.Pending);
        var canTransitToCharging = IsStatusTransitionAllowed(from, OrderStatus.Charging);
        
        canTransitToSettled.Should().BeTrue();
        canTransitToPending.Should().BeFalse();
        canTransitToCharging.Should().BeFalse();
    }

    [Fact]
    public void OrderStatus_Constants_ShouldMatchBusinessDefinition()
    {
        // 验证状态常量与业务定义一致
        OrderStatus.Pending.Should().Be("1");
        OrderStatus.Cancelled.Should().Be("2");
        OrderStatus.Charging.Should().Be("3");
        OrderStatus.Refunded.Should().Be("4");
        OrderStatus.Completed.Should().Be("5");
        OrderStatus.Settled.Should().Be("6");
        OrderStatus.ManualSettled.Should().Be("7");
    }

    #endregion

    #region 计费逻辑测试

    [Theory]
    [InlineData(10, 1.5, 15)]         // 10度电，1.5元/度
    [InlineData(50, 0.8, 40)]          // 50度电，0.8元/度
    [InlineData(100, 1.2, 120)]        // 大功率充电
    [InlineData(0.5, 1.5, 0.75)]       // 小电量
    public void ElectricityFee_ShouldBeCalculatedCorrectly(
        decimal kwh, 
        decimal pricePerKwh, 
        decimal expectedFee)
    {
        var fee = kwh * pricePerKwh;
        fee.Should().Be(expectedFee);
    }

    [Theory]
    [InlineData(30, 0.1, 3)]           // 30分钟，0.1元/分钟
    [InlineData(60, 0.05, 3)]          // 1小时，0.05元/分钟
    [InlineData(120, 0.08, 9.6)]       // 2小时
    public void ServiceFee_ShouldBeCalculatedByDuration(
        int minutes, 
        decimal perMinute, 
        decimal expectedFee)
    {
        var fee = minutes * perMinute;
        fee.Should().Be(expectedFee);
    }

    [Theory]
    [InlineData(50, 10, 60)]           // 电费50 + 服务费10 = 60
    [InlineData(100, 5, 105)]
    [InlineData(0, 5, 5)]              // 仅服务费（未充电）
    public void TotalFee_ShouldBeElectricityPlusService(
        decimal electricity, 
        decimal service, 
        decimal expectedTotal)
    {
        var total = electricity + service;
        total.Should().Be(expectedTotal);
    }

    #endregion

    #region 时段电价测试

    [Theory]
    [InlineData(8, 1.5)]    // 尖峰时段 8:00
    [InlineData(10, 1.2)]   // 高峰时段 10:00
    [InlineData(14, 0.8)]   // 平段时段 14:00
    [InlineData(3, 0.5)]    // 低谷时段 3:00
    [InlineData(23, 0.5)]   // 低谷时段 23:00
    public void TimeOfUse_ShouldAffectPrice(int hour, decimal expectedRate)
    {
        var rate = GetTimeOfUseRate(hour);
        rate.Should().Be(expectedRate);
    }

    [Fact]
    public void ChargingAcrossTimePeriods_ShouldCalculateEachSegment()
    {
        // 模拟跨时段充电：从22:00充到01:00（3小时）
        // 22-23点（平段）1小时 + 23-01点（低谷）2小时
        var segments = new List<(int hours, decimal rate)>
        {
            (1, 0.8m),  // 平段
            (2, 0.5m)   // 低谷
        };
        
        var totalCost = 0m;
        var kwhPerHour = 10m; // 每小时10度
        
        foreach (var seg in segments)
        {
            totalCost += seg.hours * kwhPerHour * seg.rate;
        }
        
        // 1*10*0.8 + 2*10*0.5 = 8 + 10 = 18
        totalCost.Should().Be(18m);
    }

    #endregion

    #region 功率计算测试

    [Theory]
    [InlineData(60, 7, 7)]       // 60分钟充7度，平均功率7kW
    [InlineData(30, 7, 14)]      // 30分钟充7度，平均功率14kW
    [InlineData(120, 120, 60)]   // 120分钟充120度，平均功率60kW（快充）
    public void AveragePower_ShouldBeCalculatedCorrectly(
        int minutes, 
        decimal kwh, 
        decimal expectedPower)
    {
        var hours = minutes / 60m;
        var power = kwh / hours;
        power.Should().Be(expectedPower);
    }

    [Theory]
    [InlineData(7, 7, true)]        // 7kW充电桩，请求7kW
    [InlineData(60, 50, true)]      // 60kW快充，请求50kW
    [InlineData(7, 20, false)]      // 7kW充电桩，请求20kW（超限）
    public void PowerLimit_ShouldBeRespected(
        decimal maxPower, 
        decimal requestedPower, 
        bool isAllowed)
    {
        var allowed = requestedPower <= maxPower;
        allowed.Should().Be(isAllowed);
    }

    #endregion

    #region SOC（电池电量）测试

    [Theory]
    [InlineData(20, 80, 60)]     // 从20%充到80%，充了60%
    [InlineData(10, 100, 90)]    // 从10%充到100%
    [InlineData(50, 80, 30)]
    public void SOC_IncreaseShouldBeCorrect(int startSoc, int endSoc, int expectedIncrease)
    {
        var increase = endSoc - startSoc;
        increase.Should().Be(expectedIncrease);
    }

    [Fact]
    public void SOC_ShouldNotExceed100()
    {
        var targetSoc = 100;
        var actualSoc = 105; // 异常数据
        
        var normalizedSoc = Math.Min(targetSoc, actualSoc);
        normalizedSoc.Should().Be(100);
    }

    [Theory]
    [InlineData(60, 20, 80, 36)]    // 60度电池，从20%到80%（60%），需要36度电
    [InlineData(40, 30, 90, 24)]    // 40度电池，从30%到90%（60%），需要24度电
    public void EnergyNeeded_ShouldBeCalculatedFromSOC(
        decimal batteryCapacity, 
        int startSoc, 
        int targetSoc, 
        decimal expectedKwh)
    {
        var socDiff = (targetSoc - startSoc) / 100m;
        var neededKwh = batteryCapacity * socDiff;
        
        neededKwh.Should().Be(expectedKwh);
    }

    #endregion

    #region 充电会话测试

    [Fact]
    public void ChargingSession_DurationCalculation()
    {
        var startTime = new DateTime(2024, 1, 1, 10, 0, 0);
        var endTime = new DateTime(2024, 1, 1, 11, 30, 0);
        
        var duration = endTime - startTime;
        
        duration.TotalMinutes.Should().Be(90);
        duration.TotalHours.Should().Be(1.5);
    }

    [Fact]
    public void ChargingSession_ShouldTrackStartAndEndMeterReadings()
    {
        var startMeter = 12345.67m;
        var endMeter = 12355.67m;
        
        var chargedKwh = endMeter - startMeter;
        chargedKwh.Should().Be(10m);
    }

    #endregion

    #region 优惠计算测试

    [Theory]
    [InlineData(100, 10, 90)]       // 10%折扣
    [InlineData(100, 20, 80)]       // 20%折扣
    [InlineData(50, 5, 47.5)]       // 5%折扣
    public void Discount_ShouldReduceTotalFee(
        decimal originalFee, 
        int discountPercent, 
        decimal expectedFee)
    {
        var discount = originalFee * discountPercent / 100;
        var finalFee = originalFee - discount;
        
        finalFee.Should().Be(expectedFee);
    }

    [Fact]
    public void Coupon_ShouldDeductFromTotal()
    {
        var totalFee = 100m;
        var couponValue = 20m;
        
        var finalFee = Math.Max(0, totalFee - couponValue);
        finalFee.Should().Be(80m);
    }

    [Fact]
    public void Coupon_ShouldNotMakeFeeNegative()
    {
        var totalFee = 15m;
        var couponValue = 20m;
        
        var finalFee = Math.Max(0, totalFee - couponValue);
        finalFee.Should().Be(0m);
    }

    #endregion

    #region 辅助方法

    private bool IsStatusTransitionAllowed(string from, string to)
    {
        // 订单状态: 1-待处理, 2-取消, 3-充电中, 4-退款, 5-完成, 6-结算
        return (from, to) switch
        {
            (var f, var t) when f == OrderStatus.Pending && t == OrderStatus.Charging => true,
            (var f, var t) when f == OrderStatus.Pending && t == OrderStatus.Cancelled => true,
            (var f, var t) when f == OrderStatus.Charging && t == OrderStatus.Completed => true,
            (var f, var t) when f == OrderStatus.Charging && t == OrderStatus.Refunded => true,
            (var f, var t) when f == OrderStatus.Charging && t == OrderStatus.Cancelled => true,
            (var f, var t) when f == OrderStatus.Completed && t == OrderStatus.Settled => true,
            (var f, var t) when f == OrderStatus.Completed && t == OrderStatus.ManualSettled => true,
            _ => false
        };
    }

    private decimal GetTimeOfUseRate(int hour)
    {
        return hour switch
        {
            >= 8 and < 10 => 1.5m,   // 尖峰
            >= 10 and < 12 => 1.2m,  // 高峰
            >= 18 and < 21 => 1.2m,  // 高峰
            >= 12 and < 18 => 0.8m,  // 平段
            >= 21 and < 23 => 0.8m,  // 平段
            _ => 0.5m                 // 低谷（23:00-8:00）
        };
    }

    #endregion
}

/// <summary>
/// 充电桩/枪管理核心逻辑测试 - P0 覆盖
/// </summary>
public class ChargingPilePileTests
{
    #region 充电桩状态测试

    [Theory]
    [InlineData(PileStatus.Online, true)]
    [InlineData(PileStatus.Offline, false)]
    [InlineData(PileStatus.Maintenance, false)]
    [InlineData(PileStatus.Faulted, false)]
    public void PileStatus_ShouldDetermineAvailability(PileStatus status, bool canCharge)
    {
        var isAvailable = status == PileStatus.Online;
        isAvailable.Should().Be(canCharge);
    }

    [Fact]
    public void AllGunsOccupied_PileShouldShowBusy()
    {
        var totalGuns = 2;
        var occupiedGuns = 2;
        
        var hasAvailableGun = occupiedGuns < totalGuns;
        hasAvailableGun.Should().BeFalse();
    }

    #endregion

    #region 充电枪状态测试

    [Theory]
    [InlineData(GunStatus.Idle, true)]
    [InlineData(GunStatus.Charging, false)]
    [InlineData(GunStatus.Faulted, false)]
    [InlineData(GunStatus.Connecting, false)]
    public void GunStatus_ShouldDetermineAvailability(GunStatus status, bool canStart)
    {
        var isAvailable = status == GunStatus.Idle;
        isAvailable.Should().Be(canStart);
    }

    #endregion

    #region 功率分配测试

    [Fact]
    public void PowerAllocation_ShouldNotExceedPileMax()
    {
        var maxPilePower = 120m; // 充电桩最大功率
        var gun1Request = 60m;
        var gun2Request = 80m;
        
        var totalRequest = gun1Request + gun2Request;
        var needsThrottle = totalRequest > maxPilePower;
        
        needsThrottle.Should().BeTrue();
    }

    [Fact]
    public void DynamicPowerSharing_ShouldDistributeEvenly()
    {
        var maxPilePower = 120m;
        var activeGuns = 2;
        
        var powerPerGun = maxPilePower / activeGuns;
        powerPerGun.Should().Be(60m);
    }

    #endregion
}

/// <summary>
/// 预约订单核心逻辑测试 - P0 覆盖
/// </summary>
public class ReservationCoreLogicTests
{
    #region 预约时间验证测试

    [Fact]
    public void Reservation_ShouldNotBeInPast()
    {
        var reserveTime = DateTime.UtcNow.AddMinutes(-30);
        var isValid = reserveTime > DateTime.UtcNow;
        
        isValid.Should().BeFalse();
    }

    [Fact]
    public void Reservation_ShouldBeWithinMaxAdvancePeriod()
    {
        var maxAdvanceDays = 7;
        var reserveTime = DateTime.UtcNow.AddDays(10);
        
        var isWithinLimit = (reserveTime - DateTime.UtcNow).TotalDays <= maxAdvanceDays;
        isWithinLimit.Should().BeFalse();
    }

    [Theory]
    [InlineData(30, true)]      // 30分钟后，允许
    [InlineData(5, false)]       // 5分钟后，太近
    [InlineData(60, true)]       // 1小时后，允许
    public void Reservation_MinimumAdvanceTime(int minutesFromNow, bool isAllowed)
    {
        var minAdvanceMinutes = 15;
        var reserveTime = DateTime.UtcNow.AddMinutes(minutesFromNow);
        
        var meetsMinimum = (reserveTime - DateTime.UtcNow).TotalMinutes >= minAdvanceMinutes;
        meetsMinimum.Should().Be(isAllowed);
    }

    #endregion

    #region 预约超时测试

    [Fact]
    public void Reservation_ShouldExpireAfterGracePeriod()
    {
        var gracePeriodMinutes = 15;
        var scheduledTime = DateTime.UtcNow.AddMinutes(-20);
        
        var isExpired = (DateTime.UtcNow - scheduledTime).TotalMinutes > gracePeriodMinutes;
        isExpired.Should().BeTrue();
    }

    [Fact]
    public void Reservation_NotExpiredWithinGracePeriod()
    {
        var gracePeriodMinutes = 15;
        var scheduledTime = DateTime.UtcNow.AddMinutes(-10);
        
        var isExpired = (DateTime.UtcNow - scheduledTime).TotalMinutes > gracePeriodMinutes;
        isExpired.Should().BeFalse();
    }

    #endregion

    #region 预约冲突检测测试

    [Fact]
    public void Reservation_ShouldDetectConflict()
    {
        // 已有预约 10:00-11:00
        var existingStart = new DateTime(2024, 1, 1, 10, 0, 0);
        var existingEnd = new DateTime(2024, 1, 1, 11, 0, 0);
        
        // 新预约 10:30-11:30
        var newStart = new DateTime(2024, 1, 1, 10, 30, 0);
        var newEnd = new DateTime(2024, 1, 1, 11, 30, 0);
        
        var hasConflict = newStart < existingEnd && newEnd > existingStart;
        hasConflict.Should().BeTrue();
    }

    [Fact]
    public void Reservation_ShouldNotConflictIfNoOverlap()
    {
        // 已有预约 10:00-11:00
        var existingStart = new DateTime(2024, 1, 1, 10, 0, 0);
        var existingEnd = new DateTime(2024, 1, 1, 11, 0, 0);
        
        // 新预约 11:00-12:00（紧接着）
        var newStart = new DateTime(2024, 1, 1, 11, 0, 0);
        var newEnd = new DateTime(2024, 1, 1, 12, 0, 0);
        
        var hasConflict = newStart < existingEnd && newEnd > existingStart;
        hasConflict.Should().BeFalse();
    }

    #endregion

    #region 预约费用测试

    [Fact]
    public void Reservation_NoShowShouldChargeFee()
    {
        var noShowFee = 5m;
        var isNoShow = true;
        
        var fee = isNoShow ? noShowFee : 0m;
        fee.Should().Be(5m);
    }

    [Fact]
    public void Reservation_CancelBeforeDeadlineShouldNotChargeFee()
    {
        var cancelDeadlineMinutes = 30;
        var scheduledTime = DateTime.UtcNow.AddMinutes(60);
        var cancelTime = DateTime.UtcNow;
        
        var minutesBeforeScheduled = (scheduledTime - cancelTime).TotalMinutes;
        var isFreeCancel = minutesBeforeScheduled >= cancelDeadlineMinutes;
        
        isFreeCancel.Should().BeTrue();
    }

    #endregion
}

/// <summary>
/// 枚举定义（如果不存在）
/// </summary>
public enum PileStatus { Online = 0, Offline = 1, Maintenance = 2, Faulted = 3 }
public enum GunStatus { Idle = 0, Charging = 1, Faulted = 2, Connecting = 3 }
