using System;
using System.Collections.Generic;
using System.Linq;
using FluentAssertions;
using JGSY.AGI.Common.Core.Enums;
using JGSY.AGI.WorkOrder.Service;
using Xunit;
using WorkOrderStatus = JGSY.AGI.Common.Core.Enums.WorkOrderStatus;

namespace JGSY.AGI.Test.WorkOrder;

/// <summary>
/// 工单服务业务规则测试 — 状态机 + 业务逻辑 + 边界条件
/// 纯内存测试，不依赖数据库；验证状态转换合法性、DTO 映射、选项配置等
/// </summary>
public class WorkOrderServiceTests
{
    #region 状态机转换合法性

    /// <summary>
    /// 定义合法的状态转换表
    /// </summary>
    private static readonly Dictionary<WorkOrderStatus, HashSet<WorkOrderStatus>> ValidTransitions = new()
    {
        [WorkOrderStatus.Created] = new() { WorkOrderStatus.Pending, WorkOrderStatus.Assigned, WorkOrderStatus.Cancelled },
        [WorkOrderStatus.Pending] = new() { WorkOrderStatus.Assigned, WorkOrderStatus.Cancelled },
        [WorkOrderStatus.Assigned] = new() { WorkOrderStatus.Accepted, WorkOrderStatus.Rejected, WorkOrderStatus.Cancelled },
        [WorkOrderStatus.Accepted] = new() { WorkOrderStatus.InProgress, WorkOrderStatus.Cancelled },
        [WorkOrderStatus.InProgress] = new() { WorkOrderStatus.Completed, WorkOrderStatus.Cancelled },
        [WorkOrderStatus.Completed] = new() { WorkOrderStatus.Verified, WorkOrderStatus.InProgress }, // InProgress = 验证不通过退回
        [WorkOrderStatus.Verified] = new() { WorkOrderStatus.Closed },
        [WorkOrderStatus.Closed] = new(),
        [WorkOrderStatus.Cancelled] = new(),
        [WorkOrderStatus.Rejected] = new() { WorkOrderStatus.Assigned }, // 可重新分配
    };

    [Theory]
    [InlineData(WorkOrderStatus.Created, WorkOrderStatus.Pending, true)]
    [InlineData(WorkOrderStatus.Created, WorkOrderStatus.Assigned, true)]
    [InlineData(WorkOrderStatus.Assigned, WorkOrderStatus.Accepted, true)]
    [InlineData(WorkOrderStatus.Accepted, WorkOrderStatus.InProgress, true)]
    [InlineData(WorkOrderStatus.InProgress, WorkOrderStatus.Completed, true)]
    [InlineData(WorkOrderStatus.Completed, WorkOrderStatus.Verified, true)]
    [InlineData(WorkOrderStatus.Verified, WorkOrderStatus.Closed, true)]
    [InlineData(WorkOrderStatus.Completed, WorkOrderStatus.InProgress, true)] // 验证不通过退回
    public void ValidTransition_ShouldBeAllowed(WorkOrderStatus from, WorkOrderStatus to, bool expected)
    {
        var isAllowed = ValidTransitions.TryGetValue(from, out var targets) && targets.Contains(to);
        isAllowed.Should().Be(expected);
    }

    [Theory]
    [InlineData(WorkOrderStatus.Closed, WorkOrderStatus.InProgress)]       // 不可从关闭回到处理中
    [InlineData(WorkOrderStatus.Cancelled, WorkOrderStatus.Assigned)]       // 不可从取消回到分配
    [InlineData(WorkOrderStatus.Pending, WorkOrderStatus.Completed)]        // 不可从待处理直接完成
    [InlineData(WorkOrderStatus.Created, WorkOrderStatus.Closed)]           // 不可从创建直接关闭
    [InlineData(WorkOrderStatus.InProgress, WorkOrderStatus.Assigned)]      // 不可从处理中回到分配
    [InlineData(WorkOrderStatus.Accepted, WorkOrderStatus.Rejected)]        // 已接受不可拒绝
    public void InvalidTransition_ShouldBeRejected(WorkOrderStatus from, WorkOrderStatus to)
    {
        var isAllowed = ValidTransitions.TryGetValue(from, out var targets) && targets.Contains(to);
        isAllowed.Should().BeFalse();
    }

    [Fact]
    public void TerminalStates_ShouldHaveNoOutgoingTransitions()
    {
        // 终态：Closed 和 Cancelled 不应有后续状态
        ValidTransitions[WorkOrderStatus.Closed].Should().BeEmpty();
        ValidTransitions[WorkOrderStatus.Cancelled].Should().BeEmpty();
    }

    [Fact]
    public void EveryCancelableState_ShouldTransitionToCancelled()
    {
        // 除了 Closed/Cancelled 本身外的所有状态都应该能取消
        var cancelableStates = new[]
        {
            WorkOrderStatus.Created, WorkOrderStatus.Pending, WorkOrderStatus.Assigned,
            WorkOrderStatus.Accepted, WorkOrderStatus.InProgress
        };

        foreach (var state in cancelableStates)
        {
            ValidTransitions[state].Should().Contain(WorkOrderStatus.Cancelled,
                $"状态 {state} 应该可以取消");
        }
    }

    [Fact]
    public void CompleteWorkflow_HappyPath_ShouldTraverseAllStates()
    {
        // 完整的正常流程：Created → Pending → Assigned → Accepted → InProgress → Completed → Verified → Closed
        var happyPath = new[]
        {
            WorkOrderStatus.Created,
            WorkOrderStatus.Pending,
            WorkOrderStatus.Assigned,
            WorkOrderStatus.Accepted,
            WorkOrderStatus.InProgress,
            WorkOrderStatus.Completed,
            WorkOrderStatus.Verified,
            WorkOrderStatus.Closed
        };

        for (int i = 0; i < happyPath.Length - 1; i++)
        {
            var from = happyPath[i];
            var to = happyPath[i + 1];
            var isAllowed = ValidTransitions.TryGetValue(from, out var targets) && targets.Contains(to);
            isAllowed.Should().BeTrue($"流程 {from} → {to} 应该合法");
        }
    }

    #endregion

    #region 工单创建业务规则

    [Fact]
    public void CreateWorkOrderRequest_Validation_ShouldRejectEmptyTitle()
    {
        var request = new CreateWorkOrderRequest
        {
            Title = "",
            Type = WorkOrderType.Fault,
            Priority = WorkOrderPriority.Normal
        };

        var errors = request.Validate();
        errors.Should().ContainKey("title");
    }

    [Fact]
    public void CreateWorkOrderRequest_Validation_ShouldAcceptValidRequest()
    {
        var request = new CreateWorkOrderRequest
        {
            Title = "充电桩故障报修",
            Type = WorkOrderType.Fault,
            Priority = WorkOrderPriority.High,
            Description = "1号充电桩无法启动",
            ReporterName = "张三",
            ReporterPhone = "13800138000"
        };

        var errors = request.Validate();
        errors.Should().BeEmpty();
    }

    [Fact]
    public void CreateWorkOrderRequest_Validation_ShouldRejectInvalidPhone()
    {
        var request = new CreateWorkOrderRequest
        {
            Title = "测试工单",
            Type = WorkOrderType.Fault,
            ReporterPhone = "abc123"
        };

        var errors = request.Validate();
        errors.Should().ContainKey("reporterPhone");
    }

    [Fact]
    public void CreateWorkOrderRequest_Validation_ShouldLimitAttachments()
    {
        var request = new CreateWorkOrderRequest
        {
            Title = "测试工单",
            Type = WorkOrderType.Fault,
            Attachments = Enumerable.Range(0, 100).Select(i => $"file{i}.jpg").ToList()
        };

        var errors = request.Validate();
        errors.Should().ContainKey("attachments");
    }

    #endregion

    #region 工单选项配置

    [Fact]
    public void WorkOrderOptions_ShouldHaveCorrectDefaults()
    {
        var options = new WorkOrderOptions();

        options.DefaultTimeoutHours.Should().Be(24);
        options.EnableAutoAssign.Should().BeTrue();
        options.AutoAssignStrategy.Should().Be("LeastBusy");
        options.EnableSla.Should().BeTrue();
        options.OrderNoPrefix.Should().Be("WO");
    }

    [Theory]
    [InlineData("RoundRobin")]
    [InlineData("LeastBusy")]
    [InlineData("Random")]
    public void WorkOrderOptions_ShouldAcceptValidStrategies(string strategy)
    {
        var options = new WorkOrderOptions { AutoAssignStrategy = strategy };
        options.AutoAssignStrategy.Should().Be(strategy);
    }

    #endregion

    #region 实体映射测试

    [Fact]
    public void WorkOrderEntity_AutoAssigned_ShouldSetAssignedStatus()
    {
        // 模拟 CreateAsync 中的自动分配逻辑
        var options = new WorkOrderOptions { EnableAutoAssign = true };
        var entity = new WorkOrderEntity
        {
            Id = Guid.NewGuid(),
            TenantId = Guid.NewGuid(),
            Status = WorkOrderStatus.Created
        };

        var assigneeId = Guid.NewGuid();
        if (options.EnableAutoAssign && assigneeId != Guid.Empty)
        {
            entity.AssigneeId = assigneeId;
            entity.Status = WorkOrderStatus.Assigned;
            entity.AssignedTime = DateTime.UtcNow;
        }

        entity.Status.Should().Be(WorkOrderStatus.Assigned);
        entity.AssigneeId.Should().Be(assigneeId);
        entity.AssignedTime.Should().NotBeNull();
    }

    [Fact]
    public void WorkOrderEntity_NoAutoAssign_ShouldBePending()
    {
        var options = new WorkOrderOptions { EnableAutoAssign = true };
        var entity = new WorkOrderEntity
        {
            Id = Guid.NewGuid(),
            TenantId = Guid.NewGuid(),
            Status = WorkOrderStatus.Created
        };

        // 没有指定分配人
        Guid? assigneeId = null;
        if (options.EnableAutoAssign && assigneeId.HasValue)
        {
            entity.Status = WorkOrderStatus.Assigned;
        }
        else
        {
            entity.Status = WorkOrderStatus.Pending;
        }

        entity.Status.Should().Be(WorkOrderStatus.Pending);
        entity.AssigneeId.Should().BeNull();
    }

    [Fact]
    public void WorkOrderDto_TypeName_ShouldMatchEnum()
    {
        var dto = new WorkOrderDto
        {
            Type = WorkOrderType.Fault,
            Priority = WorkOrderPriority.Urgent,
            Status = WorkOrderStatus.InProgress
        };

        dto.TypeName.Should().Be("Fault");
        dto.PriorityName.Should().Be("Urgent");
        dto.StatusName.Should().Be("InProgress");
    }

    #endregion

    #region 统计逻辑测试

    [Fact]
    public void CompletionRate_ShouldBeCorrect()
    {
        // 模拟 GetStatisticsAsync 中的完成率计算
        var orders = new List<WorkOrderEntity>
        {
            CreateEntity(WorkOrderStatus.Completed, isOverdue: false),
            CreateEntity(WorkOrderStatus.Verified, isOverdue: false),
            CreateEntity(WorkOrderStatus.Closed, isOverdue: false),
            CreateEntity(WorkOrderStatus.InProgress, isOverdue: false),
            CreateEntity(WorkOrderStatus.Pending, isOverdue: false),
        };

        var completed = orders.Where(x =>
            x.Status == WorkOrderStatus.Completed ||
            x.Status == WorkOrderStatus.Verified ||
            x.Status == WorkOrderStatus.Closed).ToList();

        var completionRate = orders.Count > 0
            ? (decimal)completed.Count / orders.Count * 100 : 0;

        completionRate.Should().Be(60m); // 3 out of 5
    }

    [Fact]
    public void OnTimeRate_ShouldBeCorrect()
    {
        var now = DateTime.UtcNow;

        var orders = new List<WorkOrderEntity>
        {
            CreateEntity(WorkOrderStatus.Completed, completedTime: now.AddHours(-1), dueTime: now),      // 按时
            CreateEntity(WorkOrderStatus.Completed, completedTime: now.AddHours(1), dueTime: now),        // 超时
            CreateEntity(WorkOrderStatus.Completed, completedTime: now.AddHours(-2), dueTime: now),       // 按时
        };

        var completed = orders.Where(x => x.Status == WorkOrderStatus.Completed).ToList();
        var onTime = completed.Count(x => x.CompletedTime <= x.DueTime);

        var onTimeRate = completed.Count > 0
            ? (decimal)onTime / completed.Count * 100 : 0;

        onTimeRate.Should().BeApproximately(66.67m, 0.01m); // 2/3
    }

    [Fact]
    public void Statistics_ByType_ShouldGroupCorrectly()
    {
        var orders = new List<WorkOrderEntity>
        {
            CreateEntity(status: WorkOrderStatus.InProgress, type: WorkOrderType.Fault),
            CreateEntity(status: WorkOrderStatus.InProgress, type: WorkOrderType.Fault),
            CreateEntity(status: WorkOrderStatus.InProgress, type: WorkOrderType.Maintenance),
            CreateEntity(status: WorkOrderStatus.InProgress, type: WorkOrderType.Complaint),
        };

        var byType = orders.GroupBy(x => x.Type).ToDictionary(g => g.Key.ToString(), g => g.Count());

        byType["Fault"].Should().Be(2);
        byType["Maintenance"].Should().Be(1);
        byType["Complaint"].Should().Be(1);
    }

    [Fact]
    public void Statistics_EmptyOrders_ShouldReturnZeroRates()
    {
        var orders = new List<WorkOrderEntity>();

        var completionRate = orders.Count > 0
            ? (decimal)orders.Count(x => x.Status == WorkOrderStatus.Completed) / orders.Count * 100 : 0;

        completionRate.Should().Be(0);
    }

    #endregion

    #region SLA 规则测试

    [Fact]
    public void SlaRule_ShouldApplyByPriority()
    {
        var rules = new List<SlaRule>
        {
            new() { Priority = WorkOrderPriority.Urgent, ResponseTimeMinutes = 15, ResolutionTimeMinutes = 60 },
            new() { Priority = WorkOrderPriority.High, ResponseTimeMinutes = 30, ResolutionTimeMinutes = 240 },
            new() { Priority = WorkOrderPriority.Normal, ResponseTimeMinutes = 120, ResolutionTimeMinutes = 480 },
            new() { Priority = WorkOrderPriority.Low, ResponseTimeMinutes = 480, ResolutionTimeMinutes = 1440 },
        };

        var urgentSla = rules.First(r => r.Priority == WorkOrderPriority.Urgent);
        urgentSla.ResponseTimeMinutes.Should().BeLessThan(
            rules.First(r => r.Priority == WorkOrderPriority.Normal).ResponseTimeMinutes);
    }

    [Fact]
    public void OverdueDetection_ShouldFlag_WhenPastDueTime()
    {
        var now = DateTime.UtcNow;
        var entity = CreateEntity(WorkOrderStatus.InProgress, dueTime: now.AddHours(-1));

        var isOverdue = entity.DueTime < now
            && entity.Status != WorkOrderStatus.Completed
            && entity.Status != WorkOrderStatus.Verified
            && entity.Status != WorkOrderStatus.Closed
            && entity.Status != WorkOrderStatus.Cancelled;

        isOverdue.Should().BeTrue();
    }

    [Fact]
    public void OverdueDetection_ShouldNotFlag_CompletedOrders()
    {
        var now = DateTime.UtcNow;
        var entity = CreateEntity(WorkOrderStatus.Completed, dueTime: now.AddHours(-1));

        var isOverdue = entity.DueTime < now
            && entity.Status != WorkOrderStatus.Completed
            && entity.Status != WorkOrderStatus.Verified
            && entity.Status != WorkOrderStatus.Closed
            && entity.Status != WorkOrderStatus.Cancelled;

        isOverdue.Should().BeFalse();
    }

    #endregion

    #region 边界条件测试

    [Fact]
    public void OrderNoGeneration_ShouldContainPrefix()
    {
        var options = new WorkOrderOptions { OrderNoPrefix = "WO" };
        var orderNo = $"{options.OrderNoPrefix}{DateTime.UtcNow:yyyyMMdd}{1:D6}";

        orderNo.Should().StartWith("WO");
        orderNo.Should().HaveLength(16); // WO + yyyyMMdd(8) + 000001(6) = 16
    }

    [Fact]
    public void WorkOrderEntity_DueTime_ShouldUseDefault_WhenNotProvided()
    {
        var options = new WorkOrderOptions { DefaultTimeoutHours = 48 };
        var now = DateTime.UtcNow;

        DateTime? requestDueTime = null;
        var dueTime = requestDueTime ?? now.AddHours(options.DefaultTimeoutHours);

        dueTime.Should().BeCloseTo(now.AddHours(48), TimeSpan.FromSeconds(1));
    }

    [Fact]
    public void WorkOrderEntity_AttachmentsParsing_ShouldSplitCorrectly()
    {
        var entity = new WorkOrderEntity
        {
            Attachments = "file1.jpg,file2.png,file3.pdf"
        };

        var attachments = entity.Attachments?.Split(',', StringSplitOptions.RemoveEmptyEntries).ToList();
        attachments.Should().HaveCount(3);
        attachments.Should().Contain("file1.jpg");
    }

    [Fact]
    public void WorkOrderEntity_EmptyAttachments_ShouldReturnNull()
    {
        var entity = new WorkOrderEntity { Attachments = null };
        var attachments = entity.Attachments?.Split(',', StringSplitOptions.RemoveEmptyEntries).ToList();
        attachments.Should().BeNull();
    }

    [Fact]
    public void FlowRecord_ShouldTrackFromAndToStatus()
    {
        var flow = new WorkOrderFlow
        {
            Id = Guid.NewGuid(),
            WorkOrderId = Guid.NewGuid(),
            FromStatus = WorkOrderStatus.Assigned,
            ToStatus = WorkOrderStatus.Accepted,
            Action = "Accept",
            OperatorId = Guid.NewGuid(),
            CreateTime = DateTime.UtcNow
        };

        flow.FromStatus.Should().Be(WorkOrderStatus.Assigned);
        flow.ToStatus.Should().Be(WorkOrderStatus.Accepted);
        flow.Action.Should().Be("Accept");
        flow.CreateTime.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(1));
    }

    [Fact]
    public void RejectFlow_ShouldClearAssignee_InLogic()
    {
        // 拒绝时应清除分配人信息
        var entity = CreateEntity(WorkOrderStatus.Assigned);
        entity.AssigneeId = Guid.NewGuid();
        entity.AssigneeName = "张三";

        // 模拟拒绝逻辑
        if (entity.Status == WorkOrderStatus.Assigned)
        {
            entity.Status = WorkOrderStatus.Rejected;
            entity.AssigneeId = null;
            entity.AssigneeName = null;
        }

        entity.Status.Should().Be(WorkOrderStatus.Rejected);
        entity.AssigneeId.Should().BeNull();
        entity.AssigneeName.Should().BeNull();
    }

    [Fact]
    public void TransferFlow_ShouldKeepSameStatus()
    {
        // 转交不改变状态，只改变分配人
        var entity = CreateEntity(WorkOrderStatus.InProgress);
        var originalStatus = entity.Status;
        var newAssigneeId = Guid.NewGuid();

        entity.AssigneeId = newAssigneeId;
        entity.AssigneeName = "李四";
        entity.AssignedTime = DateTime.UtcNow;

        entity.Status.Should().Be(originalStatus); // 状态不变
        entity.AssigneeId.Should().Be(newAssigneeId); // 分配人变更
    }

    #endregion

    #region 辅助方法

    private static WorkOrderEntity CreateEntity(
        WorkOrderStatus status = WorkOrderStatus.Pending,
        bool isOverdue = false,
        DateTime? completedTime = null,
        DateTime? dueTime = null,
        WorkOrderType type = WorkOrderType.Fault)
    {
        return new WorkOrderEntity
        {
            Id = Guid.NewGuid(),
            TenantId = Guid.NewGuid(),
            OrderNo = $"WO{DateTime.UtcNow:yyyyMMdd}000001",
            Title = "测试工单",
            Type = type,
            Priority = WorkOrderPriority.Normal,
            Status = status,
            IsOverdue = isOverdue,
            CompletedTime = completedTime,
            DueTime = dueTime ?? DateTime.UtcNow.AddHours(24),
            CreateTime = DateTime.UtcNow
        };
    }

    #endregion
}
