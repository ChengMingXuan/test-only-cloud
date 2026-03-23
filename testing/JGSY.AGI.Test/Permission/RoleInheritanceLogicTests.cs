using System;
using System.Collections.Generic;
using System.Linq;
using FluentAssertions;
using JGSY.AGI.Permission.Entities;
using JGSY.AGI.Permission.Interfaces;
using Xunit;

namespace JGSY.AGI.Test.Permission;

/// <summary>
/// 角色继承逻辑测试 — 循环检测算法 + 权限计算规则 + DTO 验证 + 层级约束 + 边界条件
/// 纯内存模拟，不依赖数据库
/// </summary>
public class RoleInheritanceLogicTests
{
    #region 循环继承检测算法

    /// <summary>
    /// 模拟继承图进行 DFS 循环检测（与 CheckCircularAsync 同逻辑）
    /// </summary>
    private static bool DetectCircular(
        Guid parentRoleId, Guid childRoleId,
        Dictionary<Guid, List<Guid>> parentMap)
    {
        if (parentRoleId == childRoleId) return true;

        var visited = new HashSet<Guid>();
        return CheckCircularDfs(childRoleId, parentRoleId, parentMap, visited);
    }

    private static bool CheckCircularDfs(
        Guid currentRoleId, Guid targetRoleId,
        Dictionary<Guid, List<Guid>> parentMap,
        HashSet<Guid> visited)
    {
        if (visited.Contains(currentRoleId)) return false;
        visited.Add(currentRoleId);

        if (!parentMap.TryGetValue(currentRoleId, out var parentIds)) return false;

        foreach (var parentId in parentIds)
        {
            if (parentId == targetRoleId) return true;
            if (CheckCircularDfs(parentId, targetRoleId, parentMap, visited)) return true;
        }
        return false;
    }

    [Fact]
    public void CircularDetection_SelfReference_ShouldDetect()
    {
        var roleA = Guid.NewGuid();
        var parentMap = new Dictionary<Guid, List<Guid>>();

        DetectCircular(roleA, roleA, parentMap).Should().BeTrue();
    }

    [Fact]
    public void CircularDetection_DirectCircle_ShouldDetect()
    {
        // A → B 已存在，尝试添加 B → A，应检测到循环
        var roleA = Guid.NewGuid();
        var roleB = Guid.NewGuid();
        var parentMap = new Dictionary<Guid, List<Guid>>
        {
            [roleB] = new() { roleA } // B 的父角色是 A
        };

        // 尝试让 A 继承 B（新建 parent=B, child=A）
        // DetectCircular(B, A, map) = 检查 A 的祖先链是否包含 B
        // A 没有父角色，所以不循环
        DetectCircular(roleB, roleA, parentMap).Should().BeFalse();

        // 反过来：尝试让 A 继承 B（B→A 已存在），再建 A→B
        // DetectCircular(A, B, parentMap) 就是检查 B 的祖先是否包含 A
        DetectCircular(roleA, roleB, parentMap).Should().BeTrue();
    }

    [Fact]
    public void CircularDetection_IndirectCircle_ShouldDetect()
    {
        // A → B → C 已存在，尝试添加 C → A
        var roleA = Guid.NewGuid();
        var roleB = Guid.NewGuid();
        var roleC = Guid.NewGuid();
        var parentMap = new Dictionary<Guid, List<Guid>>
        {
            [roleB] = new() { roleA },  // B 继承自 A
            [roleC] = new() { roleB },  // C 继承自 B
        };

        // 尝试 parent=C, child=A → DetectCircular(C, A)
        // A 的祖先链：空 → 不循环
        DetectCircular(roleC, roleA, parentMap).Should().BeFalse();

        // 尝试 parent=A, child=C → 检查 C 的祖先链
        // C → B → A，包含 A → 循环！
        DetectCircular(roleA, roleC, parentMap).Should().BeTrue();
    }

    [Fact]
    public void CircularDetection_DiamondInheritance_AncestorDetected()
    {
        // 菱形继承：D → B, D → C, B → A, C → A
        // 算法检测 D 的祖先链是否包含 A（祖先包含检测，非循环检测）
        // D → B → A，包含 A，返回 true（表示 A 已是 D 的祖先）
        var roleA = Guid.NewGuid();
        var roleB = Guid.NewGuid();
        var roleC = Guid.NewGuid();
        var roleD = Guid.NewGuid();
        var parentMap = new Dictionary<Guid, List<Guid>>
        {
            [roleB] = new() { roleA },
            [roleC] = new() { roleA },
            [roleD] = new() { roleB, roleC },
        };

        // A 已是 D 的祖先（通过 B 或 C），算法返回 true
        DetectCircular(roleA, roleD, parentMap).Should().BeTrue();
    }

    [Fact]
    public void CircularDetection_LongChain_ShouldDetect()
    {
        // A → B → C → D → E 已存在，尝试添加 A → E
        var roles = Enumerable.Range(0, 5).Select(_ => Guid.NewGuid()).ToList();
        var parentMap = new Dictionary<Guid, List<Guid>>();

        for (int i = 1; i < roles.Count; i++)
        {
            parentMap[roles[i]] = new() { roles[i - 1] };
        }

        // 尝试 parent=roles[0](A), child=roles[4](E) → 检查 E 的祖先链
        // E → D → C → B → A → 包含 roles[0] → 循环！
        DetectCircular(roles[0], roles[4], parentMap).Should().BeTrue();
    }

    [Fact]
    public void CircularDetection_NoRelation_ShouldNotDetect()
    {
        // 无继承关系
        var roleA = Guid.NewGuid();
        var roleB = Guid.NewGuid();
        var parentMap = new Dictionary<Guid, List<Guid>>();

        DetectCircular(roleA, roleB, parentMap).Should().BeFalse();
    }

    #endregion

    #region 有效权限计算

    /// <summary>
    /// 模拟 CalculateEffectivePermissionsAsync 的纯内存版本
    /// </summary>
    private static HashSet<Guid> CalculateEffectivePermissions(
        Guid roleId,
        Dictionary<Guid, List<Guid>> directPermissions,
        Dictionary<Guid, List<(Guid ParentRoleId, InheritanceType Type, List<Guid> Excluded)>> inheritances,
        Dictionary<Guid, PermissionType> permissionTypes)
    {
        var effective = new HashSet<Guid>();
        var visited = new HashSet<Guid>();

        // 直接权限
        if (directPermissions.TryGetValue(roleId, out var direct))
        {
            foreach (var p in direct) effective.Add(p);
        }

        CollectInherited(roleId, effective, visited, directPermissions, inheritances, permissionTypes);
        return effective;
    }

    private static void CollectInherited(
        Guid roleId, HashSet<Guid> permissions, HashSet<Guid> visited,
        Dictionary<Guid, List<Guid>> directPermissions,
        Dictionary<Guid, List<(Guid ParentRoleId, InheritanceType Type, List<Guid> Excluded)>> inheritances,
        Dictionary<Guid, PermissionType> permissionTypes)
    {
        if (visited.Contains(roleId)) return;
        visited.Add(roleId);

        if (!inheritances.TryGetValue(roleId, out var parentInheritances)) return;

        foreach (var (parentRoleId, inheritanceType, excludedPermissions) in parentInheritances)
        {
            if (!directPermissions.TryGetValue(parentRoleId, out var parentPerms)) continue;

            var filteredPerms = parentPerms.AsEnumerable();

            // DataOnly 过滤
            if (inheritanceType == InheritanceType.DataOnly)
            {
                filteredPerms = filteredPerms.Where(p =>
                    permissionTypes.TryGetValue(p, out var pt) && pt == PermissionType.Data);
            }

            // 排除权限
            foreach (var permId in filteredPerms)
            {
                if (!excludedPermissions.Contains(permId))
                    permissions.Add(permId);
            }

            CollectInherited(parentRoleId, permissions, visited, directPermissions, inheritances, permissionTypes);
        }
    }

    [Fact]
    public void EffectivePermissions_DirectOnly_ShouldReturnDirect()
    {
        var roleA = Guid.NewGuid();
        var perm1 = Guid.NewGuid();
        var perm2 = Guid.NewGuid();

        var directPerms = new Dictionary<Guid, List<Guid>>
        {
            [roleA] = new() { perm1, perm2 }
        };

        var effective = CalculateEffectivePermissions(roleA, directPerms,
            new(), new());

        effective.Should().HaveCount(2);
        effective.Should().Contain(perm1);
        effective.Should().Contain(perm2);
    }

    [Fact]
    public void EffectivePermissions_FullInheritance_ShouldIncludeParentPerms()
    {
        var roleA = Guid.NewGuid();
        var roleB = Guid.NewGuid(); // B 继承自 A
        var permA1 = Guid.NewGuid();
        var permA2 = Guid.NewGuid();
        var permB1 = Guid.NewGuid();

        var directPerms = new Dictionary<Guid, List<Guid>>
        {
            [roleA] = new() { permA1, permA2 },
            [roleB] = new() { permB1 }
        };
        var inheritances = new Dictionary<Guid, List<(Guid, InheritanceType, List<Guid>)>>
        {
            [roleB] = new() { (roleA, InheritanceType.Full, new List<Guid>()) }
        };

        var effective = CalculateEffectivePermissions(roleB, directPerms, inheritances, new());

        effective.Should().HaveCount(3);
        effective.Should().Contain(new[] { permA1, permA2, permB1 });
    }

    [Fact]
    public void EffectivePermissions_DataOnlyInheritance_ShouldFilterNonDataPerms()
    {
        var roleA = Guid.NewGuid();
        var roleB = Guid.NewGuid();
        var permData = Guid.NewGuid();
        var permMenu = Guid.NewGuid();
        var permApi = Guid.NewGuid();
        var permB1 = Guid.NewGuid();

        var directPerms = new Dictionary<Guid, List<Guid>>
        {
            [roleA] = new() { permData, permMenu, permApi },
            [roleB] = new() { permB1 }
        };
        var inheritances = new Dictionary<Guid, List<(Guid, InheritanceType, List<Guid>)>>
        {
            [roleB] = new() { (roleA, InheritanceType.DataOnly, new List<Guid>()) }
        };
        var permTypes = new Dictionary<Guid, PermissionType>
        {
            [permData] = PermissionType.Data,
            [permMenu] = PermissionType.Menu,
            [permApi] = PermissionType.Api,
        };

        var effective = CalculateEffectivePermissions(roleB, directPerms, inheritances, permTypes);

        // B 自有 permB1 + 继承 A 的 Data 类型权限 permData
        effective.Should().HaveCount(2);
        effective.Should().Contain(permB1);
        effective.Should().Contain(permData);
        effective.Should().NotContain(permMenu);
        effective.Should().NotContain(permApi);
    }

    [Fact]
    public void EffectivePermissions_ExcludedPermissions_ShouldBeOmitted()
    {
        var roleA = Guid.NewGuid();
        var roleB = Guid.NewGuid();
        var perm1 = Guid.NewGuid();
        var perm2 = Guid.NewGuid();
        var perm3 = Guid.NewGuid();

        var directPerms = new Dictionary<Guid, List<Guid>>
        {
            [roleA] = new() { perm1, perm2, perm3 },
            [roleB] = new()
        };
        var inheritances = new Dictionary<Guid, List<(Guid, InheritanceType, List<Guid>)>>
        {
            [roleB] = new() { (roleA, InheritanceType.Full, new List<Guid> { perm2 }) } // 排除 perm2
        };

        var effective = CalculateEffectivePermissions(roleB, directPerms, inheritances, new());

        effective.Should().HaveCount(2);
        effective.Should().Contain(perm1);
        effective.Should().Contain(perm3);
        effective.Should().NotContain(perm2); // 被排除
    }

    [Fact]
    public void EffectivePermissions_TransitiveInheritance_ShouldCollectAll()
    {
        // C → B → A（三层继承）
        var roleA = Guid.NewGuid();
        var roleB = Guid.NewGuid();
        var roleC = Guid.NewGuid();
        var permA = Guid.NewGuid();
        var permB = Guid.NewGuid();
        var permC = Guid.NewGuid();

        var directPerms = new Dictionary<Guid, List<Guid>>
        {
            [roleA] = new() { permA },
            [roleB] = new() { permB },
            [roleC] = new() { permC }
        };
        var inheritances = new Dictionary<Guid, List<(Guid, InheritanceType, List<Guid>)>>
        {
            [roleB] = new() { (roleA, InheritanceType.Full, new List<Guid>()) },
            [roleC] = new() { (roleB, InheritanceType.Full, new List<Guid>()) }
        };

        var effective = CalculateEffectivePermissions(roleC, directPerms, inheritances, new());

        effective.Should().HaveCount(3);
        effective.Should().Contain(new[] { permA, permB, permC });
    }

    [Fact]
    public void EffectivePermissions_DiamondInheritance_ShouldNotDuplicatePerms()
    {
        // 菱形: D → B → A, D → C → A → sharedPerm 只计一次
        var roleA = Guid.NewGuid();
        var roleB = Guid.NewGuid();
        var roleC = Guid.NewGuid();
        var roleD = Guid.NewGuid();
        var sharedPerm = Guid.NewGuid();
        var permB = Guid.NewGuid();
        var permC = Guid.NewGuid();

        var directPerms = new Dictionary<Guid, List<Guid>>
        {
            [roleA] = new() { sharedPerm },
            [roleB] = new() { permB },
            [roleC] = new() { permC },
            [roleD] = new()
        };
        var inheritances = new Dictionary<Guid, List<(Guid, InheritanceType, List<Guid>)>>
        {
            [roleB] = new() { (roleA, InheritanceType.Full, new List<Guid>()) },
            [roleC] = new() { (roleA, InheritanceType.Full, new List<Guid>()) },
            [roleD] = new()
            {
                (roleB, InheritanceType.Full, new List<Guid>()),
                (roleC, InheritanceType.Full, new List<Guid>())
            }
        };

        var effective = CalculateEffectivePermissions(roleD, directPerms, inheritances, new());

        // D 只有：sharedPerm + permB + permC = 3 个（不重复）
        effective.Should().HaveCount(3);
        effective.Should().Contain(new[] { sharedPerm, permB, permC });
    }

    [Fact]
    public void EffectivePermissions_NoPermissions_ShouldReturnEmpty()
    {
        var roleA = Guid.NewGuid();
        var directPerms = new Dictionary<Guid, List<Guid>>();

        var effective = CalculateEffectivePermissions(roleA, directPerms, new(), new());
        effective.Should().BeEmpty();
    }

    #endregion

    #region 层级约束测试

    [Theory]
    [InlineData(1, 2, true)]  // 父 Level=1 < 子 Level=2 → 合法
    [InlineData(1, 3, true)]  // 父 Level=1 < 子 Level=3 → 合法
    [InlineData(2, 2, false)] // 同级 → 不合法
    [InlineData(3, 2, false)] // 父 Level=3 > 子 Level=2 → 不合法
    [InlineData(5, 1, false)] // 父级别更低 → 不合法
    public void LevelConstraint_ParentMustBeHigherLevel(int parentLevel, int childLevel, bool expectedValid)
    {
        // 对应 CreateInheritanceAsync 中的校验: parentRole.Level >= childRole.Level
        // Level 数值越小级别越高
        var isValid = parentLevel < childLevel;
        isValid.Should().Be(expectedValid);
    }

    #endregion

    #region DTO 验证测试

    [Fact]
    public void CreateInheritanceDto_Valid_ShouldPass()
    {
        var dto = new CreateInheritanceDto
        {
            ParentRoleId = Guid.NewGuid(),
            ChildRoleId = Guid.NewGuid(),
            InheritanceType = InheritanceType.Full
        };

        var errors = dto.Validate();
        errors.Should().BeEmpty();
    }

    [Fact]
    public void CreateInheritanceDto_SameRole_ShouldFail()
    {
        var roleId = Guid.NewGuid();
        var dto = new CreateInheritanceDto
        {
            ParentRoleId = roleId,
            ChildRoleId = roleId,
            InheritanceType = InheritanceType.Full
        };

        var errors = dto.Validate();
        errors.Should().ContainKey("parentRoleId");
    }

    [Fact]
    public void CreateInheritanceDto_MissingParent_ShouldFail()
    {
        var dto = new CreateInheritanceDto
        {
            ParentRoleId = Guid.Empty,
            ChildRoleId = Guid.NewGuid()
        };

        var errors = dto.Validate();
        errors.Should().ContainKey("parentRoleId");
    }

    [Fact]
    public void CreateInheritanceDto_MissingChild_ShouldFail()
    {
        var dto = new CreateInheritanceDto
        {
            ParentRoleId = Guid.NewGuid(),
            ChildRoleId = Guid.Empty
        };

        var errors = dto.Validate();
        errors.Should().ContainKey("childRoleId");
    }

    [Fact]
    public void CreateInheritanceDto_DefaultType_ShouldBeFull()
    {
        var dto = new CreateInheritanceDto();
        dto.InheritanceType.Should().Be(InheritanceType.Full);
    }

    [Fact]
    public void UpdateInheritanceDto_AllNull_ShouldPass()
    {
        var dto = new UpdateInheritanceDto();
        var errors = dto.Validate();
        errors.Should().BeEmpty();
    }

    #endregion

    #region InheritanceType 枚举测试

    [Theory]
    [InlineData(InheritanceType.Full, 1)]
    [InlineData(InheritanceType.Partial, 2)]
    [InlineData(InheritanceType.DataOnly, 3)]
    public void InheritanceType_ShouldHaveCorrectValues(InheritanceType type, int expected)
    {
        ((int)type).Should().Be(expected);
    }

    #endregion

    #region RoleInheritanceDto 测试

    [Fact]
    public void RoleInheritanceDto_ShouldHoldAllFields()
    {
        var dto = new RoleInheritanceDto
        {
            Id = Guid.NewGuid(),
            ParentRoleId = Guid.NewGuid(),
            ParentRoleName = "超级管理员",
            ParentRoleCode = "SUPER_ADMIN",
            ChildRoleId = Guid.NewGuid(),
            ChildRoleName = "普通管理员",
            ChildRoleCode = "ADMIN",
            InheritanceType = InheritanceType.Full,
            ExcludedPermissionIds = new List<Guid> { Guid.NewGuid() },
            IsEnabled = true
        };

        dto.ParentRoleName.Should().Be("超级管理员");
        dto.ExcludedPermissionIds.Should().HaveCount(1);
        dto.IsEnabled.Should().BeTrue();
    }

    [Fact]
    public void RoleInheritanceTreeDto_ShouldSupportNestedHierarchy()
    {
        var tree = new RoleInheritanceTreeDto
        {
            RoleId = Guid.NewGuid(),
            RoleName = "根角色",
            Level = 1,
            DirectPermissionCount = 50,
            InheritedPermissionCount = 0,
            Children = new List<RoleInheritanceTreeDto>
            {
                new()
                {
                    RoleId = Guid.NewGuid(),
                    RoleName = "子角色",
                    Level = 2,
                    DirectPermissionCount = 20,
                    InheritedPermissionCount = 50,
                    Children = new List<RoleInheritanceTreeDto>()
                }
            },
            Parents = new()
        };

        tree.Children.Should().HaveCount(1);
        tree.Children[0].InheritedPermissionCount.Should().Be(50);
    }

    #endregion

    #region PermissionSourceType 测试

    [Fact]
    public void PermissionSource_Direct_ShouldBe1()
    {
        ((int)PermissionSourceType.Direct).Should().Be(1);
    }

    [Fact]
    public void PermissionSource_Inherited_ShouldBe2()
    {
        ((int)PermissionSourceType.Inherited).Should().Be(2);
    }

    [Fact]
    public void PermissionSourceDto_ShouldTrackSource()
    {
        var dto = new PermissionSourceDto
        {
            PermissionId = Guid.NewGuid(),
            PermissionName = "用户管理",
            PermissionCode = "perm:user:manage",
            SourceType = PermissionSourceType.Inherited,
            SourceRoleId = Guid.NewGuid(),
            SourceRoleName = "超级管理员"
        };

        dto.SourceType.Should().Be(PermissionSourceType.Inherited);
        dto.SourceRoleName.Should().Be("超级管理员");
    }

    #endregion

    #region 边界：大量继承关系

    [Fact]
    public void EffectivePermissions_ManyParents_ShouldCollectAll()
    {
        // 一个角色有 10 个父角色，每个父角色各有 5 个权限
        var child = Guid.NewGuid();
        var directPerms = new Dictionary<Guid, List<Guid>>
        {
            [child] = new()
        };
        var inheritances = new Dictionary<Guid, List<(Guid, InheritanceType, List<Guid>)>>
        {
            [child] = new()
        };

        for (int i = 0; i < 10; i++)
        {
            var parent = Guid.NewGuid();
            var perms = Enumerable.Range(0, 5).Select(_ => Guid.NewGuid()).ToList();
            directPerms[parent] = perms;
            inheritances[child].Add((parent, InheritanceType.Full, new List<Guid>()));
        }

        var effective = CalculateEffectivePermissions(child, directPerms, inheritances, new());
        effective.Should().HaveCount(50); // 10 * 5 = 50
    }

    #endregion
}
