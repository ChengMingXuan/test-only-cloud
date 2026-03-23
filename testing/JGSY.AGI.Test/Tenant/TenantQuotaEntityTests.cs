using System;
using Xunit;
using FluentAssertions;
using JGSY.AGI.Tenant.Entities;

namespace JGSY.AGI.Test.Tenant
{
    /// <summary>
    /// 租户配额实体单元测试（纯实体属性测试，无 DbContext 依赖）
    /// </summary>
    public class TenantQuotaEntityTests
    {
        [Fact]
        public void TenantQuota_Should_Create_Successfully()
        {
            var quota = new TenantQuota
            {
                Id = Guid.NewGuid(),
                TenantIdRef = Guid.NewGuid(),
                MaxUserCount = 50,
                CurrentUserCount = 10,
                StorageQuotaMb = 20480,
                UsedStorageMb = 5120,
                DailyApiCallQuota = 50000,
                TodayApiCallCount = 1000,
                MaxDatabaseConnections = 30,
                AllowDataExport = true,
                AllowApiAccess = true
            };

            quota.MaxUserCount.Should().Be(50);
            quota.CurrentUserCount.Should().Be(10);
            quota.StorageQuotaMb.Should().Be(20480);
            quota.UsedStorageMb.Should().Be(5120);
        }

        [Fact]
        public void TenantQuota_DefaultValues_Should_Be_Applied()
        {
            var quota = new TenantQuota
            {
                Id = Guid.NewGuid(),
                TenantIdRef = Guid.NewGuid()
            };

            quota.MaxUserCount.Should().Be(100);
            quota.CurrentUserCount.Should().Be(0);
            quota.StorageQuotaMb.Should().Be(10240);
            quota.DailyApiCallQuota.Should().Be(100000);
            quota.AllowDataExport.Should().BeTrue();
            quota.AllowApiAccess.Should().BeTrue();
        }

        [Fact]
        public void TenantQuota_Usage_Should_Track_Correctly()
        {
            var quota = new TenantQuota
            {
                Id = Guid.NewGuid(),
                TenantIdRef = Guid.NewGuid(),
                MaxUserCount = 100,
                CurrentUserCount = 50,
                StorageQuotaMb = 10240,
                UsedStorageMb = 8000,
                DailyApiCallQuota = 10000,
                TodayApiCallCount = 9500
            };

            var userUsagePercent = (double)quota.CurrentUserCount / quota.MaxUserCount * 100;
            userUsagePercent.Should().Be(50);

            var storageUsagePercent = (double)quota.UsedStorageMb / quota.StorageQuotaMb * 100;
            storageUsagePercent.Should().BeApproximately(78.125, 0.01);

            var apiUsagePercent = (double)quota.TodayApiCallCount / quota.DailyApiCallQuota * 100;
            apiUsagePercent.Should().Be(95);
        }

        [Fact]
        public void TenantQuota_UnlimitedQuota_Should_Be_Zero()
        {
            var unlimitedQuota = new TenantQuota
            {
                Id = Guid.NewGuid(),
                TenantIdRef = Guid.NewGuid(),
                MaxUserCount = 0,
                StorageQuotaMb = 0,
                DailyApiCallQuota = 0
            };

            unlimitedQuota.MaxUserCount.Should().Be(0);
            unlimitedQuota.StorageQuotaMb.Should().Be(0);
            unlimitedQuota.DailyApiCallQuota.Should().Be(0);
        }

        [Fact]
        public void TenantQuota_Permissions_Should_Be_Configurable()
        {
            var restrictedQuota = new TenantQuota
            {
                Id = Guid.NewGuid(),
                TenantIdRef = Guid.NewGuid(),
                AllowDataExport = false,
                AllowApiAccess = false
            };

            restrictedQuota.AllowDataExport.Should().BeFalse();
            restrictedQuota.AllowApiAccess.Should().BeFalse();
        }

        [Fact]
        public void TenantQuota_ApiCallQuotaDaily_Should_Be_Alias()
        {
            var quota = new TenantQuota
            {
                Id = Guid.NewGuid(),
                TenantIdRef = Guid.NewGuid(),
                DailyApiCallQuota = 50000
            };

            quota.ApiCallQuotaDaily.Should().Be(50000);
            quota.DailyApiCallQuota.Should().Be(quota.ApiCallQuotaDaily);
        }
    }
}
