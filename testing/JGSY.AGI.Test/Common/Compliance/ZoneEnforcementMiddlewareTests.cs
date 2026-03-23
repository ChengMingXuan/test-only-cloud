using FluentAssertions;
using JGSY.AGI.Common.Core.Deployment;
using JGSY.AGI.Gateway.Middleware;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using Moq;
using Xunit;

namespace JGSY.AGI.Test.Common.Compliance;

/// <summary>
/// 网关安全区域强制中间件测试
/// 合规项：DEPLOY-003（一票否决）、ZONE-001~004
/// 核心规则：云端禁止向本地控制区下发控制指令
/// </summary>
public class ZoneEnforcementMiddlewareTests
{
    private readonly Mock<IDeploymentModeProvider> _deploymentMode;
    private readonly ZoneEnforcementOptions _options;

    public ZoneEnforcementMiddlewareTests()
    {
        _deploymentMode = new Mock<IDeploymentModeProvider>();
        _options = new ZoneEnforcementOptions { Enabled = true, AuditOnlyMode = false };
    }

    private ZoneEnforcementMiddleware CreateMiddleware(RequestDelegate next)
    {
        return new ZoneEnforcementMiddleware(
            next,
            NullLogger<ZoneEnforcementMiddleware>.Instance,
            Options.Create(_options),
            _deploymentMode.Object);
    }

    #region DEPLOY-003: 云端模式 — 控制 API 写操作一票否决

    [Theory]
    [InlineData("/api/ingestion/command", "POST")]
    [InlineData("/api/device/control", "POST")]
    [InlineData("/api/device/command", "PUT")]
    [InlineData("/api/microgrid/dispatch", "POST")]
    [InlineData("/api/microgrid/control", "DELETE")]
    [InlineData("/api/pvessc/dispatch", "POST")]
    [InlineData("/api/safecontrol/execute", "POST")]
    [InlineData("/api/iotcloudai/control", "PUT")]
    public async Task 一票否决_云端模式控制API写操作应返回403(string path, string method)
    {
        _deploymentMode.Setup(x => x.IsCloudMode).Returns(true);

        var context = CreateHttpContext(path, method);
        var nextCalled = false;
        var middleware = CreateMiddleware(_ => { nextCalled = true; return Task.CompletedTask; });

        await middleware.InvokeAsync(context);

        context.Response.StatusCode.Should().Be(403,
            $"云端模式下 {method} {path} 应返回 403 — DEPLOY-003 一票否决");
        nextCalled.Should().BeFalse("被拦截的请求不应到达下游服务");
    }

    [Theory]
    [InlineData("/api/ingestion/command", "GET")]
    [InlineData("/api/device/control", "GET")]
    [InlineData("/api/device/control/status", "GET")]
    public async Task 云端模式控制API的GET请求应放行(string path, string method)
    {
        _deploymentMode.Setup(x => x.IsCloudMode).Returns(true);

        var context = CreateHttpContext(path, method);
        var nextCalled = false;
        var middleware = CreateMiddleware(_ => { nextCalled = true; return Task.CompletedTask; });

        await middleware.InvokeAsync(context);

        nextCalled.Should().BeTrue("云端模式下 GET 请求应放行（仅监控/查看/预警）");
    }

    #endregion

    #region 边缘模式 — 所有操作正常通过

    [Theory]
    [InlineData("/api/ingestion/command", "POST")]
    [InlineData("/api/device/control", "POST")]
    [InlineData("/api/microgrid/dispatch", "PUT")]
    public async Task 边缘模式控制API写操作应放行(string path, string method)
    {
        _deploymentMode.Setup(x => x.IsCloudMode).Returns(false);
        _deploymentMode.Setup(x => x.IsEdgeMode).Returns(true);

        var context = CreateHttpContext(path, method);
        // 边缘模式下本地服务请求携带正确的区域头
        context.Request.Headers["X-Security-Zone"] = "Zone-II";
        var nextCalled = false;
        var middleware = CreateMiddleware(_ => { nextCalled = true; return Task.CompletedTask; });

        await middleware.InvokeAsync(context);

        nextCalled.Should().BeTrue("边缘模式下控制 API 写操作应正常放行（本地闭环）");
    }

    #endregion

    #region 禁用模式

    [Fact]
    public async Task 禁用时所有请求直接放行()
    {
        _options.Enabled = false;
        _deploymentMode.Setup(x => x.IsCloudMode).Returns(true);

        var context = CreateHttpContext("/api/device/control", "POST");
        var nextCalled = false;
        var middleware = CreateMiddleware(_ => { nextCalled = true; return Task.CompletedTask; });

        await middleware.InvokeAsync(context);

        nextCalled.Should().BeTrue("中间件禁用时应直接放行");
    }

    #endregion

    #region 审计模式 — 记录但不阻断

    [Fact]
    public async Task 审计模式下违规请求只记录不阻断()
    {
        _options.AuditOnlyMode = true;
        _deploymentMode.Setup(x => x.IsCloudMode).Returns(true);

        var context = CreateHttpContext("/api/device/control", "POST");
        var nextCalled = false;
        var middleware = CreateMiddleware(_ => { nextCalled = true; return Task.CompletedTask; });

        await middleware.InvokeAsync(context);

        nextCalled.Should().BeTrue("审计模式下应放行（仅记录日志）");
    }

    #endregion

    #region 健康检查始终放行

    [Theory]
    [InlineData("/health")]
    [InlineData("/api/version")]
    [InlineData("/api/gateway/health")]
    public async Task 健康检查和版本API始终放行(string path)
    {
        _deploymentMode.Setup(x => x.IsCloudMode).Returns(true);

        var context = CreateHttpContext(path, "GET");
        var nextCalled = false;
        var middleware = CreateMiddleware(_ => { nextCalled = true; return Task.CompletedTask; });

        await middleware.InvokeAsync(context);

        nextCalled.Should().BeTrue($"{path} 健康检查应始终放行");
    }

    #endregion

    #region 非控制 API 正常通过

    [Theory]
    [InlineData("/api/account/users", "POST")]
    [InlineData("/api/station/list", "GET")]
    [InlineData("/api/analytics/report", "POST")]
    public async Task 非控制API的管理操作应正常放行(string path, string method)
    {
        _deploymentMode.Setup(x => x.IsCloudMode).Returns(true);

        var context = CreateHttpContext(path, method);
        var nextCalled = false;
        var middleware = CreateMiddleware(_ => { nextCalled = true; return Task.CompletedTask; });

        await middleware.InvokeAsync(context);

        nextCalled.Should().BeTrue($"非控制 API {method} {path} 应正常放行");
    }

    #endregion

    private static DefaultHttpContext CreateHttpContext(string path, string method)
    {
        var context = new DefaultHttpContext();
        context.Request.Path = path;
        context.Request.Method = method;
        context.Response.Body = new MemoryStream();
        return context;
    }
}
