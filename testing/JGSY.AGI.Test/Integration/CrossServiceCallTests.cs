using System;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Threading.Tasks;
using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.Integration;

/// <summary>
/// 跨服务调用集成测试
/// 测试层级: L2-集成测试（服务间通信）
/// 测试场景: Identity → Permission → Tenant 服务间协同
/// 依赖服务: Identity(8002), Permission(8003), Tenant(8001)
/// </summary>
/// <remarks>
/// 测试目标:
/// 1. 验证 IServiceTransport 跨服务调用机制
/// 2. 验证内部服务认证（X-Internal-Service-Key）
/// 3. 验证租户隔离（TenantId 传递）
/// 4. 验证服务间数据一致性
/// </remarks>
public class CrossServiceCallTests
{
    private const string GatewayBaseUrl = "http://localhost:5000";
    private const string IdentityBaseUrl = "http://localhost:8002";
    private const string TenantBaseUrl = "http://localhost:8001";
    private const string PermissionBaseUrl = "http://localhost:8003";
    private const string InternalServiceKey = "jgsy_internal_service_key_2024_prod_v2!@#";
    private const string SkipReason = "需要完整基础设施运行（PostgreSQL + Consul + Redis）";

    /// <summary>
    /// 场景1: 创建租户 → 初始化权限 → 创建管理员用户（跨 3 个服务）
    /// </summary>
    [Fact(Skip = SkipReason)]
    public async Task CreateTenant_InitializePermissions_CreateAdminUser_ShouldSucceed()
    {
        // ==================== Step 1: 创建租户（Tenant 服务） ====================
        using var tenantClient = new HttpClient { BaseAddress = new Uri(TenantBaseUrl) };
        tenantClient.DefaultRequestHeaders.Add("X-Internal-Service-Key", InternalServiceKey);

        var tenantCode = $"TEST_{DateTime.Now.Ticks}";
        var createTenantRequest = new
        {
            TenantCode = tenantCode,
            CompanyName = $"测试公司_{tenantCode}",
            AdminName = "张三",
            AdminPhone = "13800000000",
            AdminEmail = $"admin_{tenantCode}@test.com",
            Industry = "互联网",
            Scale = "50-200人"
        };

        var createTenantResponse = await tenantClient.PostAsJsonAsync("/api/internal/tenant/create", createTenantRequest);
        createTenantResponse.StatusCode.Should().Be(HttpStatusCode.OK, "因为创建租户的请求数据有效");

        var tenantResult = await createTenantResponse.Content.ReadFromJsonAsync<TenantCreateResult>();
        tenantResult.Should().NotBeNull();
        tenantResult!.TenantId.Should().NotBeEmpty();

        var tenantId = tenantResult.TenantId;

        // ==================== Step 2: 为租户初始化默认权限（Permission 服务） ====================
        using var permissionClient = new HttpClient { BaseAddress = new Uri(PermissionBaseUrl) };
        permissionClient.DefaultRequestHeaders.Add("X-Internal-Service-Key", InternalServiceKey);
        permissionClient.DefaultRequestHeaders.Add("X-Tenant-Id", tenantId);

        var initPermissionRequest = new
        {
            TenantId = tenantId,
            IncludeModules = new[] { "tenant", "user", "permission", "device" }
        };

        var initPermissionResponse = await permissionClient.PostAsJsonAsync("/api/internal/permission/init-tenant-permissions", initPermissionRequest);
        initPermissionResponse.StatusCode.Should().Be(HttpStatusCode.OK, "因为权限初始化数据有效");

        var permissionResult = await initPermissionResponse.Content.ReadFromJsonAsync<PermissionInitResult>();
        permissionResult.Should().NotBeNull();
        permissionResult!.InitializedRoles.Should().Contain("TENANT_ADMIN");

        // ==================== Step 3: 创建租户管理员用户（Identity 服务） ====================
        using var identityClient = new HttpClient { BaseAddress = new Uri(IdentityBaseUrl) };
        identityClient.DefaultRequestHeaders.Add("X-Internal-Service-Key", InternalServiceKey);
        identityClient.DefaultRequestHeaders.Add("X-Tenant-Id", tenantId);

        var createUserRequest = new
        {
            Username = $"admin_{tenantCode}",
            Password = "P@ssw0rd",
            Email = $"admin_{tenantCode}@test.com",
            Phone = "13800000000",
            RealName = "张三",
            Roles = new[] { "TENANT_ADMIN" }
        };

        var createUserResponse = await identityClient.PostAsJsonAsync("/api/internal/identity/create-user", createUserRequest);
        createUserResponse.StatusCode.Should().Be(HttpStatusCode.OK, "因为用户创建数据有效");

        var userResult = await createUserResponse.Content.ReadFromJsonAsync<UserCreateResult>();
        userResult.Should().NotBeNull();
        userResult!.UserId.Should().NotBeEmpty();

        // ==================== Step 4: 验证创建的用户可以登录 ====================
        using var gatewayClient = new HttpClient { BaseAddress = new Uri(GatewayBaseUrl) };

        var loginRequest = new
        {
            Username = $"admin_{tenantCode}",
            Password = "P@ssw0rd",
            TenantCode = tenantCode
        };

        var loginResponse = await gatewayClient.PostAsJsonAsync("/api/identity/auth/login", loginRequest);
        loginResponse.StatusCode.Should().Be(HttpStatusCode.OK, "因为用户已成功创建");

        var loginResult = await loginResponse.Content.ReadFromJsonAsync<LoginResult>();
        loginResult.Should().NotBeNull();
        loginResult!.AccessToken.Should().NotBeNullOrEmpty();

        // ==================== Step 5: 验证用户的权限（跨服务查询） ====================
        gatewayClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", loginResult.AccessToken);

        var myPermissionsResponse = await gatewayClient.GetAsync("/api/permission/user-permission/my-permissions");
        myPermissionsResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var myPermissions = await myPermissionsResponse.Content.ReadFromJsonAsync<MyPermissionsResult>();
        myPermissions.Should().NotBeNull();
        myPermissions!.Permissions.Should().NotBeEmpty("因为为租户初始化了默认权限");
        myPermissions.Permissions.Should().Contain(p => p.StartsWith("tenant:"), "因为包含了 tenant 模块权限");
    }

    /// <summary>
    /// 场景2: 内部服务调用未携带 Key 应返回 401
    /// </summary>
    [Fact(Skip = SkipReason)]
    public async Task InternalServiceCall_WithoutApiKey_ShouldReturn401()
    {
        using var client = new HttpClient { BaseAddress = new Uri(TenantBaseUrl) };

        var createTenantRequest = new
        {
            TenantCode = "TEST_001",
            CompanyName = "测试公司",
            AdminName = "张三",
            AdminPhone = "13800000000",
            AdminEmail = "admin@test.com"
        };

        var response = await client.PostAsJsonAsync("/api/internal/tenant/create", createTenantRequest);
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized, "因为未提供 X-Internal-Service-Key");
    }

    /// <summary>
    /// 场景3: 内部服务调用使用错误的 Key 应返回 403
    /// </summary>
    [Fact(Skip = SkipReason)]
    public async Task InternalServiceCall_WithInvalidApiKey_ShouldReturn403()
    {
        using var client = new HttpClient { BaseAddress = new Uri(TenantBaseUrl) };
        client.DefaultRequestHeaders.Add("X-Internal-Service-Key", "wrong_api_key");

        var createTenantRequest = new
        {
            TenantCode = "TEST_001",
            CompanyName = "测试公司",
            AdminName = "张三",
            AdminPhone = "13800000000",
            AdminEmail = "admin@test.com"
        };

        var response = await client.PostAsJsonAsync("/api/internal/tenant/create", createTenantRequest);
        response.StatusCode.Should().Be(HttpStatusCode.Forbidden, "因为 API Key 无效");
    }

    /// <summary>
    /// 场景4: 验证租户隔离（用户只能查询自己租户的数据）
    /// </summary>
    [Fact(Skip = SkipReason)]
    public async Task TenantIsolation_UserCanOnlySeeOwnTenantData()
    {
        // 1. 创建两个租户和用户
        var tenant1Code = $"TENANT_A_{DateTime.Now.Ticks}";
        var tenant2Code = $"TENANT_B_{DateTime.Now.Ticks}";

        // (省略租户创建逻辑，假设已创建)

        // 2. Tenant1 用户登录
        using var client = new HttpClient { BaseAddress = new Uri(GatewayBaseUrl) };
        var loginResponse = await client.PostAsJsonAsync("/api/identity/auth/login", new
        {
            Username = $"admin_{tenant1Code}",
            Password = "P@ssw0rd",
            TenantCode = tenant1Code
        });

        var loginResult = await loginResponse.Content.ReadFromJsonAsync<LoginResult>();
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", loginResult!.AccessToken);

        // 3. 查询设备列表（应该只返回 Tenant1 的设备）
        var devicesResponse = await client.GetAsync("/api/device/device/list?page=1&pageSize=100");
        var devices = await devicesResponse.Content.ReadFromJsonAsync<PagedResult<DeviceDto>>();

        devices.Should().NotBeNull();
        devices!.Items.Should().OnlyContain(d => d.TenantId == loginResult.TenantId, "因为租户隔离生效");
    }

    /// <summary>
    /// 场景5: SUPER_ADMIN 可以跨租户查询数据
    /// </summary>
    [Fact(Skip = SkipReason)]
    public async Task SuperAdmin_CanAccessMultiTenantData()
    {
        using var client = new HttpClient { BaseAddress = new Uri(GatewayBaseUrl) };

        // 1. SUPER_ADMIN 登录
        var loginResponse = await client.PostAsJsonAsync("/api/identity/auth/login", new
        {
            Username = "superadmin",
            Password = "SuperAdmin@123",
            TenantCode = "PLATFORM"
        });

        var loginResult = await loginResponse.Content.ReadFromJsonAsync<LoginResult>();
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", loginResult!.AccessToken);

        // 2. 查询所有租户列表（跨租户）
        var tenantsResponse = await client.GetAsync("/api/tenant/tenant/list?page=1&pageSize=100");
        tenantsResponse.StatusCode.Should().Be(HttpStatusCode.OK, "因为 SUPER_ADMIN 有跨租户权限");

        var tenants = await tenantsResponse.Content.ReadFromJsonAsync<PagedResult<TenantDto>>();
        tenants.Should().NotBeNull();
        tenants!.Items.Should().NotBeEmpty("因为系统中至少有一个租户");
    }

    #region Response DTOs

    private record TenantCreateResult(string TenantId, string TenantCode);
    private record PermissionInitResult(string[] InitializedRoles, int PermissionCount);
    private record UserCreateResult(string UserId, string Username);
    private record LoginResult(string AccessToken, string RefreshToken, string TenantId);
    private record MyPermissionsResult(string[] Permissions);
    private record PagedResult<T>(T[] Items, int Total, int Page, int PageSize);
    private record DeviceDto(string Id, string TenantId, string DeviceName, string DeviceType);
    private record TenantDto(string Id, string TenantCode, string CompanyName);

    #endregion
}
