using System;
using System.Collections.Generic;
using System.Linq;
using Xunit;
using FluentAssertions;
using JGSY.AGI.Permission.Entities;

namespace JGSY.AGI.Test.Permission
{
    /// <summary>
    /// 角色模板实体单元测试（纯实体属性测试，无 DbContext 依赖）
    /// </summary>
    public class RoleTemplateEntityTests
    {
        [Fact]
        public void RoleTemplate_Should_Create_Successfully()
        {
            var template = new RoleTemplate
            {
                Id = Guid.NewGuid(),
                TenantId = Guid.NewGuid(),
                Name = "运营管理员模板",
                Code = "ops_admin_template",
                Description = "运营管理员角色模板，包含运营相关的全部权限",
                TemplateType = (int)RoleTemplateType.Platform,
                Scope = (int)RoleScope.Tenant,
                Level = 50,
                Permissions = "[\"ops:view\", \"ops:manage\", \"ops:report\"]",
                IsPublic = true,
                IsEnabled = true,
                CreateBy = Guid.NewGuid(),
                UpdateBy = Guid.NewGuid()
            };

            template.Name.Should().Be("运营管理员模板");
            template.Code.Should().Be("ops_admin_template");
            template.TemplateType.Should().Be((int)RoleTemplateType.Platform);
            template.Permissions.Should().Contain("ops:view");
        }

        [Fact]
        public void RoleTemplate_Should_Support_All_Template_Types()
        {
            var templates = new List<RoleTemplate>
            {
                new() { Id = Guid.NewGuid(), Name = "系统模板", Code = "sys", TemplateType = (int)RoleTemplateType.System, Scope = (int)RoleScope.Platform },
                new() { Id = Guid.NewGuid(), Name = "平台模板", Code = "plat", TemplateType = (int)RoleTemplateType.Platform, Scope = (int)RoleScope.Tenant },
                new() { Id = Guid.NewGuid(), Name = "租户模板", Code = "ten", TemplateType = (int)RoleTemplateType.Tenant, Scope = (int)RoleScope.Department },
            };

            templates.Should().HaveCount(3);
            templates.Should().Contain(t => t.TemplateType == (int)RoleTemplateType.System);
            templates.Should().Contain(t => t.TemplateType == (int)RoleTemplateType.Platform);
            templates.Should().Contain(t => t.TemplateType == (int)RoleTemplateType.Tenant);
        }

        [Fact]
        public void RoleTemplate_IsPublic_Should_Control_Visibility()
        {
            var templates = new List<RoleTemplate>
            {
                new() { Id = Guid.NewGuid(), Name = "公开模板", Code = "public_template", IsPublic = true },
                new() { Id = Guid.NewGuid(), Name = "私有模板", Code = "private_template", IsPublic = false },
            };

            var publicResults = templates.Where(t => t.IsPublic).ToList();
            publicResults.Should().HaveCount(1);
            publicResults[0].Name.Should().Be("公开模板");

            var privateResults = templates.Where(t => !t.IsPublic).ToList();
            privateResults.Should().HaveCount(1);
            privateResults[0].Name.Should().Be("私有模板");
        }

        [Fact]
        public void RoleTemplate_Level_Should_Support_Hierarchy()
        {
            var templates = new List<RoleTemplate>
            {
                new() { Id = Guid.NewGuid(), Name = "超级管理员模板", Code = "super_admin", Level = 1 },
                new() { Id = Guid.NewGuid(), Name = "管理员模板", Code = "admin", Level = 10 },
                new() { Id = Guid.NewGuid(), Name = "操作员模板", Code = "operator", Level = 50 },
                new() { Id = Guid.NewGuid(), Name = "普通用户模板", Code = "user", Level = 100 },
            };

            var results = templates.OrderBy(t => t.Level).ToList();
            results.Should().HaveCount(4);
            results[0].Name.Should().Be("超级管理员模板");
            results[1].Name.Should().Be("管理员模板");
            results[2].Name.Should().Be("操作员模板");
            results[3].Name.Should().Be("普通用户模板");
        }

        [Fact]
        public void RoleTemplate_DataPermissionRules_Should_Store_Json()
        {
            var dataRulesJson = @"{
                ""rules"": [
                    {""resource"": ""Order"", ""scope"": ""Department""},
                    {""resource"": ""Customer"", ""scope"": ""Self""}
                ]
            }";

            var template = new RoleTemplate
            {
                Id = Guid.NewGuid(),
                Name = "带数据权限的模板",
                Code = "data_perm_template",
                DataPermissionRules = dataRulesJson,
            };

            template.DataPermissionRules.Should().NotBeNull();
            template.DataPermissionRules.Should().Contain("Order");
            template.DataPermissionRules.Should().Contain("Customer");
        }
    }
}
