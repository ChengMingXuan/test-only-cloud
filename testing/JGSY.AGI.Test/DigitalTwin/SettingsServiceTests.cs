using System.Text.Json;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;
using JGSY.AGI.Common.Core.Interfaces;
using JGSY.AGI.DigitalTwin.Data.Repositories;
using JGSY.AGI.DigitalTwin.Models;
using JGSY.AGI.DigitalTwin.Services;

namespace JGSY.AGI.Test.DigitalTwin;

/// <summary>
/// 系统设置服务单元测试（CRUD + JSON 校验 + 租户绑定）
/// </summary>
public class SettingsServiceTests
{
    private readonly Mock<ISystemConfigRepository> _configRepo;
    private readonly Mock<ITenantContext> _tenantContext;
    private readonly SettingsService _service;

    private static readonly Guid TenantId = Guid.NewGuid();

    public SettingsServiceTests()
    {
        _configRepo = new Mock<ISystemConfigRepository>();
        _tenantContext = new Mock<ITenantContext>();
        _tenantContext.Setup(t => t.TenantId).Returns(TenantId);

        _service = new SettingsService(
            _configRepo.Object,
            _tenantContext.Object,
            NullLogger<SettingsService>.Instance);
    }

    #region GetAllAsync / GetByGroupAsync / GetByKeyAsync

    [Fact]
    public async Task GetAll_DelegatesToRepo()
    {
        var configs = new List<SystemConfig>
        {
            new() { Id = Guid.NewGuid(), ConfigKey = "key1", ConfigGroup = "general" },
            new() { Id = Guid.NewGuid(), ConfigKey = "key2", ConfigGroup = "3d_engine" }
        };
        _configRepo.Setup(r => r.GetAllAsync()).ReturnsAsync(configs);

        var result = await _service.GetAllAsync();
        result.Should().HaveCount(2);
    }

    [Fact]
    public async Task GetByGroup_PassesGroupToRepo()
    {
        _configRepo.Setup(r => r.GetByGroupAsync("data_sync")).ReturnsAsync(new List<SystemConfig>());
        await _service.GetByGroupAsync("data_sync");
        _configRepo.Verify(r => r.GetByGroupAsync("data_sync"), Times.Once);
    }

    [Fact]
    public async Task GetByKey_Found_ReturnsConfig()
    {
        var config = new SystemConfig { ConfigKey = "refresh_interval", ConfigValue = "30" };
        _configRepo.Setup(r => r.GetByKeyAsync("refresh_interval")).ReturnsAsync(config);

        var result = await _service.GetByKeyAsync("refresh_interval");
        result.Should().NotBeNull();
        result!.ConfigKey.Should().Be("refresh_interval");
    }

    [Fact]
    public async Task GetByKey_NotFound_ReturnsNull()
    {
        _configRepo.Setup(r => r.GetByKeyAsync("missing")).ReturnsAsync((SystemConfig?)null);
        var result = await _service.GetByKeyAsync("missing");
        result.Should().BeNull();
    }

    #endregion

    #region SaveAsync

    [Fact]
    public async Task Save_ValidJson_PassesThrough()
    {
        var config = new SystemConfig
        {
            Id = Guid.Empty,
            ConfigKey = "theme",
            ConfigValue = "{\"mode\":\"dark\"}",
            ConfigGroup = "general"
        };

        await _service.SaveAsync(config);

        _configRepo.Verify(r => r.UpsertAsync(It.Is<SystemConfig>(c =>
            c.TenantId == TenantId &&
            c.Id != Guid.Empty &&          // SequentialGuid 应已分配
            c.ConfigValue == "{\"mode\":\"dark\"}" &&
            c.UpdateTime > DateTime.MinValue)), Times.Once);
    }

    [Fact]
    public async Task Save_InvalidJson_WrapsAsJsonString()
    {
        var config = new SystemConfig
        {
            Id = Guid.NewGuid(),
            ConfigKey = "plain_value",
            ConfigValue = "hello world",  // 非 JSON
            ConfigGroup = "general"
        };

        await _service.SaveAsync(config);

        // 非 JSON 值应被 JsonSerializer.Serialize 包装为 JSON 字符串 "\"hello world\""
        _configRepo.Verify(r => r.UpsertAsync(It.Is<SystemConfig>(c =>
            c.ConfigValue == "\"hello world\"")), Times.Once);
    }

    [Fact]
    public async Task Save_EmptyValue_DefaultsToEmptyJsonObject()
    {
        var config = new SystemConfig
        {
            Id = Guid.NewGuid(),
            ConfigKey = "empty",
            ConfigValue = "",
            ConfigGroup = "general"
        };

        await _service.SaveAsync(config);

        _configRepo.Verify(r => r.UpsertAsync(It.Is<SystemConfig>(c =>
            c.ConfigValue == "{}")), Times.Once);
    }

    [Fact]
    public async Task Save_NullValue_DefaultsToEmptyJsonObject()
    {
        var config = new SystemConfig
        {
            Id = Guid.NewGuid(),
            ConfigKey = "null_val",
            ConfigValue = null!,
            ConfigGroup = "general"
        };

        await _service.SaveAsync(config);

        _configRepo.Verify(r => r.UpsertAsync(It.Is<SystemConfig>(c =>
            c.ConfigValue == "{}")), Times.Once);
    }

    [Fact]
    public async Task Save_ExistingId_PreservesId()
    {
        var existingId = Guid.NewGuid();
        var config = new SystemConfig
        {
            Id = existingId,
            ConfigKey = "existing",
            ConfigValue = "{}",
            ConfigGroup = "general"
        };

        await _service.SaveAsync(config);

        _configRepo.Verify(r => r.UpsertAsync(It.Is<SystemConfig>(c =>
            c.Id == existingId)), Times.Once);
    }

    #endregion

    #region BatchSaveAsync

    [Fact]
    public async Task BatchSave_SavesEachConfig()
    {
        var configs = new List<SystemConfig>
        {
            new() { ConfigKey = "k1", ConfigValue = "{}", ConfigGroup = "g1" },
            new() { ConfigKey = "k2", ConfigValue = "{}", ConfigGroup = "g1" },
            new() { ConfigKey = "k3", ConfigValue = "{}", ConfigGroup = "g2" }
        };

        await _service.BatchSaveAsync(configs);

        // 每个配置都应该调用 UpsertAsync
        _configRepo.Verify(r => r.UpsertAsync(It.IsAny<SystemConfig>()), Times.Exactly(3));
    }

    #endregion

    #region DeleteAsync

    [Fact]
    public async Task Delete_CallsSoftDelete()
    {
        var id = Guid.NewGuid();
        await _service.DeleteAsync(id);
        _configRepo.Verify(r => r.SoftDeleteAsync(id), Times.Once);
    }

    #endregion
}
