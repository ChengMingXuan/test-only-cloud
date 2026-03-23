using FluentAssertions;
using JGSY.AGI.Ingestion.Entities;
using JGSY.AGI.Ingestion.Models;
using Xunit;

namespace JGSY.AGI.Test.Ingestion;

/// <summary>
/// 数据采集服务实体与 DTO 单元测试
/// </summary>
public class IngestionEntityTests
{
    #region DataSource 测试

    [Fact]
    public void DataSource_ShouldHaveCorrectDefaults()
    {
        var source = new DataSource();
        source.DeleteAt.Should().BeNull();
        source.DeviceCount.Should().Be(0);
    }

    [Fact]
    public void DataSource_ShouldSetAllProperties()
    {
        var source = new DataSource
        {
            Name = "OCPP 充电桩数据源",
            SourceType = "ocpp",
            Protocol = "OCPP2.0",
            ConnectionAddress = "wss://charger.jgsy.com:9000",
            AuthType = "certificate",
            DataFormat = "json",
            ConnectionStatus = "connected",
            DeviceCount = 50
        };

        source.Name.Should().NotBeEmpty();
        source.Protocol.Should().Be("OCPP2.0");
        source.ConnectionStatus.Should().Be("connected");
        source.DeviceCount.Should().BePositive();
    }

    #endregion

    #region IngestionTask 测试

    [Fact]
    public void IngestionTask_ShouldHaveCorrectDefaults()
    {
        var task = new IngestionTask();
        task.Status.Should().Be("stopped");
        task.TotalCollected.Should().Be(0);
        task.TotalFailed.Should().Be(0);
        task.DeleteAt.Should().BeNull();
    }

    [Fact]
    public void IngestionTask_ShouldSetAllProperties()
    {
        var task = new IngestionTask
        {
            Name = "充电桩遥测采集",
            TaskType = "realtime",
            ProtocolType = "mqtt",
            IntervalSeconds = 10,
            Status = "running",
            CronExpression = "*/10 * * * * *",
            TotalCollected = 15000,
            TotalFailed = 3
        };

        task.IntervalSeconds.Should().BePositive();
        task.Status.Should().Be("running");
        task.TotalFailed.Should().BeLessThan(task.TotalCollected);
    }

    [Fact]
    public void IngestionTask_FailureRate_ShouldBeCalculable()
    {
        var task = new IngestionTask
        {
            TotalCollected = 10000,
            TotalFailed = 50
        };

        var failureRate = task.TotalCollected > 0
            ? (double)task.TotalFailed / task.TotalCollected * 100
            : 0;

        failureRate.Should().BeInRange(0, 100);
        failureRate.Should().BeLessThan(1); // 失败率应低于 1%
    }

    #endregion

    #region IngestionMessage 测试

    [Fact]
    public void IngestionMessage_ShouldSetAllProperties()
    {
        var deviceId = Guid.NewGuid();
        var msg = new IngestionMessage
        {
            DeviceId = deviceId,
            ProtocolType = "ocpp",
            RawPayload = "{\"action\":\"MeterValues\"}",
            ReceivedTime = DateTime.UtcNow
        };

        msg.DeviceId.Should().Be(deviceId);
        msg.RawPayload.Should().Contain("MeterValues");
        msg.ReceivedTime.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(5));
    }

    #endregion
}

/// <summary>
/// 数据采集 DTO 测试
/// </summary>
public class IngestionDtoTests
{
    [Fact]
    public void RawIngestionRequest_ShouldHaveRequiredFields()
    {
        var request = new RawIngestionRequest
        {
            DeviceId = Guid.NewGuid(),
            ProtocolType = "AUTO",
            Payload = "{\"voltage\": 380, \"current\": 32}",
            ReceivedTime = DateTime.UtcNow
        };

        request.DeviceId.Should().NotBeEmpty();
        request.Payload.Should().NotBeEmpty();
        request.ProtocolType.Should().Be("AUTO");
    }

    [Fact]
    public void RawIngestionRequest_DefaultProtocol_ShouldBeAuto()
    {
        var request = new RawIngestionRequest { DeviceId = Guid.NewGuid(), Payload = "{}" };
        request.ProtocolType.Should().Be("AUTO");
    }

    [Fact]
    public void ProcessingResultDto_ShouldSetAllProperties()
    {
        var result = new ProcessingResultDto
        {
            MessageId = Guid.NewGuid(),
            DeviceId = Guid.NewGuid(),
            ProtocolType = "ocpp",
            Status = "processed",
            Published = true,
            IsReplay = false
        };

        result.Published.Should().BeTrue();
        result.IsReplay.Should().BeFalse();
        result.Status.Should().Be("processed");
    }

    [Fact]
    public void ProcessingResultDto_WithError_ShouldHaveMessage()
    {
        var result = new ProcessingResultDto
        {
            MessageId = Guid.NewGuid(),
            DeviceId = Guid.NewGuid(),
            Status = "failed",
            Published = false,
            ErrorMessage = "Invalid payload format"
        };

        result.Status.Should().Be("failed");
        result.ErrorMessage.Should().NotBeNullOrEmpty();
        result.Published.Should().BeFalse();
    }
}
