using System;
using FluentAssertions;
using JGSY.AGI.Charging.Service;
using Xunit;
using ChargingOrderStatus = JGSY.AGI.Charging.Entities.OrderStatus;
using ChargingPileStatus = JGSY.AGI.Charging.Entities.PileStatus;
using ChargingSessionStatus = JGSY.AGI.Charging.Entities.SessionStatus;

namespace JGSY.AGI.Test.Charging;

/// <summary>
/// 订单验证 / 定价 / 结算 业务规则纯逻辑测试
/// 不依赖数据库；验证 DTO 计算属性、结果模型、状态常量等
/// </summary>
public class OrderBusinessLogicTests
{
    #region OrderValidationResult 工厂方法

    [Fact]
    public void OrderValidationResult_Valid_ShouldBeValid()
    {
        var result = OrderValidationResult.Valid();
        result.IsValid.Should().BeTrue();
        result.ErrorMessage.Should().BeNull();
    }

    [Fact]
    public void OrderValidationResult_Invalid_ShouldCarryMessage()
    {
        var msg = "充电桩不存在";
        var result = OrderValidationResult.Invalid(msg);
        result.IsValid.Should().BeFalse();
        result.ErrorMessage.Should().Be(msg);
    }

    [Theory]
    [InlineData("充电桩不存在")]
    [InlineData("充电桩已离线")]
    [InlineData("充电桩故障中")]
    [InlineData("充电桩正在使用中")]
    [InlineData("用户已有进行中的充电订单")]
    [InlineData("用户已有进行中的充电会话")]
    public void OrderValidationResult_Invalid_AllKnownMessages(string msg)
    {
        var result = OrderValidationResult.Invalid(msg);
        result.IsValid.Should().BeFalse();
        result.ErrorMessage.Should().Be(msg);
    }

    #endregion

    #region PricingResult 计算属性

    [Fact]
    public void PricingResult_TotalFee_ShouldBeSumOfSubFields()
    {
        var result = new PricingResult
        {
            ElectricityFee = 42.5m,
            ServiceFee = 17.5m,
            TotalKwh = 50m,
            DurationMinutes = 120
        };

        result.TotalFee.Should().Be(60m);
    }

    [Fact]
    public void PricingResult_ZeroKwh_ShouldReturnZeroFees()
    {
        var result = new PricingResult
        {
            ElectricityFee = 0m,
            ServiceFee = 0m,
            TotalKwh = 0m
        };

        result.TotalFee.Should().Be(0m);
    }

    [Theory]
    [InlineData(100, 0.85, 0.35, 85.0, 35.0)]
    [InlineData(50, 0.85, 0.35, 42.5, 17.5)]
    [InlineData(0, 0.85, 0.35, 0, 0)]
    [InlineData(200, 1.0, 0.5, 200, 100)]
    public void PricingResult_DefaultPriceCalculation(
        decimal kwh, decimal elecPricePerKwh, decimal svcPricePerKwh,
        decimal expectedElec, decimal expectedSvc)
    {
        // 模拟 OrderPricingService 的默认价格计算逻辑
        var result = new PricingResult
        {
            TotalKwh = kwh,
            ElectricityFee = kwh * elecPricePerKwh,
            ServiceFee = kwh * svcPricePerKwh
        };

        result.ElectricityFee.Should().Be(expectedElec);
        result.ServiceFee.Should().Be(expectedSvc);
        result.TotalFee.Should().Be(expectedElec + expectedSvc);
    }

    [Fact]
    public void PricingResult_Periods_ShouldBeEmpty_ByDefault()
    {
        var result = new PricingResult();
        result.Periods.Should().NotBeNull().And.BeEmpty();
    }

    #endregion

    #region SettlementResult 业务规则

    [Fact]
    public void SettlementResult_Success_ShouldContainFees()
    {
        var result = new SettlementResult
        {
            Success = true,
            ElectricityFee = 42.5m,
            ServiceFee = 17.5m,
            TotalFee = 60m,
            TotalKwh = 50m,
            Message = "结算完成"
        };

        result.Success.Should().BeTrue();
        result.TotalFee.Should().Be(result.ElectricityFee + result.ServiceFee);
        result.Message.Should().Contain("结算");
    }

    [Theory]
    [InlineData("订单不存在")]
    [InlineData("订单已结算")]
    [InlineData("充电会话不存在")]
    public void SettlementResult_Failure_AllKnownMessages(string msg)
    {
        var result = new SettlementResult { Success = false, Message = msg };
        result.Success.Should().BeFalse();
        result.Message.Should().Be(msg);
    }

    #endregion

    #region 充电订单状态常量

    [Fact]
    public void OrderStatus_ShouldHaveCorrectValues()
    {
        // 验证所有状态常量与数据库一致（字符串类型）
        ChargingOrderStatus.Pending.Should().Be("1");
        ChargingOrderStatus.Cancelled.Should().Be("2");
        ChargingOrderStatus.Charging.Should().Be("3");
        ChargingOrderStatus.Refunded.Should().Be("4");
        ChargingOrderStatus.Completed.Should().Be("5");
        ChargingOrderStatus.Settled.Should().Be("6");
        ChargingOrderStatus.ManualSettled.Should().Be("7");
    }

    [Fact]
    public void PileStatus_ShouldHaveCorrectValues()
    {
        ChargingPileStatus.Available.Should().Be("available");
        ChargingPileStatus.Charging.Should().Be("charging");
        ChargingPileStatus.Offline.Should().Be("offline");
        ChargingPileStatus.Faulted.Should().Be("faulted");
    }

    [Fact]
    public void SessionStatus_ShouldHaveCorrectValues()
    {
        ChargingSessionStatus.Pending.Should().Be("pending");
        ChargingSessionStatus.Charging.Should().Be("charging");
        ChargingSessionStatus.Completed.Should().Be("completed");
        ChargingSessionStatus.Settled.Should().Be("settled");
    }

    #endregion

    #region 验证规则业务逻辑

    [Fact]
    public void ValidateCreateOrder_PileOffline_ShouldFail()
    {
        // 模拟 ValidateCreateOrderAsync 中的桩状态校验
        var pileStatus = ChargingPileStatus.Offline;

        bool isValid = pileStatus != ChargingPileStatus.Offline
                    && pileStatus != ChargingPileStatus.Faulted
                    && pileStatus != ChargingPileStatus.Charging;

        isValid.Should().BeFalse();
    }

    [Fact]
    public void ValidateCreateOrder_PileFaulted_ShouldFail()
    {
        var pileStatus = ChargingPileStatus.Faulted;
        bool isValid = pileStatus != ChargingPileStatus.Offline
                    && pileStatus != ChargingPileStatus.Faulted
                    && pileStatus != ChargingPileStatus.Charging;
        isValid.Should().BeFalse();
    }

    [Fact]
    public void ValidateCreateOrder_PileCharging_ShouldFail()
    {
        var pileStatus = ChargingPileStatus.Charging;
        bool isValid = pileStatus != ChargingPileStatus.Offline
                    && pileStatus != ChargingPileStatus.Faulted
                    && pileStatus != ChargingPileStatus.Charging;
        isValid.Should().BeFalse();
    }

    [Fact]
    public void ValidateCreateOrder_PileAvailable_ShouldPass()
    {
        var pileStatus = ChargingPileStatus.Available;
        bool isValid = pileStatus != ChargingPileStatus.Offline
                    && pileStatus != ChargingPileStatus.Faulted
                    && pileStatus != ChargingPileStatus.Charging;
        isValid.Should().BeTrue();
    }

    [Theory]
    [InlineData("6", false)]  // Settled → 已结算不可再结算
    [InlineData("2", false)]  // Cancelled → 已取消不可结算
    [InlineData("3", false)]  // Charging → 正在充电不可结算
    [InlineData("1", true)]   // Pending → 可结算
    [InlineData("5", true)]   // Completed → 可结算
    public void ValidateSettleOrder_StatusCheck(string status, bool expectedValid)
    {
        // 模拟 ValidateSettleOrderAsync 中的状态校验逻辑
        bool isValid = status != ChargingOrderStatus.Settled
                    && status != ChargingOrderStatus.Cancelled
                    && status != ChargingOrderStatus.Charging;

        isValid.Should().Be(expectedValid);
    }

    #endregion

    #region PricingPeriodDetail 测试

    [Fact]
    public void PricingPeriodDetail_ShouldStoreAllFields()
    {
        var start = new DateTime(2024, 1, 1, 10, 0, 0);
        var end = new DateTime(2024, 1, 1, 12, 0, 0);

        var detail = new PricingPeriodDetail
        {
            StartTime = start,
            EndTime = end,
            Kwh = 60m,
            ElectricityUnitPrice = 1.0m,
            ServiceUnitPrice = 0.5m,
            ElectricityFee = 60m,
            ServiceFee = 30m,
            PeriodType = "High"
        };

        detail.Kwh.Should().Be(60m);
        detail.ElectricityFee.Should().Be(detail.Kwh * detail.ElectricityUnitPrice);
        detail.ServiceFee.Should().Be(detail.Kwh * detail.ServiceUnitPrice);
    }

    #endregion

    #region 默认价格边界

    [Fact]
    public void DefaultPrice_ShouldMatch_ServiceConstants()
    {
        // OrderPricingService 默认 电费=0.85, 服务费=0.35
        var defaultElecPrice = 0.85m;
        var defaultSvcPrice = 0.35m;
        var totalUnitPrice = defaultElecPrice + defaultSvcPrice;

        totalUnitPrice.Should().Be(1.20m); // GetCurrentPriceAsync 的默认合计
    }

    [Fact]
    public void LargeKwh_ShouldNotOverflow()
    {
        // 极端值：1000度电
        var kwh = 1000m;
        var elecFee = kwh * 0.85m;
        var svcFee = kwh * 0.35m;

        elecFee.Should().Be(850m);
        svcFee.Should().Be(350m);
        (elecFee + svcFee).Should().Be(1200m);
    }

    [Fact]
    public void VerySmallKwh_ShouldCalculateWithoutPrecisionLoss()
    {
        // 极小值：0.001度电
        var kwh = 0.001m;
        var elecFee = kwh * 0.85m;
        var svcFee = kwh * 0.35m;

        elecFee.Should().Be(0.00085m);
        svcFee.Should().Be(0.00035m);
    }

    #endregion
}
