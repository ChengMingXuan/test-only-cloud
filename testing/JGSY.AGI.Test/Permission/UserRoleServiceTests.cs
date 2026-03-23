using Xunit;
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using JGSY.AGI.Permission.Business;
using JGSY.AGI.Permission.Interfaces;
using JGSY.AGI.Permission.Entities;
using JGSY.AGI.Common.Core.Interfaces;
using JGSY.AGI.Common.Core.Exceptions;

namespace JGSY.AGI.Test.Permission;

/// <summary>
/// UserRoleService 单元测试
/// 覆盖：AssignRoles / RemoveAll / RemoveRole / GetUserRoles / HasRole / HasRoleByCode / UpdateRoleExpiry / BatchUpdateRoleExpiry
/// </summary>
public class UserRoleServiceTests
{
    private readonly Mock<IUserRoleRepository> _userRoleRepo = new();
    private readonly Mock<IRoleRepository> _roleRepo = new();
    private readonly Mock<IPermissionChecker> _permChecker = new();
    private readonly Mock<ITenantContext> _tenantCtx = new();
    private readonly UserRoleService _sut;

    private readonly Guid _tenantId = Guid.NewGuid();
    private readonly Guid _userId = Guid.NewGuid();
    private readonly Guid _operatorId = Guid.NewGuid();

    public UserRoleServiceTests()
    {
        _tenantCtx.Setup(t => t.TenantId).Returns(_tenantId);
        _tenantCtx.Setup(t => t.UserId).Returns(_operatorId);

        _sut = new UserRoleService(
            _userRoleRepo.Object,
            _roleRepo.Object,
            _permChecker.Object,
            _tenantCtx.Object,
            NullLogger<UserRoleService>.Instance);
    }

    // ========== AssignRolesAsync ==========

    [Fact]
    public async Task AssignRolesAsync_角色不存在_抛BusinessException()
    {
        var roleId = Guid.NewGuid();
        _roleRepo.Setup(r => r.GetByIdAsync(roleId, It.IsAny<CancellationToken>()))
            .ReturnsAsync((Role?)null);

        var act = () => _sut.AssignRolesAsync(_userId, new[] { roleId });
        await act.Should().ThrowAsync<BusinessException>();
    }

    [Fact]
    public async Task AssignRolesAsync_角色已禁用_抛BusinessException()
    {
        var roleId = Guid.NewGuid();
        _roleRepo.Setup(r => r.GetByIdAsync(roleId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new Role { Id = roleId, Status = (int)RoleStatus.Disabled, RoleName = "禁角" });

        var act = () => _sut.AssignRolesAsync(_userId, new[] { roleId });
        await act.Should().ThrowAsync<BusinessException>();
    }

    [Fact]
    public async Task AssignRolesAsync_成功_删旧增新并清缓存()
    {
        var roleId = Guid.NewGuid();
        _roleRepo.Setup(r => r.GetByIdAsync(roleId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new Role { Id = roleId, Status = (int)RoleStatus.Enabled, RoleName = "Admin" });
        _userRoleRepo.Setup(r => r.DeleteByUserIdAsync(_userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(1);
        _userRoleRepo.Setup(r => r.BatchAddAsync(_userId, It.IsAny<IEnumerable<Guid>>(), _operatorId, null, It.IsAny<CancellationToken>()))
            .ReturnsAsync(1);
        _permChecker.Setup(p => p.InvalidateUserCacheAsync(_userId, It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        var result = await _sut.AssignRolesAsync(_userId, new[] { roleId });

        result.Should().BeTrue();
        _userRoleRepo.Verify(r => r.DeleteByUserIdAsync(_userId, It.IsAny<CancellationToken>()), Times.Once);
        _userRoleRepo.Verify(r => r.BatchAddAsync(_userId, It.IsAny<IEnumerable<Guid>>(), _operatorId, null, It.IsAny<CancellationToken>()), Times.Once);
        _permChecker.Verify(p => p.InvalidateUserCacheAsync(_userId, It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task AssignRolesAsync_带过期时间()
    {
        var roleId = Guid.NewGuid();
        var expiry = DateTime.UtcNow.AddDays(30);
        _roleRepo.Setup(r => r.GetByIdAsync(roleId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new Role { Id = roleId, Status = (int)RoleStatus.Enabled, RoleName = "TempRole" });
        _userRoleRepo.Setup(r => r.DeleteByUserIdAsync(_userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(0);
        _userRoleRepo.Setup(r => r.BatchAddAsync(_userId, It.IsAny<IEnumerable<Guid>>(), _operatorId, expiry, It.IsAny<CancellationToken>()))
            .ReturnsAsync(1);
        _permChecker.Setup(p => p.InvalidateUserCacheAsync(_userId, It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        var result = await _sut.AssignRolesAsync(_userId, new[] { roleId }, expiry);

        result.Should().BeTrue();
        _userRoleRepo.Verify(r => r.BatchAddAsync(_userId, It.IsAny<IEnumerable<Guid>>(), _operatorId, expiry, It.IsAny<CancellationToken>()), Times.Once);
    }

    // ========== RemoveAllRolesAsync ==========

    [Fact]
    public async Task RemoveAllRolesAsync_成功_删除并清缓存()
    {
        _userRoleRepo.Setup(r => r.DeleteByUserIdAsync(_userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(3);
        _permChecker.Setup(p => p.InvalidateUserCacheAsync(_userId, It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        var result = await _sut.RemoveAllRolesAsync(_userId);

        result.Should().BeTrue();
        _permChecker.Verify(p => p.InvalidateUserCacheAsync(_userId, It.IsAny<CancellationToken>()), Times.Once);
    }

    // ========== RemoveRoleAsync ==========

    [Fact]
    public async Task RemoveRoleAsync_移除指定角色并清缓存()
    {
        var roleId = Guid.NewGuid();
        _userRoleRepo.Setup(r => r.RemoveAsync(_userId, It.IsAny<IEnumerable<Guid>>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(1);
        _permChecker.Setup(p => p.InvalidateUserCacheAsync(_userId, It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        var result = await _sut.RemoveRoleAsync(_userId, roleId);

        result.Should().BeTrue();
        _permChecker.Verify(p => p.InvalidateUserCacheAsync(_userId, It.IsAny<CancellationToken>()), Times.Once);
    }

    // ========== GetUserRolesAsync ==========

    [Fact]
    public async Task GetUserRolesAsync_返回角色DTO列表()
    {
        var roleId = Guid.NewGuid();
        _userRoleRepo.Setup(r => r.GetByUserIdAsync(_userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<UserRole>
            {
                new()
                {
                    UserId = _userId,
                    RoleId = roleId,
                    ExpiryDate = null,
                    Role = new Role { Id = roleId, RoleName = "管理员", RoleCode = "ADMIN" }
                }
            });

        var result = await _sut.GetUserRolesAsync(_userId);

        result.Should().HaveCount(1);
        result[0].RoleId.Should().Be(roleId);
        result[0].RoleName.Should().Be("管理员");
        result[0].RoleCode.Should().Be("ADMIN");
    }

    // ========== HasRoleAsync / HasRoleByCodeAsync ==========

    [Fact]
    public async Task HasRoleAsync_调用仓储()
    {
        var roleId = Guid.NewGuid();
        _userRoleRepo.Setup(r => r.HasRoleAsync(_userId, roleId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var result = await _sut.HasRoleAsync(_userId, roleId);
        result.Should().BeTrue();
    }

    [Fact]
    public async Task HasRoleByCodeAsync_角色编码不存在_返回false()
    {
        _roleRepo.Setup(r => r.GetByCodeAsync("NOEXIST", It.IsAny<CancellationToken>()))
            .ReturnsAsync((Role?)null);

        var result = await _sut.HasRoleByCodeAsync(_userId, "NOEXIST");
        result.Should().BeFalse();
    }

    [Fact]
    public async Task HasRoleByCodeAsync_角色存在_委托HasRoleAsync()
    {
        var roleId = Guid.NewGuid();
        _roleRepo.Setup(r => r.GetByCodeAsync("ADMIN", It.IsAny<CancellationToken>()))
            .ReturnsAsync(new Role { Id = roleId, RoleCode = "ADMIN" });
        _userRoleRepo.Setup(r => r.HasRoleAsync(_userId, roleId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var result = await _sut.HasRoleByCodeAsync(_userId, "ADMIN");
        result.Should().BeTrue();
    }

    // ========== UpdateRoleExpiryAsync ==========

    [Fact]
    public async Task UpdateRoleExpiryAsync_关联不存在_抛BusinessException()
    {
        var roleId = Guid.NewGuid();
        _userRoleRepo.Setup(r => r.GetByUserAndRoleAsync(_userId, roleId, It.IsAny<CancellationToken>()))
            .ReturnsAsync((UserRole?)null);

        var act = () => _sut.UpdateRoleExpiryAsync(_userId, roleId, DateTime.UtcNow.AddDays(30));
        await act.Should().ThrowAsync<BusinessException>();
    }

    [Fact]
    public async Task UpdateRoleExpiryAsync_成功更新过期时间()
    {
        var roleId = Guid.NewGuid();
        var newExpiry = DateTime.UtcNow.AddDays(60);
        _userRoleRepo.Setup(r => r.GetByUserAndRoleAsync(_userId, roleId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new UserRole { UserId = _userId, RoleId = roleId });
        _userRoleRepo.Setup(r => r.UpdateAsync(It.IsAny<UserRole>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((UserRole e, CancellationToken _) => e);
        _permChecker.Setup(p => p.InvalidateUserCacheAsync(_userId, It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        var result = await _sut.UpdateRoleExpiryAsync(_userId, roleId, newExpiry);

        result.Should().BeTrue();
        _userRoleRepo.Verify(r => r.UpdateAsync(It.Is<UserRole>(ur => ur.ExpiryDate == newExpiry), It.IsAny<CancellationToken>()), Times.Once);
        _permChecker.Verify(p => p.InvalidateUserCacheAsync(_userId, It.IsAny<CancellationToken>()), Times.Once);
    }

    // ========== BatchUpdateRoleExpiryAsync ==========

    [Fact]
    public async Task BatchUpdateRoleExpiryAsync_部分成功_返回成功计数()
    {
        var roleId1 = Guid.NewGuid();
        var roleId2 = Guid.NewGuid();

        // roleId1 存在, roleId2 不存在
        _userRoleRepo.Setup(r => r.GetByUserAndRoleAsync(_userId, roleId1, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new UserRole { UserId = _userId, RoleId = roleId1 });
        _userRoleRepo.Setup(r => r.GetByUserAndRoleAsync(_userId, roleId2, It.IsAny<CancellationToken>()))
            .ReturnsAsync((UserRole?)null);
        _userRoleRepo.Setup(r => r.UpdateAsync(It.IsAny<UserRole>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((UserRole e, CancellationToken _) => e);
        _permChecker.Setup(p => p.InvalidateUserCacheAsync(_userId, It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        var updates = new List<RoleExpiryUpdateItem>
        {
            new() { RoleId = roleId1, NewExpiryDate = DateTime.UtcNow.AddDays(30) },
            new() { RoleId = roleId2, NewExpiryDate = DateTime.UtcNow.AddDays(60) }
        };

        var result = await _sut.BatchUpdateRoleExpiryAsync(_userId, updates);

        result.Should().Be(1); // 只有 roleId1 成功
    }

    [Fact]
    public async Task BatchUpdateRoleExpiryAsync_全部成功_返回总数()
    {
        var roleId1 = Guid.NewGuid();
        var roleId2 = Guid.NewGuid();

        _userRoleRepo.Setup(r => r.GetByUserAndRoleAsync(_userId, It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((Guid uid, Guid rid, CancellationToken _) => new UserRole { UserId = uid, RoleId = rid });
        _userRoleRepo.Setup(r => r.UpdateAsync(It.IsAny<UserRole>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((UserRole e, CancellationToken _) => e);
        _permChecker.Setup(p => p.InvalidateUserCacheAsync(_userId, It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        var updates = new List<RoleExpiryUpdateItem>
        {
            new() { RoleId = roleId1, NewExpiryDate = DateTime.UtcNow.AddDays(30) },
            new() { RoleId = roleId2, NewExpiryDate = DateTime.UtcNow.AddDays(60) }
        };

        var result = await _sut.BatchUpdateRoleExpiryAsync(_userId, updates);

        result.Should().Be(2);
    }
}
