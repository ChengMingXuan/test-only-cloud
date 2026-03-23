using System;
using System.Collections.Generic;
using System.Linq;
using Xunit;
using FluentAssertions;
using global::JGSY.AGI.Tenant.Entities;

namespace JGSY.AGI.Test.Tenant
{
    /// <summary>
    /// 租户实体单元测试（纯实体属性测试，无 DbContext 依赖）
    /// </summary>
    public class TenantEntityTests
    {
        [Fact]
        public void Tenant_Should_Create_Successfully()
        {
            var tenant = new global::JGSY.AGI.Tenant.Entities.Tenant
            {
                Id = Guid.NewGuid(),
                TenantName = "测试租户公司",
                TenantDomain = "test.example.com",
                TenantCode = "test_tenant_001",
                Status = (int)TenantStatus.Active,
                PackageType = "Enterprise",
                ContactPerson = "张三",
                ContactPhone = "13800138000",
                ContactEmail = "zhangsan@example.com",
                IsolationMode = (int)IsolationMode.Logical,
                ExpireTime = DateTime.UtcNow.AddYears(1)
            };

            tenant.TenantName.Should().Be("测试租户公司");
            tenant.TenantDomain.Should().Be("test.example.com");
            tenant.TenantCode.Should().Be("test_tenant_001");
            tenant.PackageType.Should().Be("Enterprise");
            tenant.Status.Should().Be((int)TenantStatus.Active);
            tenant.ContactPerson.Should().Be("张三");
            tenant.IsolationMode.Should().Be((int)IsolationMode.Logical);
        }

        [Fact]
        public void Tenant_Should_Support_All_Status_Values()
        {
            var tenants = new List<global::JGSY.AGI.Tenant.Entities.Tenant>
            {
                new() { Id = Guid.NewGuid(), TenantName = "未激活", TenantCode = "t1", Status = (int)TenantStatus.Inactive },
                new() { Id = Guid.NewGuid(), TenantName = "活跃", TenantCode = "t2", Status = (int)TenantStatus.Active },
                new() { Id = Guid.NewGuid(), TenantName = "停用", TenantCode = "t3", Status = (int)TenantStatus.Disabled },
                new() { Id = Guid.NewGuid(), TenantName = "过期", TenantCode = "t4", Status = (int)TenantStatus.Expired },
            };

            tenants.Should().HaveCount(4);
            tenants.Should().Contain(t => t.Status == (int)TenantStatus.Inactive);
            tenants.Should().Contain(t => t.Status == (int)TenantStatus.Active);
            tenants.Should().Contain(t => t.Status == (int)TenantStatus.Disabled);
            tenants.Should().Contain(t => t.Status == (int)TenantStatus.Expired);
        }

        [Fact]
        public void Tenant_Should_Support_All_Isolation_Modes()
        {
            var logical = new global::JGSY.AGI.Tenant.Entities.Tenant
            {
                Id = Guid.NewGuid(),
                TenantName = "逻辑隔离租户",
                TenantCode = "logical_001",
                IsolationMode = (int)IsolationMode.Logical
            };

            var schema = new global::JGSY.AGI.Tenant.Entities.Tenant
            {
                Id = Guid.NewGuid(),
                TenantName = "Schema隔离租户",
                TenantCode = "schema_001",
                IsolationMode = (int)IsolationMode.Schema,
                DataSourceConfig = "{\"SchemaName\": \"tenant_schema_001\"}"
            };

            var database = new global::JGSY.AGI.Tenant.Entities.Tenant
            {
                Id = Guid.NewGuid(),
                TenantName = "独立库隔离租户",
                TenantCode = "database_001",
                IsolationMode = (int)IsolationMode.IndependentDatabase,
                DataSourceConfig = "{\"ConnectionString\": \"Host=localhost;Database=tenant_db_001\"}"
            };

            logical.IsolationMode.Should().Be((int)IsolationMode.Logical);
            schema.IsolationMode.Should().Be((int)IsolationMode.Schema);
            schema.DataSourceConfig.Should().Contain("SchemaName");
            database.IsolationMode.Should().Be((int)IsolationMode.IndependentDatabase);
            database.DataSourceConfig.Should().Contain("ConnectionString");
        }

        [Fact]
        public void Tenant_ExpireTime_Should_Be_Nullable()
        {
            var permanentTenant = new global::JGSY.AGI.Tenant.Entities.Tenant
            {
                Id = Guid.NewGuid(),
                TenantName = "永久租户",
                TenantCode = "permanent_001",
                ExpireTime = null
            };

            var temporaryTenant = new global::JGSY.AGI.Tenant.Entities.Tenant
            {
                Id = Guid.NewGuid(),
                TenantName = "临时租户",
                TenantCode = "temporary_001",
                ExpireTime = DateTime.UtcNow.AddMonths(1)
            };

            permanentTenant.ExpireTime.Should().BeNull();
            temporaryTenant.ExpireTime.Should().NotBeNull();
            temporaryTenant.ExpireTime.Should().BeAfter(DateTime.UtcNow);
        }

        [Fact]
        public void Tenant_Should_Support_Active_Filter()
        {
            var tenants = new List<global::JGSY.AGI.Tenant.Entities.Tenant>
            {
                new() { Id = Guid.NewGuid(), TenantName = "活跃1", TenantCode = "a1", Status = (int)TenantStatus.Active },
                new() { Id = Guid.NewGuid(), TenantName = "活跃2", TenantCode = "a2", Status = (int)TenantStatus.Active },
                new() { Id = Guid.NewGuid(), TenantName = "停用", TenantCode = "d1", Status = (int)TenantStatus.Disabled },
            };

            var activeResults = tenants.Where(t => t.Status == (int)TenantStatus.Active).ToList();
            activeResults.Should().HaveCount(2);
            activeResults.Should().OnlyContain(t => t.Status == (int)TenantStatus.Active);
        }
    }
}
