using System;
using System.Collections.Generic;
using System.Linq;
using Xunit;
using FluentAssertions;
using JGSY.AGI.Permission.Entities;

namespace JGSY.AGI.Test.Permission
{
    /// <summary>
    /// 角色实体单元测试（纯实体属性测试，无 DbContext 依赖）
    /// </summary>
    public class RoleEntityTests
    {
        #region Role Entity Tests

        [Fact]
        public void Role_Should_Create_Successfully()
        {
            var role = new Role
            {
                Id = Guid.NewGuid(),
                TenantId = Guid.NewGuid(),
                RoleName = "系统管理员",
                RoleCode = "SYSTEM_ADMIN",
                Status = (int)RoleStatus.Enabled,
                Scope = (int)RoleScope.Platform,
                Level = 1,
                IsSystem = true,
                Remark = "系统内置管理员角色",
                CreateBy = Guid.NewGuid(),
                UpdateBy = Guid.NewGuid()
            };

            role.RoleName.Should().Be("系统管理员");
            role.RoleCode.Should().Be("SYSTEM_ADMIN");
            role.Status.Should().Be((int)RoleStatus.Enabled);
            role.IsSystem.Should().BeTrue();
        }

        [Fact]
        public void Role_Should_Support_All_Scopes()
        {
            var deptId = Guid.NewGuid();

            var platformRole = new Role
            {
                Id = Guid.NewGuid(),
                RoleName = "平台管理员",
                RoleCode = "PLATFORM_ADMIN",
                Scope = (int)RoleScope.Platform,
            };

            var tenantRole = new Role
            {
                Id = Guid.NewGuid(),
                RoleName = "租户管理员",
                RoleCode = "TENANT_ADMIN",
                Scope = (int)RoleScope.Tenant,
            };

            var deptRole = new Role
            {
                Id = Guid.NewGuid(),
                RoleName = "部门经理",
                RoleCode = "DEPT_MANAGER",
                Scope = (int)RoleScope.Department,
                DepartmentId = deptId,
            };

            platformRole.Scope.Should().Be((int)RoleScope.Platform);
            tenantRole.Scope.Should().Be((int)RoleScope.Tenant);
            deptRole.Scope.Should().Be((int)RoleScope.Department);
            deptRole.DepartmentId.Should().Be(deptId);
        }

        [Fact]
        public void Role_Should_Support_Status_Toggle()
        {
            var role = new Role
            {
                Id = Guid.NewGuid(),
                RoleName = "测试角色",
                RoleCode = "TEST_ROLE",
                Status = (int)RoleStatus.Enabled,
            };

            role.Status.Should().Be((int)RoleStatus.Enabled);

            role.Status = (int)RoleStatus.Disabled;
            role.Status.Should().Be((int)RoleStatus.Disabled);
        }

        [Fact]
        public void Role_Level_Should_Determine_Hierarchy()
        {
            var roles = new List<Role>
            {
                new() { Id = Guid.NewGuid(), RoleName = "超级管理员", RoleCode = "SUPER_ADMIN", Level = 1 },
                new() { Id = Guid.NewGuid(), RoleName = "管理员", RoleCode = "ADMIN", Level = 10 },
                new() { Id = Guid.NewGuid(), RoleName = "普通员工", RoleCode = "EMPLOYEE", Level = 100 },
            };

            var sorted = roles.OrderBy(r => r.Level).ToList();
            sorted.Should().HaveCount(3);
            sorted[0].RoleCode.Should().Be("SUPER_ADMIN");
            sorted[1].RoleCode.Should().Be("ADMIN");
            sorted[2].RoleCode.Should().Be("EMPLOYEE");
        }

        #endregion

        #region RolePermission Tests

        [Fact]
        public void RolePermission_Should_Associate_Role_With_Permission()
        {
            var roleId = Guid.NewGuid();
            var permId = Guid.NewGuid();

            var rolePermission = new RolePermission
            {
                Id = Guid.NewGuid(),
                TenantId = Guid.NewGuid(),
                RoleId = roleId,
                PermId = permId,
                CreateBy = Guid.NewGuid(),
                UpdateBy = Guid.NewGuid()
            };

            rolePermission.RoleId.Should().Be(roleId);
            rolePermission.PermId.Should().Be(permId);
        }

        #endregion

        #region UserRole Tests

        [Fact]
        public void UserRole_Should_Associate_User_With_Role()
        {
            var roleId = Guid.NewGuid();
            var targetUserId = Guid.NewGuid();

            var userRole = new UserRole
            {
                Id = Guid.NewGuid(),
                TenantId = Guid.NewGuid(),
                UserId = targetUserId,
                RoleId = roleId,
                CreateBy = Guid.NewGuid(),
                UpdateBy = Guid.NewGuid()
            };

            userRole.UserId.Should().Be(targetUserId);
            userRole.RoleId.Should().Be(roleId);
        }

        [Fact]
        public void User_Should_Have_Multiple_Roles()
        {
            var targetUserId = Guid.NewGuid();
            var adminRoleId = Guid.NewGuid();
            var editorRoleId = Guid.NewGuid();

            var userRoles = new List<UserRole>
            {
                new() { Id = Guid.NewGuid(), UserId = targetUserId, RoleId = adminRoleId },
                new() { Id = Guid.NewGuid(), UserId = targetUserId, RoleId = editorRoleId },
            };

            var result = userRoles.Where(ur => ur.UserId == targetUserId).ToList();
            result.Should().HaveCount(2);
            result.Select(ur => ur.RoleId).Should().Contain(adminRoleId);
            result.Select(ur => ur.RoleId).Should().Contain(editorRoleId);
        }

        #endregion
    }
}
