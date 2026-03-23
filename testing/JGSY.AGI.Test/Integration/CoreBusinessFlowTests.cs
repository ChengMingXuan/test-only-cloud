using System;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading.Tasks;
using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.Integration;

/// <summary>
/// 核心业务流程集成测试
/// 测试层级: L2-集成测试（跨服务调用）
/// 测试场景: 用户登录 → JWT Token → 权限校验 → 受保护 API 访问
/// 依赖服务: Gateway(5000), Identity(8002), Permission(8003), Tenant(8001)
/// </summary>
/// <remarks>
/// 执行前提:
/// 1. 启动基础设施: docker compose -f docker-compose.infrastructure.yml up -d
/// 2. 启动平台服务: docker compose -f docker-compose.platform-standalone.yml up -d
/// 3. 初始化数据库: .\scripts\init-databases.ps1
/// 4. 导入种子数据: .\scripts\import-seed-data.ps1
/// </remarks>
public class CoreBusinessFlowTests
{
    private const string GatewayBaseUrl = "http://localhost:5000";
    private const string SkipReason = "需要完整基础设施运行（PostgreSQL + Consul + Redis）";

    /// <summary>
    /// 场景1: 完整的用户登录→权限验证→API访问流程
    /// </summary>
    [Fact(Skip = SkipReason)]
    public async Task UserLogin_PermissionCheck_ProtectedApiAccess_ShouldSucceed()
    {
        using var client = new HttpClient { BaseAddress = new Uri(GatewayBaseUrl) };

        // ==================== Step 1: 用户登录获取 JWT Token ====================
        var loginRequest = new
        {
            Username = "admin",
            Password = "Admin@123",
            TenantCode = "PLATFORM"
        };

        var loginResponse = await client.PostAsJsonAsync("/api/identity/auth/login", loginRequest);
        loginResponse.StatusCode.Should().Be(HttpStatusCode.OK, "因为使用了正确的用户名和密码");

        var loginResult = await loginResponse.Content.ReadFromJsonAsync<ApiResult<LoginResponse>>();
        loginResult.Should().NotBeNull();
        loginResult!.Success.Should().BeTrue("因为登录应该成功");
        loginResult.Data.Should().NotBeNull();
        loginResult.Data!.AccessToken.Should().NotBeNullOrEmpty("因为登录成功应返回访问令牌");
        loginResult.Data.RefreshToken.Should().NotBeNullOrEmpty("因为应返回刷新令牌");
        loginResult.Data.TokenType.Should().Be("Bearer");

        var accessToken = loginResult.Data.AccessToken;

        // ==================== Step 2: 验证 JWT Token 信息 ====================
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", accessToken);

        var userInfoResponse = await client.GetAsync("/api/identity/auth/userinfo");
        userInfoResponse.StatusCode.Should().Be(HttpStatusCode.OK, "因为携带了有效的 JWT Token");

        var userInfo = await userInfoResponse.Content.ReadFromJsonAsync<ApiResult<UserInfoResponse>>();
        userInfo.Should().NotBeNull();
        userInfo!.Success.Should().BeTrue();
        userInfo.Data.Should().NotBeNull();
        userInfo.Data!.Username.Should().Be("admin");

        // ==================== Step 3: 获取用户权限列表 ====================
        var permissionsResponse = await client.GetAsync("/api/permission/user-permission/my-permissions");
        permissionsResponse.StatusCode.Should().Be(HttpStatusCode.OK, "因为已经通过身份验证");

        var permissions = await permissionsResponse.Content.ReadFromJsonAsync<ApiResult<PermissionListResponse>>();
        permissions.Should().NotBeNull();
        permissions!.Success.Should().BeTrue();
        permissions.Data.Should().NotBeNull();
        permissions.Data!.Permissions.Should().NotBeEmpty("因为 admin 用户应该有权限");

        // ==================== Step 4: 访问受保护的 API（需要权限） ====================
        var tenantListResponse = await client.GetAsync("/api/tenant/tenant/list?page=1&pageSize=20");
        tenantListResponse.StatusCode.Should().Be(HttpStatusCode.OK, "因为 admin 有 tenant:tenant:view 权限");

        var tenants = await tenantListResponse.Content.ReadFromJsonAsync<ApiResult<PagedResult<TenantDto>>>();
        tenants.Should().NotBeNull();
        tenants!.Success.Should().BeTrue();
        tenants.Data.Should().NotBeNull();

        // ==================== Step 5: 尝试访问无权限的 API（应返回 403） ====================
        var unauthorizedResponse = await client.DeleteAsync("/api/tenant/tenant/999");
        unauthorizedResponse.StatusCode.Should().Be(HttpStatusCode.Forbidden, "因为普通 admin 没有删除租户的权限");
    }

    /// <summary>
    /// 场景2: 无效登录凭据应返回 401
    /// </summary>
    [Fact(Skip = SkipReason)]
    public async Task Login_WithInvalidCredentials_ShouldReturn401()
    {
        using var client = new HttpClient { BaseAddress = new Uri(GatewayBaseUrl) };

        var loginRequest = new
        {
            Username = "admin",
            Password = "WrongPassword",
            TenantCode = "PLATFORM"
        };

        var response = await client.PostAsJsonAsync("/api/identity/auth/login", loginRequest);
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized, "因为密码错误");

        var result = await response.Content.ReadFromJsonAsync<ApiResult<object>>();
        result.Should().NotBeNull();
        result!.Success.Should().BeFalse();
        result.Message.Should().Contain("密码");
    }

    /// <summary>
    /// 场景3: 访问受保护 API 时未携带 Token 应返回 401
    /// </summary>
    [Fact(Skip = SkipReason)]
    public async Task AccessProtectedApi_WithoutToken_ShouldReturn401()
    {
        using var client = new HttpClient { BaseAddress = new Uri(GatewayBaseUrl) };

        var response = await client.GetAsync("/api/tenant/tenant/list");
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized, "因为未提供 JWT Token");
    }

    /// <summary>
    /// 场景4: 使用过期或无效的 Token 应返回 401
    /// </summary>
    [Fact(Skip = SkipReason)]
    public async Task AccessProtectedApi_WithExpiredToken_ShouldReturn401()
    {
        using var client = new HttpClient { BaseAddress = new Uri(GatewayBaseUrl) };

        var invalidToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c";
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", invalidToken);

        var response = await client.GetAsync("/api/tenant/tenant/list");
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized, "因为 Token 无效");
    }

    /// <summary>
    /// 场景5: Refresh Token 刷新流程
    /// </summary>
    [Fact(Skip = SkipReason)]
    public async Task RefreshToken_ShouldReturnNewAccessToken()
    {
        using var client = new HttpClient { BaseAddress = new Uri(GatewayBaseUrl) };

        // 1. 先登录获取 Token 对
        var loginRequest = new { Username = "admin", Password = "Admin@123", TenantCode = "PLATFORM" };
        var loginResponse = await client.PostAsJsonAsync("/api/identity/auth/login", loginRequest);
        var loginResult = await loginResponse.Content.ReadFromJsonAsync<ApiResult<LoginResponse>>();

        var refreshToken = loginResult!.Data!.RefreshToken;

        // 2. 使用 Refresh Token 刷新
        var refreshRequest = new { RefreshToken = refreshToken };
        var refreshResponse = await client.PostAsJsonAsync("/api/identity/auth/refresh", refreshRequest);
        refreshResponse.StatusCode.Should().Be(HttpStatusCode.OK, "因为 Refresh Token 是有效的");

        var refreshResult = await refreshResponse.Content.ReadFromJsonAsync<ApiResult<LoginResponse>>();
        refreshResult.Should().NotBeNull();
        refreshResult!.Success.Should().BeTrue();
        refreshResult.Data!.AccessToken.Should().NotBeNullOrEmpty("因为应返回新的 Access Token");
        refreshResult.Data.AccessToken.Should().NotBe(loginResult.Data.AccessToken, "因为应该是新生成的 Token");
    }

    #region Response DTOs

    private record ApiResult<T>(bool Success, int Code, string Message, T? Data, string Timestamp, string TraceId);
    private record PagedResult<T>(T[] Items, int Total, int Page, int PageSize);
    private record LoginResponse(string AccessToken, string RefreshToken, string TokenType, int ExpiresIn);
    private record UserInfoResponse(string UserId, string Username, string TenantId, string TenantCode, string[] Roles);
    private record PermissionListResponse(string[] Permissions);
    private record TenantDto(string Id, string TenantCode, string CompanyName, string Status);

    #endregion
}
