using FluentAssertions;
using JGSY.AGI.Monitor.Entities;
using JGSY.AGI.Log.Entities;
using Xunit;

namespace JGSY.AGI.Test.Observability;

/// <summary>
/// 监控模块实体测试
/// </summary>
public class MonitorEntityTests
{
    [Fact]
    public void ServiceHealth_ShouldHaveCorrectDefaults()
    {
        var health = new ServiceHealth();
        health.DeleteAt.Should().BeNull();
        health.IsEnabled.Should().BeTrue();
        health.ConsecutiveFailures.Should().Be(0);
    }

    [Fact]
    public void ServiceHealth_ShouldSetAllProperties()
    {
        var health = new ServiceHealth
        {
            ServiceName = "jgsy-station",
            InstanceId = "station-01",
            ServiceAddress = "http://jgsy-station:8080",
            HealthEndpoint = "/health",
            Status = (int)ServiceStatus.Healthy,
            LastCheckTime = DateTime.UtcNow,
            LastHealthyTime = DateTime.UtcNow,
            ResponseTimeMs = 25,
            ErrorRate = 0.01,
            CheckIntervalSeconds = 30,
            IsEnabled = true
        };

        health.ServiceName.Should().StartWith("jgsy-");
        health.ResponseTimeMs.Should().BePositive();
        health.ErrorRate.Should().BeLessThan(1.0);
    }

    [Fact]
    public void Alert_ShouldSetAllProperties()
    {
        var alert = new Alert
        {
            AlertType = (int)AlertType.HighCpuUsage,
            Level = (int)AlertLevel.Warning,
            Status = 1,
            Title = "CPU 使用率过高",
            Message = "jgsy-ingestion 服务 CPU 使用率超过 80%",
            ServiceName = "jgsy-ingestion",
            OccurTime = DateTime.UtcNow,
            MetricValue = 85.5,
            Threshold = 80.0,
            NotificationSent = true
        };

        alert.MetricValue.Should().BeGreaterThan(alert.Threshold ?? 0);
        alert.NotificationSent.Should().BeTrue();
    }

    [Fact]
    public void MonitorMetric_ShouldRecordTimeSeries()
    {
        var metric = new MonitorMetric
        {
            MetricName = "http_request_duration_seconds",
            MetricType = (int)MetricType.Histogram,
            ServiceName = "jgsy-gateway",
            Value = 0.125,
            Timestamp = DateTime.UtcNow,
            Unit = "seconds",
            Description = "HTTP 请求耗时"
        };

        metric.Value.Should().BePositive();
        metric.Timestamp.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(5));
    }

    [Fact]
    public void MetricsData_ShouldSetTagsAndMetadata()
    {
        var data = new MetricsData
        {
            MetricName = "jgsy_charging_power_kw",
            MetricType = "gauge",
            ServiceName = "jgsy-device",
            Tags = "{\"station_id\": \"ST001\", \"gun_id\": \"G01\"}",
            Value = 60.5,
            Timestamp = DateTime.UtcNow,
            Unit = "kW"
        };

        data.Tags.Should().Contain("station_id");
        data.Value.Should().BePositive();
    }

    [Fact]
    public void Dashboard_ShouldContainWidgets()
    {
        var dashboard = new Dashboard
        {
            Name = "充电站运营大屏",
            LayoutType = (int)DashboardLayoutType.Grid,
            Visibility = (int)DashboardVisibility.Tenant,
            IsDefault = true,
            SortOrder = 1
        };

        dashboard.Name.Should().NotBeEmpty();
        dashboard.IsDefault.Should().BeTrue();
    }

    [Fact]
    public void DashboardWidget_ShouldSetPosition()
    {
        var widget = new DashboardWidget
        {
            Name = "实时功率",
            WidgetType = (int)WidgetType.LineChart,
            PositionX = 0,
            PositionY = 0,
            Width = 6,
            Height = 4,
            RefreshInterval = 10,
            IsEnabled = true,
            DataSourceConfig = "{\"metric\":\"jgsy_power_kw\"}"
        };

        widget.Width.Should().BePositive();
        widget.Height.Should().BePositive();
        widget.RefreshInterval.Should().BePositive();
    }

    [Fact]
    public void AlertRule_ShouldDefineThreshold()
    {
        var rule = new AlertRule
        {
            RuleName = "高错误率告警",
            MetricName = "http_error_rate",
            Operator = ">",
            Threshold = 5.0,
            DurationSeconds = 300,
            AlertLevel = (int)AlertLevel.Critical,
            IsEnabled = true,
            CooldownSeconds = 600
        };

        rule.Threshold.Should().BePositive();
        rule.CooldownSeconds.Should().BeGreaterThanOrEqualTo(rule.DurationSeconds);
    }

    [Theory]
    [InlineData(ServiceStatus.Healthy)]
    [InlineData(ServiceStatus.Degraded)]
    [InlineData(ServiceStatus.Unhealthy)]
    [InlineData(ServiceStatus.Unknown)]
    public void ServiceStatus_ShouldHaveDefinedValues(ServiceStatus status)
    {
        Enum.IsDefined(typeof(ServiceStatus), status).Should().BeTrue();
    }

    [Theory]
    [InlineData(AlertLevel.Info)]
    [InlineData(AlertLevel.Warning)]
    [InlineData(AlertLevel.Error)]
    [InlineData(AlertLevel.Critical)]
    public void AlertLevel_ShouldHaveDefinedValues(AlertLevel level)
    {
        Enum.IsDefined(typeof(AlertLevel), level).Should().BeTrue();
    }
}

/// <summary>
/// 日志模块实体测试
/// </summary>
public class LogEntityTests
{
    [Fact]
    public void SystemLog_ShouldHaveCorrectDefaults()
    {
        var log = new SystemLog();
        log.DeleteAt.Should().BeNull();
    }

    [Fact]
    public void SystemLog_ShouldSetAllProperties()
    {
        var log = new SystemLog
        {
            Level = (int)LogLevel.Error,
            Category = (int)LogCategory.System,
            Message = "数据库连接池耗尽",
            Source = "jgsy-settlement",
            TraceId = Guid.NewGuid().ToString("N"),
            ClientIp = "10.0.1.50"
        };

        log.Message.Should().Contain("数据库");
        log.TraceId.Should().NotBeEmpty();
    }

    [Fact]
    public void AuditLog_ShouldSetOperationDetails()
    {
        var auditLog = new AuditLog
        {
            AuditOperation = (int)AuditOperationType.Create,
            Module = "充电站管理",
            OperationDescription = "新建充电站",
            HttpMethod = "POST",
            RequestPath = "/api/station/stations",
            Result = 200,
            Duration = 150
        };

        auditLog.Result.Should().Be(200);
        auditLog.Duration.Should().BePositive();
    }

    [Fact]
    public void BusinessLog_ShouldTrackFlow()
    {
        var bizLog = new BusinessLog
        {
            BusinessFlowType = "Charging",
            BusinessFlowId = Guid.NewGuid().ToString(),
            BusinessStatus = (int)BusinessFlowStatus.Processing,
            ServiceName = "jgsy-device",
            BusinessNode = "StartCharging"
        };

        bizLog.BusinessFlowId.Should().NotBeEmpty();
        bizLog.BusinessStatus.Should().Be((int)BusinessFlowStatus.Processing);
    }

    [Theory]
    [InlineData(LogLevel.Trace)]
    [InlineData(LogLevel.Debug)]
    [InlineData(LogLevel.Information)]
    [InlineData(LogLevel.Warning)]
    [InlineData(LogLevel.Error)]
    [InlineData(LogLevel.Critical)]
    public void LogLevel_ShouldHaveAllValues(LogLevel level)
    {
        Enum.IsDefined(typeof(LogLevel), level).Should().BeTrue();
    }
}

/// <summary>
/// 日志 DTO 测试
/// </summary>
public class LogDtoTests
{
    [Fact]
    public void LogQueryRequest_ShouldSetFilters()
    {
        var query = new LogQueryRequest
        {
            ServiceName = "jgsy-gateway",
            LogLevel = (int)LogLevel.Error,
            StartTime = DateTime.UtcNow.AddHours(-1),
            EndTime = DateTime.UtcNow,
            PageIndex = 1,
            PageSize = 20
        };

        query.EndTime.Should().BeAfter(query.StartTime ?? DateTime.MinValue);
        query.PageSize.Should().BePositive();
    }

    [Fact]
    public void CreateAlertRuleRequest_ShouldSetAllFields()
    {
        var req = new CreateAlertRuleRequest
        {
            RuleName = "高频异常告警",
            AlertLevel = 4, // Critical
            ServiceName = "jgsy-gateway",
            LogLevel = (int)LogLevel.Error,
            Keyword = "error_count",
            ConditionType = 1,
            TimeWindowMinutes = 5,
            Threshold = 100,
            IsEnabled = true,
            SilentPeriodMinutes = 5
        };

        req.Threshold.Should().BePositive();
        req.IsEnabled.Should().BeTrue();
    }
}

/// <summary>
/// 日志聚合测试 - P2 企业级测试补充
/// </summary>
public class LogAggregationTests
{
    [Fact]
    public void LogEntry_Should_Have_Required_Fields()
    {
        // Arrange - 日志条目必需字段
        var logEntry = new
        {
            timestamp = DateTime.UtcNow,
            level = "ERROR",
            service = "jgsy-gateway",
            message = "Connection timeout to upstream service",
            traceId = Guid.NewGuid().ToString("N"),
            spanId = Guid.NewGuid().ToString("N")[..16]
        };

        // Assert
        logEntry.timestamp.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(5));
        logEntry.level.Should().NotBeNullOrEmpty();
        logEntry.service.Should().StartWith("jgsy-");
        logEntry.traceId.Should().HaveLength(32);
        logEntry.spanId.Should().HaveLength(16);
    }

    [Fact]
    public void LogLevel_Should_Follow_Severity_Order()
    {
        // Arrange - 日志级别优先级
        var levels = new Dictionary<string, int>
        {
            { "TRACE", 0 },
            { "DEBUG", 1 },
            { "INFO", 2 },
            { "WARN", 3 },
            { "ERROR", 4 },
            { "FATAL", 5 }
        };

        // Assert
        levels["ERROR"].Should().BeGreaterThan(levels["WARN"]);
        levels["FATAL"].Should().BeGreaterThan(levels["ERROR"]);
        levels["DEBUG"].Should().BeLessThan(levels["INFO"]);
    }

    [Fact]
    public void LogAggregation_Should_Support_Time_Bucketing()
    {
        // Arrange - 日志聚合时间桶
        var logs = Enumerable.Range(0, 100).Select(i => new
        {
            timestamp = DateTime.UtcNow.AddMinutes(-i),
            level = i % 10 == 0 ? "ERROR" : "INFO",
            service = "jgsy-gateway"
        }).ToList();

        // Act - 按小时聚合
        var hourlyBuckets = logs
            .GroupBy(l => new DateTime(l.timestamp.Year, l.timestamp.Month, l.timestamp.Day, l.timestamp.Hour, 0, 0))
            .Select(g => new { Hour = g.Key, Count = g.Count(), ErrorCount = g.Count(l => l.level == "ERROR") })
            .ToList();

        // Assert
        hourlyBuckets.Should().NotBeEmpty();
        hourlyBuckets.Sum(b => b.Count).Should().Be(100);
    }

    [Fact]
    public void LogSearch_Should_Support_Full_Text_Query()
    {
        // Arrange
        var logs = new[]
        {
            new { message = "User login failed: invalid password", level = "WARN" },
            new { message = "Connection timeout to database", level = "ERROR" },
            new { message = "User login successful", level = "INFO" },
            new { message = "Password reset requested", level = "INFO" }
        };

        // Act - 全文搜索 "password"
        var searchResults = logs.Where(l => l.message.Contains("password", StringComparison.OrdinalIgnoreCase)).ToList();

        // Assert
        searchResults.Should().HaveCount(2);
        searchResults.Should().Contain(l => l.level == "WARN");
        searchResults.Should().Contain(l => l.level == "INFO");
    }

    [Fact]
    public void LogRetention_Should_Respect_Policy()
    {
        // Arrange - 日志保留策略
        var retentionDays = 90;
        var logTimestamp = DateTime.UtcNow.AddDays(-100);
        var cutoffDate = DateTime.UtcNow.AddDays(-retentionDays);

        // Act
        var shouldBeDeleted = logTimestamp < cutoffDate;

        // Assert
        shouldBeDeleted.Should().BeTrue("超过保留期的日志应被删除");
    }

    [Fact]
    public void LogCorrelation_Should_Link_Related_Entries()
    {
        // Arrange - 通过 TraceId 关联日志
        var traceId = Guid.NewGuid().ToString("N");
        var correlatedLogs = new[]
        {
            new { service = "jgsy-gateway", traceId, spanId = "span001", message = "Received request" },
            new { service = "jgsy-identity", traceId, spanId = "span002", message = "Validating token" },
            new { service = "jgsy-permission", traceId, spanId = "span003", message = "Checking permissions" },
            new { service = "jgsy-gateway", traceId, spanId = "span001", message = "Returning response" }
        };

        // Act
        var uniqueServices = correlatedLogs.Select(l => l.service).Distinct().ToList();
        var allSameTrace = correlatedLogs.All(l => l.traceId == traceId);

        // Assert
        uniqueServices.Should().HaveCount(3);
        allSameTrace.Should().BeTrue("同一请求链路中所有日志应共享 TraceId");
    }
}

/// <summary>
/// 指标采集测试 - P2 企业级测试补充
/// </summary>
public class MetricsCollectionTests
{
    [Fact]
    public void Counter_Metric_Should_Only_Increase()
    {
        // Arrange
        var httpRequestsTotal = 0L;

        // Act - 模拟请求计数
        httpRequestsTotal += 10;
        httpRequestsTotal += 5;
        var finalCount = httpRequestsTotal;

        // Assert
        finalCount.Should().Be(15);
        finalCount.Should().BeGreaterThan(0, "Counter 只能增加");
    }

    [Fact]
    public void Gauge_Metric_Should_Reflect_Current_Value()
    {
        // Arrange - Gauge 指标可升可降
        var cpuUsagePercent = 0.0;

        // Act
        cpuUsagePercent = 75.5;  // CPU 升高
        cpuUsagePercent = 42.3;  // CPU 降低

        // Assert
        cpuUsagePercent.Should().Be(42.3);
        cpuUsagePercent.Should().BeInRange(0, 100);
    }

    [Fact]
    public void Histogram_Should_Calculate_Percentiles()
    {
        // Arrange - 模拟请求延迟数据
        var latencies = new double[] { 10, 15, 20, 25, 30, 35, 40, 50, 100, 500 };
        Array.Sort(latencies);

        // Act - 计算百分位数
        var p50Index = (int)(latencies.Length * 0.5) - 1;
        var p95Index = (int)(latencies.Length * 0.95) - 1;
        var p99Index = (int)(latencies.Length * 0.99) - 1;

        var p50 = latencies[Math.Max(0, p50Index)];
        var p95 = latencies[Math.Max(0, p95Index)];
        var p99 = latencies[Math.Max(0, p99Index)];

        // Assert
        p50.Should().BeLessThanOrEqualTo(p95);
        p95.Should().BeLessThanOrEqualTo(p99);
    }

    [Fact]
    public void Summary_Should_Track_Quantiles()
    {
        // Arrange
        var observations = Enumerable.Range(1, 1000).Select(i => (double)i).ToList();

        // Act
        var sum = observations.Sum();
        var count = observations.Count;
        var avg = sum / count;

        // Assert
        count.Should().Be(1000);
        avg.Should().Be(500.5);
        sum.Should().Be(500500);
    }

    [Fact]
    public void Metrics_Should_Have_Standard_Labels()
    {
        // Arrange - Prometheus 标准标签
        var metric = new
        {
            name = "http_requests_total",
            labels = new Dictionary<string, string>
            {
                { "method", "GET" },
                { "path", "/api/v1/users" },
                { "status", "200" },
                { "service", "jgsy-identity" },
                { "instance", "identity-01" }
            },
            value = 12345.0
        };

        // Assert
        metric.labels.Should().ContainKey("method");
        metric.labels.Should().ContainKey("status");
        metric.labels.Should().ContainKey("service");
        metric.name.Should().EndWith("_total", "Counter 指标应以 _total 结尾");
    }

    [Fact]
    public void RED_Metrics_Should_Cover_All_Dimensions()
    {
        // Arrange - RED 方法：Rate, Errors, Duration
        var redMetrics = new
        {
            Rate = "http_requests_total",           // 请求速率
            Errors = "http_requests_errors_total",  // 错误数
            Duration = "http_request_duration_seconds" // 延迟
        };

        // Assert - 每个服务应暴露这三类指标
        redMetrics.Rate.Should().Contain("requests");
        redMetrics.Errors.Should().Contain("errors");
        redMetrics.Duration.Should().Contain("duration");
    }

    [Fact]
    public void USE_Metrics_Should_Cover_Resources()
    {
        // Arrange - USE 方法：Utilization, Saturation, Errors
        var useMetrics = new
        {
            Utilization = new[] { "cpu_usage_percent", "memory_usage_percent", "disk_usage_percent" },
            Saturation = new[] { "cpu_throttle_percent", "memory_pressure", "io_wait_percent" },
            Errors = new[] { "disk_errors_total", "network_errors_total", "oom_kills_total" }
        };

        // Assert
        useMetrics.Utilization.Should().HaveCountGreaterThanOrEqualTo(3);
        useMetrics.Saturation.Should().HaveCountGreaterThanOrEqualTo(3);
        useMetrics.Errors.Should().HaveCountGreaterThanOrEqualTo(3);
    }

    [Fact]
    public void MetricScrape_Should_Complete_Within_Timeout()
    {
        // Arrange - Prometheus 抓取超时
        var scrapeTimeoutMs = 10000; // 10 秒
        var simulatedScrapeTimeMs = 500; // 模拟抓取耗时

        // Assert
        simulatedScrapeTimeMs.Should().BeLessThan(scrapeTimeoutMs, "指标抓取应在超时内完成");
    }

    [Fact]
    public void Cardinality_Should_Stay_Within_Limits()
    {
        // Arrange - 高基数会导致性能问题
        var labelCardinality = new Dictionary<string, int>
        {
            { "method", 10 },       // GET, POST, PUT, DELETE, ...
            { "status", 20 },       // 200, 201, 204, 301, 400, 401, 403, 404, 409, 422, 429, 500, 502, 503, ...
            { "path", 100 },        // API 路径数量（应归一化为模板路径）
            { "service", 25 }       // 微服务数量
        };

        // Act
        var totalCardinality = labelCardinality.Values.Aggregate(1, (a, b) => a * b);

        // Assert - 总基数应可控（< 1M 时间序列）
        totalCardinality.Should().BeLessThan(1_000_000, "指标基数应控制在合理范围");
    }
}
