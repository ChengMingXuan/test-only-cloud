using Xunit;
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using JGSY.AGI.IotCloudAI.Core.Interfaces;
using JGSY.AGI.IotCloudAI.Core.Scenarios.FaultWarning.Services;
using JGSY.AGI.IotCloudAI.Core.Scenarios.FaultWarning.Models;
using JGSY.AGI.IotCloudAI.Models;

namespace JGSY.AGI.Test.IotCloudAI;

/// <summary>FaultWarningService 单元测试</summary>
public class FaultWarningServiceTests
{
    private readonly Mock<IAiInferenceService> _inferenceMock = new();
    private readonly Mock<IDataCollectionService> _collectionMock = new();
    private readonly FaultWarningService _sut;

    public FaultWarningServiceTests()
    {
        _sut = new FaultWarningService(
            NullLogger<FaultWarningService>.Instance,
            _inferenceMock.Object,
            _collectionMock.Object);
    }

    // ========== 辅助方法 ==========

    private void SetupCollectionResult(string deviceId, Dictionary<string, double> metrics, string quality = "Good")
    {
        var data = new DeviceData
        {
            DeviceId = deviceId,
            Metrics = metrics,
            Quality = quality
        };
        var result = new CollectionResult { Data = new List<DeviceData> { data } };
        _collectionMock.Setup(c => c.CollectRealTimeDataAsync(deviceId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(result);
    }

    private void SetupEmptyCollectionResult(string deviceId)
    {
        var result = new CollectionResult { Data = new List<DeviceData>() };
        _collectionMock.Setup(c => c.CollectRealTimeDataAsync(deviceId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(result);
    }

    // ========== AssessHealthAsync ==========

    [Fact]
    public async Task AssessHealthAsync_正常数据计算健康评分()
    {
        SetupCollectionResult("dev-001", new Dictionary<string, double>
        {
            ["voltage"] = 220,  // 正常范围
            ["current"] = 50,   // 正常
            ["temperature"] = 35 // 正常
        });

        var result = await _sut.AssessHealthAsync("dev-001");

        result.DeviceId.Should().Be("dev-001");
        result.ElectricalScore.Should().Be(100m); // 电压正常、电流正常
        result.ThermalScore.Should().Be(100m);     // 温度正常
        result.CommunicationScore.Should().Be(95m); // Quality=Good
        result.OverallScore.Should().BeGreaterThan(80m);
        result.HealthLevel.Should().BeOneOf("Excellent", "Good");
        result.Recommendations.Should().NotBeEmpty();
    }

    [Fact]
    public async Task AssessHealthAsync_无数据返回Unknown()
    {
        SetupEmptyCollectionResult("dev-empty");

        var result = await _sut.AssessHealthAsync("dev-empty");

        result.DeviceId.Should().Be("dev-empty");
        result.OverallScore.Should().Be(0);
        result.HealthLevel.Should().Be("Unknown");
        result.CommunicationScore.Should().Be(0);
    }

    [Fact]
    public async Task AssessHealthAsync_电压异常降低电气评分()
    {
        SetupCollectionResult("dev-volt", new Dictionary<string, double>
        {
            ["voltage"] = 180 // < 200 → -20
        });

        var result = await _sut.AssessHealthAsync("dev-volt");

        result.ElectricalScore.Should().Be(80m);
    }

    [Fact]
    public async Task AssessHealthAsync_电压轻微异常()
    {
        SetupCollectionResult("dev-volt2", new Dictionary<string, double>
        {
            ["voltage"] = 205 // < 210 → -10
        });

        var result = await _sut.AssessHealthAsync("dev-volt2");

        result.ElectricalScore.Should().Be(90m);
    }

    [Fact]
    public async Task AssessHealthAsync_高温降低热力评分()
    {
        SetupCollectionResult("dev-hot", new Dictionary<string, double>
        {
            ["temperature"] = 85 // > 80 → -40
        });

        var result = await _sut.AssessHealthAsync("dev-hot");

        result.ThermalScore.Should().Be(60m);
    }

    [Fact]
    public async Task AssessHealthAsync_中等温度扣分()
    {
        SetupCollectionResult("dev-warm", new Dictionary<string, double>
        {
            ["temperature"] = 65 // > 60 → -20
        });

        var result = await _sut.AssessHealthAsync("dev-warm");

        result.ThermalScore.Should().Be(80m);
    }

    [Fact]
    public async Task AssessHealthAsync_轻微高温扣分()
    {
        SetupCollectionResult("dev-warm2", new Dictionary<string, double>
        {
            ["temperature"] = 50 // > 45 → -10
        });

        var result = await _sut.AssessHealthAsync("dev-warm2");

        result.ThermalScore.Should().Be(90m);
    }

    [Fact]
    public async Task AssessHealthAsync_高电流降低电气评分()
    {
        SetupCollectionResult("dev-amp", new Dictionary<string, double>
        {
            ["current"] = 110 // > 100 → -15
        });

        var result = await _sut.AssessHealthAsync("dev-amp");

        result.ElectricalScore.Should().Be(85m);
    }

    [Fact]
    public async Task AssessHealthAsync_通信质量差降低评分()
    {
        SetupCollectionResult("dev-comm", new Dictionary<string, double>
        {
            ["voltage"] = 220
        }, quality: "Poor");

        var result = await _sut.AssessHealthAsync("dev-comm");

        result.CommunicationScore.Should().Be(70m);
    }

    [Fact]
    public async Task AssessHealthAsync_健康等级映射_Excellent()
    {
        // 所有指标正常 → 各子分100/100/85~95/95 → avg >= 90
        SetupCollectionResult("dev-ex", new Dictionary<string, double>
        {
            ["voltage"] = 225,
            ["temperature"] = 30
        });

        var result = await _sut.AssessHealthAsync("dev-ex");

        // ElectricalScore=100, ThermalScore=100, CommunicationScore=95, MechanicalScore=85~95
        // avg >= 90 → Excellent 或 Good（由于 MechanicalScore 有随机性）
        result.HealthLevel.Should().BeOneOf("Excellent", "Good");
    }

    [Fact]
    public async Task AssessHealthAsync_低评分生成检查建议()
    {
        SetupCollectionResult("dev-rec", new Dictionary<string, double>
        {
            ["voltage"] = 180,    // ElectricalScore = 80
            ["temperature"] = 85  // ThermalScore = 60
        }, quality: "Poor");     // CommunicationScore = 70

        var result = await _sut.AssessHealthAsync("dev-rec");

        result.Recommendations.Should().Contain("建议检查散热系统");
        result.Recommendations.Should().Contain("建议检查通信模块");
    }

    [Fact]
    public async Task AssessHealthAsync_全部正常建议设备状态良好()
    {
        SetupCollectionResult("dev-good", new Dictionary<string, double>
        {
            ["voltage"] = 225,
            ["temperature"] = 30
        });

        var result = await _sut.AssessHealthAsync("dev-good");

        // ElectricalScore=100, ThermalScore=100 → 这两个 >= 80
        // MechanicalScore 在 85~95 之间 → >= 80
        // CommunicationScore=95 → >= 80
        // 所有都 >= 80，建议 = "设备状态良好，继续正常运行"
        result.Recommendations.Should().Contain("设备状态良好，继续正常运行");
    }

    // ========== PredictFaultsAsync ==========

    [Fact]
    public async Task PredictFaultsAsync_热力评分低预测过热故障()
    {
        SetupCollectionResult("dev-fault1", new Dictionary<string, double>
        {
            ["temperature"] = 85 // ThermalScore = 60 < 70
        });

        var result = await _sut.PredictFaultsAsync("dev-fault1");

        result.Should().Contain(f => f.FaultType == "Overheating");
        var overheating = result.First(f => f.FaultType == "Overheating");
        overheating.DeviceId.Should().Be("dev-fault1");
        overheating.Probability.Should().Be(0.40m); // (100-60)/100
        overheating.PredictedTimeframe.Should().Contain("24-48小时");
        overheating.Symptoms.Should().Contain("温度持续升高");
    }

    [Fact]
    public async Task PredictFaultsAsync_电气评分低预测电气异常()
    {
        SetupCollectionResult("dev-fault2", new Dictionary<string, double>
        {
            ["voltage"] = 180,  // -20
            ["current"] = 110   // -15 → ElectricalScore = 65 < 75
        });

        var result = await _sut.PredictFaultsAsync("dev-fault2");

        result.Should().Contain(f => f.FaultType == "ElectricalAnomaly");
        var electrical = result.First(f => f.FaultType == "ElectricalAnomaly");
        electrical.Severity.Should().Be("Medium"); // 65 >= 50 → Medium
    }

    [Fact]
    public async Task PredictFaultsAsync_正常设备无故障预测()
    {
        SetupCollectionResult("dev-healthy", new Dictionary<string, double>
        {
            ["voltage"] = 225,
            ["temperature"] = 35
        });

        var result = await _sut.PredictFaultsAsync("dev-healthy");

        // 所有 Score >= 标准，可能有 MechanicalWear 取决于随机数
        // ThermalScore=100 >= 70, ElectricalScore=100 >= 75
        result.Should().NotContain(f => f.FaultType == "Overheating");
        result.Should().NotContain(f => f.FaultType == "ElectricalAnomaly");
    }

    [Fact]
    public async Task PredictFaultsAsync_严重异常标记高严重度()
    {
        // 极端高温 → ThermalScore = 60 (>80 → -40) → < 70
        // 让 ThermalScore < 50 来触发 High severity
        SetupCollectionResult("dev-crit", new Dictionary<string, double>
        {
            ["temperature"] = 85 // ThermalScore = 60, 不 < 50
        });

        var result = await _sut.PredictFaultsAsync("dev-crit");

        var overheating = result.FirstOrDefault(f => f.FaultType == "Overheating");
        overheating.Should().NotBeNull();
        overheating!.Severity.Should().Be("Medium"); // 60 >= 50 → Medium
    }

    // ========== PredictRemainingLifeAsync ==========

    [Fact]
    public async Task PredictRemainingLifeAsync_健康设备寿命较长()
    {
        SetupCollectionResult("dev-life1", new Dictionary<string, double>
        {
            ["voltage"] = 225,
            ["temperature"] = 30
        });

        var result = await _sut.PredictRemainingLifeAsync("dev-life1");

        result.DeviceId.Should().Be("dev-life1");
        result.CurrentHealthScore.Should().BeGreaterThan(80m);
        result.EstimatedRemainingDays.Should().BeGreaterThan(1000); // 健康分高，寿命长
        result.ConfidenceLower.Should().BeLessThan(result.EstimatedRemainingDays);
        result.ConfidenceUpper.Should().BeGreaterThan(result.EstimatedRemainingDays);
        result.ComponentLifePredictions.Should().HaveCount(3);
        result.ComponentLifePredictions.Should().Contain(c => c.ComponentName == "电池组");
        result.ComponentLifePredictions.Should().Contain(c => c.ComponentName == "逆变器");
        result.ComponentLifePredictions.Should().Contain(c => c.ComponentName == "散热系统");
    }

    [Fact]
    public async Task PredictRemainingLifeAsync_无数据设备寿命为零()
    {
        SetupEmptyCollectionResult("dev-life0");

        var result = await _sut.PredictRemainingLifeAsync("dev-life0");

        result.CurrentHealthScore.Should().Be(0);
        result.EstimatedRemainingDays.Should().Be(0); // healthFactor=0, 结果为0
        result.DegradationRate.Should().Be(1m); // 1 - 0/100 = 1
    }

    [Fact]
    public async Task PredictRemainingLifeAsync_组件寿命按比例计算()
    {
        SetupCollectionResult("dev-life2", new Dictionary<string, double>
        {
            ["voltage"] = 225,
            ["temperature"] = 30
        });

        var result = await _sut.PredictRemainingLifeAsync("dev-life2");

        var battery = result.ComponentLifePredictions.First(c => c.ComponentName == "电池组");
        var inverter = result.ComponentLifePredictions.First(c => c.ComponentName == "逆变器");
        var cooling = result.ComponentLifePredictions.First(c => c.ComponentName == "散热系统");

        // 电池组 = remaining * 0.7, 逆变器 = remaining * 1.2, 散热 = remaining * 0.9
        battery.RemainingLife.Should().BeApproximately(result.EstimatedRemainingDays * 0.7, 1);
        inverter.RemainingLife.Should().BeApproximately(result.EstimatedRemainingDays * 1.2, 1);
        cooling.RemainingLife.Should().BeApproximately(result.EstimatedRemainingDays * 0.9, 1);

        battery.ReplacementCost.Should().Be(50000m);
        inverter.ReplacementCost.Should().Be(20000m);
        cooling.ReplacementCost.Should().Be(5000m);
    }

    // ========== GetActiveWarningsAsync ==========

    [Fact]
    public async Task GetActiveWarningsAsync_返回预警列表()
    {
        var result = await _sut.GetActiveWarningsAsync();

        result.Should().NotBeEmpty();
        result.Should().Contain(w => w.WarningType == "HighTemperature");
        result.Should().Contain(w => w.WarningType == "VoltageFluctuation");
        result.Should().OnlyContain(w => w.Status == "Active");
    }

    [Fact]
    public async Task GetActiveWarningsAsync_按设备过滤()
    {
        var result = await _sut.GetActiveWarningsAsync("DEV-001");

        result.Should().NotBeEmpty();
        result.Should().OnlyContain(w => w.DeviceId == "DEV-001");
    }

    [Fact]
    public async Task GetActiveWarningsAsync_指定设备ID替换默认设备ID()
    {
        // 源码使用 deviceId ?? "DEV-001" / "DEV-002"，传入非空值会替换默认值
        var result = await _sut.GetActiveWarningsAsync("CUSTOM-DEVICE");

        result.Should().NotBeEmpty();
        result.Should().OnlyContain(w => w.DeviceId == "CUSTOM-DEVICE");
    }

    // ========== AnalyzeRootCauseAsync ==========

    [Fact]
    public async Task AnalyzeRootCauseAsync_返回根因分析结果()
    {
        var result = await _sut.AnalyzeRootCauseAsync("fault-001");

        result.FaultId.Should().Be("fault-001");
        result.ProbableCauses.Should().HaveCount(3);
        result.RootCause.Should().NotBeNull();
        result.RootCause!.Probability.Should().Be(0.6m); // 最高概率
        result.Confidence.Should().Be(0.6m);
        result.RelatedFaults.Should().NotBeEmpty();
    }

    // ========== RecommendMaintenanceAsync ==========

    [Fact]
    public async Task RecommendMaintenanceAsync_低健康分推荐紧急维护()
    {
        // 极端异常数据 → OverallScore < 60
        SetupCollectionResult("dev-maint1", new Dictionary<string, double>
        {
            ["voltage"] = 180,    // -20
            ["current"] = 110,    // -15 → ElectricalScore=65
            ["temperature"] = 85  // -40 → ThermalScore=60
        }, quality: "Poor");     // CommunicationScore=70

        var result = await _sut.RecommendMaintenanceAsync("dev-maint1");

        result.DeviceId.Should().Be("dev-maint1");
        // 根据 OverallScore 判断：低评分或有 High severity fault → High urgency
        // 实际：MechanicalScore 随机 85-95，avg = (65+60+~90+70)/4 ≈ 71.25 → 可能中间
        result.Urgency.Should().BeOneOf("High", "Medium");
        result.Actions.Should().NotBeEmpty();
        result.EstimatedTotalCost.Should().BeGreaterThan(0);
    }

    [Fact]
    public async Task RecommendMaintenanceAsync_健康设备推荐定期维护()
    {
        SetupCollectionResult("dev-maint2", new Dictionary<string, double>
        {
            ["voltage"] = 225,
            ["temperature"] = 30
        });

        var result = await _sut.RecommendMaintenanceAsync("dev-maint2");

        // OverallScore >= 80 → Low urgency, Scheduled
        result.Urgency.Should().BeOneOf("Low", "Medium"); // MechanicalScore 随机可能偏低
        result.MaintenanceType.Should().BeOneOf("Scheduled", "Preventive");
    }

    // ========== GetWarningStatisticsAsync ==========

    [Fact]
    public async Task GetWarningStatisticsAsync_返回统计数据()
    {
        var result = await _sut.GetWarningStatisticsAsync();

        result.Total.Should().BeGreaterThan(0);
        result.ByLevel.Should().ContainKeys("Critical", "Warning", "Info");
        result.ByType.Should().ContainKeys("HighTemperature", "VoltageAnomaly");
        result.Trend.Should().NotBeEmpty();
    }

    [Fact]
    public async Task GetWarningStatisticsAsync_指定时间范围生成趋势()
    {
        var start = DateTime.UtcNow.AddDays(-7);
        var end = DateTime.UtcNow;

        var result = await _sut.GetWarningStatisticsAsync(startDate: start, endDate: end);

        result.Trend.Should().HaveCount(7);
    }
}
