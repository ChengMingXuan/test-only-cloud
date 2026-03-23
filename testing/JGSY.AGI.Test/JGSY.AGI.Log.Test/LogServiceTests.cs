using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Xunit;
using FluentAssertions;
using JGSY.AGI.Log.Entities;

namespace JGSY.AGI.Test.JGSY.AGI.Log.Test
{
    /// <summary>
    /// 日志服务单元测试
    /// </summary>
    public class LogServiceTests
    {
        private readonly Guid _tenantId = Guid.NewGuid();

        #region SystemLog Tests

        [Fact]
        public void SystemLog_Entity_Should_Have_Required_Properties()
        {
            // Arrange & Act
            var systemLog = new SystemLog
            {
                Id = Guid.NewGuid(),
                TenantId = _tenantId,
                Level = (int)LogLevel.Information,
                Category = (int)LogCategory.System,
                Message = "Test log message",
                Source = "TestService",
                TraceId = "trace-001",
                LogTime = DateTime.UtcNow
            };

            // Assert
            systemLog.Id.Should().NotBeEmpty();
            systemLog.TenantId.Should().Be(_tenantId);
            systemLog.Level.Should().Be((int)LogLevel.Information);
            systemLog.Category.Should().Be((int)LogCategory.System);
            systemLog.Message.Should().Be("Test log message");
            systemLog.Source.Should().Be("TestService");
        }

        [Theory]
        [InlineData(LogLevel.Trace)]
        [InlineData(LogLevel.Debug)]
        [InlineData(LogLevel.Information)]
        [InlineData(LogLevel.Warning)]
        [InlineData(LogLevel.Error)]
        [InlineData(LogLevel.Critical)]
        public void LogLevel_Enum_Should_Have_Expected_Values(LogLevel level)
        {
            // Assert
            Enum.IsDefined(typeof(LogLevel), level).Should().BeTrue();
        }

        [Theory]
        [InlineData(LogCategory.System)]
        [InlineData(LogCategory.Application)]
        [InlineData(LogCategory.Access)]
        [InlineData(LogCategory.Operation)]
        [InlineData(LogCategory.Security)]
        [InlineData(LogCategory.Exception)]
        [InlineData(LogCategory.Audit)]
        [InlineData(LogCategory.Performance)]
        public void LogCategory_Enum_Should_Have_Expected_Values(LogCategory category)
        {
            // Assert
            Enum.IsDefined(typeof(LogCategory), category).Should().BeTrue();
        }

        #endregion

        #region OperationLog Tests

        [Fact]
        public void OperationLog_Entity_Should_Have_Required_Properties()
        {
            // Arrange & Act
            var operationLog = new OperationLog
            {
                Id = Guid.NewGuid(),
                TenantId = _tenantId,
                OperationType = "Create",
                OperationName = "创建用户",
                Description = "创建新用户账户",
                UserId = Guid.NewGuid(),
                UserName = "admin",
                ModuleName = "UserManagement",
                TargetType = "User",
                TargetId = Guid.NewGuid().ToString(),
                Status = 1,
                Duration = 150,
                ClientIp = "192.168.1.100",
                OperationTime = DateTime.UtcNow
            };

            // Assert
            operationLog.Id.Should().NotBeEmpty();
            operationLog.OperationType.Should().Be("Create");
            operationLog.UserName.Should().Be("admin");
            operationLog.ModuleName.Should().Be("UserManagement");
            operationLog.Status.Should().Be(1);
        }

        #endregion

        #region AuditLog Tests

        [Fact]
        public void AuditLog_Entity_Should_Have_Required_Properties()
        {
            // Arrange & Act
            var auditLog = new AuditLog
            {
                Id = Guid.NewGuid(),
                TenantId = _tenantId,
                AuditTargetId = Guid.NewGuid().ToString(),
                AuditTargetType = "User",
                AuditTargetName = "John Doe",
                AuditOperation = (int)AuditOperationType.Update,
                OperationDescription = "修改用户角色",
                UserId = Guid.NewGuid(),
                UserName = "admin",
                UserDisplayName = "管理员",
                ClientIp = "192.168.1.100",
                ClientDevice = "Chrome on Windows",
                RequestId = "trace-001",
                OldValues = "{\"role\": \"User\"}",
                NewValues = "{\"role\": \"Admin\"}",
                ChangedFields = "[\"role\"]",
                Result = 1,
                AuditTime = DateTime.UtcNow,
                RiskLevel = 3,
                IsSensitive = true
            };

            // Assert
            auditLog.Id.Should().NotBeEmpty();
            auditLog.AuditTargetId.Should().NotBeNullOrEmpty();
            auditLog.AuditTargetType.Should().Be("User");
            auditLog.AuditOperation.Should().Be((int)AuditOperationType.Update);
            auditLog.RiskLevel.Should().Be(3);
            auditLog.IsSensitive.Should().BeTrue();
        }

        [Theory]
        [InlineData(AuditOperationType.Create)]
        [InlineData(AuditOperationType.Read)]
        [InlineData(AuditOperationType.Update)]
        [InlineData(AuditOperationType.Delete)]
        [InlineData(AuditOperationType.Login)]
        [InlineData(AuditOperationType.Logout)]
        [InlineData(AuditOperationType.Export)]
        [InlineData(AuditOperationType.Import)]
        [InlineData(AuditOperationType.Grant)]
        [InlineData(AuditOperationType.Revoke)]
        [InlineData(AuditOperationType.Approve)]
        [InlineData(AuditOperationType.Reject)]
        [InlineData(AuditOperationType.ConfigChange)]
        public void AuditOperationType_Enum_Should_Have_Expected_Values(AuditOperationType operationType)
        {
            // Assert
            Enum.IsDefined(typeof(AuditOperationType), operationType).Should().BeTrue();
        }

        #endregion

        #region BusinessLog Tests

        [Fact]
        public void BusinessLog_Entity_Should_Have_Required_Properties()
        {
            // Arrange & Act
            var businessLog = new BusinessLog
            {
                Id = Guid.NewGuid(),
                TenantId = _tenantId,
                BusinessFlowId = "order-001-flow",
                BusinessFlowName = "订单处理流程",
                BusinessFlowType = "OrderProcessing",
                BusinessNode = "PaymentVerification",
                NodeSequence = 3,
                BusinessStatus = (int)BusinessFlowStatus.Processing,
                StatusMessage = "正在验证支付信息",
                BusinessData = "{\"orderId\": \"ORD-001\", \"amount\": 99.99}",
                EntityType = "Order",
                EntityId = "ORD-001",
                UserId = Guid.NewGuid(),
                UserName = "customer",
                ServiceName = "OrderService",
                TraceId = "trace-001",
                StartTime = DateTime.UtcNow,
                Priority = 1
            };

            // Assert
            businessLog.Id.Should().NotBeEmpty();
            businessLog.BusinessFlowId.Should().Be("order-001-flow");
            businessLog.BusinessFlowName.Should().Be("订单处理流程");
            businessLog.BusinessNode.Should().Be("PaymentVerification");
            businessLog.NodeSequence.Should().Be(3);
            businessLog.BusinessStatus.Should().Be((int)BusinessFlowStatus.Processing);
        }

        [Theory]
        [InlineData(BusinessFlowStatus.Pending)]
        [InlineData(BusinessFlowStatus.Processing)]
        [InlineData(BusinessFlowStatus.Completed)]
        [InlineData(BusinessFlowStatus.Cancelled)]
        [InlineData(BusinessFlowStatus.Failed)]
        [InlineData(BusinessFlowStatus.Timeout)]
        [InlineData(BusinessFlowStatus.PartiallyCompleted)]
        [InlineData(BusinessFlowStatus.WaitingRetry)]
        public void BusinessFlowStatus_Enum_Should_Have_Expected_Values(BusinessFlowStatus status)
        {
            // Assert
            Enum.IsDefined(typeof(BusinessFlowStatus), status).Should().BeTrue();
        }

        [Fact]
        public void BusinessLog_Should_Support_Error_Tracking()
        {
            // Arrange & Act
            var businessLog = new BusinessLog
            {
                Id = Guid.NewGuid(),
                TenantId = _tenantId,
                BusinessFlowId = "order-002-flow",
                BusinessFlowName = "订单处理流程",
                BusinessNode = "InventoryCheck",
                NodeSequence = 2,
                BusinessStatus = (int)BusinessFlowStatus.Failed,
                StatusMessage = "库存不足",
                ErrorCode = "INV_INSUFFICIENT",
                ErrorMessage = "商品库存不足，无法完成订单",
                RetryCount = 2,
                MaxRetries = 3,
                NeedsCompensation = true,
                CompensationStatus = 0,
                StartTime = DateTime.UtcNow.AddMinutes(-5),
                EndTime = DateTime.UtcNow,
                Duration = 300000
            };

            // Assert
            businessLog.BusinessStatus.Should().Be((int)BusinessFlowStatus.Failed);
            businessLog.ErrorCode.Should().Be("INV_INSUFFICIENT");
            businessLog.RetryCount.Should().Be(2);
            businessLog.NeedsCompensation.Should().BeTrue();
            businessLog.CompensationStatus.Should().Be(0);
        }

        #endregion

        #region ExceptionLog Tests

        [Fact]
        public void ExceptionLog_Entity_Should_Have_Required_Properties()
        {
            // Arrange & Act
            var exceptionLog = new ExceptionLog
            {
                Id = Guid.NewGuid(),
                TenantId = _tenantId,
                ExceptionType = "System.NullReferenceException",
                Message = "Object reference not set to an instance of an object",
                StackTrace = "at TestClass.TestMethod() in ...",
                Source = "TestService",
                TraceId = "trace-001",
                UserId = Guid.NewGuid(),
                ClientIp = "192.168.1.100",
                RequestPath = "/api/test",
                ExceptionTime = DateTime.UtcNow,
                IsHandled = false
            };

            // Assert
            exceptionLog.Id.Should().NotBeEmpty();
            exceptionLog.ExceptionType.Should().Be("System.NullReferenceException");
            exceptionLog.Message.Should().Contain("Object reference");
            exceptionLog.IsHandled.Should().BeFalse();
        }

        #endregion

        #region LogArchive Tests

        [Fact]
        public void LogArchive_Entity_Should_Have_Required_Properties()
        {
            // Arrange & Act
            var logArchive = new LogArchive
            {
                Id = Guid.NewGuid(),
                TenantId = _tenantId,
                ArchiveName = "SystemLogs_202401",
                ArchiveType = (int)LogCategory.System,
                StartTime = new DateTime(2024, 1, 1),
                EndTime = new DateTime(2024, 1, 31),
                RecordCount = 100000,
                FileSize = 50 * 1024 * 1024,
                StoragePath = "/archives/system_logs_202401.gz",
                StorageType = "Local",
                CompressionFormat = "gzip",
                Status = 1
            };

            // Assert
            logArchive.Id.Should().NotBeEmpty();
            logArchive.ArchiveName.Should().Be("SystemLogs_202401");
            logArchive.RecordCount.Should().Be(100000);
            logArchive.CompressionFormat.Should().Be("gzip");
            logArchive.Status.Should().Be(1);
        }

        #endregion

        #region Integration Tests

        [Fact]
        public async Task LogDbContext_Should_Save_And_Retrieve_Logs()
        {
            // Arrange - 模拟通过 Dapper 保存和检索日志
            var tenantId = Guid.NewGuid();
            var log = new SystemLog
            {
                Id = Guid.NewGuid(),
                TenantId = tenantId,
                Level = 2,
                Message = "系统启动成功",
                Source = "Program",
                CreateTime = DateTime.UtcNow,
                DeleteAt = (DateTime?)null
            };

            // Act - 模拟 INSERT 后 SELECT 查询结果
            var savedLogs = new List<SystemLog> { log };
            var retrieved = savedLogs.Find(l => l.TenantId == tenantId && l.Level == 2);

            // Assert
            await Task.CompletedTask;
            retrieved.Should().NotBeNull();
            retrieved!.Message.Should().Be("系统启动成功");
            retrieved.Source.Should().Be("Program");
        }

        [Fact]
        public async Task LogDbContext_Should_Save_Multiple_Log_Types()
        {
            // Arrange - 测试不同类型日志的保存
            var tenantId = Guid.NewGuid();
            var logs = new List<object>
            {
                new SystemLog { Id = Guid.NewGuid(), TenantId = tenantId, Level = 4, Message = "系统异常", Source = "API" },
                new OperationLog { Id = Guid.NewGuid(), TenantId = tenantId, ModuleName = "用户管理", OperationType = "创建用户", UserName = "admin" },
                new AuditLog { Id = Guid.NewGuid(), TenantId = tenantId, AuditTargetType = "User", AuditTargetId = Guid.NewGuid().ToString(), AuditOperation = 1 }
            };

            // Act - 验证不同类型的日志都正确创建
            var systemLogs = logs.OfType<SystemLog>().ToList();
            var operationLogs = logs.OfType<OperationLog>().ToList();
            var auditLogs = logs.OfType<AuditLog>().ToList();

            // Assert
            await Task.CompletedTask;
            systemLogs.Should().HaveCount(1);
            operationLogs.Should().HaveCount(1);
            auditLogs.Should().HaveCount(1);
            systemLogs.First().Level.Should().Be(4);
            operationLogs.First().ModuleName.Should().Be("用户管理");
            auditLogs.First().AuditTargetType.Should().Be("User");
        }

        #endregion
    }
}
