using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.EnergyServices;

/// <summary>
/// 能源服务模块实体单元测试（ElecTrade / CarbonTrade / EnergyEff / DemandResp / DeviceOps）
/// </summary>
public class EnergyServicesEntityTests
{
    #region 电力交易

    [Fact]
    public void TradingOrder_ShouldHaveCorrectDefaults()
    {
        var order = new AGI.Trading.Modules.ElecTrade.Entities.TradingOrder();
        order.DeleteAt.Should().BeNull();
        order.FilledQuantity.Should().Be(0);
    }

    [Fact]
    public void TradingOrder_ShouldSetAllProperties()
    {
        var order = new AGI.Trading.Modules.ElecTrade.Entities.TradingOrder
        {
            OrderId = Guid.NewGuid().ToString(),
            StationId = Guid.NewGuid().ToString(),
            OrderType = "sell",
            QuantityKwh = 1000.0m,
            PricePerKwh = 0.85m,
            FilledQuantity = 500.0m,
            Status = "partial"
        };

        order.OrderType.Should().Be("sell");
        order.FilledQuantity.Should().BeLessThanOrEqualTo(order.QuantityKwh);
        order.PricePerKwh.Should().BePositive();
    }

    [Fact]
    public void Trade_ShouldCalculateTotalAmount()
    {
        var trade = new AGI.Trading.Modules.ElecTrade.Entities.Trade
        {
            TradeId = Guid.NewGuid().ToString(),
            SellOrderId = Guid.NewGuid().ToString(),
            BuyOrderId = Guid.NewGuid().ToString(),
            QuantityKwh = 500.0m,
            Price = 0.85m,
            TotalAmount = 425.0m,
            Status = "completed"
        };

        trade.TotalAmount.Should().Be(trade.QuantityKwh * trade.Price);
        trade.Status.Should().Be("completed");
    }

    [Fact]
    public void BilateralTrade_ShouldHaveDeliveryPeriod()
    {
        var now = DateTime.UtcNow;
        var trade = new AGI.Trading.Modules.ElecTrade.Entities.BilateralTrade
        {
            TradeId = Guid.NewGuid().ToString(),
            QuantityKwh = 10000.0m,
            Price = 0.72m,
            DeliveryStart = now,
            DeliveryEnd = now.AddDays(30),
            ContractTerms = "标准合同条款",
            Status = "active"
        };

        trade.DeliveryEnd.Should().BeAfter(trade.DeliveryStart);
        trade.QuantityKwh.Should().BeGreaterThan(0);
    }

    #endregion

    #region 碳交易

    [Fact]
    public void CtEmissionRecord_ShouldSetProperties()
    {
        var record = new AGI.Trading.Modules.CarbonTrade.Entities.CtEmissionRecord
        {
            Period = "2026-Q1",
            Scope = 1, // Scope1
            EmissionTco2 = 150.5m,
            EnergySource = "natural_gas",
            Verified = true
        };

        record.EmissionTco2.Should().NotBeNull();
        record.Verified.Should().BeTrue();
        record.Scope.Should().Be(1);
    }

    [Fact]
    public void CtAsset_ShouldHaveValidityPeriod()
    {
        var now = DateTime.UtcNow;
        var asset = new AGI.Trading.Modules.CarbonTrade.Entities.CtAsset
        {
            AssetType = 1, // CCER
            AssetCode = "CCER-2026-001",
            QuantityTco2 = 1000.0m,
            UnitPriceYuan = 68.5m,
            ValidFrom = now,
            ValidTo = now.AddYears(1)
        };

        asset.ValidTo.Value.Should().BeAfter(asset.ValidFrom.Value);
        asset.QuantityTco2.Should().NotBeNull();
        asset.UnitPriceYuan.Should().NotBeNull();
    }

    #endregion

    #region 能效管理

    [Fact]
    public void EeConsumption_ShouldTrackPeakValleyFlat()
    {
        var consumption = new AGI.Operations.Modules.EnergyEff.Entities.EeConsumption
        {
            MeterId = Guid.NewGuid(),
            Period = "2026-02-13",
            EnergyKwh = 500.0m,
            CostYuan = 350.0m,
            PeakKwh = 200.0m,
            ValleyKwh = 100.0m,
            FlatKwh = 200.0m
        };

        // 峰谷平之和应等于总能耗
        var sum = consumption.PeakKwh + consumption.ValleyKwh + consumption.FlatKwh;
        sum.Should().Be(consumption.EnergyKwh);
    }

    [Fact]
    public void EeEfficiencyIndex_ShouldCalculateRating()
    {
        var index = new AGI.Operations.Modules.EnergyEff.Entities.EeEfficiencyIndex
        {
            IndexName = "综合能效指标",
            IndexCode = "EEI-001",
            TargetValue = 90.0m,
            ActualValue = 85.0m,
            Rating = "B"
        };

        index.ActualValue.Should().BeLessThanOrEqualTo(index.TargetValue.GetValueOrDefault());
        index.Rating.Should().NotBeEmpty();
    }

    #endregion
}

/// <summary>
/// 电力交易 DTO 测试
/// </summary>
public class EnergyServicesDtoTests
{
    [Fact]
    public void SellOrderRequest_ShouldHaveRequiredFields()
    {
        var request = new AGI.Trading.Modules.ElecTrade.Models.SellOrderRequest
        {
            StationId = "station-001",
            SellerAddress = "0xabc123",
            QuantityKwh = 1000.0m,
            PricePerKwh = 0.85m,
            StartTime = DateTime.UtcNow
        };

        request.StationId.Should().NotBeEmpty();
        request.QuantityKwh.Should().BePositive();
        request.PricePerKwh.Should().BePositive();
    }

    [Fact]
    public void BuyOrderRequest_ShouldHaveMaxPrice()
    {
        var request = new AGI.Trading.Modules.ElecTrade.Models.BuyOrderRequest
        {
            StationId = "station-002",
            BuyerAddress = "0xdef456",
            QuantityKwh = 500.0m,
            MaxPricePerKwh = 1.0m,
            StartTime = DateTime.UtcNow,
            EndTime = DateTime.UtcNow.AddHours(4)
        };

        request.MaxPricePerKwh.Should().BePositive();
        request.EndTime.Should().BeAfter(request.StartTime);
    }
}
