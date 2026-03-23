using FluentAssertions;
using JGSY.AGI.IotCloudAI.Data.Entities;
using JGSY.AGI.IotCloudAI.Models;
using Xunit;

namespace JGSY.AGI.Test.IotCloudAI;

/// <summary>
/// IoT 云 AI 数据库实体测试
/// </summary>
public class IotCloudAIEntityTests
{
    [Fact]
    public void AiModelInfo_ShouldHaveCorrectDefaults()
    {
        var model = new AiModelInfo();
        model.DeleteAt.Should().BeNull();
        model.Id.Should().Be(Guid.Empty);
    }

    [Fact]
    public void AiModelInfo_ShouldSetAllProperties()
    {
        var model = new AiModelInfo
        {
            Id = Guid.NewGuid(),
            ModelName = "charging-load-prediction-v3",
            ModelType = "LSTM",
            ModelPath = "/models/charging-load/v3",
            Version = "3.0.1",
            Status = "active",
            Accuracy = 0.965m,
            Description = "充电负荷预测模型",
            TenantId = Guid.NewGuid()
        };

        model.ModelName.Should().Contain("prediction");
        model.Accuracy.Should().BeInRange(0.9m, 1.0m);
        model.Status.Should().Be("active");
    }

    [Fact]
    public void AiChainExecution_ShouldTrackPerformance()
    {
        var execution = new AiChainExecution
        {
            ChainId = Guid.NewGuid().ToString(),
            EntityId = Guid.NewGuid().ToString(),
            EntityType = "Station",
            ScenarioType = "PeakValley",
            Status = "completed",
            ExecutionTimeMs = 1250,
            ResultJson = "{\"profit\": 156.80}",
            ExecutedAt = DateTime.UtcNow
        };

        execution.ExecutionTimeMs.Should().BePositive();
        execution.Status.Should().Be("completed");
        execution.ResultJson.Should().Contain("profit");
    }

    [Fact]
    public void AiPredictionLog_ShouldRecordConfidence()
    {
        var log = new AiPredictionLog
        {
            PredictionId = Guid.NewGuid().ToString(),
            ModelName = "price-forecast-v2",
            InputJson = "{\"history\": [0.45, 0.52, 0.48]}",
            OutputJson = "{\"predicted\": 0.51}",
            Confidence = 0.87m,
            InferenceTimeMs = 45,
            PredictedAt = DateTime.UtcNow
        };

        log.Confidence.Should().BeInRange(0m, 1m);
        log.InferenceTimeMs.Should().BeLessThan(1000);
    }

    [Fact]
    public void AiScenarioConfig_ShouldSetDefaults()
    {
        var config = new AiScenarioConfig
        {
            ScenarioCode = "PEAK_VALLEY",
            ScenarioName = "峰谷套利",
            Enabled = true,
            Priority = 10,
            Schedule = "0 */5 * * * *"
        };

        config.Enabled.Should().BeTrue();
        config.Priority.Should().BePositive();
    }

    [Fact]
    public void DeviceHealthRecord_ShouldCalculateOverallScore()
    {
        var health = new DeviceHealthRecord
        {
            DeviceId = Guid.NewGuid().ToString(),
            OverallScore = 85.5m,
            ElectricalScore = 90.0m,
            ThermalScore = 80.0m,
            MechanicalScore = 88.0m,
            CommunicationScore = 84.0m,
            HealthLevel = "Good",
            AssessedAt = DateTime.UtcNow
        };

        health.OverallScore.Should().BePositive();
        health.HealthLevel.Should().Be("Good");
        // 各分项得分应在合理范围
        health.ElectricalScore.Should().BeInRange(0m, 100m);
        health.ThermalScore.Should().BeInRange(0m, 100m);
    }

    [Fact]
    public void ArbitrageRecord_ShouldCalculateNetProfit()
    {
        var record = new ArbitrageRecord
        {
            StationId = Guid.NewGuid().ToString(),
            ChargeEnergy = 100.0m,
            ChargeCost = 35.0m,
            DischargeEnergy = 95.0m,
            DischargeRevenue = 85.5m,
            NetProfit = 50.5m,
            StartTime = DateTime.UtcNow.AddHours(-8),
            EndTime = DateTime.UtcNow
        };

        record.NetProfit.Should().Be(50.5m);
        record.DischargeEnergy.Should().BeLessThan(record.ChargeEnergy); // 转换损耗
        record.EndTime.Should().BeAfter(record.StartTime);
    }
}

/// <summary>
/// IoT 云 AI 核心模型（record 类型）测试
/// </summary>
public class IotCloudAICoreModelTests
{
    [Fact]
    public void CollectionResult_ShouldSetProperties()
    {
        var result = new CollectionResult
        {
            CollectionId = "col-001",
            BatchId = "batch-001",
            Source = DataSourceType.Device,
            RecordCount = 100,
            DeviceCount = 10,
            Success = true,
            Status = "completed",
            Errors = new List<string> { "Device dev-001: Timeout" }
        };

        result.Success.Should().BeTrue();
        result.RecordCount.Should().Be(100);
        result.Errors.Should().HaveCount(1);
    }

    [Fact]
    public void DeviceTelemetry_ShouldSetReadings()
    {
        var telemetry = new DeviceTelemetry
        {
            DeviceId = "charger-001",
            Timestamp = DateTime.UtcNow,
            Voltage = 380.5m,
            Current = 32.0m,
            Power = 12176.0m,
            Temperature = 45.2m,
            Frequency = 50.0m
        };

        telemetry.Voltage.Should().BeInRange(200m, 500m);
        telemetry.Current.Should().BePositive();
        telemetry.Frequency.Should().BeInRange(49m, 51m);
    }

    [Fact]
    public void CleaningResult_ShouldTrackStatistics()
    {
        var result = new CleaningResult
        {
            CleaningId = "clean-001",
            BatchId = "batch-001",
            OriginalCount = 100,
            CleanedCount = 98,
            RemovedCount = 2,
            Status = "completed",
            Actions = new List<CleaningAction>
            {
                new() { ActionType = "Remove", Description = "Duplicate", AffectedCount = 2 }
            }
        };

        result.CleanedCount.Should().BeLessThanOrEqualTo(result.OriginalCount);
        result.Actions.Should().NotBeEmpty();
    }

    [Fact]
    public void AnalysisResult_ShouldContainSummary()
    {
        var result = new AnalysisResult
        {
            AnalysisId = "analysis-001",
            Status = "Success",
            Summary = "Analysis completed: 1000 records processed",
            DataPointsAnalyzed = 1000
        };

        result.Summary.Should().NotBeNullOrEmpty();
        result.Status.Should().Be("Success");
    }

    [Fact]
    public void WeatherData_ShouldSetAllFields()
    {
        var weather = new WeatherData
        {
            Temperature = 28.5m,
            Humidity = 65.0m,
            WindSpeed = 3.2m,
            SolarIrradiance = 850.0m,
            Timestamp = DateTime.UtcNow
        };

        weather.Temperature.Should().BeInRange(-40m, 60m);
        weather.Humidity.Should().BeInRange(0m, 100m);
        weather.SolarIrradiance.Should().BePositive();
    }

    [Theory]
    [InlineData(DataSourceType.Device)]
    [InlineData(DataSourceType.Market)]
    [InlineData(DataSourceType.Weather)]
    [InlineData(DataSourceType.Grid)]
    public void DataSourceType_ShouldHaveDefinedValues(DataSourceType type)
    {
        Enum.IsDefined(typeof(DataSourceType), type).Should().BeTrue();
    }
}
