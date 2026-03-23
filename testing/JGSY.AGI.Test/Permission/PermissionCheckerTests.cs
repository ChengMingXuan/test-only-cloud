using Xunit;
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Logging.Abstractions;
using JGSY.AGI.Permission.Business;
using JGSY.AGI.Permission.Interfaces;
using JGSY.AGI.Permission.Entities;
using JGSY.AGI.Common.Core.Interfaces;

namespace JGSY.AGI.Test.Permission;

/// <summary>
/// PermissionChecker 单元测试
/// 覆盖：CheckPermission / CheckPermissions(AND/OR) / CheckRole / GetUserPermissionCodes(L1→L2→DB) / InvalidateUserCache / InvalidateRoleCache / WarmupCache
/// </summary>
public class PermissionCheckerTests
{
    private readonly Mock<IPermissionRepository> _permRepo = new();
    private readonly Mock<IRoleRepository> _roleRepo = new();
    private readonly Mock<IUserRoleRepository> _userRoleRepo = new();
    private readonly Mock<ICacheManager> _cacheManager = new();
    private readonly Mock<ITenantContext> _tenantCtx = new();
    private readonly IMemoryCache _memoryCache;
    private readonly PermissionChecker _sut;

    private readonly Guid _tenantId = Guid.NewGuid();
    private readonly Guid _userId = Guid.NewGuid();

    public PermissionCheckerTests()
    {
        _tenantCtx.Setup(t => t.TenantId).Returns(_tenantId);
        _tenantCtx.Setup(t => t.UserId).Returns(_userId);

        // 使用真实 MemoryCache 以测试两级缓存逻辑
        _memoryCache = new MemoryCache(new MemoryCacheOptions());

        _sut = new PermissionChecker(
            _permRepo.Object,
            _roleRepo.Object,
            _userRoleRepo.Object,
            _cacheManager.Object,
            _memoryCache,
            _tenantCtx.Object,
            NullLogger<PermissionChecker>.Instance);
    }

    // ========== CheckPermissionAsync ==========

    [Fact]
    public async Task CheckPermissionAsync_空UserId_返回false()
    {
        var result = await _sut.CheckPermissionAsync(Guid.Empty, "user:create");
        result.Should().BeFalse();
    }

    [Fact]
    public async Task CheckPermissionAsync_空PermCode_返回false()
    {
        var result = await _sut.CheckPermissionAsync(_userId, "");
        result.Should().BeFalse();
    }

    [Fact]
    public async Task CheckPermissionAsync_SUPER_ADMIN_直接放行()
    {
        // L2 缓存返回角色含 SUPER_ADMIN
        var roleCacheKey = $"perm:user:roles:{_tenantId}:{_userId}";
        _cacheManager.Setup(c => c.GetAsync<HashSet<string>>(roleCacheKey, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new HashSet<string> { "SUPER_ADMIN" });

        var result = await _sut.CheckPermissionAsync(_userId, "any:perm");
        result.Should().BeTrue();
    }

    [Fact]
    public async Task CheckPermissionAsync_有权限_返回true()
    {
        SetupUserRolesFromDb(new HashSet<string> { "OPERATOR" });
        SetupUserPermissionsFromDb(new HashSet<string> { "user:create", "user:read" });

        var result = await _sut.CheckPermissionAsync(_userId, "user:create");
        result.Should().BeTrue();
    }

    [Fact]
    public async Task CheckPermissionAsync_无权限_返回false()
    {
        SetupUserRolesFromDb(new HashSet<string> { "VIEWER" });
        SetupUserPermissionsFromDb(new HashSet<string> { "user:read" });

        var result = await _sut.CheckPermissionAsync(_userId, "user:delete");
        result.Should().BeFalse();
    }

    [Fact]
    public async Task CheckPermissionAsync_异常时_返回false()
    {
        // 让角色加载直接抛异常
        var roleCacheKey = $"perm:user:roles:{_tenantId}:{_userId}";
        _cacheManager.Setup(c => c.GetAsync<HashSet<string>>(roleCacheKey, It.IsAny<CancellationToken>()))
            .ThrowsAsync(new InvalidOperationException("Redis宕机"));

        var result = await _sut.CheckPermissionAsync(_userId, "some:perm");
        result.Should().BeFalse(); // 失败默认拒绝
    }

    // ========== CheckPermissionsAsync ==========

    [Fact]
    public async Task CheckPermissionsAsync_空UserId_返回false()
    {
        var result = await _sut.CheckPermissionsAsync(Guid.Empty, new[] { "a" });
        result.Should().BeFalse();
    }

    [Fact]
    public async Task CheckPermissionsAsync_空权限列表_返回true()
    {
        var result = await _sut.CheckPermissionsAsync(_userId, Array.Empty<string>());
        result.Should().BeTrue();
    }

    [Fact]
    public async Task CheckPermissionsAsync_SUPER_ADMIN_直接放行()
    {
        SetupUserRolesFromDb(new HashSet<string> { "SUPER_ADMIN" });

        var result = await _sut.CheckPermissionsAsync(_userId, new[] { "a", "b", "c" }, requireAll: true);
        result.Should().BeTrue();
    }

    [Fact]
    public async Task CheckPermissionsAsync_AND模式_需要全部权限()
    {
        SetupUserRolesFromDb(new HashSet<string> { "USER" });
        SetupUserPermissionsFromDb(new HashSet<string> { "a", "b" });

        var resultAll = await _sut.CheckPermissionsAsync(_userId, new[] { "a", "b" }, requireAll: true);
        resultAll.Should().BeTrue();

        // 清缓存重新测试，缺少 c
        _memoryCache.Remove($"perm:user:perms:{_tenantId}:{_userId}");
        _memoryCache.Remove($"perm:user:roles:{_tenantId}:{_userId}");

        SetupUserRolesFromDb(new HashSet<string> { "USER" });
        SetupUserPermissionsFromDb(new HashSet<string> { "a", "b" });

        var resultMissing = await _sut.CheckPermissionsAsync(_userId, new[] { "a", "b", "c" }, requireAll: true);
        resultMissing.Should().BeFalse();
    }

    [Fact]
    public async Task CheckPermissionsAsync_OR模式_任一权限即可()
    {
        SetupUserRolesFromDb(new HashSet<string> { "USER" });
        SetupUserPermissionsFromDb(new HashSet<string> { "a" });

        var result = await _sut.CheckPermissionsAsync(_userId, new[] { "a", "b", "c" }, requireAll: false);
        result.Should().BeTrue();
    }

    [Fact]
    public async Task CheckPermissionsAsync_OR模式_全部缺少_返回false()
    {
        SetupUserRolesFromDb(new HashSet<string> { "USER" });
        SetupUserPermissionsFromDb(new HashSet<string> { "x" });

        var result = await _sut.CheckPermissionsAsync(_userId, new[] { "a", "b" }, requireAll: false);
        result.Should().BeFalse();
    }

    // ========== CheckRoleAsync ==========

    [Fact]
    public async Task CheckRoleAsync_空UserId_返回false()
    {
        var result = await _sut.CheckRoleAsync(Guid.Empty, "ADMIN");
        result.Should().BeFalse();
    }

    [Fact]
    public async Task CheckRoleAsync_空RoleCode_返回false()
    {
        var result = await _sut.CheckRoleAsync(_userId, "");
        result.Should().BeFalse();
    }

    [Fact]
    public async Task CheckRoleAsync_有角色_返回true()
    {
        SetupUserRolesFromDb(new HashSet<string> { "ADMIN", "OPERATOR" });

        var result = await _sut.CheckRoleAsync(_userId, "ADMIN");
        result.Should().BeTrue();
    }

    [Fact]
    public async Task CheckRoleAsync_无角色_返回false()
    {
        SetupUserRolesFromDb(new HashSet<string> { "VIEWER" });

        var result = await _sut.CheckRoleAsync(_userId, "ADMIN");
        result.Should().BeFalse();
    }

    // ========== 两级缓存测试 ==========

    [Fact]
    public async Task GetUserPermissionCodes_L1缓存命中_不查L2()
    {
        var cacheKey = $"perm:user:perms:{_tenantId}:{_userId}";
        _memoryCache.Set(cacheKey, new HashSet<string> { "cached:perm" });

        var result = await _sut.GetUserPermissionCodesAsync(_userId);

        result.Should().Contain("cached:perm");
        // 不应调用 L2 缓存
        _cacheManager.Verify(c => c.GetAsync<HashSet<string>>(cacheKey, It.IsAny<CancellationToken>()), Times.Never);
    }

    [Fact]
    public async Task GetUserPermissionCodes_L2缓存命中_回写L1()
    {
        var cacheKey = $"perm:user:perms:{_tenantId}:{_userId}";
        _cacheManager.Setup(c => c.GetAsync<HashSet<string>>(cacheKey, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new HashSet<string> { "redis:perm" });

        var result = await _sut.GetUserPermissionCodesAsync(_userId);

        result.Should().Contain("redis:perm");
        // L1 应已被回写
        _memoryCache.TryGetValue(cacheKey, out HashSet<string>? l1).Should().BeTrue();
        l1.Should().Contain("redis:perm");
    }

    [Fact]
    public async Task GetUserPermissionCodes_缓存全Miss_从DB加载并写入双缓存()
    {
        var cacheKey = $"perm:user:perms:{_tenantId}:{_userId}";
        _cacheManager.Setup(c => c.GetAsync<HashSet<string>>(cacheKey, It.IsAny<CancellationToken>()))
            .ReturnsAsync((HashSet<string>?)null);

        // DB 加载路径
        _userRoleRepo.Setup(r => r.GetValidRoleIdsAsync(_userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<Guid> { Guid.NewGuid() });
        _permRepo.Setup(r => r.GetByRoleIdsAsync(It.IsAny<IEnumerable<Guid>>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<PermissionEntity>
            {
                new() { PermCode = "db:perm1", IsEnabled = true },
                new() { PermCode = "db:perm2", IsEnabled = true },
                new() { PermCode = "disabled:perm", IsEnabled = false }
            });

        var result = await _sut.GetUserPermissionCodesAsync(_userId);

        result.Should().Contain("db:perm1");
        result.Should().Contain("db:perm2");
        result.Should().NotContain("disabled:perm"); // 禁用权限不返回

        // 写入 L2
        _cacheManager.Verify(c => c.SetAsync(cacheKey, It.IsAny<HashSet<string>>(), It.IsAny<TimeSpan?>(), It.IsAny<CancellationToken>()), Times.Once);
        // 写入 L1
        _memoryCache.TryGetValue(cacheKey, out _).Should().BeTrue();
    }

    [Fact]
    public async Task GetUserPermissionCodes_无角色_返回空集合()
    {
        _cacheManager.Setup(c => c.GetAsync<HashSet<string>>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((HashSet<string>?)null);
        _userRoleRepo.Setup(r => r.GetValidRoleIdsAsync(_userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<Guid>());

        var result = await _sut.GetUserPermissionCodesAsync(_userId);
        result.Should().BeEmpty();
    }

    // ========== GetUserRoleCodesAsync ==========

    [Fact]
    public async Task GetUserRoleCodes_从DB加载角色编码()
    {
        var roleCacheKey = $"perm:user:roles:{_tenantId}:{_userId}";
        _cacheManager.Setup(c => c.GetAsync<HashSet<string>>(roleCacheKey, It.IsAny<CancellationToken>()))
            .ReturnsAsync((HashSet<string>?)null);
        _roleRepo.Setup(r => r.GetUserRolesAsync(_userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<Role>
            {
                new() { RoleCode = "ADMIN" },
                new() { RoleCode = "OPERATOR" }
            });

        var result = await _sut.GetUserRoleCodesAsync(_userId);

        result.Should().Contain("ADMIN");
        result.Should().Contain("OPERATOR");
    }

    // ========== InvalidateUserCacheAsync ==========

    [Fact]
    public async Task InvalidateUserCacheAsync_清除双缓存()
    {
        var permKey = $"perm:user:perms:{_tenantId}:{_userId}";
        var roleKey = $"perm:user:roles:{_tenantId}:{_userId}";

        // 预置 L1 缓存
        _memoryCache.Set(permKey, new HashSet<string> { "cached" });
        _memoryCache.Set(roleKey, new HashSet<string> { "cached" });

        await _sut.InvalidateUserCacheAsync(_userId);

        // L1 已清除
        _memoryCache.TryGetValue(permKey, out _).Should().BeFalse();
        _memoryCache.TryGetValue(roleKey, out _).Should().BeFalse();

        // L2 也清除
        _cacheManager.Verify(c => c.RemoveAsync(permKey, It.IsAny<CancellationToken>()), Times.Once);
        _cacheManager.Verify(c => c.RemoveAsync(roleKey, It.IsAny<CancellationToken>()), Times.Once);
    }

    // ========== InvalidateRoleCacheAsync ==========

    [Fact]
    public async Task InvalidateRoleCacheAsync_清除角色权限缓存()
    {
        var roleId = Guid.NewGuid();
        var cacheKey = $"perm:role:perms:{_tenantId}:{roleId}";

        _memoryCache.Set(cacheKey, new HashSet<string> { "cached" });

        await _sut.InvalidateRoleCacheAsync(roleId);

        _memoryCache.TryGetValue(cacheKey, out _).Should().BeFalse();
        _cacheManager.Verify(c => c.RemoveAsync(cacheKey, It.IsAny<CancellationToken>()), Times.Once);
    }

    // ========== InvalidateUsersCacheAsync ==========

    [Fact]
    public async Task InvalidateUsersCacheAsync_批量清除()
    {
        var user1 = Guid.NewGuid();
        var user2 = Guid.NewGuid();

        // 仅验证不抛异常即可
        await _sut.InvalidateUsersCacheAsync(new[] { user1, user2 });

        _cacheManager.Verify(c => c.RemoveAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()), Times.Exactly(4)); // 2用户 × 2缓存key
    }

    // ========== WarmupUserCacheAsync ==========

    [Fact]
    public async Task WarmupUserCacheAsync_预热用户缓存()
    {
        // DB 路径
        SetupUserRolesFromDb(new HashSet<string>());
        SetupUserPermissionsFromDb(new HashSet<string>());

        await _sut.WarmupUserCacheAsync(_userId);

        // 缓存应该已写入
        var permKey = $"perm:user:perms:{_tenantId}:{_userId}";
        var roleKey = $"perm:user:roles:{_tenantId}:{_userId}";
        _memoryCache.TryGetValue(permKey, out _).Should().BeTrue();
        _memoryCache.TryGetValue(roleKey, out _).Should().BeTrue();
    }

    // ========== 辅助方法 ==========

    /// <summary>
    /// 配置从 DB 加载用户角色编码（绕过缓存）
    /// </summary>
    private void SetupUserRolesFromDb(HashSet<string> roleCodes)
    {
        var roleCacheKey = $"perm:user:roles:{_tenantId}:{_userId}";
        _cacheManager.Setup(c => c.GetAsync<HashSet<string>>(roleCacheKey, It.IsAny<CancellationToken>()))
            .ReturnsAsync((HashSet<string>?)null);
        _roleRepo.Setup(r => r.GetUserRolesAsync(_userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(roleCodes.Select(code => new Role { RoleCode = code }).ToList());
    }

    /// <summary>
    /// 配置从 DB 加载用户权限编码（绕过缓存）
    /// </summary>
    private void SetupUserPermissionsFromDb(HashSet<string> permCodes)
    {
        var permCacheKey = $"perm:user:perms:{_tenantId}:{_userId}";
        _cacheManager.Setup(c => c.GetAsync<HashSet<string>>(permCacheKey, It.IsAny<CancellationToken>()))
            .ReturnsAsync((HashSet<string>?)null);
        _userRoleRepo.Setup(r => r.GetValidRoleIdsAsync(_userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<Guid> { Guid.NewGuid() });
        _permRepo.Setup(r => r.GetByRoleIdsAsync(It.IsAny<IEnumerable<Guid>>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(permCodes.Select(code => new PermissionEntity { PermCode = code, IsEnabled = true }).ToList());
    }
}
