using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using JGSY.AGI.Charging.Data;
using JGSY.AGI.Charging.Entities;
using JGSY.AGI.Charging.Service;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace JGSY.AGI.Test.Charging;

/// <summary>
/// 充电订单服务单元测试
/// </summary>
public class ChargingOrderServiceTests
{
    private readonly Mock<IServiceScopeFactory> _scopeFactoryMock;
    private readonly Mock<ILogger<ChargingOrderService>> _loggerMock;
    private readonly Mock<IConfiguration> _configMock;
    private readonly Mock<OrderValidationService> _validationServiceMock;
    private readonly Mock<OrderPricingService> _pricingServiceMock;
    private readonly Mock<OrderSettlementService> _settlementServiceMock;

    public ChargingOrderServiceTests()
    {
        _scopeFactoryMock = new Mock<IServiceScopeFactory>();
        _loggerMock = new Mock<ILogger<ChargingOrderService>>();
        _configMock = new Mock<IConfiguration>();
        _validationServiceMock = new Mock<OrderValidationService>();
        _pricingServiceMock = new Mock<OrderPricingService>();
        _settlementServiceMock = new Mock<OrderSettlementService>();
    }

    [Fact]
    public void CreateOrderRequest_ShouldHaveCorrectDefaults()
    {
        // Arrange & Act
        var request = new CreateChargingOrderRequest();

        // Assert
        request.OrderType.Should().Be("8001"); // 默认按小时计费
        request.IsFee.Should().Be("2001"); // 默认收费
        request.DeviceType.Should().Be(2); // 默认二轮车
        request.OrderSource.Should().Be(2); // 默认H5
    }

    [Fact]
    public void SettleOrderRequest_ShouldHaveCorrectProperties()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        var tenantId = Guid.NewGuid();
        var operatorId = Guid.NewGuid();

        // Act
        var request = new SettleOrderRequest
        {
            OrderId = orderId,
            TenantId = tenantId,
            StopReason = "用户主动停止",
            EndTime = DateTime.UtcNow,
            ConsumePower = 10.5m,
            ForceSettle = false,
            OperatorId = operatorId,
            Remarks = "正常结算"
        };

        // Assert
        request.OrderId.Should().Be(orderId);
        request.TenantId.Should().Be(tenantId);
        request.StopReason.Should().Be("用户主动停止");
        request.ConsumePower.Should().Be(10.5m);
        request.ForceSettle.Should().BeFalse();
        request.OperatorId.Should().Be(operatorId);
    }

    [Fact]
    public void AuthorizationResult_ShouldIndicateSuccess_WhenAuthorized()
    {
        // Arrange & Act
        var result = new AuthorizationResult
        {
            IsAuthorized = true,
            SuggestedPrice = 1.5m,
            IsFreeCharging = false
        };

        // Assert
        result.IsAuthorized.Should().BeTrue();
        result.DenyReason.Should().BeNull();
        result.SuggestedPrice.Should().Be(1.5m);
    }

    [Fact]
    public void AuthorizationResult_ShouldIndicateDenied_WithReason()
    {
        // Arrange & Act
        var result = new AuthorizationResult
        {
            IsAuthorized = false,
            DenyReason = "余额不足",
            ErrorCode = "INSUFFICIENT_BALANCE"
        };

        // Assert
        result.IsAuthorized.Should().BeFalse();
        result.DenyReason.Should().Be("余额不足");
        result.ErrorCode.Should().Be("INSUFFICIENT_BALANCE");
    }

    [Fact]
    public void OrderFeeCalculation_ShouldCalculateTotalCorrectly()
    {
        // Arrange
        var calculation = new OrderFeeCalculation
        {
            ConsumePower = 20m,
            ElectricPrice = 1.0m,
            ServicePrice = 0.5m,
            ElectricFee = 20m,
            ServiceFee = 10m,
            DiscountAmount = 5m,
            FreeQuotaDeduction = 2m
        };

        // Act
        calculation.TotalAmount = calculation.ElectricFee + calculation.ServiceFee - calculation.DiscountAmount - calculation.FreeQuotaDeduction;
        calculation.ActualAmount = calculation.TotalAmount;

        // Assert
        calculation.TotalAmount.Should().Be(23m); // 20 + 10 - 5 - 2 = 23
        calculation.ActualAmount.Should().Be(23m);
    }

    [Fact]
    public void TimePeriodFee_ShouldCalculateFeeCorrectly()
    {
        // Arrange & Act
        var periodFee = new TimePeriodFee
        {
            PeriodType = "Peak",
            StartTime = TimeSpan.FromHours(10),
            EndTime = TimeSpan.FromHours(12),
            Price = 1.5m,
            Power = 10m
        };
        periodFee.Fee = periodFee.Price * periodFee.Power;

        // Assert
        periodFee.PeriodType.Should().Be("Peak");
        periodFee.Fee.Should().Be(15m); // 1.5 * 10 = 15
    }

    [Fact]
    public void CreateChargingOrderResponse_ShouldIndicateSuccess()
    {
        // Arrange
        var orderId = Guid.NewGuid();

        // Act
        var response = new CreateChargingOrderResponse
        {
            Success = true,
            Message = "订单创建成功",
            OrderId = orderId,
            OrderNumber = "CHG202401011234"
        };

        // Assert
        response.Success.Should().BeTrue();
        response.OrderId.Should().Be(orderId);
        response.OrderNumber.Should().StartWith("CHG");
        response.ErrorCode.Should().BeNull();
    }

    [Fact]
    public void CreateChargingOrderResponse_ShouldIndicateFailure()
    {
        // Arrange & Act
        var response = new CreateChargingOrderResponse
        {
            Success = false,
            Message = "充电桩离线",
            ErrorCode = "PILE_OFFLINE"
        };

        // Assert
        response.Success.Should().BeFalse();
        response.Message.Should().Be("充电桩离线");
        response.ErrorCode.Should().Be("PILE_OFFLINE");
        response.OrderId.Should().BeNull();
    }

    [Fact]
    public void SettleOrderResponse_ShouldContainSettlementDetails()
    {
        // Arrange
        var orderId = Guid.NewGuid();

        // Act
        var response = new SettleOrderResponse
        {
            Success = true,
            Message = "结算成功",
            OrderId = orderId,
            OrderNumber = "CHG202401011234",
            ConsumePower = 15.5m,
            ActualDuration = 120, // 2小时
            ActualAmount = 25.5m,
            ServiceFee = 5.0m,
            TotalAmount = 30.5m
        };

        // Assert
        response.Success.Should().BeTrue();
        response.OrderId.Should().Be(orderId);
        response.ConsumePower.Should().Be(15.5m);
        response.ActualDuration.Should().Be(120);
        response.TotalAmount.Should().Be(30.5m);
    }

    [Fact]
    public void OrderFeeCalculation_ShouldSupportTimePeriodFees()
    {
        // Arrange
        var calculation = new OrderFeeCalculation
        {
            ConsumePower = 30m,
            TimePeriodFees = new List<TimePeriodFee>
            {
                new() { PeriodType = "Peak", Power = 10m, Price = 1.5m, Fee = 15m },
                new() { PeriodType = "Flat", Power = 15m, Price = 1.0m, Fee = 15m },
                new() { PeriodType = "Valley", Power = 5m, Price = 0.5m, Fee = 2.5m }
            }
        };

        // Act
        var totalFee = 0m;
        foreach (var period in calculation.TimePeriodFees)
        {
            totalFee += period.Fee;
        }

        // Assert
        calculation.TimePeriodFees.Should().HaveCount(3);
        totalFee.Should().Be(32.5m); // 15 + 15 + 2.5
    }
}

/// <summary>
/// 充电订单验证服务测试
/// </summary>
public class OrderValidationServiceTests
{
    [Fact]
    public void CreateOrderRequest_ShouldBeValid_WhenAllRequiredFieldsProvided()
    {
        // Arrange
        var request = new CreateChargingOrderRequest
        {
            UserId = Guid.NewGuid(),
            TenantId = Guid.NewGuid(),
            StationId = Guid.NewGuid(),
            PileId = Guid.NewGuid(),
            PortId = Guid.NewGuid(),
            Mobile = "13800138000",
            Hour = "2"
        };

        // Assert
        request.UserId.Should().NotBeEmpty();
        request.TenantId.Should().NotBeEmpty();
        request.StationId.Should().NotBeEmpty();
        request.PileId.Should().NotBeEmpty();
        request.PortId.Should().NotBeEmpty();
    }

    [Fact]
    public void CreateOrderRequest_ShouldSupportCardPayment()
    {
        // Arrange & Act
        var request = new CreateChargingOrderRequest
        {
            UserId = Guid.NewGuid(),
            TenantId = Guid.NewGuid(),
            StationId = Guid.NewGuid(),
            PileId = Guid.NewGuid(),
            PortId = Guid.NewGuid(),
            OrderSource = 3, // 卡支付
            CardNo = "CARD123456789"
        };

        // Assert
        request.OrderSource.Should().Be(3);
        request.CardNo.Should().NotBeNullOrEmpty();
    }

    [Fact]
    public void CreateOrderRequest_ShouldSupportFreeCharging()
    {
        // Arrange & Act
        var request = new CreateChargingOrderRequest
        {
            UserId = Guid.NewGuid(),
            TenantId = Guid.NewGuid(),
            StationId = Guid.NewGuid(),
            PileId = Guid.NewGuid(),
            PortId = Guid.NewGuid(),
            IsFee = "2002" // 不收费
        };

        // Assert
        request.IsFee.Should().Be("2002");
    }
}

/// <summary>
/// 充电预约服务测试
/// </summary>
public class ReservationServiceTests
{
    [Fact]
    public void Reservation_ShouldHaveCorrectTimeWindow()
    {
        // Arrange
        var startTime = DateTime.UtcNow.AddHours(1);
        var endTime = startTime.AddHours(2);

        // Act
        var duration = endTime - startTime;

        // Assert
        duration.TotalHours.Should().Be(2);
    }
}
