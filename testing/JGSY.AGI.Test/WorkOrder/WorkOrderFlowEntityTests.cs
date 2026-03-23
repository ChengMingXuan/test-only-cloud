using System;
using System.Collections.Generic;
using System.Linq;
using Xunit;
using FluentAssertions;
using JGSY.AGI.WorkOrder.Entities;

namespace JGSY.AGI.Test.WorkOrder
{
    /// <summary>
    /// 工单流转实体单元测试（纯实体属性测试，无 DbContext 依赖）
    /// </summary>
    public class WorkOrderFlowEntityTests
    {
        [Fact]
        public void WorkOrderFlow_Should_Track_Status_Change()
        {
            var flow = new WorkOrderFlow
            {
                Id = Guid.NewGuid(),
                TenantId = Guid.NewGuid(),
                WorkOrderId = Guid.NewGuid(),
                FromStatus = "Created",
                ToStatus = "Assigned",
                Action = "分配工单",
                OperatorId = Guid.NewGuid(),
                OperatorName = "管理员",
                Remark = "分配给维修工程师",
                ActionTime = DateTime.UtcNow,
                CreateBy = Guid.NewGuid(),
                UpdateBy = Guid.NewGuid()
            };

            flow.FromStatus.Should().Be("Created");
            flow.ToStatus.Should().Be("Assigned");
            flow.Action.Should().Be("分配工单");
        }

        [Fact]
        public void WorkOrderFlow_Should_Support_Full_Workflow()
        {
            var workOrderId = Guid.NewGuid();
            var operatorId = Guid.NewGuid();

            var flows = new List<WorkOrderFlow>
            {
                new() { Id = Guid.NewGuid(), WorkOrderId = workOrderId, FromStatus = "Created", ToStatus = "Assigned", Action = "分配工单", OperatorId = operatorId, ActionTime = DateTime.UtcNow.AddHours(-3), CreateTime = DateTime.UtcNow.AddHours(-3), CreateBy = operatorId, UpdateBy = operatorId },
                new() { Id = Guid.NewGuid(), WorkOrderId = workOrderId, FromStatus = "Assigned", ToStatus = "Accepted", Action = "接受工单", OperatorId = operatorId, ActionTime = DateTime.UtcNow.AddHours(-2), CreateTime = DateTime.UtcNow.AddHours(-2), CreateBy = operatorId, UpdateBy = operatorId },
                new() { Id = Guid.NewGuid(), WorkOrderId = workOrderId, FromStatus = "Accepted", ToStatus = "InProgress", Action = "开始处理", OperatorId = operatorId, ActionTime = DateTime.UtcNow.AddHours(-1), CreateTime = DateTime.UtcNow.AddHours(-1), CreateBy = operatorId, UpdateBy = operatorId },
                new() { Id = Guid.NewGuid(), WorkOrderId = workOrderId, FromStatus = "InProgress", ToStatus = "Completed", Action = "完成工单", OperatorId = operatorId, ActionTime = DateTime.UtcNow, CreateTime = DateTime.UtcNow, CreateBy = operatorId, UpdateBy = operatorId },
            };

            var results = flows.Where(f => f.WorkOrderId == workOrderId).OrderBy(f => f.CreateTime).ToList();
            results.Should().HaveCount(4);
            results[0].ToStatus.Should().Be("Assigned");
            results[3].ToStatus.Should().Be("Completed");
        }

        [Fact]
        public void WorkOrderComment_Should_Create_Successfully()
        {
            var comment = new WorkOrderComment
            {
                Id = Guid.NewGuid(),
                TenantId = Guid.NewGuid(),
                WorkOrderId = Guid.NewGuid(),
                UserId = Guid.NewGuid(),
                UserName = "张三",
                Content = "已检查设备，发现是电源模块故障，需要更换。",
                IsInternal = false,
                Attachments = "[\"image1.jpg\",\"image2.jpg\"]",
                CreateBy = Guid.NewGuid(),
                UpdateBy = Guid.NewGuid()
            };

            comment.Content.Should().Contain("电源模块故障");
            comment.IsInternal.Should().BeFalse();
        }

        [Fact]
        public void WorkOrderComment_Should_Support_Internal_Notes()
        {
            var workOrderId = Guid.NewGuid();
            var userId = Guid.NewGuid();

            var comments = new List<WorkOrderComment>
            {
                new() { Id = Guid.NewGuid(), WorkOrderId = workOrderId, UserId = userId, UserName = "客服", Content = "正在处理", IsInternal = false, CreateBy = userId, UpdateBy = userId },
                new() { Id = Guid.NewGuid(), WorkOrderId = workOrderId, UserId = userId, UserName = "技术主管", Content = "需要厂家支持", IsInternal = true, CreateBy = userId, UpdateBy = userId },
            };

            var publicComments = comments.Where(c => c.WorkOrderId == workOrderId && !c.IsInternal).ToList();
            publicComments.Should().HaveCount(1);

            var allComments = comments.Where(c => c.WorkOrderId == workOrderId).ToList();
            allComments.Should().HaveCount(2);
        }

        [Fact]
        public void WorkOrderFlow_Should_Query_By_WorkOrderId()
        {
            var workOrderId1 = Guid.NewGuid();
            var workOrderId2 = Guid.NewGuid();
            var operatorId = Guid.NewGuid();

            var flows = new List<WorkOrderFlow>
            {
                new() { Id = Guid.NewGuid(), WorkOrderId = workOrderId1, FromStatus = "Created", ToStatus = "Assigned", Action = "分配", OperatorId = operatorId, CreateBy = operatorId, UpdateBy = operatorId },
                new() { Id = Guid.NewGuid(), WorkOrderId = workOrderId1, FromStatus = "Assigned", ToStatus = "InProgress", Action = "开始处理", OperatorId = operatorId, CreateBy = operatorId, UpdateBy = operatorId },
                new() { Id = Guid.NewGuid(), WorkOrderId = workOrderId2, FromStatus = "Created", ToStatus = "Cancelled", Action = "取消", OperatorId = operatorId, CreateBy = operatorId, UpdateBy = operatorId },
            };

            var flowsForOrder1 = flows.Where(f => f.WorkOrderId == workOrderId1).ToList();
            flowsForOrder1.Should().HaveCount(2);
        }

        [Fact]
        public void WorkOrderComment_Should_Support_Attachments()
        {
            var comment = new WorkOrderComment
            {
                Id = Guid.NewGuid(),
                TenantId = Guid.NewGuid(),
                WorkOrderId = Guid.NewGuid(),
                UserId = Guid.NewGuid(),
                UserName = "维修工程师",
                Content = "维修完成，附件为维修前后照片",
                IsInternal = false,
                Attachments = "[\"before.jpg\",\"after.jpg\",\"receipt.pdf\"]",
                CreateBy = Guid.NewGuid(),
                UpdateBy = Guid.NewGuid()
            };

            comment.Attachments.Should().Contain("before.jpg");
            comment.Attachments.Should().Contain("receipt.pdf");
        }
    }
}
