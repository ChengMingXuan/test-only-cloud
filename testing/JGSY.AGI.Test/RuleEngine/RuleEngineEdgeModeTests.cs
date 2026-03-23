using FluentAssertions;
using JGSY.AGI.RuleEngine.Edge;
using Microsoft.Extensions.Configuration;
using Xunit;

namespace JGSY.AGI.Test.RuleEngine;

/// <summary>
/// 规则引擎 Edge 边缘模式 — 纯内存单元测试
/// 覆盖：配置验证、SQLite 建表、同步模型、离线状态、数据清理逻辑
/// </summary>
public class RuleEngineEdgeModeTests
{
    #region 配置模型测试

    [Fact]
    public void EdgeRuleOptions_ShouldHaveCorrectDefaults()
    {
        var opts = new EdgeRuleOptions();
        opts.Enabled.Should().BeFalse();
        opts.NodeId.Should().BeEmpty();
        opts.NodeName.Should().Be("edge-ruleengine-01");
        opts.CloudEndpoint.Should().BeEmpty();
        opts.CloudApiKey.Should().BeEmpty();
        opts.Offline.Should().NotBeNull();
        opts.Sync.Should().NotBeNull();
        opts.Mqtt.Should().NotBeNull();
    }

    [Fact]
    public void OfflineModeConfig_ShouldHaveReasonableDefaults()
    {
        var cfg = new RuleOfflineModeConfig();
        cfg.HeartbeatIntervalSeconds.Should().Be(30);
        cfg.OfflineThreshold.Should().Be(3);
        cfg.MaxOfflineLogRecords.Should().Be(100000);
        cfg.RetentionDays.Should().Be(7);
    }

    [Fact]
    public void SyncConfig_ShouldHaveReasonableDefaults()
    {
        var cfg = new RuleSyncConfig();
        cfg.IntervalSeconds.Should().Be(300);
        cfg.LogUploadBatchSize.Should().Be(200);
        cfg.MaxRetries.Should().Be(5);
    }

    [Fact]
    public void MqttTriggerConfig_ShouldHaveReasonableDefaults()
    {
        var cfg = new RuleMqttTriggerConfig();
        cfg.Enabled.Should().BeTrue();
        cfg.BrokerHost.Should().Be("localhost");
        cfg.BrokerPort.Should().Be(1883);
        cfg.UseTls.Should().BeFalse();
        cfg.ClientId.Should().Be("ruleengine-edge");
        cfg.Username.Should().BeEmpty();
        cfg.Password.Should().BeEmpty();
        cfg.Topics.Should().HaveCount(4);
        cfg.Topics.Should().Contain("device/+/telemetry");
        cfg.Topics.Should().Contain("device/+/alarm");
    }

    [Fact]
    public void EdgeRuleOptions_ShouldSetAllProperties()
    {
        var opts = new EdgeRuleOptions
        {
            Enabled = true,
            NodeId = "edge-node-01",
            NodeName = "测试边缘节点",
            CloudEndpoint = "https://cloud.example.com",
            CloudApiKey = "test-key-123",
            Offline = new RuleOfflineModeConfig
            {
                HeartbeatIntervalSeconds = 15,
                OfflineThreshold = 5,
                MaxOfflineLogRecords = 50000,
                RetentionDays = 3
            },
            Sync = new RuleSyncConfig
            {
                IntervalSeconds = 60,
                LogUploadBatchSize = 500,
                MaxRetries = 10
            },
            Mqtt = new RuleMqttTriggerConfig
            {
                Enabled = true,
                BrokerHost = "mqtt.edge.local",
                BrokerPort = 8883,
                UseTls = true,
                ClientId = "ruleengine-edge-test",
                Topics = ["device/+/telemetry", "custom/+/data"]
            }
        };

        opts.Enabled.Should().BeTrue();
        opts.NodeId.Should().Be("edge-node-01");
        opts.CloudEndpoint.Should().Contain("cloud.example.com");
        opts.Offline.HeartbeatIntervalSeconds.Should().Be(15);
        opts.Sync.LogUploadBatchSize.Should().Be(500);
        opts.Mqtt.BrokerPort.Should().Be(8883);
        opts.Mqtt.UseTls.Should().BeTrue();
        opts.Mqtt.Topics.Should().HaveCount(2);
    }

    #endregion

    #region SQLite 连接工厂测试

    [Fact]
    public void SqliteRuleConnectionFactory_ShouldCreateConnection()
    {
        // 使用内存 SQLite 配置
        var config = new ConfigurationBuilder()
            .AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["ConnectionStrings:SQLite"] = "Data Source=:memory:"
            })
            .Build();

        var factory = new SqliteRuleConnectionFactory(config);

        using var conn = factory.CreateConnection();
        conn.Open();
        conn.State.Should().Be(System.Data.ConnectionState.Open);
    }

    [Fact]
    public void SqliteRuleConnectionFactory_ConnectionString_ShouldMatchConfig()
    {
        var config = new ConfigurationBuilder()
            .AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["ConnectionStrings:SQLite"] = "Data Source=/tmp/test_edge.db"
            })
            .Build();

        var factory = new SqliteRuleConnectionFactory(config);
        factory.ConnectionString.Should().Contain("test_edge.db");
    }

    #endregion

    #region 同步数据模型测试

    [Fact]
    public void RuleSyncSnapshot_ShouldInitializeWithDefaults()
    {
        var snapshot = new RuleSyncSnapshot();
        snapshot.IsFullSync.Should().BeFalse();
        snapshot.Chains.Should().BeEmpty();
        snapshot.Nodes.Should().BeEmpty();
        snapshot.Connections.Should().BeEmpty();
        snapshot.AlarmDefinitions.Should().BeEmpty();
    }

    [Fact]
    public void RuleSyncChain_ShouldSetAllFields()
    {
        var chain = new RuleSyncChain
        {
            Id = Guid.NewGuid().ToString(),
            Name = "充电桩告警规则",
            Description = "监控充电桩异常",
            DeviceType = "charging_pile",
            TriggerType = "telemetry",
            Priority = 10,
            IsEnabled = 1,
            Config = "{\"threshold\": 85}",
            RowVersion = 1
        };

        chain.Name.Should().Contain("充电桩");
        chain.TriggerType.Should().Be("telemetry");
        chain.Priority.Should().Be(10);
        chain.IsEnabled.Should().Be(1);
    }

    [Fact]
    public void RuleSyncNode_ShouldPreservePositionData()
    {
        var node = new RuleSyncNode
        {
            Id = Guid.NewGuid().ToString(),
            ChainId = Guid.NewGuid().ToString(),
            Name = "温度阈值判断",
            NodeType = "filter",
            SubType = "threshold",
            Config = "{\"field\": \"temperature\", \"op\": \">\", \"value\": 85}",
            PositionX = 250.5,
            PositionY = 120.3,
            RowVersion = 1
        };

        node.NodeType.Should().Be("filter");
        node.PositionX.Should().BeApproximately(250.5, 0.01);
        node.PositionY.Should().BeApproximately(120.3, 0.01);
    }

    [Fact]
    public void RuleSyncConnection_ShouldDefaultConditionType()
    {
        var conn = new RuleSyncConnection();
        conn.ConditionType.Should().Be("success");
    }

    [Fact]
    public void RuleSyncAlarmDef_ShouldDefaultSeverity()
    {
        var alarm = new RuleSyncAlarmDef();
        alarm.Severity.Should().Be("warning");
    }

    #endregion

    #region 边缘上传记录模型测试

    [Fact]
    public void EdgeExecutionLogRecord_ShouldSetAllFields()
    {
        var log = new EdgeExecutionLogRecord
        {
            Id = Guid.NewGuid().ToString(),
            RuleChainId = Guid.NewGuid().ToString(),
            TriggerType = "telemetry",
            TriggerData = "{\"deviceId\": \"d1\", \"temperature\": 90}",
            ExecutionResult = "{\"actions\": [\"alarm\"]}",
            ExecutionTimeMs = 45,
            Success = 1,
            CreatedAt = DateTime.UtcNow.ToString("O")
        };

        log.TriggerType.Should().Be("telemetry");
        log.ExecutionTimeMs.Should().Be(45);
        log.Success.Should().Be(1);
        log.ErrorMessage.Should().BeNull();
    }

    [Fact]
    public void EdgeAlarmInstanceRecord_ShouldSetAllFields()
    {
        var alarm = new EdgeAlarmInstanceRecord
        {
            Id = Guid.NewGuid().ToString(),
            AlarmDefinitionId = Guid.NewGuid().ToString(),
            RuleChainId = Guid.NewGuid().ToString(),
            DeviceId = Guid.NewGuid().ToString(),
            Severity = "critical",
            Message = "温度超限告警",
            TriggeredAt = DateTime.UtcNow.ToString("O"),
            Status = "active"
        };

        alarm.Severity.Should().Be("critical");
        alarm.Message.Should().Contain("温度");
        alarm.ResolvedAt.Should().BeNull();
        alarm.Status.Should().Be("active");
    }

    #endregion

    #region 离线状态模型测试

    [Fact]
    public void EdgeRuleNodeStatus_ShouldReportNodeInfo()
    {
        var status = new EdgeRuleNodeStatus
        {
            NodeId = "edge-01",
            NodeName = "厂区边缘节点",
            IsOffline = true,
            OfflineSince = DateTime.UtcNow.AddMinutes(-30),
            LastHeartbeat = DateTime.UtcNow.AddMinutes(-31),
            ConsecutiveFailures = 5,
            CloudEndpoint = "https://cloud.jgsy.com"
        };

        status.IsOffline.Should().BeTrue();
        status.ConsecutiveFailures.Should().Be(5);
        status.NodeId.Should().Be("edge-01");
        status.OfflineSince.Should().NotBeNull();
        status.LastHeartbeat.Should().NotBeNull();
    }

    [Fact]
    public void EdgeRuleNodeStatus_OnlineNode_ShouldHaveZeroFailures()
    {
        var status = new EdgeRuleNodeStatus
        {
            NodeId = "edge-02",
            NodeName = "在线节点",
            IsOffline = false,
            ConsecutiveFailures = 0,
            CloudEndpoint = "https://cloud.jgsy.com"
        };

        status.IsOffline.Should().BeFalse();
        status.ConsecutiveFailures.Should().Be(0);
        status.OfflineSince.Should().BeNull();
    }

    #endregion

    #region 完整同步快照测试

    [Fact]
    public void FullSyncSnapshot_ShouldContainAllComponents()
    {
        var snapshot = new RuleSyncSnapshot
        {
            IsFullSync = true,
            Chains =
            [
                new RuleSyncChain { Id = "c1", Name = "规则链1", TriggerType = "telemetry", IsEnabled = 1, RowVersion = 1 },
                new RuleSyncChain { Id = "c2", Name = "规则链2", TriggerType = "event", IsEnabled = 0, RowVersion = 2 }
            ],
            Nodes =
            [
                new RuleSyncNode { Id = "n1", ChainId = "c1", Name = "输入", NodeType = "input", PositionX = 0, PositionY = 0 },
                new RuleSyncNode { Id = "n2", ChainId = "c1", Name = "过滤", NodeType = "filter", PositionX = 200, PositionY = 0 },
                new RuleSyncNode { Id = "n3", ChainId = "c1", Name = "输出", NodeType = "action", PositionX = 400, PositionY = 0 }
            ],
            Connections =
            [
                new RuleSyncConnection { Id = "conn1", ChainId = "c1", SourceNodeId = "n1", TargetNodeId = "n2", ConditionType = "success" },
                new RuleSyncConnection { Id = "conn2", ChainId = "c1", SourceNodeId = "n2", TargetNodeId = "n3", ConditionType = "true" }
            ],
            AlarmDefinitions =
            [
                new RuleSyncAlarmDef { Id = "a1", Name = "温度告警", Severity = "critical" }
            ]
        };

        snapshot.IsFullSync.Should().BeTrue();
        snapshot.Chains.Should().HaveCount(2);
        snapshot.Nodes.Should().HaveCount(3);
        snapshot.Connections.Should().HaveCount(2);
        snapshot.AlarmDefinitions.Should().HaveCount(1);

        // 验证链路关系
        snapshot.Connections.Should().AllSatisfy(c => c.ChainId.Should().Be("c1"));
        snapshot.Nodes.Where(n => n.ChainId == "c1").Should().HaveCount(3);
    }

    #endregion
}
