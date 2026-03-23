using FluentAssertions;
using Microsoft.AspNetCore.Http;
using Moq;
using JGSY.AGI.Common.Core.Service;
using System.Security.Claims;
using Xunit;

namespace JGSY.AGI.Test.Common
{
    public class TenantContextTests
    {
        #region TenantId from JWT Claims

        [Fact]
        public void TenantId_FromAuthenticatedUser_ShouldReturnTenantId()
        {
            var expectedTenantId = Guid.NewGuid();
            var context = CreateAuthenticatedContext(expectedTenantId.ToString(), null, "USER");

            var tenantContext = new TenantContext(CreateAccessor(context));

            tenantContext.TenantId.Should().Be(expectedTenantId);
        }

        [Fact]
        public void TenantId_SuperAdmin_ShouldReturnSystemAdminTenantId()
        {
            // No tenant_id claim but SUPER_ADMIN role
            var context = CreateAuthenticatedContext(null, null, "SUPER_ADMIN");

            var tenantContext = new TenantContext(CreateAccessor(context));

            tenantContext.TenantId.Should().Be(TenantContext.SystemAdminTenantId);
        }

        [Fact]
        public void TenantId_InternalService_ShouldReturnSystemAdminTenantId()
        {
            var context = CreateAuthenticatedContext(null, null, "INTERNAL_SERVICE");

            var tenantContext = new TenantContext(CreateAccessor(context));

            tenantContext.TenantId.Should().Be(TenantContext.SystemAdminTenantId);
        }

        [Fact]
        public void TenantId_AuthenticatedNoTenantClaim_ShouldReturnEmpty()
        {
            var context = CreateAuthenticatedContext(null, null, "REGULAR_USER");

            var tenantContext = new TenantContext(CreateAccessor(context));

            tenantContext.TenantId.Should().Be(Guid.Empty);
        }

        #endregion

        #region TenantId from Header

        [Fact]
        public void TenantId_FromHeader_ShouldReturnTenantId()
        {
            var expectedTenantId = Guid.NewGuid();
            var context = new DefaultHttpContext();
            context.Request.Headers["X-Tenant-Id"] = expectedTenantId.ToString();

            var tenantContext = new TenantContext(CreateAccessor(context));

            tenantContext.TenantId.Should().Be(expectedTenantId);
        }

        [Fact]
        public void TenantId_InvalidHeader_ShouldReturnEmpty()
        {
            var context = new DefaultHttpContext();
            context.Request.Headers["X-Tenant-Id"] = "not-a-guid";

            var tenantContext = new TenantContext(CreateAccessor(context));

            tenantContext.TenantId.Should().Be(Guid.Empty);
        }

        [Fact]
        public void TenantId_NoHeader_ShouldReturnEmpty()
        {
            var context = new DefaultHttpContext();

            var tenantContext = new TenantContext(CreateAccessor(context));

            tenantContext.TenantId.Should().Be(Guid.Empty);
        }

        #endregion

        #region TenantId from SetTenant

        [Fact]
        public void TenantId_AfterSetTenant_ShouldReturnSetValue()
        {
            var expectedTenantId = Guid.NewGuid();
            var tenantContext = new TenantContext(CreateAccessor(new DefaultHttpContext()));

            tenantContext.SetTenant(expectedTenantId, "TestTenant");

            tenantContext.TenantId.Should().Be(expectedTenantId);
            tenantContext.TenantName.Should().Be("TestTenant");
        }

        #endregion

        #region TenantName

        [Fact]
        public void TenantName_FromHeader_ShouldReturnName()
        {
            var context = new DefaultHttpContext();
            context.Request.Headers["X-Tenant-Name"] = "MyTenant";

            var tenantContext = new TenantContext(CreateAccessor(context));

            tenantContext.TenantName.Should().Be("MyTenant");
        }

        [Fact]
        public void TenantName_NoHeader_ShouldReturnEmpty()
        {
            var context = new DefaultHttpContext();
            var tenantContext = new TenantContext(CreateAccessor(context));

            tenantContext.TenantName.Should().Be(string.Empty);
        }

        [Fact]
        public void TenantName_SetOverridesHeader()
        {
            var context = new DefaultHttpContext();
            context.Request.Headers["X-Tenant-Name"] = "HeaderTenant";
            var tenantContext = new TenantContext(CreateAccessor(context));

            tenantContext.SetTenant(Guid.NewGuid(), "OverrideTenant");

            tenantContext.TenantName.Should().Be("OverrideTenant");
        }

        #endregion

        #region UserId

        [Fact]
        public void UserId_FromClaims_ShouldReturnUserId()
        {
            var expectedUserId = Guid.NewGuid();
            var context = CreateAuthenticatedContext(null, expectedUserId.ToString(), "USER");

            var tenantContext = new TenantContext(CreateAccessor(context));

            tenantContext.UserId.Should().Be(expectedUserId);
        }

        [Fact]
        public void UserId_FromHeader_ShouldReturnUserId()
        {
            var expectedUserId = Guid.NewGuid();
            var context = new DefaultHttpContext();
            context.Request.Headers["X-User-Id"] = expectedUserId.ToString();

            var tenantContext = new TenantContext(CreateAccessor(context));

            tenantContext.UserId.Should().Be(expectedUserId);
        }

        [Fact]
        public void UserId_NoClaimsOrHeaders_ShouldReturnEmpty()
        {
            var context = new DefaultHttpContext();
            var tenantContext = new TenantContext(CreateAccessor(context));

            tenantContext.UserId.Should().Be(Guid.Empty);
        }

        [Fact]
        public void UserId_AfterSetUser_ShouldReturnSetValue()
        {
            var expectedUserId = Guid.NewGuid();
            var tenantContext = new TenantContext(CreateAccessor(new DefaultHttpContext()));

            tenantContext.SetUser(expectedUserId);

            tenantContext.UserId.Should().Be(expectedUserId);
        }

        #endregion

        #region HasValidTenant / HasUser / RequireTenantId

        [Fact]
        public void HasValidTenant_WithTenantId_ShouldReturnTrue()
        {
            var tenantContext = new TenantContext(CreateAccessor(new DefaultHttpContext()));
            tenantContext.SetTenant(Guid.NewGuid(), "Test");

            tenantContext.HasValidTenant.Should().BeTrue();
        }

        [Fact]
        public void HasValidTenant_NoTenantId_ShouldReturnFalse()
        {
            var tenantContext = new TenantContext(CreateAccessor(new DefaultHttpContext()));

            tenantContext.HasValidTenant.Should().BeFalse();
        }

        [Fact]
        public void RequireTenantId_WithTenant_ShouldReturnId()
        {
            var id = Guid.NewGuid();
            var tenantContext = new TenantContext(CreateAccessor(new DefaultHttpContext()));
            tenantContext.SetTenant(id, "Test");

            tenantContext.RequireTenantId().Should().Be(id);
        }

        [Fact]
        public void RequireTenantId_NoTenant_ShouldThrow()
        {
            var tenantContext = new TenantContext(CreateAccessor(new DefaultHttpContext()));

            var action = () => tenantContext.RequireTenantId();
            action.Should().Throw<UnauthorizedAccessException>()
                  .WithMessage("*租户*");
        }

        #endregion

        #region NullHttpContext

        [Fact]
        public void TenantId_NullHttpContext_ShouldReturnEmpty()
        {
            var accessor = new Mock<IHttpContextAccessor>();
            accessor.Setup(x => x.HttpContext).Returns((HttpContext?)null);

            var tenantContext = new TenantContext(accessor.Object);

            tenantContext.TenantId.Should().Be(Guid.Empty);
        }

        [Fact]
        public void UserId_NullHttpContext_ShouldReturnEmpty()
        {
            var accessor = new Mock<IHttpContextAccessor>();
            accessor.Setup(x => x.HttpContext).Returns((HttpContext?)null);

            var tenantContext = new TenantContext(accessor.Object);

            tenantContext.UserId.Should().Be(Guid.Empty);
        }

        #endregion

        #region SystemAdminTenantId

        [Fact]
        public void SystemAdminTenantId_ShouldBeConstants()
        {
            TenantContext.SystemAdminTenantId.Should().Be(new Guid("00000000-0000-0000-0000-000000000001"));
        }

        #endregion

        private static IHttpContextAccessor CreateAccessor(HttpContext context)
        {
            var accessor = new Mock<IHttpContextAccessor>();
            accessor.Setup(x => x.HttpContext).Returns(context);
            return accessor.Object;
        }

        private static DefaultHttpContext CreateAuthenticatedContext(string? tenantId, string? userId, string role)
        {
            var claims = new List<Claim>();

            if (!string.IsNullOrEmpty(tenantId))
                claims.Add(new Claim("tenant_id", tenantId));

            if (!string.IsNullOrEmpty(userId))
                claims.Add(new Claim(ClaimTypes.NameIdentifier, userId));

            claims.Add(new Claim(ClaimTypes.Role, role));
            claims.Add(new Claim(ClaimTypes.Name, "testuser"));

            var identity = new ClaimsIdentity(claims, "TestAuth");
            var principal = new ClaimsPrincipal(identity);

            var context = new DefaultHttpContext();
            context.User = principal;
            return context;
        }
    }
}
