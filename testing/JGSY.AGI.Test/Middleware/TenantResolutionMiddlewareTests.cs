using FluentAssertions;
using Microsoft.AspNetCore.Http;
using Moq;
using JGSY.AGI.Common.Core.Interfaces;
using JGSY.AGI.Common.Core.Service;
using JGSY.AGI.Common.Core.Middlewares;
using Xunit;

namespace JGSY.AGI.Test.Middleware
{
    public class TenantResolutionMiddlewareTests
    {
        [Fact]
        public async Task InvokeAsync_ValidTenantId_ShouldSetTenantContext()
        {
            var tenantId = Guid.NewGuid();
            var tenantName = "TestTenant";

            var tenantProvider = new Mock<ITenantProvider>();
            tenantProvider.Setup(x => x.GetTenantId()).Returns(tenantId.ToString());
            tenantProvider.Setup(x => x.GetTenantName()).Returns(tenantName);

            var tenantContext = new TenantContext(new Mock<IHttpContextAccessor>().Object);

            var nextCalled = false;
            var middleware = new TenantResolutionMiddleware(ctx =>
            {
                nextCalled = true;
                return Task.CompletedTask;
            });

            var httpContext = new DefaultHttpContext();
            await middleware.InvokeAsync(httpContext, tenantProvider.Object, tenantContext);

            nextCalled.Should().BeTrue();
            tenantContext.TenantId.Should().Be(tenantId);
            tenantContext.TenantName.Should().Be(tenantName);
        }

        [Fact]
        public async Task InvokeAsync_EmptyTenantId_ShouldSetEmptyGuid()
        {
            var tenantProvider = new Mock<ITenantProvider>();
            tenantProvider.Setup(x => x.GetTenantId()).Returns(string.Empty);
            tenantProvider.Setup(x => x.GetTenantName()).Returns("Test");

            var tenantContext = new TenantContext(new Mock<IHttpContextAccessor>().Object);
            var middleware = new TenantResolutionMiddleware(ctx => Task.CompletedTask);

            await middleware.InvokeAsync(new DefaultHttpContext(), tenantProvider.Object, tenantContext);

            tenantContext.TenantId.Should().Be(Guid.Empty);
        }

        [Fact]
        public async Task InvokeAsync_NullTenantId_ShouldSetEmptyGuid()
        {
            var tenantProvider = new Mock<ITenantProvider>();
            tenantProvider.Setup(x => x.GetTenantId()).Returns((string?)null!);
            tenantProvider.Setup(x => x.GetTenantName()).Returns((string?)null!);

            var tenantContext = new TenantContext(new Mock<IHttpContextAccessor>().Object);
            var middleware = new TenantResolutionMiddleware(ctx => Task.CompletedTask);

            await middleware.InvokeAsync(new DefaultHttpContext(), tenantProvider.Object, tenantContext);

            tenantContext.TenantId.Should().Be(Guid.Empty);
            tenantContext.TenantName.Should().Be(string.Empty);
        }

        [Fact]
        public async Task InvokeAsync_InvalidGuidString_ShouldSetEmptyGuid()
        {
            var tenantProvider = new Mock<ITenantProvider>();
            tenantProvider.Setup(x => x.GetTenantId()).Returns("not-a-valid-guid");
            tenantProvider.Setup(x => x.GetTenantName()).Returns("Test");

            var tenantContext = new TenantContext(new Mock<IHttpContextAccessor>().Object);
            var middleware = new TenantResolutionMiddleware(ctx => Task.CompletedTask);

            await middleware.InvokeAsync(new DefaultHttpContext(), tenantProvider.Object, tenantContext);

            tenantContext.TenantId.Should().Be(Guid.Empty);
        }

        [Fact]
        public async Task InvokeAsync_WhitespaceTenantId_ShouldSetEmptyGuid()
        {
            var tenantProvider = new Mock<ITenantProvider>();
            tenantProvider.Setup(x => x.GetTenantId()).Returns("   ");
            tenantProvider.Setup(x => x.GetTenantName()).Returns("Test");

            var tenantContext = new TenantContext(new Mock<IHttpContextAccessor>().Object);
            var middleware = new TenantResolutionMiddleware(ctx => Task.CompletedTask);

            await middleware.InvokeAsync(new DefaultHttpContext(), tenantProvider.Object, tenantContext);

            tenantContext.TenantId.Should().Be(Guid.Empty);
        }

        [Fact]
        public async Task InvokeAsync_ShouldAlwaysCallNext()
        {
            var tenantProvider = new Mock<ITenantProvider>();
            tenantProvider.Setup(x => x.GetTenantId()).Returns(Guid.NewGuid().ToString());
            tenantProvider.Setup(x => x.GetTenantName()).Returns("Test");

            var nextCalled = false;
            var middleware = new TenantResolutionMiddleware(ctx =>
            {
                nextCalled = true;
                return Task.CompletedTask;
            });

            var tenantContext = new TenantContext(new Mock<IHttpContextAccessor>().Object);
            await middleware.InvokeAsync(new DefaultHttpContext(), tenantProvider.Object, tenantContext);

            nextCalled.Should().BeTrue();
        }
    }
}
