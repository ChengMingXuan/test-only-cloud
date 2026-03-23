using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using JGSY.AGI.Common.Core.Security;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;

namespace JGSY.AGI.Test.Permission;

/// <summary>
/// 权限中间件的基础行为验证（401/403/SUPER_ADMIN/正常放行）
/// </summary>
public class PermissionAuthorizationMiddlewareTests
{
    private static HttpContext CreateHttpContext(params Attribute[] metadata)
    {
        var context = new DefaultHttpContext();
        context.Response.Body = new MemoryStream();
        context.SetEndpoint(new Endpoint(_ => Task.CompletedTask, new EndpointMetadataCollection(metadata), "test"));
        return context;
    }

    [Fact]
    public async Task ShouldReturn401WhenUserMissing()
    {
        var checker = new Mock<IPermissionChecker>(MockBehavior.Strict);
        var nextCalled = false;
        var middleware = new PermissionAuthorizationMiddleware(_ =>
        {
            nextCalled = true;
            return Task.CompletedTask;
        }, NullLogger<PermissionAuthorizationMiddleware>.Instance);

        var context = CreateHttpContext(new RequirePermissionAttribute("perm:a"));

        await middleware.InvokeAsync(context, checker.Object);

        context.Response.StatusCode.Should().Be(StatusCodes.Status401Unauthorized);
        nextCalled.Should().BeFalse();
    }

    [Fact]
    public async Task ShouldBypassWhenSuperAdminRole()
    {
        var checker = new Mock<IPermissionChecker>(MockBehavior.Strict);
        var nextCalled = false;
        var middleware = new PermissionAuthorizationMiddleware(_ =>
        {
            nextCalled = true;
            return Task.CompletedTask;
        }, NullLogger<PermissionAuthorizationMiddleware>.Instance);

        var context = CreateHttpContext(new RequirePermissionAttribute("perm:a"));
        context.User = new ClaimsPrincipal(new ClaimsIdentity(new[]
        {
            new Claim(ClaimTypes.Role, "SUPER_ADMIN"),
            new Claim(ClaimTypes.NameIdentifier, Guid.NewGuid().ToString())
        }, authenticationType: "Test"));

        await middleware.InvokeAsync(context, checker.Object);

        nextCalled.Should().BeTrue();
        checker.Invocations.Should().BeEmpty();
        context.Response.StatusCode.Should().Be(StatusCodes.Status200OK);
    }

    [Fact]
    public async Task ShouldReturn403WhenPermissionDenied()
    {
        var checker = new Mock<IPermissionChecker>();
        checker.Setup(p => p.CheckPermissionsAsync(It.IsAny<Guid>(), It.IsAny<IEnumerable<string>>(), true, It.IsAny<CancellationToken>()))
            .ReturnsAsync(false);

        var middleware = new PermissionAuthorizationMiddleware(_ => Task.CompletedTask, NullLogger<PermissionAuthorizationMiddleware>.Instance);

        var context = CreateHttpContext(new RequirePermissionAttribute("perm:x"));
        context.User = new ClaimsPrincipal(new ClaimsIdentity(new[]
        {
            new Claim(ClaimTypes.NameIdentifier, Guid.NewGuid().ToString())
        }, authenticationType: "Test"));

        await middleware.InvokeAsync(context, checker.Object);

        context.Response.StatusCode.Should().Be(StatusCodes.Status403Forbidden);
        context.Response.Body.Position = 0;
        using var reader = new StreamReader(context.Response.Body);
        var body = await reader.ReadToEndAsync();
        body.Should().Contain("缺少权限");
    }

    [Fact]
    public async Task ShouldCallNextWhenPermissionGranted()
    {
        var checker = new Mock<IPermissionChecker>();
        var userId = Guid.NewGuid();
        checker.Setup(p => p.CheckPermissionsAsync(userId, It.Is<IEnumerable<string>>(codes => codes.Contains("perm:y")), true, It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var nextCalled = false;
        var middleware = new PermissionAuthorizationMiddleware(_ =>
        {
            nextCalled = true;
            return Task.CompletedTask;
        }, NullLogger<PermissionAuthorizationMiddleware>.Instance);

        var context = CreateHttpContext(new RequirePermissionAttribute("perm:y"));
        context.User = new ClaimsPrincipal(new ClaimsIdentity(new[]
        {
            new Claim(ClaimTypes.NameIdentifier, userId.ToString())
        }, authenticationType: "Test"));

        await middleware.InvokeAsync(context, checker.Object);

        nextCalled.Should().BeTrue();
        context.Response.StatusCode.Should().Be(StatusCodes.Status200OK);
        checker.VerifyAll();
    }
}
