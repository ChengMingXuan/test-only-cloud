using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Xunit;
using FluentAssertions;
using JGSY.AGI.User.Entities;

namespace JGSY.AGI.Test.User
{
    /// <summary>
    /// 用户档案实体单元测试
    /// </summary>
    public class UserProfileEntityTests
    {

        [Fact]
        public void UserProfile_Should_Create_Successfully()
        {
            // Arrange
            var tenantId = Guid.NewGuid();
            var userId = Guid.NewGuid();

            // Act
            var profile = new UserProfile
            {
                Id = Guid.NewGuid(),
                TenantId = tenantId,
                UserId = userId,
                Address = "北京市朝阳区xxx街道",
                City = "北京",
                Province = "北京",
                Country = "中国",
                PostalCode = "100000",
                Bio = "测试用户简介",
                Company = "测试公司",
                Department = "研发部",
                Tags = "tag1,tag2",
                Preferences = "{\"theme\":\"dark\",\"language\":\"zh-CN\"}",
                CreateBy = userId,
                UpdateBy = userId
            };

            // Assert
            profile.Should().NotBeNull();
            profile.UserId.Should().Be(userId);
            profile.Address.Should().Be("北京市朝阳区xxx街道");
            profile.City.Should().Be("北京");
            profile.Company.Should().Be("测试公司");
        }

        [Fact]
        public void UserProfile_Should_Support_Nullable_Fields()
        {
            // Arrange
            var tenantId = Guid.NewGuid();
            var userId = Guid.NewGuid();

            // Act
            var profile = new UserProfile
            {
                Id = Guid.NewGuid(),
                TenantId = tenantId,
                UserId = userId,
                CreateBy = userId,
                UpdateBy = userId
                // 所有可空字段保持为null
            };

            // Assert
            profile.Should().NotBeNull();
            profile.Address.Should().BeNull();
            profile.City.Should().BeNull();
            profile.Bio.Should().BeNull();
        }

        [Fact]
        public void UserLoginHistory_Should_Track_Login_Attempts()
        {
            // Arrange
            var tenantId = Guid.NewGuid();
            var userId = Guid.NewGuid();

            // Act
            var loginHistory = new UserLoginHistory
            {
                Id = Guid.NewGuid(),
                TenantId = tenantId,
                UserId = userId,
                LoginTime = DateTime.UtcNow,
                IpAddress = "192.168.1.100",
                UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                Device = "Desktop",
                Result = (int)LoginResult.Success,
                FailReason = null,
                Location = "北京市朝阳区",
                CreateBy = userId,
                UpdateBy = userId
            };

            // Assert
            loginHistory.Should().NotBeNull();
            loginHistory.UserId.Should().Be(userId);
            loginHistory.IpAddress.Should().Be("192.168.1.100");
            loginHistory.Result.Should().Be((int)LoginResult.Success);
        }

        [Fact]
        public void UserLoginHistory_Should_Track_Failed_Login()
        {
            // Arrange
            var tenantId = Guid.NewGuid();
            var userId = Guid.NewGuid();

            // Act
            var loginHistory = new UserLoginHistory
            {
                Id = Guid.NewGuid(),
                TenantId = tenantId,
                UserId = userId,
                LoginTime = DateTime.UtcNow,
                IpAddress = "192.168.1.101",
                Result = (int)LoginResult.InvalidCredentials,
                FailReason = "密码错误",
                CreateBy = userId,
                UpdateBy = userId
            };

            // Assert
            loginHistory.Should().NotBeNull();
            loginHistory.Result.Should().Be((int)LoginResult.InvalidCredentials);
            loginHistory.FailReason.Should().Be("密码错误");
        }

        [Fact]
        public async Task UserProfile_Should_Query_By_UserId()
        {
            // Arrange - 模拟用户档案列表（Dapper.AOT 返回结果）
            var targetUserId = Guid.NewGuid();
            var profiles = new List<UserProfile>
            {
                new() { Id = Guid.NewGuid(), UserId = targetUserId, City = "测试城市A", TenantId = Guid.NewGuid() },
                new() { Id = Guid.NewGuid(), UserId = Guid.NewGuid(), City = "测试城市B", TenantId = Guid.NewGuid() },
                new() { Id = Guid.NewGuid(), UserId = Guid.NewGuid(), City = "测试城市C", TenantId = Guid.NewGuid() }
            };

            // Act - 模拟 WHERE user_id = @UserId 查询
            var result = profiles.FirstOrDefault(p => p.UserId == targetUserId);

            // Assert
            await Task.CompletedTask;
            result.Should().NotBeNull();
            result!.City.Should().Be("测试城市A");
            result.UserId.Should().Be(targetUserId);
        }
    }
}
