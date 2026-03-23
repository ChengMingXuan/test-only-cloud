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
/// PermissionService 单元测试
/// 覆盖：Create / Update / Delete / GetById / GetByCode / GetTree / GetList / SetEnabled / BatchImport
/// </summary>
public class PermissionServiceTests
{
    private readonly Mock<IPermissionRepository> _permRepo = new();
    private readonly Mock<IRolePermissionRepository> _rolePermRepo = new();
    private readonly Mock<IUserRoleRepository> _userRoleRepo = new();
    private readonly Mock<IPermissionChecker> _permChecker = new();
    private readonly Mock<ITenantContext> _tenantCtx = new();
    private readonly PermissionService _sut;

    private readonly Guid _tenantId = Guid.NewGuid();
    private readonly Guid _userId = Guid.NewGuid();

    public PermissionServiceTests()
    {
        _tenantCtx.Setup(t => t.TenantId).Returns(_tenantId);
        _tenantCtx.Setup(t => t.UserId).Returns(_userId);

        _sut = new PermissionService(
            _permRepo.Object,
            _rolePermRepo.Object,
            _userRoleRepo.Object,
            _permChecker.Object,
            _tenantCtx.Object,
            NullLogger<PermissionService>.Instance);
    }

    // ========== CreateAsync ==========

    [Fact]
    public async Task CreateAsync_成功_返回新Id()
    {
        var req = new PermissionCreateRequest
        {
            PermName = "用户管理",
            PermCode = "user:manage",
            PermType = PermissionType.Menu
        };

        _permRepo.Setup(r => r.ExistsByCodeAsync("user:manage", null, It.IsAny<CancellationToken>()))
            .ReturnsAsync(false);
        _permRepo.Setup(r => r.AddAsync(It.IsAny<PermissionEntity>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity e, CancellationToken _) => e);

        var result = await _sut.CreateAsync(req);

        result.Should().NotBeEmpty();
        _permRepo.Verify(r => r.AddAsync(It.Is<PermissionEntity>(e =>
            e.PermCode == "user:manage" &&
            e.TenantId == _tenantId &&
            e.IsEnabled == true), It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_编码已存在_抛BusinessException()
    {
        _permRepo.Setup(r => r.ExistsByCodeAsync("dup:code", null, It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var req = new PermissionCreateRequest { PermCode = "dup:code", PermName = "重复" };

        var act = () => _sut.CreateAsync(req);
        await act.Should().ThrowAsync<BusinessException>();
    }

    [Fact]
    public async Task CreateAsync_有效ParentId_不抛异常()
    {
        var parentId = Guid.NewGuid();
        _permRepo.Setup(r => r.ExistsByCodeAsync(It.IsAny<string>(), null, It.IsAny<CancellationToken>()))
            .ReturnsAsync(false);
        _permRepo.Setup(r => r.GetByIdAsync(parentId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new PermissionEntity { Id = parentId });
        _permRepo.Setup(r => r.AddAsync(It.IsAny<PermissionEntity>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity e, CancellationToken _) => e);

        var req = new PermissionCreateRequest
        {
            PermName = "子权限",
            PermCode = "sub:perm",
            ParentId = parentId
        };

        var result = await _sut.CreateAsync(req);
        result.Should().NotBeEmpty();
    }

    [Fact]
    public async Task CreateAsync_ParentId不存在_抛BusinessException()
    {
        var parentId = Guid.NewGuid();
        _permRepo.Setup(r => r.ExistsByCodeAsync(It.IsAny<string>(), null, It.IsAny<CancellationToken>()))
            .ReturnsAsync(false);
        _permRepo.Setup(r => r.GetByIdAsync(parentId, It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity?)null);

        var req = new PermissionCreateRequest
        {
            PermCode = "child:perm",
            PermName = "子",
            ParentId = parentId
        };

        var act = () => _sut.CreateAsync(req);
        await act.Should().ThrowAsync<BusinessException>();
    }

    // ========== UpdateAsync ==========

    [Fact]
    public async Task UpdateAsync_权限不存在_抛NotFoundException()
    {
        var permId = Guid.NewGuid();
        _permRepo.Setup(r => r.GetByIdAsync(permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity?)null);

        var act = () => _sut.UpdateAsync(permId, new PermissionUpdateRequest());
        await act.Should().ThrowAsync<NotFoundException>();
    }

    [Fact]
    public async Task UpdateAsync_编码唯一性校验_已存在则抛BusinessException()
    {
        var permId = Guid.NewGuid();
        _permRepo.Setup(r => r.GetByIdAsync(permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new PermissionEntity { Id = permId, PermCode = "old:code" });
        _permRepo.Setup(r => r.ExistsByCodeAsync("new:code", permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var act = () => _sut.UpdateAsync(permId, new PermissionUpdateRequest { PermCode = "new:code" });
        await act.Should().ThrowAsync<BusinessException>();
    }

    [Fact]
    public async Task UpdateAsync_自引用父级_抛BusinessException()
    {
        var permId = Guid.NewGuid();
        _permRepo.Setup(r => r.GetByIdAsync(permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new PermissionEntity { Id = permId, PermCode = "self" });

        var act = () => _sut.UpdateAsync(permId, new PermissionUpdateRequest { ParentId = permId });
        await act.Should().ThrowAsync<BusinessException>();
    }

    [Fact]
    public async Task UpdateAsync_循环引用_子权限设为父级_抛BusinessException()
    {
        var permId = Guid.NewGuid();
        var childId = Guid.NewGuid();
        _permRepo.Setup(r => r.GetByIdAsync(permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new PermissionEntity { Id = permId, PermCode = "parent" });
        _permRepo.Setup(r => r.GetChildIdsAsync(permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<Guid> { permId, childId });

        var act = () => _sut.UpdateAsync(permId, new PermissionUpdateRequest { ParentId = childId });
        await act.Should().ThrowAsync<BusinessException>();
    }

    [Fact]
    public async Task UpdateAsync_父级不存在_抛BusinessException()
    {
        var permId = Guid.NewGuid();
        var newParentId = Guid.NewGuid();
        _permRepo.Setup(r => r.GetByIdAsync(permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new PermissionEntity { Id = permId, PermCode = "x" });
        _permRepo.Setup(r => r.GetChildIdsAsync(permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<Guid> { permId });
        _permRepo.Setup(r => r.GetByIdAsync(newParentId, It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity?)null);

        var act = () => _sut.UpdateAsync(permId, new PermissionUpdateRequest { ParentId = newParentId });
        await act.Should().ThrowAsync<BusinessException>();
    }

    [Fact]
    public async Task UpdateAsync_正常更新_返回true()
    {
        var permId = Guid.NewGuid();
        _permRepo.Setup(r => r.GetByIdAsync(permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new PermissionEntity { Id = permId, PermCode = "old" });
        _permRepo.Setup(r => r.ExistsByCodeAsync("new:code", permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(false);
        _permRepo.Setup(r => r.UpdateAsync(It.IsAny<PermissionEntity>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity e, CancellationToken _) => e);

        var result = await _sut.UpdateAsync(permId, new PermissionUpdateRequest
        {
            PermCode = "new:code",
            PermName = "新名称",
            SortOrder = 10,
            Remark = "备注"
        });

        result.Should().BeTrue();
        _permRepo.Verify(r => r.UpdateAsync(It.Is<PermissionEntity>(e =>
            e.PermCode == "new:code" && e.PermName == "新名称" && e.SortOrder == 10 && e.UpdateBy == _userId),
            It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task UpdateAsync_清除ParentId_设为null()
    {
        var permId = Guid.NewGuid();
        var oldParentId = Guid.NewGuid();
        _permRepo.Setup(r => r.GetByIdAsync(permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new PermissionEntity { Id = permId, PermCode = "x", ParentId = oldParentId });
        _permRepo.Setup(r => r.UpdateAsync(It.IsAny<PermissionEntity>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity e, CancellationToken _) => e);

        // ParentId 显式传 null 且原来有值 → 清除
        var result = await _sut.UpdateAsync(permId, new PermissionUpdateRequest());

        result.Should().BeTrue();
    }

    // ========== DeleteAsync ==========

    [Fact]
    public async Task DeleteAsync_权限不存在_抛NotFoundException()
    {
        var permId = Guid.NewGuid();
        _permRepo.Setup(r => r.GetByIdAsync(permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity?)null);

        var act = () => _sut.DeleteAsync(permId);
        await act.Should().ThrowAsync<NotFoundException>();
    }

    [Fact]
    public async Task DeleteAsync_级联删除子权限和角色关联()
    {
        var permId = Guid.NewGuid();
        var child1 = Guid.NewGuid();
        var child2 = Guid.NewGuid();

        _permRepo.Setup(r => r.GetByIdAsync(permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new PermissionEntity { Id = permId });
        _permRepo.Setup(r => r.GetChildIdsAsync(permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<Guid> { permId, child1, child2 });
        _rolePermRepo.Setup(r => r.DeleteByPermIdAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(1);
        _permRepo.Setup(r => r.DeleteAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var result = await _sut.DeleteAsync(permId);

        result.Should().BeTrue();
        // 3个权限的角色关联都要删除
        _rolePermRepo.Verify(r => r.DeleteByPermIdAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()), Times.Exactly(3));
        // 3个权限本身也要删除
        _permRepo.Verify(r => r.DeleteAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()), Times.Exactly(3));
    }

    // ========== GetByIdAsync ==========

    [Fact]
    public async Task GetByIdAsync_不存在_返回null()
    {
        _permRepo.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity?)null);

        var result = await _sut.GetByIdAsync(Guid.NewGuid());
        result.Should().BeNull();
    }

    [Fact]
    public async Task GetByIdAsync_有父级_解析ParentName()
    {
        var permId = Guid.NewGuid();
        var parentId = Guid.NewGuid();

        var callCount = 0;
        _permRepo.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((Guid id, CancellationToken _) =>
            {
                callCount++;
                if (callCount == 1)
                    return new PermissionEntity { Id = permId, PermCode = "child", PermName = "子权限", ParentId = parentId };
                return new PermissionEntity { Id = parentId, PermCode = "parent", PermName = "父权限" };
            });

        var result = await _sut.GetByIdAsync(permId);

        result.Should().NotBeNull();
        result!.PermCode.Should().Be("child");
        result.ParentName.Should().Be("父权限");
    }

    [Fact]
    public async Task GetByIdAsync_无父级_ParentName为null()
    {
        var permId = Guid.NewGuid();
        _permRepo.Setup(r => r.GetByIdAsync(permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new PermissionEntity { Id = permId, PermCode = "root", PermName = "根" });

        var result = await _sut.GetByIdAsync(permId);

        result.Should().NotBeNull();
        result!.ParentName.Should().BeNull();
    }

    // ========== GetByCodeAsync ==========

    [Fact]
    public async Task GetByCodeAsync_不存在_返回null()
    {
        _permRepo.Setup(r => r.GetByCodeAsync("no:exist", It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity?)null);

        var result = await _sut.GetByCodeAsync("no:exist");
        result.Should().BeNull();
    }

    // ========== GetTreeAsync ==========

    [Fact]
    public async Task GetTreeAsync_返回树结构()
    {
        var rootId = Guid.NewGuid();
        var childId = Guid.NewGuid();
        var allPerms = new List<PermissionEntity>
        {
            new() { Id = rootId, PermName = "根", PermCode = "root", SortOrder = 1 },
            new() { Id = childId, PermName = "子", PermCode = "child", ParentId = rootId, SortOrder = 2 }
        };

        _permRepo.Setup(r => r.GetAllAsync(It.IsAny<CancellationToken>()))
            .ReturnsAsync(allPerms);

        var result = await _sut.GetTreeAsync();

        result.Should().HaveCount(1);
        result[0].Children.Should().HaveCount(1);
        result[0].Children[0].PermCode.Should().Be("child");
    }

    [Fact]
    public async Task GetTreeAsync_按类型过滤()
    {
        _permRepo.Setup(r => r.GetByTypeAsync(PermissionType.Api, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<PermissionEntity>
            {
                new() { Id = Guid.NewGuid(), PermCode = "api:test", PermType = PermissionType.Api }
            });

        var result = await _sut.GetTreeAsync(PermissionType.Api);
        result.Should().HaveCount(1);
    }

    // ========== GetListAsync ==========

    [Fact]
    public async Task GetListAsync_按关键词过滤()
    {
        _permRepo.Setup(r => r.GetAllAsync(It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<PermissionEntity>
            {
                new() { Id = Guid.NewGuid(), PermName = "用户管理", PermCode = "user:manage", SortOrder = 1 },
                new() { Id = Guid.NewGuid(), PermName = "设备管理", PermCode = "device:manage", SortOrder = 2 }
            });

        var result = await _sut.GetListAsync(new PermissionQueryRequest { Keyword = "用户" });
        result.Should().HaveCount(1);
        result[0].PermCode.Should().Be("user:manage");
    }

    [Fact]
    public async Task GetListAsync_按启用状态过滤()
    {
        _permRepo.Setup(r => r.GetAllAsync(It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<PermissionEntity>
            {
                new() { Id = Guid.NewGuid(), PermCode = "a", IsEnabled = true, SortOrder = 1 },
                new() { Id = Guid.NewGuid(), PermCode = "b", IsEnabled = false, SortOrder = 2 }
            });

        var result = await _sut.GetListAsync(new PermissionQueryRequest { IsEnabled = true });
        result.Should().HaveCount(1);
        result[0].PermCode.Should().Be("a");
    }

    // ========== SetEnabledAsync ==========

    [Fact]
    public async Task SetEnabledAsync_不存在_抛NotFoundException()
    {
        _permRepo.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity?)null);

        var act = () => _sut.SetEnabledAsync(Guid.NewGuid(), true);
        await act.Should().ThrowAsync<NotFoundException>();
    }

    [Fact]
    public async Task SetEnabledAsync_成功_更新IsEnabled()
    {
        var permId = Guid.NewGuid();
        _permRepo.Setup(r => r.GetByIdAsync(permId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new PermissionEntity { Id = permId, IsEnabled = false });
        _permRepo.Setup(r => r.UpdateAsync(It.IsAny<PermissionEntity>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity e, CancellationToken _) => e);

        var result = await _sut.SetEnabledAsync(permId, true);

        result.Should().BeTrue();
        _permRepo.Verify(r => r.UpdateAsync(It.Is<PermissionEntity>(e =>
            e.IsEnabled == true && e.UpdateBy == _userId), It.IsAny<CancellationToken>()), Times.Once);
    }

    // ========== BatchImportAsync ==========

    [Fact]
    public async Task BatchImportAsync_跳过已存在的编码_返回实际导入数量()
    {
        var existingPerm = new PermissionEntity { Id = Guid.NewGuid(), PermCode = "existing:code" };
        _permRepo.Setup(r => r.GetAllAsync(It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<PermissionEntity> { existingPerm });
        _permRepo.Setup(r => r.AddAsync(It.IsAny<PermissionEntity>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity e, CancellationToken _) => e);
        _permRepo.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity?)null);

        var importList = new List<PermissionImportDto>
        {
            new() { PermCode = "existing:code", PermName = "已存在" },
            new() { PermCode = "new:code", PermName = "新权限", PermType = PermissionType.Api }
        };

        var result = await _sut.BatchImportAsync(importList);

        result.Should().Be(1); // 只有 new:code 被导入
    }

    [Fact]
    public async Task BatchImportAsync_处理父级关系()
    {
        _permRepo.Setup(r => r.GetAllAsync(It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<PermissionEntity>());
        _permRepo.Setup(r => r.AddAsync(It.IsAny<PermissionEntity>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity e, CancellationToken _) => e);
        _permRepo.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((Guid id, CancellationToken _) => new PermissionEntity { Id = id });
        _permRepo.Setup(r => r.UpdateAsync(It.IsAny<PermissionEntity>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((PermissionEntity e, CancellationToken _) => e);

        var importList = new List<PermissionImportDto>
        {
            new() { PermCode = "parent:code", PermName = "父权限" },
            new() { PermCode = "child:code", PermName = "子权限", ParentCode = "parent:code" }
        };

        var result = await _sut.BatchImportAsync(importList);

        result.Should().Be(2);
        // 第二轮应该更新子权限的 ParentId
        _permRepo.Verify(r => r.UpdateAsync(It.IsAny<PermissionEntity>(), It.IsAny<CancellationToken>()), Times.AtLeastOnce);
    }
}
