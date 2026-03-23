using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;
using JGSY.AGI.Common.Core.Maps;
using JGSY.AGI.WorkOrder.Service;

namespace JGSY.AGI.Test.WorkOrder;

/// <summary>
/// 地理位置服务单元测试（Haversine 距离计算 + 高德地图 API 集成）
/// </summary>
public class GeolocationServiceTests
{
    private readonly Mock<IMapService> _mapService;
    private readonly GeolocationService _service;
    private readonly GeolocationService _serviceWithoutMap;

    public GeolocationServiceTests()
    {
        _mapService = new Mock<IMapService>();

        _service = new GeolocationService(
            NullLogger<GeolocationService>.Instance,
            _mapService.Object);

        // 无地图服务实例（测试降级逻辑）
        _serviceWithoutMap = new GeolocationService(
            NullLogger<GeolocationService>.Instance);
    }

    #region CalculateDistance Haversine 公式测试

    [Fact]
    public void CalculateDistance_SamePoint_ReturnsZero()
    {
        var result = _service.CalculateDistance(39.9042, 116.4074, 39.9042, 116.4074);
        result.Should().Be(0);
    }

    [Fact]
    public void CalculateDistance_BeijingToShanghai_ReturnsApprox1068km()
    {
        // 北京 (39.9042, 116.4074) → 上海 (31.2304, 121.4737)
        var result = _service.CalculateDistance(39.9042, 116.4074, 31.2304, 121.4737);
        result.Should().BeApproximately(1068, 20); // 约1068公里，误差20公里
    }

    [Fact]
    public void CalculateDistance_BeijingToGuangzhou_ReturnsApprox1890km()
    {
        // 北京 → 广州 (23.1291, 113.2644)
        var result = _service.CalculateDistance(39.9042, 116.4074, 23.1291, 113.2644);
        result.Should().BeApproximately(1890, 30);
    }

    [Fact]
    public void CalculateDistance_ShortDistance_CalculatesCorrectly()
    {
        // 天安门 → 故宫（约1km）
        var result = _service.CalculateDistance(39.9087, 116.3975, 39.9163, 116.3972);
        result.Should().BeInRange(0.5, 2.0);
    }

    [Fact]
    public void CalculateDistance_CrossEquator_CalculatesCorrectly()
    {
        // 新加坡 (1.3521, 103.8198) → 悉尼 (-33.8688, 151.2093)
        var result = _service.CalculateDistance(1.3521, 103.8198, -33.8688, 151.2093);
        result.Should().BeApproximately(6288, 100);
    }

    [Fact]
    public void CalculateDistance_IsSymmetric()
    {
        var d1 = _service.CalculateDistance(39.9042, 116.4074, 31.2304, 121.4737);
        var d2 = _service.CalculateDistance(31.2304, 121.4737, 39.9042, 116.4074);
        d1.Should().BeApproximately(d2, 0.001);
    }

    #endregion

    #region GetCoordinatesFromAddressAsync 地址解析

    [Fact]
    public async Task GetCoordinatesFromAddress_MapServiceAvailable_ReturnsCoordinates()
    {
        _mapService.Setup(m => m.GeocodeAsync("北京市海淀区中关村", null, default))
            .ReturnsAsync(new GeocodeResult
            {
                Success = true,
                Coordinate = new GeoCoordinate { Latitude = 39.98, Longitude = 116.31 }
            });

        var result = await _service.GetCoordinatesFromAddressAsync("北京市海淀区中关村");
        result.Should().NotBeNull();
        result!.Value.Latitude.Should().BeApproximately(39.98, 0.01);
        result!.Value.Longitude.Should().BeApproximately(116.31, 0.01);
    }

    [Fact]
    public async Task GetCoordinatesFromAddress_MapServiceReturnsFailure_ReturnsNull()
    {
        _mapService.Setup(m => m.GeocodeAsync(It.IsAny<string>(), It.IsAny<string?>(), default))
            .ReturnsAsync(new GeocodeResult { Success = false, ErrorMessage = "地址不存在" });

        var result = await _service.GetCoordinatesFromAddressAsync("不合法地址xxx");
        result.Should().BeNull();
    }

    [Fact]
    public async Task GetCoordinatesFromAddress_NoMapService_ReturnsNull()
    {
        var result = await _serviceWithoutMap.GetCoordinatesFromAddressAsync("北京市");
        result.Should().BeNull();
    }

    [Fact]
    public async Task GetCoordinatesFromAddress_WithCity_PassesCityParam()
    {
        _mapService.Setup(m => m.GeocodeAsync("中关村", "北京", default))
            .ReturnsAsync(new GeocodeResult
            {
                Success = true,
                Coordinate = new GeoCoordinate { Latitude = 39.98, Longitude = 116.31 }
            });

        var result = await _service.GetCoordinatesFromAddressAsync("中关村", "北京");
        result.Should().NotBeNull();
        _mapService.Verify(m => m.GeocodeAsync("中关村", "北京", default), Times.Once);
    }

    #endregion
}
