using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using Xunit;
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using JGSY.AGI.Common.Core.Enums;
using JGSY.AGI.Monitor.Interfaces;
using JGSY.AGI.Monitor.Business;
using JGSY.AGI.Monitor.Entities;
using JGSY.AGI.Common.Core.Interfaces;

namespace JGSY.AGI.Test.JGSY.AGI.Monitor.Test
{
    /// <summary>
    /// 健康检查服务测试
    /// </summary>
    public class HealthCheckServiceTests
    {
        private readonly Mock<ITenantContext> _mockTenantContext;
        private readonly Mock<ILogger<HealthCheckService>> _mockLogger;
        private readonly Guid _tenantId = Guid.NewGuid();

        public HealthCheckServiceTests()
        {
            _mockTenantContext = new Mock<ITenantContext>();
            _mockTenantContext.Setup(x => x.TenantId).Returns(_tenantId);

            _mockLogger = new Mock<ILogger<HealthCheckService>>();
        }

        [Fact]
        public void ServiceHealth_Entity_Should_Have_Required_Properties()
        {
            // Arrange & Act
            var serviceHealth = new ServiceHealth
            {
                Id = Guid.NewGuid(),
                ServiceName = "TestService",
                InstanceId = "instance-001",
                Status = (int)ServiceStatus.Healthy,
                ServiceAddress = "http://localhost:5000",
                HealthEndpoint = "/health",
                CheckIntervalSeconds = 30,
                ResponseTimeMs = 50,
                LastCheckTime = DateTime.UtcNow,
                TenantId = _tenantId
            };

            // Assert
            serviceHealth.Id.Should().NotBeEmpty();
            serviceHealth.ServiceName.Should().Be("TestService");
            serviceHealth.InstanceId.Should().Be("instance-001");
            serviceHealth.Status.Should().Be((int)ServiceStatus.Healthy);
            serviceHealth.ResponseTimeMs.Should().Be(50);
        }

        [Theory]
        [InlineData(ServiceStatus.Unknown)]
        [InlineData(ServiceStatus.Healthy)]
        [InlineData(ServiceStatus.Unhealthy)]
        [InlineData(ServiceStatus.Degraded)]
        public void ServiceStatus_Enum_Should_Have_Expected_Values(ServiceStatus status)
        {
            // Assert
            Enum.IsDefined(typeof(ServiceStatus), status).Should().BeTrue();
        }
    }

    /// <summary>
    /// 告警服务测试
    /// </summary>
    public class AlertServiceTests
    {
        private readonly Mock<ITenantContext> _mockTenantContext;
        private readonly Mock<ILogger<AlertService>> _mockLogger;
        private readonly Guid _tenantId = Guid.NewGuid();

        public AlertServiceTests()
        {
            _mockTenantContext = new Mock<ITenantContext>();
            _mockTenantContext.Setup(x => x.TenantId).Returns(_tenantId);

            _mockLogger = new Mock<ILogger<AlertService>>();
        }

        [Fact]
        public void Alert_Entity_Should_Have_Required_Properties()
        {
            // Arrange & Act
            var alert = new Alert
            {
                Id = Guid.NewGuid(),
                AlertType = (int)AlertType.ServiceDown,
                Level = (int)AlertLevel.Critical,
                Status = (int)AlertStatus.Active,
                Title = "Service Unavailable",
                Message = "Service is not responding",
                ServiceName = "TestService",
                OccurTime = DateTime.UtcNow,
                TenantId = _tenantId
            };

            // Assert
            alert.Id.Should().NotBeEmpty();
            alert.AlertType.Should().Be((int)AlertType.ServiceDown);
            alert.Level.Should().Be((int)AlertLevel.Critical);
            alert.Status.Should().Be((int)AlertStatus.Active);
            alert.Title.Should().Be("Service Unavailable");
        }

        [Theory]
        [InlineData(AlertLevel.Info)]
        [InlineData(AlertLevel.Warning)]
        [InlineData(AlertLevel.Error)]
        [InlineData(AlertLevel.Critical)]
        public void AlertLevel_Enum_Should_Have_Expected_Values(AlertLevel level)
        {
            // Assert
            Enum.IsDefined(typeof(AlertLevel), level).Should().BeTrue();
        }

        [Theory]
        [InlineData(AlertStatus.Active)]
        [InlineData(AlertStatus.Acknowledged)]
        [InlineData(AlertStatus.Resolved)]
        [InlineData(AlertStatus.Ignored)]
        public void AlertStatus_Enum_Should_Have_Expected_Values(AlertStatus status)
        {
            // Assert
            Enum.IsDefined(typeof(AlertStatus), status).Should().BeTrue();
        }

        [Theory]
        [InlineData(AlertType.ServiceDown)]
        [InlineData(AlertType.ResponseTimeout)]
        [InlineData(AlertType.HighCpuUsage)]
        [InlineData(AlertType.HighMemoryUsage)]
        [InlineData(AlertType.LowDiskSpace)]
        [InlineData(AlertType.HighErrorRate)]
        public void AlertType_Enum_Should_Have_Expected_Values(AlertType type)
        {
            // Assert
            Enum.IsDefined(typeof(AlertType), type).Should().BeTrue();
        }
    }

    /// <summary>
    /// 自愈服务测试
    /// </summary>
    public class AutoHealingServiceTests
    {
        [Fact]
        public void HealingPolicyEntity_Should_Have_Required_Properties()
        {
            // Arrange & Act
            var policy = new HealingPolicyEntity
            {
                Id = Guid.NewGuid(),
                Name = "Restart on failure",
                Description = "Auto restart service when health check fails",
                ServiceName = "TestService",
                TriggerType = (int)HealingTriggerType.HealthCheckFailed,
                TriggerCondition = "{\"consecutiveFailures\": 3}",
                ActionType = (int)HealingActionType.RestartService,
                ActionConfig = "{\"restartEndpoint\": \"http://localhost:8080/restart\"}",
                CooldownSeconds = 300,
                MaxRetries = 3,
                IsEnabled = true,
                TenantId = Guid.NewGuid()
            };

            // Assert
            policy.Id.Should().NotBeEmpty();
            policy.Name.Should().Be("Restart on failure");
            policy.TriggerType.Should().Be((int)HealingTriggerType.HealthCheckFailed);
            policy.ActionType.Should().Be((int)HealingActionType.RestartService);
            policy.CooldownSeconds.Should().Be(300);
            policy.MaxRetries.Should().Be(3);
            policy.IsEnabled.Should().BeTrue();
        }

        [Fact]
        public void HealingRecordEntity_Should_Have_Required_Properties()
        {
            // Arrange & Act
            var record = new HealingRecordEntity
            {
                Id = Guid.NewGuid(),
                PolicyId = Guid.NewGuid(),
                PolicyName = "Restart on failure",
                ServiceName = "TestService",
                TriggerType = (int)HealingTriggerType.HealthCheckFailed,
                ActionType = (int)HealingActionType.RestartService,
                TriggerReason = "Health check failed 3 times",
                Success = true,
                Message = "Service restarted successfully",
                ExecutedAt = DateTime.UtcNow,
                DurationMs = 1500,
                TenantId = Guid.NewGuid()
            };

            // Assert
            record.Id.Should().NotBeEmpty();
            record.PolicyId.Should().NotBeEmpty();
            record.Success.Should().BeTrue();
            record.DurationMs.Should().Be(1500);
        }

        [Theory]
        [InlineData(HealingTriggerType.HealthCheckFailed)]
        [InlineData(HealingTriggerType.ErrorRateThreshold)]
        [InlineData(HealingTriggerType.LatencyThreshold)]
        [InlineData(HealingTriggerType.ResourceThreshold)]
        [InlineData(HealingTriggerType.AlertTriggered)]
        [InlineData(HealingTriggerType.Manual)]
        public void HealingTriggerType_Enum_Should_Have_Expected_Values(HealingTriggerType triggerType)
        {
            // Assert
            Enum.IsDefined(typeof(HealingTriggerType), triggerType).Should().BeTrue();
        }

        [Theory]
        [InlineData(HealingActionType.RestartService)]
        [InlineData(HealingActionType.ScaleUp)]
        [InlineData(HealingActionType.ScaleDown)]
        [InlineData(HealingActionType.Failover)]
        [InlineData(HealingActionType.RateLimit)]
        [InlineData(HealingActionType.CircuitBreaker)]
        [InlineData(HealingActionType.ExecuteScript)]
        [InlineData(HealingActionType.Notify)]
        [InlineData(HealingActionType.WebhookCall)]
        public void HealingActionType_Enum_Should_Have_Expected_Values(HealingActionType actionType)
        {
            // Assert
            Enum.IsDefined(typeof(HealingActionType), actionType).Should().BeTrue();
        }
    }

    /// <summary>
    /// 指标服务测试
    /// </summary>
    public class MetricServiceTests
    {
        [Fact]
        public void MonitorMetric_Entity_Should_Have_Required_Properties()
        {
            // Arrange & Act
            var metric = new MonitorMetric
            {
                Id = Guid.NewGuid(),
                MetricName = "cpu_usage",
                MetricType = (int)MetricType.Gauge,
                Value = 45.5,
                Unit = "percent",
                ServiceName = "TestService",
                InstanceId = "instance-001",
                Timestamp = DateTime.UtcNow,
                TenantId = Guid.NewGuid()
            };

            // Assert
            metric.Id.Should().NotBeEmpty();
            metric.MetricName.Should().Be("cpu_usage");
            metric.MetricType.Should().Be((int)MetricType.Gauge);
            metric.Value.Should().Be(45.5);
            metric.Unit.Should().Be("percent");
        }

        [Theory]
        [InlineData(MetricType.Counter)]
        [InlineData(MetricType.Gauge)]
        [InlineData(MetricType.Histogram)]
        [InlineData(MetricType.Summary)]
        public void MetricType_Enum_Should_Have_Expected_Values(MetricType metricType)
        {
            // Assert
            Enum.IsDefined(typeof(MetricType), metricType).Should().BeTrue();
        }
    }
}

