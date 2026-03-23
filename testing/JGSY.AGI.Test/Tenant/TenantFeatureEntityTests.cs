using System;
using System.Collections.Generic;
using System.Linq;
using Xunit;
using FluentAssertions;
using JGSY.AGI.Tenant.Entities;

namespace JGSY.AGI.Test.Tenant
{
    /// <summary>
    /// 租户功能特性实体单元测试（纯实体属性测试，无 DbContext 依赖）
    /// </summary>
    public class TenantFeatureEntityTests
    {
        [Fact]
        public void TenantFeature_Should_Create_Successfully()
        {
            var feature = new TenantFeature
            {
                Id = Guid.NewGuid(),
                TenantId = Guid.NewGuid(),
                FeatureCode = "ADVANCED_ANALYTICS",
                IsEnabled = true,
                ExpireTime = DateTime.UtcNow.AddYears(1),
                Config = "{\"maxReports\":100,\"customDashboards\":true}",
                CreateBy = Guid.NewGuid(),
                UpdateBy = Guid.NewGuid()
            };

            feature.FeatureCode.Should().Be("ADVANCED_ANALYTICS");
            feature.IsEnabled.Should().BeTrue();
            feature.Config.Should().Contain("maxReports");
        }

        [Fact]
        public void TenantFeature_Should_Support_Disabled_State()
        {
            var feature = new TenantFeature
            {
                Id = Guid.NewGuid(),
                TenantId = Guid.NewGuid(),
                FeatureCode = "PREMIUM_SUPPORT",
                IsEnabled = false,
                CreateBy = Guid.NewGuid(),
                UpdateBy = Guid.NewGuid()
            };

            feature.IsEnabled.Should().BeFalse();
        }

        [Fact]
        public void TenantSetting_Should_Create_Successfully()
        {
            var setting = new TenantSetting
            {
                Id = Guid.NewGuid(),
                TenantId = Guid.NewGuid(),
                SettingKey = "notification.email.enabled",
                SettingValue = "true",
                Category = "Notification",
                Description = "是否启用邮件通知",
                IsEncrypted = false,
                CreateBy = Guid.NewGuid(),
                UpdateBy = Guid.NewGuid()
            };

            setting.SettingKey.Should().Be("notification.email.enabled");
            setting.SettingValue.Should().Be("true");
            setting.Category.Should().Be("Notification");
        }

        [Fact]
        public void TenantSetting_Should_Support_Encrypted_Values()
        {
            var setting = new TenantSetting
            {
                Id = Guid.NewGuid(),
                TenantId = Guid.NewGuid(),
                SettingKey = "payment.api_secret",
                SettingValue = "encrypted_value_xxxxx",
                Category = "Payment",
                Description = "支付API密钥",
                IsEncrypted = true,
                CreateBy = Guid.NewGuid(),
                UpdateBy = Guid.NewGuid()
            };

            setting.IsEncrypted.Should().BeTrue();
        }

        [Fact]
        public void TenantUsageStats_Should_Track_Daily_Usage()
        {
            var stats = new TenantUsageStats
            {
                Id = Guid.NewGuid(),
                TenantId = Guid.NewGuid(),
                StatDate = DateTime.UtcNow.Date,
                UserCount = 150,
                StationCount = 20,
                DeviceCount = 100,
                StorageUsed = 1024 * 1024 * 500,
                ApiCalls = 25000,
                Revenue = 15000.00m,
                CreateBy = Guid.NewGuid(),
                UpdateBy = Guid.NewGuid()
            };

            stats.UserCount.Should().Be(150);
            stats.ApiCalls.Should().Be(25000);
            stats.StationCount.Should().Be(20);
            stats.Revenue.Should().Be(15000.00m);
        }

        [Fact]
        public void TenantUsageStats_Should_Query_By_DateRange()
        {
            var tenantId = Guid.NewGuid();
            var userId = Guid.NewGuid();
            var statsList = new List<TenantUsageStats>();

            for (int i = 0; i < 7; i++)
            {
                statsList.Add(new TenantUsageStats
                {
                    Id = Guid.NewGuid(),
                    TenantId = tenantId,
                    StatDate = DateTime.UtcNow.Date.AddDays(-i),
                    UserCount = 100 + i * 10,
                    ApiCalls = 10000 + i * 1000,
                    CreateBy = userId,
                    UpdateBy = userId
                });
            }

            var startDate = DateTime.UtcNow.Date.AddDays(-3);
            var endDate = DateTime.UtcNow.Date;
            var results = statsList
                .Where(s => s.TenantId == tenantId && s.StatDate >= startDate && s.StatDate <= endDate)
                .ToList();

            results.Should().HaveCount(4);
        }

        [Fact]
        public void TenantFeature_Should_Query_Enabled_Features()
        {
            var tenantId = Guid.NewGuid();
            var userId = Guid.NewGuid();

            var features = new List<TenantFeature>
            {
                new() { Id = Guid.NewGuid(), TenantId = tenantId, FeatureCode = "FEATURE_A", IsEnabled = true, CreateBy = userId, UpdateBy = userId },
                new() { Id = Guid.NewGuid(), TenantId = tenantId, FeatureCode = "FEATURE_B", IsEnabled = false, CreateBy = userId, UpdateBy = userId },
                new() { Id = Guid.NewGuid(), TenantId = tenantId, FeatureCode = "FEATURE_C", IsEnabled = true, CreateBy = userId, UpdateBy = userId },
            };

            var enabledFeatures = features
                .Where(f => f.TenantId == tenantId && f.IsEnabled)
                .ToList();

            enabledFeatures.Should().HaveCount(2);
            enabledFeatures.Should().Contain(f => f.FeatureCode == "FEATURE_A");
            enabledFeatures.Should().Contain(f => f.FeatureCode == "FEATURE_C");
        }
    }
}
