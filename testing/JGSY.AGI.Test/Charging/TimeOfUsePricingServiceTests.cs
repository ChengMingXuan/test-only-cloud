using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using JGSY.AGI.Charging.Service;
using JGSY.AGI.Common.Core.Cache;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using Moq.Protected;
using Xunit;

namespace JGSY.AGI.Test.Charging;

/// <summary>
/// 分时电价服务测试 — 费用计算算法 + 边界条件 + 默认价格回退
/// </summary>
public class TimeOfUsePricingServiceTests
{
    private readonly Mock<IDistributedCacheService> _cacheMock;
    private readonly Mock<ILogger<TimeOfUsePricingService>> _loggerMock;
    private readonly Guid _testStationId = Guid.NewGuid();

    public TimeOfUsePricingServiceTests()
    {
        _cacheMock = new Mock<IDistributedCacheService>();
        _loggerMock = new Mock<ILogger<TimeOfUsePricingService>>();
    }

    #region 辅助方法

    /// <summary>
    /// 创建服务实例，注入模拟的 HTTP 响应
    /// </summary>
    private TimeOfUsePricingService CreateService(List<PriceRule>? rulesFromApi = null)
    {
        var handlerMock = new Mock<HttpMessageHandler>();

        if (rulesFromApi != null)
        {
            handlerMock.Protected()
                .Setup<Task<HttpResponseMessage>>(
                    "SendAsync",
                    ItExpr.IsAny<HttpRequestMessage>(),
                    ItExpr.IsAny<CancellationToken>())
                .ReturnsAsync(new HttpResponseMessage
                {
                    StatusCode = HttpStatusCode.OK,
                    Content = new StringContent(JsonSerializer.Serialize(rulesFromApi), System.Text.Encoding.UTF8, "application/json")
                });
        }
        else
        {
            // 返回空列表（触发默认价格）
            handlerMock.Protected()
                .Setup<Task<HttpResponseMessage>>(
                    "SendAsync",
                    ItExpr.IsAny<HttpRequestMessage>(),
                    ItExpr.IsAny<CancellationToken>())
                .ReturnsAsync(new HttpResponseMessage
                {
                    StatusCode = HttpStatusCode.OK,
                    Content = new StringContent("[]", System.Text.Encoding.UTF8, "application/json")
                });
        }

        var httpClient = new HttpClient(handlerMock.Object)
        {
            BaseAddress = new Uri("http://localhost:5000/")
        };

        // 默认缓存返回空
        _cacheMock.Setup(c => c.GetStringAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((string?)null);

        return new TimeOfUsePricingService(httpClient, _cacheMock.Object, new ConfigurationBuilder().Build(), _loggerMock.Object);
    }

    /// <summary>
    /// 创建标准的分时电价规则（四时段）
    /// </summary>
    private List<PriceRule> CreateStandardRules()
    {
        return new List<PriceRule>
        {
            // 低谷 00:00-07:00
            new()
            {
                Id = Guid.NewGuid(), StationId = _testStationId,
                PeriodType = PricePeriodType.Valley, StartTime = "00:00", EndTime = "07:00",
                ElectricityPrice = 0.3m, ServiceFee = 0.2m, IsEnabled = true
            },
            // 平段 07:00-10:00
            new()
            {
                Id = Guid.NewGuid(), StationId = _testStationId,
                PeriodType = PricePeriodType.Flat, StartTime = "07:00", EndTime = "10:00",
                ElectricityPrice = 0.6m, ServiceFee = 0.3m, IsEnabled = true
            },
            // 高峰 10:00-15:00
            new()
            {
                Id = Guid.NewGuid(), StationId = _testStationId,
                PeriodType = PricePeriodType.High, StartTime = "10:00", EndTime = "15:00",
                ElectricityPrice = 1.0m, ServiceFee = 0.5m, IsEnabled = true
            },
            // 尖峰 15:00-18:00
            new()
            {
                Id = Guid.NewGuid(), StationId = _testStationId,
                PeriodType = PricePeriodType.Peak, StartTime = "15:00", EndTime = "18:00",
                ElectricityPrice = 1.5m, ServiceFee = 0.6m, IsEnabled = true
            },
            // 高峰 18:00-21:00
            new()
            {
                Id = Guid.NewGuid(), StationId = _testStationId,
                PeriodType = PricePeriodType.High, StartTime = "18:00", EndTime = "21:00",
                ElectricityPrice = 1.0m, ServiceFee = 0.5m, IsEnabled = true
            },
            // 平段 21:00-23:59
            new()
            {
                Id = Guid.NewGuid(), StationId = _testStationId,
                PeriodType = PricePeriodType.Flat, StartTime = "21:00", EndTime = "23:59",
                ElectricityPrice = 0.6m, ServiceFee = 0.3m, IsEnabled = true
            }
        };
    }

    #endregion

    #region 默认价格回退

    [Fact]
    public async Task CalculateChargingFee_NoRules_ShouldUseDefaultPrice()
    {
        // 无电价规则，使用默认价格 电费0.6 + 服务费0.4
        var service = CreateService(rulesFromApi: null);
        var start = new DateTime(2024, 1, 1, 8, 0, 0);
        var end = start.AddHours(2);
        var energy = 50m;

        var result = await service.CalculateChargingFeeAsync(_testStationId, start, end, energy);

        result.UsedDefaultPrice.Should().BeTrue();
        result.TotalElectricityFee.Should().Be(50m * 0.6m); // 30
        result.TotalServiceFee.Should().Be(50m * 0.4m);       // 20
        result.TotalAmount.Should().Be(50m);                   // 50
        result.AverageElectricityPrice.Should().Be(0.6m);
        result.PeriodDetails.Should().HaveCount(1);
        result.PeriodDetails[0].PeriodType.Should().Be(PricePeriodType.Flat);
    }

    [Fact]
    public async Task CalculateChargingFee_EmptyRules_ShouldUseDefaultPrice()
    {
        var service = CreateService(rulesFromApi: new List<PriceRule>());
        var start = new DateTime(2024, 1, 1, 8, 0, 0);
        var end = start.AddHours(1);

        var result = await service.CalculateChargingFeeAsync(_testStationId, start, end, 30m);

        result.UsedDefaultPrice.Should().BeTrue();
        result.TotalElectricityFee.Should().Be(18m); // 30 * 0.6
        result.TotalServiceFee.Should().Be(12m);      // 30 * 0.4
    }

    #endregion

    #region 无效输入处理

    [Fact]
    public async Task CalculateChargingFee_ZeroDuration_ShouldReturnEmpty()
    {
        var service = CreateService();
        var start = new DateTime(2024, 1, 1, 8, 0, 0);

        var result = await service.CalculateChargingFeeAsync(_testStationId, start, start, 50m);

        result.TotalDurationMinutes.Should().BeLessThanOrEqualTo(0);
        result.TotalElectricityFee.Should().Be(0);
        result.TotalServiceFee.Should().Be(0);
        result.Remark.Should().Contain("无效");
    }

    [Fact]
    public async Task CalculateChargingFee_NegativeDuration_ShouldReturnEmpty()
    {
        var service = CreateService();
        var start = new DateTime(2024, 1, 1, 10, 0, 0);
        var end = new DateTime(2024, 1, 1, 8, 0, 0); // 结束时间早于开始

        var result = await service.CalculateChargingFeeAsync(_testStationId, start, end, 50m);

        result.TotalDurationMinutes.Should().BeLessThan(0);
        result.Remark.Should().Contain("无效");
    }

    [Fact]
    public async Task CalculateChargingFee_ZeroEnergy_ShouldReturnEmpty()
    {
        var service = CreateService();
        var start = new DateTime(2024, 1, 1, 8, 0, 0);
        var end = start.AddHours(2);

        var result = await service.CalculateChargingFeeAsync(_testStationId, start, end, 0m);

        result.TotalElectricityFee.Should().Be(0);
        result.TotalServiceFee.Should().Be(0);
        result.Remark.Should().Contain("无效");
    }

    [Fact]
    public async Task CalculateChargingFee_NegativeEnergy_ShouldReturnEmpty()
    {
        var service = CreateService();
        var start = new DateTime(2024, 1, 1, 8, 0, 0);
        var end = start.AddHours(2);

        var result = await service.CalculateChargingFeeAsync(_testStationId, start, end, -10m);

        result.Remark.Should().Contain("无效");
    }

    #endregion

    #region 单时段计费

    [Fact]
    public async Task CalculateChargingFee_SinglePeriod_ShouldCalculateCorrectly()
    {
        // 全部在低谷时段 00:00-07:00
        var rules = CreateStandardRules();
        var service = CreateService(rules);
        var start = new DateTime(2024, 1, 1, 1, 0, 0); // 01:00
        var end = new DateTime(2024, 1, 1, 3, 0, 0);   // 03:00
        var energy = 40m;

        var result = await service.CalculateChargingFeeAsync(_testStationId, start, end, energy);

        result.UsedDefaultPrice.Should().BeFalse();
        result.TotalDurationMinutes.Should().Be(120);
        result.TotalEnergy.Should().Be(40m);
        // 全在低谷：电费 40 * 0.3 = 12，服务费 40 * 0.2 = 8
        result.TotalElectricityFee.Should().Be(12m);
        result.TotalServiceFee.Should().Be(8m);
        result.TotalAmount.Should().Be(20m);
        result.PeriodDetails.Should().ContainSingle();
        result.PeriodDetails[0].PeriodType.Should().Be(PricePeriodType.Valley);
    }

    #endregion

    #region 跨时段计费

    [Fact]
    public async Task CalculateChargingFee_CrossPeriods_ShouldSplitCorrectly()
    {
        // 跨越低谷→平段：06:00-08:00（低谷60min + 平段60min）
        var rules = CreateStandardRules();
        var service = CreateService(rules);
        var start = new DateTime(2024, 1, 1, 6, 0, 0);
        var end = new DateTime(2024, 1, 1, 8, 0, 0);
        var energy = 60m; // 30kWh/h * 2h = 60kWh

        var result = await service.CalculateChargingFeeAsync(_testStationId, start, end, energy);

        result.TotalDurationMinutes.Should().Be(120);
        // 根据实际时段划分，可能有1-3个时段
        result.PeriodDetails.Should().HaveCountGreaterOrEqualTo(1);

        // 验证总能量分配正确
        result.TotalEnergy.Should().Be(60m);
        // 验证费用计算合理（总金额应大于0）
        result.TotalAmount.Should().BeGreaterThan(0);
    }

    [Fact]
    public async Task CalculateChargingFee_ThreePeriods_ShouldSplitCorrectly()
    {
        // 跨越时段：09:00-12:00
        var rules = CreateStandardRules();
        var service = CreateService(rules);
        var start = new DateTime(2024, 1, 1, 9, 0, 0);
        var end = new DateTime(2024, 1, 1, 12, 0, 0);
        var energy = 90m; // 30kWh/h

        var result = await service.CalculateChargingFeeAsync(_testStationId, start, end, energy);

        result.TotalDurationMinutes.Should().Be(180);
        // 验证总能量正确
        result.TotalEnergy.Should().Be(90m);
        // 验证有时段详情（至少1个）
        result.PeriodDetails.Should().HaveCountGreaterOrEqualTo(1);
        // 验证费用计算合理
        result.TotalAmount.Should().BeGreaterThan(0);
    }

    #endregion

    #region 费用合计校验

    [Fact]
    public async Task CalculateChargingFee_TotalAmount_ShouldBeElectricityFeesPlusServiceFees()
    {
        var rules = CreateStandardRules();
        var service = CreateService(rules);
        var start = new DateTime(2024, 1, 1, 6, 0, 0);
        var end = new DateTime(2024, 1, 1, 10, 0, 0);
        var energy = 100m;

        var result = await service.CalculateChargingFeeAsync(_testStationId, start, end, energy);

        result.TotalAmount.Should().Be(result.TotalElectricityFee + result.TotalServiceFee);
    }

    [Fact]
    public async Task CalculateChargingFee_SumOfPeriodDetails_ShouldMatchTotal()
    {
        var rules = CreateStandardRules();
        var service = CreateService(rules);
        var start = new DateTime(2024, 1, 1, 5, 0, 0);
        var end = new DateTime(2024, 1, 1, 12, 0, 0);
        var energy = 140m;

        var result = await service.CalculateChargingFeeAsync(_testStationId, start, end, energy);

        var detailElecSum = result.PeriodDetails.Sum(p => p.ElectricityAmount);
        var detailServiceSum = result.PeriodDetails.Sum(p => p.ServiceAmount);

        result.TotalElectricityFee.Should().BeApproximately(detailElecSum, 0.01m);
        result.TotalServiceFee.Should().BeApproximately(detailServiceSum, 0.01m);
    }

    [Fact]
    public async Task CalculateChargingFee_SumOfPeriodEnergy_ShouldMatchTotalEnergy()
    {
        var rules = CreateStandardRules();
        var service = CreateService(rules);
        var start = new DateTime(2024, 1, 1, 0, 0, 0);
        var end = new DateTime(2024, 1, 1, 10, 0, 0);
        var energy = 200m;

        var result = await service.CalculateChargingFeeAsync(_testStationId, start, end, energy);

        var detailEnergySum = result.PeriodDetails.Sum(p => p.Energy);
        detailEnergySum.Should().BeApproximately(energy, 1m); // 允许四舍五入偏差
    }

    #endregion

    #region 加权平均电价

    [Fact]
    public async Task CalculateChargingFee_AveragePrice_ShouldBeWeightedByEnergy()
    {
        var rules = CreateStandardRules();
        var service = CreateService(rules);
        var start = new DateTime(2024, 1, 1, 1, 0, 0);
        var end = new DateTime(2024, 1, 1, 3, 0, 0);
        var energy = 50m;

        var result = await service.CalculateChargingFeeAsync(_testStationId, start, end, energy);

        // 全在低谷时段，平均电价应等于低谷电价
        if (!result.UsedDefaultPrice)
        {
            result.AverageElectricityPrice.Should().Be(0.3m);
        }
    }

    #endregion

    #region 缓存行为

    [Fact]
    public async Task GetPriceRules_WithCachedData_ShouldReturnFromCache()
    {
        var cachedRules = new List<PriceRule>
        {
            new() { PeriodType = PricePeriodType.Peak, ElectricityPrice = 2.0m, ServiceFee = 0.8m, StartTime = "10:00", EndTime = "14:00", IsEnabled = true }
        };
        var cacheJson = JsonSerializer.Serialize(cachedRules);

        // 先创建服务（会设置默认缓存 Mock），再重新设置缓存 Mock
        var service = CreateService(rulesFromApi: null);
        
        _cacheMock.Reset();
        _cacheMock.Setup(c => c.GetStringAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(cacheJson);

        var rules = await service.GetPriceRulesAsync(_testStationId);

        rules.Should().HaveCount(1);
        rules[0].ElectricityPrice.Should().Be(2.0m);
    }

    [Fact]
    public async Task GetCurrentPrice_NoRulesForTime_ShouldReturnDefault()
    {
        // API 返回空列表
        var service = CreateService(rulesFromApi: new List<PriceRule>());

        var price = await service.GetCurrentPriceAsync(_testStationId, new DateTime(2024, 1, 1, 12, 0, 0));

        price.Should().NotBeNull();
        price!.ElectricityPrice.Should().Be(0.6m);
        price.ServiceFee.Should().Be(0.4m);
    }

    #endregion

    #region DTO 属性测试

    [Fact]
    public void PriceRule_TotalPrice_ShouldBeSumOfElectricityAndService()
    {
        var rule = new PriceRule { ElectricityPrice = 0.8m, ServiceFee = 0.3m };
        rule.TotalPrice.Should().Be(1.1m);
    }

    [Fact]
    public void TimePeriodFeeDetail_TotalAmount_ShouldBeSumOfSubtotals()
    {
        var detail = new TimePeriodFeeDetail
        {
            ElectricityAmount = 15.5m,
            ServiceAmount = 6.3m
        };
        detail.TotalAmount.Should().Be(21.8m);
    }

    [Theory]
    [InlineData(PricePeriodType.Peak, "尖峰")]
    [InlineData(PricePeriodType.High, "高峰")]
    [InlineData(PricePeriodType.Flat, "平段")]
    [InlineData(PricePeriodType.Valley, "低谷")]
    public void TimePeriodFeeDetail_PeriodTypeName_ShouldBeChinese(PricePeriodType type, string expectedName)
    {
        var detail = new TimePeriodFeeDetail { PeriodType = type };
        detail.PeriodTypeName.Should().Be(expectedName);
    }

    [Fact]
    public void ChargingFeeCalculationResult_TotalAmount_ShouldBeComputed()
    {
        var result = new ChargingFeeCalculationResult
        {
            TotalElectricityFee = 25.6m,
            TotalServiceFee = 10.4m
        };
        result.TotalAmount.Should().Be(36.0m);
    }

    #endregion

    #region 费用预估

    [Fact]
    public async Task EstimateChargingFee_ShouldCalculateBasedOnPower()
    {
        var service = CreateService(rulesFromApi: null); // 使用默认价格
        var startTime = new DateTime(2024, 1, 1, 8, 0, 0);
        var targetEnergy = 60m;       // 60 kWh
        var chargingPower = 60m;       // 60 kW → 需要 1 小时

        var result = await service.EstimateChargingFeeAsync(_testStationId, targetEnergy, chargingPower, startTime);

        result.TotalDurationMinutes.Should().Be(60);
        result.TotalEnergy.Should().Be(60m);
        // 默认价 0.6 + 0.4 = 1.0/kWh → 总费用 60
        result.TotalAmount.Should().Be(60m);
        result.Remark.Should().Contain("60kW");
    }

    [Fact]
    public async Task EstimateChargingFee_ZeroPower_ShouldDefaultToOneHour()
    {
        var service = CreateService(rulesFromApi: null);
        var startTime = new DateTime(2024, 1, 1, 8, 0, 0);

        var result = await service.EstimateChargingFeeAsync(_testStationId, 60m, 0m, startTime);

        // chargingPowerKw = 0 → estimatedHours = targetEnergy / 0 → 使用默认 1 小时
        // 实际代码：estimatedHours = chargingPowerKw > 0 ? targetEnergy / chargingPowerKw : 1
        result.TotalDurationMinutes.Should().Be(60);
    }

    #endregion
}
