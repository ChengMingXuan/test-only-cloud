using System;
using Xunit;
using FluentAssertions;
using JGSY.AGI.Permission.Entities;

namespace JGSY.AGI.Test.Permission
{
    /// <summary>
    /// 权限实体单元测试（纯实体属性测试，无 DbContext 依赖）
    /// </summary>
    public class PermissionEntityTests
    {
        #region Permission Entity Tests

        [Fact]
        public void Permission_Should_Create_Successfully()
        {
            var permission = new PermissionEntity
            {
                Id = Guid.NewGuid(),
                TenantId = Guid.NewGuid(),
                PermName = "用户管理",
                PermCode = "user:manage",
                PermType = PermissionType.Menu,
                ResourcePath = "/system/user",
                Icon = "UserOutlined",
                SortOrder = 1,
                IsEnabled = true,
                Remark = "用户管理菜单权限",
                CreateBy = Guid.NewGuid(),
                UpdateBy = Guid.NewGuid()
            };

            permission.PermName.Should().Be("用户管理");
            permission.PermCode.Should().Be("user:manage");
            permission.PermType.Should().Be(PermissionType.Menu);
            permission.IsEnabled.Should().BeTrue();
        }

        [Fact]
        public void Permission_Should_Support_All_Types()
        {
            var menuPerm = new PermissionEntity { Id = Guid.NewGuid(), PermCode = "system:settings", PermType = PermissionType.Menu };
            var buttonPerm = new PermissionEntity { Id = Guid.NewGuid(), PermCode = "user:create", PermType = PermissionType.Button };
            var apiPerm = new PermissionEntity { Id = Guid.NewGuid(), PermCode = "api:user:list", PermType = PermissionType.Api, HttpMethod = "GET" };
            var dataPerm = new PermissionEntity { Id = Guid.NewGuid(), PermCode = "data:department", PermType = PermissionType.Data };

            menuPerm.PermType.Should().Be(PermissionType.Menu);
            buttonPerm.PermType.Should().Be(PermissionType.Button);
            apiPerm.PermType.Should().Be(PermissionType.Api);
            apiPerm.HttpMethod.Should().Be("GET");
            dataPerm.PermType.Should().Be(PermissionType.Data);
        }

        [Fact]
        public void Permission_Should_Support_Parent_Child_Relationship()
        {
            var parentId = Guid.NewGuid();
            var parentPermission = new PermissionEntity
            {
                Id = parentId,
                PermName = "用户管理",
                PermCode = "user:manage",
                PermType = PermissionType.Menu,
            };

            var childPermission = new PermissionEntity
            {
                Id = Guid.NewGuid(),
                PermName = "用户列表",
                PermCode = "user:list",
                PermType = PermissionType.Menu,
                ParentId = parentId,
            };

            childPermission.ParentId.Should().Be(parentId);
            parentPermission.PermCode.Should().Be("user:manage");
        }

        [Fact]
        public void Permission_Disabled_Should_Be_Persisted()
        {
            var permission = new PermissionEntity
            {
                Id = Guid.NewGuid(),
                PermName = "已禁用功能",
                PermCode = "feature:disabled",
                PermType = PermissionType.Button,
                IsEnabled = false,
            };

            permission.IsEnabled.Should().BeFalse();
        }

        #endregion
    }
}
