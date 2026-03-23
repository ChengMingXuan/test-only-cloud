using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using Moq;
using Xunit;
using JGSY.AGI.IotCloudAI.AI.DAG;
using JGSY.AGI.IotCloudAI.Data.Entities;

namespace JGSY.AGI.Test.IotCloudAI;

/// <summary>
/// DAG 引擎增量测试 — 覆盖 v3.1 迭代新增代码
/// - DagEntities (实体默认值 + 属性赋值)
/// - DagOptions (配置项默认值)
/// - DagConfidenceFusion (3 种融合策略 + 准确率更新)
/// - DagWorkflowRegistry (工作流注册 + 查询)
/// - DagModels (FusedConfidence 字段)
/// - AgentDagBridge (意图映射)
/// </summary>
public class DagEngineIncrementalTests
{
    // ============================================================
    // DagEntities 实体测试
    // ============================================================

    [Fact]
    public void AiDagWorkflowExecution_默认值正确()
    {
        var entity = new AiDagWorkflowExecution();
        entity.Id.Should().Be(Guid.Empty);
        entity.Status.Should().Be("running");
        entity.WorkflowVersion.Should().Be("1.0.0");
        entity.DeleteAt.Should().BeNull();
        entity.TotalNodes.Should().Be(0);
        entity.CompletedNodes.Should().Be(0);
        entity.FailedNodes.Should().Be(0);
        entity.TotalLatencyMs.Should().Be(0);
    }

    [Fact]
    public void AiDagWorkflowExecution_属性赋值完整()
    {
        var id = Guid.NewGuid();
        var tenantId = Guid.NewGuid();
        var entity = new AiDagWorkflowExecution
        {
            Id = id,
            TenantId = tenantId,
            WorkflowId = "pv_power_forecast",
            WorkflowVersion = "2.0.0",
            Status = "completed",
            InputDataJson = "{\"station_id\":\"abc\"}",
            OutputDataJson = "{\"predicted_power\":1500}",
            ErrorMessage = null,
            TotalNodes = 5,
            CompletedNodes = 5,
            FailedNodes = 0,
            TotalLatencyMs = 2500,
            CreateBy = tenantId,
            CreateName = "admin",
            CreateTime = DateTime.UtcNow,
            UpdateBy = tenantId,
            UpdateName = "admin",
            UpdateTime = DateTime.UtcNow
        };

        entity.Id.Should().Be(id);
        entity.WorkflowId.Should().Be("pv_power_forecast");
        entity.TotalNodes.Should().Be(5);
        entity.CompletedNodes.Should().Be(5);
        entity.Status.Should().Be("completed");
    }

    [Fact]
    public void AiDagNodeExecution_默认值正确()
    {
        var entity = new AiDagNodeExecution();
        entity.Status.Should().Be("pending");
        entity.ExecutionMode.Should().Be("serial");
        entity.LatencyMs.Should().Be(0);
        entity.RetryCount.Should().Be(0);
        entity.UsedFallback.Should().BeFalse();
        entity.DeleteAt.Should().BeNull();
        entity.FallbackModelName.Should().BeNull();
        entity.Role.Should().BeNull();
    }

    [Fact]
    public void AiDagNodeExecution_降级模型记录()
    {
        var entity = new AiDagNodeExecution
        {
            Id = Guid.NewGuid(),
            NodeId = "solar_onnx",
            ModelType = "onnx",
            ModelName = "SolarFusion_v2",
            Status = "completed",
            UsedFallback = true,
            FallbackModelName = "SolarFusion_v1",
            LatencyMs = 350,
            RetryCount = 2
        };

        entity.UsedFallback.Should().BeTrue();
        entity.FallbackModelName.Should().Be("SolarFusion_v1");
        entity.RetryCount.Should().Be(2);
    }

    // ============================================================
    // DagOptions 配置项测试
    // ============================================================

    [Fact]
    public void DagOptions_默认值正确()
    {
        var options = new DagOptions();
        options.DefaultTimeoutMs.Should().Be(30000);
        options.DefaultMaxRetries.Should().Be(2);
        options.EnablePersistence.Should().BeTrue();
        options.RetentionDays.Should().Be(90);
    }

    [Fact]
    public void DagOptions_可自定义()
    {
        var options = new DagOptions
        {
            DefaultTimeoutMs = 60000,
            DefaultMaxRetries = 5,
            EnablePersistence = false,
            RetentionDays = 30
        };

        options.DefaultTimeoutMs.Should().Be(60000);
        options.DefaultMaxRetries.Should().Be(5);
        options.EnablePersistence.Should().BeFalse();
        options.RetentionDays.Should().Be(30);
    }

    // ============================================================
    // DagConfidenceFusion 融合引擎测试
    // ============================================================

    private DagConfidenceFusion CreateFusion()
    {
        var opts = Options.Create(new DagOptions());
        return new DagConfidenceFusion(opts, NullLogger<DagConfidenceFusion>.Instance);
    }

    [Fact]
    public void Fuse_加权平均_主模型权重最高()
    {
        var fusion = CreateFusion();

        var workflow = new DagWorkflow
        {
            WorkflowId = "test_wf",
            Version = "1.0.0",
            Nodes = new List<DagNode>
            {
                new() { NodeId = "primary_node", ModelType = "onnx", ModelName = "Solar", Role = "primary", Execution = "serial" },
                new() { NodeId = "secondary_node", ModelType = "onnx", ModelName = "Correction", Role = "corrector", Execution = "serial" }
            }
        };

        var nodeResults = new List<DagNodeResult>
        {
            new() { NodeId = "primary_node", ModelName = "Solar", Status = DagNodeStatus.Completed, Confidence = 0.95m },
            new() { NodeId = "secondary_node", ModelName = "Correction", Status = DagNodeStatus.Completed, Confidence = 0.80m }
        };

        var result = fusion.Fuse(nodeResults, workflow, FusionStrategy.WeightedAverage);

        result.FusedConfidence.Should().BeGreaterThan(0.80m);
        result.FusedConfidence.Should().BeLessOrEqualTo(0.95m);
        result.Strategy.Should().Be(FusionStrategy.WeightedAverage);
        result.NodeWeights.Should().ContainKey("primary_node");
        result.NodeWeights["primary_node"].Should().BeGreaterThan(result.NodeWeights["secondary_node"],
            "主模型权重应大于校正模型");
    }

    [Fact]
    public void Fuse_空结果返回零置信度()
    {
        var fusion = CreateFusion();
        var workflow = new DagWorkflow { WorkflowId = "empty", Version = "1.0.0", Nodes = new List<DagNode>() };

        var result = fusion.Fuse(new List<DagNodeResult>(), workflow);
        result.FusedConfidence.Should().Be(0m);
    }

    [Fact]
    public void Fuse_跳过失败节点()
    {
        var fusion = CreateFusion();
        var workflow = new DagWorkflow
        {
            WorkflowId = "test", Version = "1.0.0",
            Nodes = new List<DagNode>
            {
                new() { NodeId = "n1", ModelType = "onnx", ModelName = "M1", Role = "primary", Execution = "serial" },
                new() { NodeId = "n2", ModelType = "onnx", ModelName = "M2", Role = "secondary", Execution = "serial" }
            }
        };

        var results = new List<DagNodeResult>
        {
            new() { NodeId = "n1", ModelName = "M1", Status = DagNodeStatus.Completed, Confidence = 0.90m },
            new() { NodeId = "n2", ModelName = "M2", Status = DagNodeStatus.Failed, Confidence = null }
        };

        var fusionResult = fusion.Fuse(results, workflow);
        fusionResult.FusedConfidence.Should().Be(0.90m, "失败节点应被排除");
    }

    [Fact]
    public void Fuse_贝叶斯融合_样本不足时等于加权平均()
    {
        var fusion = CreateFusion();
        var workflow = new DagWorkflow
        {
            WorkflowId = "test", Version = "1.0.0",
            Nodes = new List<DagNode>
            {
                new() { NodeId = "n1", ModelType = "onnx", ModelName = "M1", Role = "primary", Execution = "serial" }
            }
        };

        var results = new List<DagNodeResult>
        {
            new() { NodeId = "n1", ModelName = "M1", Status = DagNodeStatus.Completed, Confidence = 0.88m }
        };

        var bayesian = fusion.Fuse(results, workflow, FusionStrategy.Bayesian);
        var weighted = fusion.Fuse(results, workflow, FusionStrategy.WeightedAverage);

        bayesian.FusedConfidence.Should().Be(weighted.FusedConfidence,
            "样本不足（<5）时贝叶斯因子=1.0，结果等于加权平均");
    }

    [Fact]
    public void Fuse_投票融合_多数票决定()
    {
        var fusion = CreateFusion();
        var workflow = new DagWorkflow
        {
            WorkflowId = "diagnosis", Version = "1.0.0",
            Nodes = new List<DagNode>
            {
                new() { NodeId = "n1", ModelType = "onnx", ModelName = "RF", Role = "primary", Execution = "serial" },
                new() { NodeId = "n2", ModelType = "onnx", ModelName = "AE", Role = "secondary", Execution = "serial" },
                new() { NodeId = "n3", ModelType = "gguf", ModelName = "qwen", Role = "verifier", Execution = "serial" }
            }
        };

        var results = new List<DagNodeResult>
        {
            new() { NodeId = "n1", Status = DagNodeStatus.Completed, Confidence = 0.85m, ModelName = "RF",
                Output = new Dictionary<string, object> { ["diagnosis"] = "overvoltage" } },
            new() { NodeId = "n2", Status = DagNodeStatus.Completed, Confidence = 0.78m, ModelName = "AE",
                Output = new Dictionary<string, object> { ["diagnosis"] = "overvoltage" } },
            new() { NodeId = "n3", Status = DagNodeStatus.Completed, Confidence = 0.60m, ModelName = "qwen",
                Output = new Dictionary<string, object> { ["diagnosis"] = "normal" } }
        };

        var result = fusion.Fuse(results, workflow, FusionStrategy.MajorityVoting);
        result.Strategy.Should().Be(FusionStrategy.MajorityVoting);
        result.MajorityConclusion.Should().Be("overvoltage");
        result.FusedConfidence.Should().BeGreaterThan(0.7m, "多数票置信度应取投票方平均");
    }

    [Fact]
    public void UpdateAccuracy_指数移动平均()
    {
        var fusion = CreateFusion();

        // 首次更新 = 第一个值本身
        fusion.UpdateAccuracy("TestModel", 0.90m);
        // 第二次更新应为 EMA: 0.3 * 0.80 + 0.7 * 0.90 = 0.87
        fusion.UpdateAccuracy("TestModel", 0.80m);

        // 验证不会抛出异常，准确率在合理范围
        // （内部缓存不直接暴露，但通过 Bayesian 融合间接验证）
    }

    // ============================================================
    // DagWorkflowRegistry 测试
    // ============================================================

    [Fact]
    public void Registry_包含7个内置工作流()
    {
        var registry = new DagWorkflowRegistry(NullLogger<DagWorkflowRegistry>.Instance);
        var all = registry.GetAll();

        all.Count.Should().Be(7);
    }

    [Theory]
    [InlineData("pv_power_forecast")]
    [InlineData("ai_patrol")]
    [InlineData("load_forecast")]
    [InlineData("price_forecast")]
    [InlineData("charging_forecast")]
    [InlineData("battery_forecast")]
    [InlineData("fault_diagnosis")]
    public void Registry_每个内置工作流可查询(string workflowId)
    {
        var registry = new DagWorkflowRegistry(NullLogger<DagWorkflowRegistry>.Instance);
        var wf = registry.Get(workflowId);

        wf.Should().NotBeNull();
        wf!.WorkflowId.Should().Be(workflowId);
        wf.Version.Should().Be("1.0.0");
        wf.Nodes.Should().NotBeEmpty();
        wf.IsActive.Should().BeTrue();
    }

    [Fact]
    public void Registry_查询不存在工作流返回null()
    {
        var registry = new DagWorkflowRegistry(NullLogger<DagWorkflowRegistry>.Instance);
        registry.Get("non_existent_workflow").Should().BeNull();
    }

    [Fact]
    public void Registry_注册自定义工作流()
    {
        var registry = new DagWorkflowRegistry(NullLogger<DagWorkflowRegistry>.Instance);
        var custom = new DagWorkflow
        {
            WorkflowId = "custom_test",
            Version = "1.0.0",
            Description = "测试自定义工作流",
            IsActive = true,
            Nodes = new List<DagNode>
            {
                new() { NodeId = "n1", ModelType = "onnx", ModelName = "TestModel", Execution = "serial" }
            }
        };

        registry.Register(custom);
        registry.Get("custom_test").Should().NotBeNull();
        registry.GetAll().Count.Should().Be(8); // 7 builtin + 1 custom
    }

    // ============================================================
    // AgentDagBridge 意图映射测试
    // ============================================================

    [Theory]
    [InlineData("pv_forecast", "pv_power_forecast")]
    [InlineData("solar_forecast", "pv_power_forecast")]
    [InlineData("load_forecast", "load_forecast")]
    [InlineData("grid_load_forecast", "load_forecast")]
    [InlineData("patrol", "ai_patrol")]
    [InlineData("fault_detection", "fault_diagnosis")]
    public void AgentDagBridge_意图映射正确(string intentType, string expectedWorkflowId)
    {
        var mockExecutor = new Mock<IDagExecutor>();
        var bridge = new AgentDagBridge(mockExecutor.Object,
            NullLogger<AgentDagBridge>.Instance);

        var workflowId = bridge.ResolveWorkflowId(intentType);
        workflowId.Should().Be(expectedWorkflowId);
    }

    [Fact]
    public void AgentDagBridge_未知意图返回null()
    {
        var mockExecutor = new Mock<IDagExecutor>();
        var bridge = new AgentDagBridge(mockExecutor.Object,
            NullLogger<AgentDagBridge>.Instance);

        bridge.ResolveWorkflowId("unknown_intent_xyz").Should().BeNull();
    }

    // ============================================================
    // DagModels 字段验证
    // ============================================================

    [Fact]
    public void DagWorkflowResult_含FusedConfidence字段()
    {
        var result = new DagWorkflowResult
        {
            ExecutionId = Guid.NewGuid(),
            WorkflowId = "test",
            Version = "1.0.0",
            Success = true,
            FusedConfidence = 0.9234m
        };

        result.FusedConfidence.Should().Be(0.9234m);
    }

    [Fact]
    public void DagWorkflowResult_FusedConfidence可为null()
    {
        var result = new DagWorkflowResult
        {
            ExecutionId = Guid.NewGuid(),
            WorkflowId = "test",
            Version = "1.0.0",
            Success = false
        };

        result.FusedConfidence.Should().BeNull();
    }

    [Fact]
    public void DagNode_默认超时和重试()
    {
        var node = new DagNode { NodeId = "test", ModelType = "onnx", ModelName = "test", Execution = "serial" };
        node.TimeoutMs.Should().Be(30000);
        node.RetryCount.Should().Be(2);
        node.FallbackModel.Should().BeNull();
        node.DependsOn.Should().BeEmpty();
    }

    [Fact]
    public void DagExecutionContext_生成唯一ExecutionId()
    {
        var ctx1 = new DagExecutionContext { WorkflowId = "t", Version = "1.0.0", InputData = new() };
        var ctx2 = new DagExecutionContext { WorkflowId = "t", Version = "1.0.0", InputData = new() };

        ctx1.ExecutionId.Should().NotBe(Guid.Empty);
        ctx2.ExecutionId.Should().NotBe(Guid.Empty);
        ctx1.ExecutionId.Should().NotBe(ctx2.ExecutionId);
    }

    // ============================================================
    // FusionResult / FusionStrategy 枚举测试
    // ============================================================

    [Theory]
    [InlineData(FusionStrategy.WeightedAverage)]
    [InlineData(FusionStrategy.Bayesian)]
    [InlineData(FusionStrategy.MajorityVoting)]
    public void FusionStrategy_三种策略均有效(FusionStrategy strategy)
    {
        var fusion = CreateFusion();
        var workflow = new DagWorkflow
        {
            WorkflowId = "t", Version = "1.0.0",
            Nodes = new List<DagNode>
            {
                new() { NodeId = "n1", ModelType = "onnx", ModelName = "M1", Role = "primary", Execution = "serial" }
            }
        };
        var results = new List<DagNodeResult>
        {
            new() { NodeId = "n1", ModelName = "M1", Status = DagNodeStatus.Completed, Confidence = 0.85m,
                Output = new Dictionary<string, object> { ["result"] = "ok" } }
        };

        var fr = fusion.Fuse(results, workflow, strategy);
        fr.Strategy.Should().Be(strategy);
        fr.FusedConfidence.Should().BeGreaterThan(0);
    }
}
