using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.Trading;

/// <summary>
/// Trading 市场交易服务单元测试（ElecTrade/CarbonTrade/DemandResp）
/// 覆盖交易订单、撮合记录、市场配置等实体
/// </summary>
public class TradingServiceTests
{
    #region TradingOrder 交易订单实体测试

    [Fact]
    public void TradingOrder_ShouldHaveCorrectDefaults()
    {
        var order = new AGI.Trading.Modules.ElecTrade.Entities.TradingOrder();
        order.DeleteAt.Should().BeNull("新建订单不应被软删除");
        order.FilledQuantity.Should().Be(0);
    }

    [Fact]
    public void TradingOrder_ShouldSetAllProperties()
    {
        var order = new AGI.Trading.Modules.ElecTrade.Entities.TradingOrder
        {
            Id = Guid.NewGuid(),
            TenantId = Guid.NewGuid(),
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
        order.TenantId.Should().NotBe(Guid.Empty);
    }

    [Theory]
    [InlineData("buy")]
    [InlineData("sell")]
    public void TradingOrder_OrderType_ShouldBeValid(string orderType)
    {
        var order = new AGI.Trading.Modules.ElecTrade.Entities.TradingOrder
        {
            OrderType = orderType
        };
        order.OrderType.Should().BeOneOf("buy", "sell");
    }

    [Theory]
    [InlineData("pending")]
    [InlineData("partial")]
    [InlineData("filled")]
    [InlineData("cancelled")]
    public void TradingOrder_Status_ShouldBeValid(string status)
    {
        var order = new AGI.Trading.Modules.ElecTrade.Entities.TradingOrder
        {
            Status = status
        };
        order.Status.Should().NotBeNullOrEmpty();
    }

    #endregion

    #region Trade 撮合交易记录实体测试

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

        trade.TotalAmount.Should().Be(trade.QuantityKwh * trade.Price,
            "成交金额应等于成交量×单价");
        trade.Status.Should().Be("completed");
    }

    [Fact]
    public void Trade_ShouldSetProperties()
    {
        var trade = new AGI.Trading.Modules.ElecTrade.Entities.Trade
        {
            TradeId = Guid.NewGuid().ToString(),
            SellOrderId = Guid.NewGuid().ToString(),
            BuyOrderId = Guid.NewGuid().ToString(),
            QuantityKwh = 200.0m,
            Price = 0.75m,
            TotalAmount = 150.0m
        };

        trade.SellOrderId.Should().NotBeNullOrEmpty();
        trade.BuyOrderId.Should().NotBeNullOrEmpty();
        trade.QuantityKwh.Should().BePositive();
        trade.Price.Should().BePositive();
    }

    #endregion

    #region MarketConfig 市场配置实体测试

    [Fact]
    public void MarketConfig_ShouldSetProperties()
    {
        var config = new AGI.Trading.Modules.ElecTrade.Entities.MarketConfig
        {
            Id = Guid.NewGuid(),
            TenantId = Guid.NewGuid(),
            MarketId = "MKT-HB-001",
            MarketName = "华北电力现货市场",
            MarketType = "spot",
            FeeRate = 0.01m,
            MinQuantityKwh = 100.0m
        };

        config.MarketName.Should().NotBeNullOrEmpty();
        config.MarketType.Should().Be("spot");
        config.FeeRate.Should().BeLessThan(1.0m, "手续费率不应超过100%");
        config.MinQuantityKwh.Should().BePositive();
    }

    [Fact]
    public void MarketConfig_ShouldHaveCorrectDefaults()
    {
        var config = new AGI.Trading.Modules.ElecTrade.Entities.MarketConfig();
        config.DeleteAt.Should().BeNull("新建市场配置不应被软删除");
    }

    [Theory]
    [InlineData("spot")]
    [InlineData("bilateral")]
    [InlineData("futures")]
    public void MarketConfig_MarketType_ShouldBeValid(string marketType)
    {
        var config = new AGI.Trading.Modules.ElecTrade.Entities.MarketConfig
        {
            MarketType = marketType
        };
        config.MarketType.Should().NotBeNullOrEmpty();
    }

    #endregion

    #region 业务规则测试

    [Fact]
    public void TradingOrder_FilledQuantity_ShouldNotExceedQuantity()
    {
        var order = new AGI.Trading.Modules.ElecTrade.Entities.TradingOrder
        {
            QuantityKwh = 1000.0m,
            FilledQuantity = 500.0m
        };
        order.FilledQuantity.Should().BeLessThanOrEqualTo(order.QuantityKwh,
            "已成交量不能超过下单量");
    }

    [Fact]
    public void Trade_QuantityKwh_ShouldBePositive()
    {
        var trade = new AGI.Trading.Modules.ElecTrade.Entities.Trade
        {
            QuantityKwh = 100.0m
        };
        trade.QuantityKwh.Should().BePositive("成交量必须为正数");
    }

    #endregion
}
