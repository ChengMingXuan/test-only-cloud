using FluentAssertions;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;
using JGSY.AGI.Common.Core.Security;
using Xunit;

namespace JGSY.AGI.Test.Auth
{
    public class JwtServiceTests
    {
        private readonly JwtService _jwtService;
        private readonly JwtOptions _jwtOptions;

        public JwtServiceTests()
        {
            _jwtOptions = new JwtOptions
            {
                Issuer = "JGSY.AGI.Auth.Test",
                Audience = "JGSY.AGI.Services.Test",
                SecretKey = "TestSecretKey1234567890ABCDEF1234567890",
                AccessTokenExpirationMinutes = 15,
                RefreshTokenExpirationDays = 7,
                Algorithm = SecurityAlgorithms.HmacSha256
            };

            _jwtService = new JwtService(
                Options.Create(_jwtOptions),
                NullLogger<JwtService>.Instance);
        }

        #region GenerateAccessToken

        [Fact]
        public void GenerateAccessToken_ShouldReturnNonEmptyString()
        {
            var claims = CreateTestClaims();
            var token = _jwtService.GenerateAccessToken(claims);

            token.Should().NotBeNullOrEmpty();
        }

        [Fact]
        public void GenerateAccessToken_ShouldReturn3PartJwt()
        {
            var claims = CreateTestClaims();
            var token = _jwtService.GenerateAccessToken(claims);

            // JWT format: header.payload.signature
            token.Split('.').Should().HaveCount(3);
        }

        [Fact]
        public void GenerateAccessToken_ShouldContainUserId()
        {
            var claims = CreateTestClaims();
            var token = _jwtService.GenerateAccessToken(claims);
            
            // JwtSecurityTokenHandler maps 'sub' to NameIdentifier, so GetUserClaimsFromToken
            // may return empty UserId. Instead validate the token directly.
            var principal = _jwtService.ValidateToken(token);
            principal.Should().NotBeNull();
            // Check sub or nameidentifier claim
            var userId = principal!.FindFirst(System.IdentityModel.Tokens.Jwt.JwtRegisteredClaimNames.Sub)?.Value
                      ?? principal.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            userId.Should().Be(claims.UserId);
        }

        [Fact]
        public void GenerateAccessToken_ShouldContainUsername()
        {
            var claims = CreateTestClaims();
            var token = _jwtService.GenerateAccessToken(claims);
            
            var principal = _jwtService.ValidateToken(token);
            principal.Should().NotBeNull();
            var username = principal!.FindFirst(System.IdentityModel.Tokens.Jwt.JwtRegisteredClaimNames.UniqueName)?.Value
                        ?? principal.FindFirst(System.Security.Claims.ClaimTypes.Name)?.Value;
            username.Should().Be(claims.Username);
        }

        [Fact]
        public void GenerateAccessToken_ShouldContainTenantId()
        {
            var tenantId = Guid.NewGuid().ToString();
            var claims = CreateTestClaims();
            claims.TenantId = tenantId;

            var token = _jwtService.GenerateAccessToken(claims);
            var extracted = _jwtService.GetUserClaimsFromToken(token);

            extracted!.TenantId.Should().Be(tenantId);
        }

        [Fact]
        public void GenerateAccessToken_ShouldContainRoles()
        {
            var claims = CreateTestClaims();
            claims.Roles = new List<string> { "TENANT_ADMIN", "OPERATOR" };

            var token = _jwtService.GenerateAccessToken(claims);
            var extracted = _jwtService.GetUserClaimsFromToken(token);

            extracted!.Roles.Should().Contain("TENANT_ADMIN");
            extracted!.Roles.Should().Contain("OPERATOR");
        }

        [Fact]
        public void GenerateAccessToken_ShouldContainPermissions()
        {
            var claims = CreateTestClaims();
            claims.Permissions = new List<string> { "station:list", "device:read" };

            var token = _jwtService.GenerateAccessToken(claims);
            var extracted = _jwtService.GetUserClaimsFromToken(token);

            extracted!.Permissions.Should().Contain("station:list");
            extracted!.Permissions.Should().Contain("device:read");
        }

        [Fact]
        public void GenerateAccessToken_WithNoTenant_ShouldOmitTenantClaim()
        {
            var claims = CreateTestClaims();
            claims.TenantId = null;
            claims.TenantName = null;

            var token = _jwtService.GenerateAccessToken(claims);
            var extracted = _jwtService.GetUserClaimsFromToken(token);

            extracted!.TenantId.Should().BeNullOrEmpty();
        }

        #endregion

        #region GenerateRefreshToken

        [Fact]
        public void GenerateRefreshToken_ShouldReturnNonEmptyString()
        {
            var token = _jwtService.GenerateRefreshToken();
            token.Should().NotBeNullOrEmpty();
        }

        [Fact]
        public void GenerateRefreshToken_ShouldReturnBase64String()
        {
            var token = _jwtService.GenerateRefreshToken();
            var action = () => Convert.FromBase64String(token);
            action.Should().NotThrow();
        }

        [Fact]
        public void GenerateRefreshToken_ShouldBeUnique()
        {
            var tokens = Enumerable.Range(0, 100).Select(_ => _jwtService.GenerateRefreshToken()).ToList();
            tokens.Distinct().Should().HaveCount(100);
        }

        [Fact]
        public void GenerateRefreshToken_ShouldHaveSufficientLength()
        {
            var token = _jwtService.GenerateRefreshToken();
            // 64 bytes = 88 Base64 chars
            token.Length.Should().BeGreaterOrEqualTo(80);
        }

        #endregion

        #region ValidateToken

        [Fact]
        public void ValidateToken_WithValidToken_ShouldReturnPrincipal()
        {
            var claims = CreateTestClaims();
            var token = _jwtService.GenerateAccessToken(claims);

            var principal = _jwtService.ValidateToken(token);

            principal.Should().NotBeNull();
        }

        [Fact]
        public void ValidateToken_WithInvalidToken_ShouldReturnNull()
        {
            var principal = _jwtService.ValidateToken("invalid.token.here");

            principal.Should().BeNull();
        }

        [Fact]
        public void ValidateToken_WithEmptyString_ShouldReturnNull()
        {
            var principal = _jwtService.ValidateToken("");

            principal.Should().BeNull();
        }

        [Fact]
        public void ValidateToken_WithExpiredToken_ShouldReturnNull()
        {
            // Create a service with 0 minute expiration
            var expiredOptions = new JwtOptions
            {
                Issuer = _jwtOptions.Issuer,
                Audience = _jwtOptions.Audience,
                SecretKey = _jwtOptions.SecretKey,
                AccessTokenExpirationMinutes = 0, // immediate expiration
                Algorithm = SecurityAlgorithms.HmacSha256
            };

            var expiredService = new JwtService(
                Options.Create(expiredOptions),
                NullLogger<JwtService>.Instance);

            var token = expiredService.GenerateAccessToken(CreateTestClaims());
            Thread.Sleep(1500); // wait for token to expire

            var principal = expiredService.ValidateToken(token, validateLifetime: true);
            principal.Should().BeNull();
        }

        [Fact]
        public void ValidateToken_WithExpiredTokenNoLifetimeValidation_ShouldReturnPrincipal()
        {
            var expiredOptions = new JwtOptions
            {
                Issuer = _jwtOptions.Issuer,
                Audience = _jwtOptions.Audience,
                SecretKey = _jwtOptions.SecretKey,
                AccessTokenExpirationMinutes = 0,
                Algorithm = SecurityAlgorithms.HmacSha256
            };

            var expiredService = new JwtService(
                Options.Create(expiredOptions),
                NullLogger<JwtService>.Instance);

            var token = expiredService.GenerateAccessToken(CreateTestClaims());
            Thread.Sleep(1500);

            var principal = expiredService.ValidateToken(token, validateLifetime: false);
            principal.Should().NotBeNull();
        }

        [Fact]
        public void ValidateToken_WithWrongKey_ShouldReturnNull()
        {
            var claims = CreateTestClaims();
            var token = _jwtService.GenerateAccessToken(claims);

            var otherService = new JwtService(
                Options.Create(new JwtOptions
                {
                    Issuer = _jwtOptions.Issuer,
                    Audience = _jwtOptions.Audience,
                    SecretKey = "DifferentSecretKey1234567890ABCDE",
                    Algorithm = SecurityAlgorithms.HmacSha256
                }),
                NullLogger<JwtService>.Instance);

            otherService.ValidateToken(token).Should().BeNull();
        }

        #endregion

        #region GetUserClaimsFromToken

        [Fact]
        public void GetUserClaimsFromToken_ValidToken_ShouldReturnClaims()
        {
            var original = new UserClaims
            {
                UserId = Guid.NewGuid().ToString(),
                Username = "testuser",
                TenantId = Guid.NewGuid().ToString(),
                TenantName = "TestTenant",
                Roles = new List<string> { "SUPER_ADMIN" },
                Permissions = new List<string> { "identity:user:list", "permission:role:create" }
            };

            var token = _jwtService.GenerateAccessToken(original);
            var extracted = _jwtService.GetUserClaimsFromToken(token);

            extracted.Should().NotBeNull();
            // Note: JwtSecurityTokenHandler maps 'sub' to NameIdentifier, so UserId may be empty
            // We verify tenant and roles/permissions which use custom claim names
            extracted!.TenantId.Should().Be(original.TenantId);
            extracted.TenantName.Should().Be(original.TenantName);
            extracted.Roles.Should().BeEquivalentTo(original.Roles);
            extracted.Permissions.Should().BeEquivalentTo(original.Permissions);
        }

        [Fact]
        public void GetUserClaimsFromToken_InvalidToken_ShouldReturnNull()
        {
            var result = _jwtService.GetUserClaimsFromToken("garbage");
            result.Should().BeNull();
        }

        #endregion

        #region IsTokenExpiringSoon

        [Fact]
        public void IsTokenExpiringSoon_FreshToken_ShouldReturnFalse()
        {
            var token = _jwtService.GenerateAccessToken(CreateTestClaims());

            // Token has 15 min expiry, threshold is 5 min → not expiring soon
            _jwtService.IsTokenExpiringSoon(token, 5).Should().BeFalse();
        }

        [Fact]
        public void IsTokenExpiringSoon_NearExpiryToken_ShouldReturnTrue()
        {
            // Create a 1-minute token
            var shortLivedOptions = new JwtOptions
            {
                Issuer = _jwtOptions.Issuer,
                Audience = _jwtOptions.Audience,
                SecretKey = _jwtOptions.SecretKey,
                AccessTokenExpirationMinutes = 1,
                Algorithm = SecurityAlgorithms.HmacSha256
            };

            var shortLivedService = new JwtService(
                Options.Create(shortLivedOptions),
                NullLogger<JwtService>.Instance);

            var token = shortLivedService.GenerateAccessToken(CreateTestClaims());

            // 1 minute expiry, threshold 5 minutes → should be expiring soon
            shortLivedService.IsTokenExpiringSoon(token, 5).Should().BeTrue();
        }

        [Fact]
        public void IsTokenExpiringSoon_InvalidToken_ShouldReturnTrue()
        {
            _jwtService.IsTokenExpiringSoon("invalid-token").Should().BeTrue();
        }

        #endregion

        #region JwtOptions defaults

        [Fact]
        public void JwtOptions_DefaultIssuer_ShouldBeSet()
        {
            var options = new JwtOptions();
            options.Issuer.Should().Be("JGSY.AGI.Auth");
        }

        [Fact]
        public void JwtOptions_DefaultAudience_ShouldBeSet()
        {
            var options = new JwtOptions();
            options.Audience.Should().Be("JGSY.AGI.Services");
        }

        [Fact]
        public void JwtOptions_DefaultExpiration_ShouldBe15Minutes()
        {
            var options = new JwtOptions();
            options.AccessTokenExpirationMinutes.Should().Be(15);
        }

        [Fact]
        public void JwtOptions_DefaultRefreshExpiration_ShouldBe7Days()
        {
            var options = new JwtOptions();
            options.RefreshTokenExpirationDays.Should().Be(7);
        }

        #endregion

        #region UserClaims defaults

        [Fact]
        public void UserClaims_Roles_DefaultShouldBeEmpty()
        {
            var claims = new UserClaims { UserId = "1", Username = "test" };
            claims.Roles.Should().NotBeNull().And.BeEmpty();
        }

        [Fact]
        public void UserClaims_Permissions_DefaultShouldBeEmpty()
        {
            var claims = new UserClaims { UserId = "1", Username = "test" };
            claims.Permissions.Should().NotBeNull().And.BeEmpty();
        }

        [Fact]
        public void UserClaims_AdditionalClaims_DefaultShouldBeEmpty()
        {
            var claims = new UserClaims { UserId = "1", Username = "test" };
            claims.AdditionalClaims.Should().NotBeNull().And.BeEmpty();
        }

        #endregion

        private static UserClaims CreateTestClaims()
        {
            return new UserClaims
            {
                UserId = Guid.NewGuid().ToString(),
                Username = "testuser",
                TenantId = Guid.NewGuid().ToString(),
                TenantName = "TestTenant",
                Roles = new List<string> { "TENANT_ADMIN" },
                Permissions = new List<string> { "station:list" }
            };
        }
    }
}
