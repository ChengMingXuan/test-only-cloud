using Xunit;
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using JGSY.AGI.IotCloudAI.Core.Interfaces;
using JGSY.AGI.IotCloudAI.Core.Services;
using JGSY.AGI.IotCloudAI.Models;

namespace JGSY.AGI.Test.IotCloudAI;

/// <summary>PredictionService 单元测试</summary>
public class PredictionServiceTests
{
    private readonly Mock<IAiInferenceService> _inferenceMock = new();
    private readonly PredictionService _sut;

    public PredictionServiceTests()
    {
        _sut = new PredictionService(
            NullLogger<PredictionService>.Instance,
            _inferenceMock.Object);
    }

    // ========== PredictAsync ==========

    [Fact]
    public async Task PredictAsync_映射推理结果为预测列表()
    {
        var inference = new InferenceResult
        {
            InferenceId = "inf-001",
            Confidence = 0.92,
            Predictions = new Dictionary<string, double>
            {
                ["power"] = 1500.5,
                ["voltage"] = 220.3,
                ["temperature"] = 45.2
            }
        };

        var result = await _sut.PredictAsync(inference);

        result.Status.Should().Be("Success");
        result.Predictions.Should().HaveCount(3);
        result.OverallConfidence.Should().Be(0.92);
        result.Predictions.Should().Contain(p => p.Name == "power" && p.Value == 1500.5);
        result.Predictions.Should().Contain(p => p.Name == "voltage" && p.Value == 220.3);
        result.Predictions.Should().Contain(p => p.Name == "temperature" && p.Value == 45.2);
        result.Predictions.Should().OnlyContain(p => p.Confidence == 0.92);
    }

    [Fact]
    public async Task PredictAsync_空预测字典返回空列表()
    {
        var inference = new InferenceResult
        {
            Confidence = 0.8,
            Predictions = new Dictionary<string, double>()
        };

        var result = await _sut.PredictAsync(inference);

        result.Status.Should().Be("Success");
        result.Predictions.Should().BeEmpty();
        result.OverallConfidence.Should().Be(0.8);
    }

    // ========== ForecastTimeSeriesAsync ==========

    [Fact]
    public async Task ForecastTimeSeriesAsync_空历史数据返回失败()
    {
        var result = await _sut.ForecastTimeSeriesAsync(new List<TimeSeriesPoint>(), 5);

        result.Status.Should().Be("Failed");
        result.Errors.Should().Contain("历史数据为空");
        result.Predictions.Should().BeEmpty();
    }

    [Fact]
    public async Task ForecastTimeSeriesAsync_生成指定步数的预测()
    {
        var now = DateTime.UtcNow;
        var history = new List<TimeSeriesPoint>
        {
            new() { Timestamp = now.AddHours(-3), Value = 100m },
            new() { Timestamp = now.AddHours(-2), Value = 110m },
            new() { Timestamp = now.AddHours(-1), Value = 120m }
        };

        var result = await _sut.ForecastTimeSeriesAsync(history, 5);

        result.Status.Should().Be("Success");
        result.Predictions.Should().HaveCount(5);
        result.OverallConfidence.Should().Be(0.85);

        // 预测名称格式
        result.Predictions[0].Name.Should().Be("forecast_1");
        result.Predictions[4].Name.Should().Be("forecast_5");

        // 置信度递减
        result.Predictions[0].Confidence.Should().BeGreaterThanOrEqualTo(result.Predictions[4].Confidence);

        // 时间戳递增
        for (int i = 1; i < result.Predictions.Count; i++)
        {
            result.Predictions[i].PredictedAt.Should().BeAfter(result.Predictions[i - 1].PredictedAt);
        }
    }

    [Fact]
    public async Task ForecastTimeSeriesAsync_单数据点仍可预测()
    {
        var history = new List<TimeSeriesPoint>
        {
            new() { Timestamp = DateTime.UtcNow, Value = 200m }
        };

        var result = await _sut.ForecastTimeSeriesAsync(history, 3);

        result.Status.Should().Be("Success");
        result.Predictions.Should().HaveCount(3);
    }

    // ========== PredictAnomaly ==========

    [Fact]
    public async Task PredictAnomaly_电压异常检测出异常()
    {
        var data = new List<DeviceData>
        {
            new()
            {
                DeviceId = "dev-001",
                Metrics = new Dictionary<string, double>
                {
                    ["voltage"] = 180, // < 200 → +0.3
                    ["temperature"] = 70 // > 60 → +0.4
                }
            }
        };

        var result = await _sut.PredictAnomaly(data);

        result.Status.Should().Be("Success");
        result.Predictions.Should().HaveCount(1);
        result.Predictions[0].Name.Should().Contain("anomaly_dev-001");
        result.Predictions[0].Value.Should().Be(0.7); // 0.3+0.4=0.7
    }

    [Fact]
    public async Task PredictAnomaly_正常数据不产生异常()
    {
        var data = new List<DeviceData>
        {
            new()
            {
                DeviceId = "dev-002",
                Metrics = new Dictionary<string, double>
                {
                    ["voltage"] = 220, // 200~250，正常
                    ["temperature"] = 40  // < 60，正常
                }
            }
        };

        var result = await _sut.PredictAnomaly(data);

        result.Status.Should().Be("Success");
        result.Predictions.Should().BeEmpty(); // score=0 < 0.5，不报告
    }

    [Fact]
    public async Task PredictAnomaly_仅电压异常得分0_3不追加()
    {
        var data = new List<DeviceData>
        {
            new()
            {
                DeviceId = "dev-003",
                Metrics = new Dictionary<string, double>
                {
                    ["voltage"] = 260 // > 250 → +0.3 仅0.3 < 0.5 不报告
                }
            }
        };

        var result = await _sut.PredictAnomaly(data);

        result.Predictions.Should().BeEmpty();
    }

    [Fact]
    public async Task PredictAnomaly_仅温度异常得分0_4不追加()
    {
        var data = new List<DeviceData>
        {
            new()
            {
                DeviceId = "dev-004",
                Metrics = new Dictionary<string, double>
                {
                    ["temperature"] = 65 // > 60 → +0.4，正好不到0.5？
                    // 实际 0.4 < 0.5，不报告
                }
            }
        };

        var result = await _sut.PredictAnomaly(data);

        result.Predictions.Should().BeEmpty();
    }

    [Fact]
    public async Task PredictAnomaly_多设备混合异常()
    {
        var data = new List<DeviceData>
        {
            new()
            {
                DeviceId = "normal",
                Metrics = new Dictionary<string, double> { ["voltage"] = 225 }
            },
            new()
            {
                DeviceId = "anomalous",
                Metrics = new Dictionary<string, double>
                {
                    ["voltage"] = 190, // +0.3
                    ["temperature"] = 80 // +0.4 → 0.7 > 0.5
                }
            }
        };

        var result = await _sut.PredictAnomaly(data);

        result.Predictions.Should().HaveCount(1);
        result.Predictions[0].Name.Should().Contain("anomalous");
    }

    [Fact]
    public async Task PredictAnomaly_空数据列表返回空预测()
    {
        var result = await _sut.PredictAnomaly(new List<DeviceData>());

        result.Status.Should().Be("Success");
        result.Predictions.Should().BeEmpty();
    }

    // ========== PredictTrend ==========

    [Fact]
    public async Task PredictTrend_计算各指标趋势()
    {
        var data = new List<DeviceData>
        {
            new()
            {
                DeviceId = "dev-a",
                Metrics = new Dictionary<string, double> { ["power"] = 100, ["temp"] = 40 }
            },
            new()
            {
                DeviceId = "dev-a",
                Metrics = new Dictionary<string, double> { ["power"] = 150, ["temp"] = 50 }
            }
        };

        var result = await _sut.PredictTrend(data);

        result.Status.Should().Be("Success");
        result.Predictions.Should().HaveCount(2);

        var powerTrend = result.Predictions.First(p => p.Name == "trend_power");
        powerTrend.Value.Should().Be(0.5); // (150-100)/100

        var tempTrend = result.Predictions.First(p => p.Name == "trend_temp");
        tempTrend.Value.Should().Be(0.25); // (50-40)/40
    }

    [Fact]
    public async Task PredictTrend_单条数据无法计算趋势()
    {
        var data = new List<DeviceData>
        {
            new()
            {
                DeviceId = "dev-b",
                Metrics = new Dictionary<string, double> { ["power"] = 500 }
            }
        };

        var result = await _sut.PredictTrend(data);

        // 只有1个值，values.Count < 2，跳过
        result.Predictions.Should().BeEmpty();
    }

    [Fact]
    public async Task PredictTrend_空数据列表()
    {
        var result = await _sut.PredictTrend(new List<DeviceData>());

        result.Status.Should().Be("Success");
        result.Predictions.Should().BeEmpty();
    }

    [Fact]
    public async Task PredictTrend_下降趋势为负值()
    {
        var data = new List<DeviceData>
        {
            new() { DeviceId = "d", Metrics = new Dictionary<string, double> { ["voltage"] = 240 } },
            new() { DeviceId = "d", Metrics = new Dictionary<string, double> { ["voltage"] = 200 } }
        };

        var result = await _sut.PredictTrend(data);

        var voltageTrend = result.Predictions.First(p => p.Name == "trend_voltage");
        voltageTrend.Value.Should().BeApproximately(-0.1667, 0.001); // (200-240)/240 ≈ -0.1667
    }
}
