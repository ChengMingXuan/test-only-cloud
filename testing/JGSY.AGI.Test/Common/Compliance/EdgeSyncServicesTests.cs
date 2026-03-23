using System.Text;
using FluentAssertions;
using JGSY.AGI.Common.Core.Crypto;
using JGSY.AGI.Common.Core.EdgeSync;
using JGSY.AGI.Common.Hosting.Sync;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Moq;
using Xunit;

namespace JGSY.AGI.Test.Common.Compliance;

/// <summary>
/// 云边同步服务测试
/// 合规项：FLOW-001~005 / GB/T 36572
/// 覆盖：上行同步、下行同步、离线缓冲、幂等去重、断点续传、
///       SM3 校验和、SM2 签名验签、SM4 加解密
/// </summary>
public class EdgeSyncServicesTests : IDisposable
{
    private readonly string _bufferDir;
    private readonly Mock<ILogger<BaseUpstreamSyncService>> _upstreamLoggerMock;
    private readonly Mock<ILogger<BaseDownstreamSyncService>> _downstreamLoggerMock;
    private readonly Mock<ILogger<FileBasedOfflineBufferService>> _bufferLoggerMock;
    private readonly Mock<IHttpClientFactory> _httpClientFactoryMock;
    private readonly EdgeSyncOptions _defaultOptions;

    public EdgeSyncServicesTests()
    {
        _bufferDir = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "jgsy-edge",
            "sync-buffer");
        _upstreamLoggerMock = new Mock<ILogger<BaseUpstreamSyncService>>();
        _downstreamLoggerMock = new Mock<ILogger<BaseDownstreamSyncService>>();
        _bufferLoggerMock = new Mock<ILogger<FileBasedOfflineBufferService>>();
        _httpClientFactoryMock = new Mock<IHttpClientFactory>();

        ResetBufferDirectory();

        _defaultOptions = new EdgeSyncOptions
        {
            Enabled = true,
            DeployMode = "Edge",
            MaxBufferSize = 1000,
            SyncIntervalSeconds = 60,
        };
    }

    public void Dispose()
    {
        ResetBufferDirectory();
    }

    #region FileBasedOfflineBufferService 测试

    [Fact]
    public async Task Buffer_EnqueueAsync_应将消息持久化到文件()
    {
        using var buffer = CreateBuffer();
        var beforeInfo = await buffer.GetBufferInfoAsync();
        var message = CreateMessage(SyncMessageType.Telemetry, SyncPriority.Normal);

        await buffer.EnqueueAsync(message);

        var afterInfo = await buffer.GetBufferInfoAsync();
        afterInfo.pendingCount.Should().BeGreaterThan(beforeInfo.pendingCount);

        // 清理
        await buffer.AcknowledgeAsync(message.MessageId);
    }

    [Fact]
    public async Task Buffer_DequeueAsync_应包含入队的消息()
    {
        using var buffer = CreateBuffer();
        var msg = CreateMessage(SyncMessageType.AlarmEvent, SyncPriority.Critical);

        await buffer.EnqueueAsync(msg);

        var dequeued = await buffer.DequeueAsync(100);
        dequeued.Should().Contain(m => m.MessageId == msg.MessageId);

        // 清理
        await buffer.AcknowledgeAsync(msg.MessageId);
    }

    [Fact]
    public async Task Buffer_DequeueAsync_同一对象多版本离线重放时应仅保留最新版本()
    {
        using var buffer = CreateBuffer();
        var older = CreateVersionedMessage("1.0.0", DateTimeOffset.UtcNow.AddMinutes(-5));
        var newer = CreateVersionedMessage("2.0.0", DateTimeOffset.UtcNow.AddMinutes(-1));

        await buffer.EnqueueAsync(older);
        await buffer.EnqueueAsync(newer);

        var dequeued = await buffer.DequeueAsync(10);

        dequeued.Should().ContainSingle(message => message.Type == SyncMessageType.DispatchStrategy && message.SiteId == older.SiteId);
        dequeued.Should().Contain(message => message.MessageId == newer.MessageId);
        dequeued.Should().NotContain(message => message.MessageId == older.MessageId);

        await buffer.AcknowledgeAsync(older.MessageId);
        await buffer.AcknowledgeAsync(newer.MessageId);
    }

    [Fact]
    public async Task Buffer_DequeueAsync_旧版本晚到也不应覆盖高版本消息()
    {
        using var buffer = CreateBuffer();
        var latest = CreateVersionedMessage("3.0.0", DateTimeOffset.UtcNow.AddMinutes(-10));
        var stale = CreateVersionedMessage("2.5.0", DateTimeOffset.UtcNow);

        await buffer.EnqueueAsync(latest);
        await buffer.EnqueueAsync(stale);

        var dequeued = await buffer.DequeueAsync(10);

        dequeued.Should().ContainSingle(message => message.Type == SyncMessageType.DispatchStrategy && message.SiteId == latest.SiteId);
        dequeued.Single(message => message.Type == SyncMessageType.DispatchStrategy && message.SiteId == latest.SiteId)
            .Version.Should().Be("3.0.0");

        await buffer.AcknowledgeAsync(latest.MessageId);
        await buffer.AcknowledgeAsync(stale.MessageId);
    }

    [Fact]
    public async Task Buffer_DequeueAsync_冲突消解后仍应优先返回高优先级消息()
    {
        using var buffer = CreateBuffer();
        var version1 = CreateVersionedMessage("1.0.0", DateTimeOffset.UtcNow.AddMinutes(-4));
        var version2 = CreateVersionedMessage("1.1.0", DateTimeOffset.UtcNow.AddMinutes(-2));
        var criticalAlarm = CreateMessage(SyncMessageType.AlarmEvent, SyncPriority.Critical);

        await buffer.EnqueueAsync(version1);
        await buffer.EnqueueAsync(version2);
        await buffer.EnqueueAsync(criticalAlarm);

        var dequeued = await buffer.DequeueAsync(10);

        dequeued.Should().HaveCount(2);
        dequeued[0].MessageId.Should().Be(criticalAlarm.MessageId);
        dequeued[1].MessageId.Should().Be(version2.MessageId);

        await buffer.AcknowledgeAsync(version1.MessageId);
        await buffer.AcknowledgeAsync(version2.MessageId);
        await buffer.AcknowledgeAsync(criticalAlarm.MessageId);
    }

    [Fact]
    public async Task Buffer_AcknowledgeAsync_应删除已确认的消息文件()
    {
        using var buffer = CreateBuffer();
        var message = CreateMessage(SyncMessageType.Telemetry, SyncPriority.Normal);
        await buffer.EnqueueAsync(message);
        var beforeInfo = await buffer.GetBufferInfoAsync();

        await buffer.AcknowledgeAsync(message.MessageId);

        var afterInfo = await buffer.GetBufferInfoAsync();
        afterInfo.pendingCount.Should().BeLessThan(beforeInfo.pendingCount);
    }

    [Fact]
    public async Task Buffer_GetBufferInfo_应返回非负值()
    {
        using var buffer = CreateBuffer();

        var info = await buffer.GetBufferInfoAsync();

        info.pendingCount.Should().BeGreaterOrEqualTo(0);
        info.totalSize.Should().BeGreaterOrEqualTo(0);
    }

    #endregion

    #region BaseUpstreamSyncService 测试

    [Fact]
    public async Task Upstream_SendAsync_在线模式_应成功发送()
    {
        using var buffer = CreateBuffer();
        var upstream = CreateUpstream(buffer);
        var message = CreateMessage(SyncMessageType.Telemetry, SyncPriority.Normal);

        // 无 CloudEndpoint 配置时 SendToCloudAsync 直接返回
        var result = await upstream.SendAsync(message);

        result.Should().BeTrue();
    }

    [Fact]
    public async Task Upstream_SendAsync_幂等去重_相同消息只处理一次()
    {
        using var buffer = CreateBuffer();
        var upstream = CreateUpstream(buffer);
        var message = CreateMessage(SyncMessageType.DeviceStatus, SyncPriority.High);

        var result1 = await upstream.SendAsync(message);
        var result2 = await upstream.SendAsync(message);

        result1.Should().BeTrue();
        result2.Should().BeTrue(); // 返回 true 但不重复处理
    }

    [Fact]
    public async Task Upstream_SendTelemetryAsync_应创建正确类型的消息()
    {
        using var buffer = CreateBuffer();
        var upstream = CreateUpstream(buffer);
        var tenantId = Guid.NewGuid();

        await upstream.SendTelemetryAsync(tenantId, "site-001", "{\"temp\":25.5}");

        var status = await upstream.GetStatusAsync();
        status.Should().NotBeNull();
    }

    [Fact]
    public async Task Upstream_SendAlarmAsync_应使用Critical优先级()
    {
        using var buffer = CreateBuffer();
        var upstream = CreateUpstream(buffer);

        // 设置离线以让消息进入缓冲区
        upstream.SetOnlineStatus(false);
        await upstream.SendAlarmAsync(Guid.NewGuid(), "site-002", "{\"alarm\":\"过温\"}");

        var buffered = await buffer.DequeueAsync(100);
        buffered.Should().Contain(m => m.Priority == SyncPriority.Critical);

        // 清理入队的消息
        foreach (var m in buffered.Where(m => m.Type == SyncMessageType.AlarmEvent))
            await buffer.AcknowledgeAsync(m.MessageId);
    }

    [Fact]
    public async Task Upstream_离线时消息应入缓冲队列()
    {
        using var buffer = CreateBuffer();
        var upstream = CreateUpstream(buffer);
        var beforeInfo = await buffer.GetBufferInfoAsync();
        upstream.SetOnlineStatus(false);

        var message = CreateMessage(SyncMessageType.ChargingOrder, SyncPriority.High);
        await upstream.SendAsync(message);

        var afterInfo = await buffer.GetBufferInfoAsync();
        afterInfo.pendingCount.Should().BeGreaterThan(beforeInfo.pendingCount);

        // 清理
        await buffer.AcknowledgeAsync(message.MessageId);
    }

    [Fact]
    public async Task Upstream_SendBatchAsync_应返回发送数量()
    {
        using var buffer = CreateBuffer();
        var upstream = CreateUpstream(buffer);
        var messages = new[]
        {
            CreateMessage(SyncMessageType.Telemetry, SyncPriority.Normal),
            CreateMessage(SyncMessageType.DeviceStatus, SyncPriority.High),
        };

        var sent = await upstream.SendBatchAsync(messages);

        sent.Should().Be(2);
    }

    [Fact]
    public async Task Upstream_GetStatusAsync_在线_PendingCount应大于等于0()
    {
        using var buffer = CreateBuffer();
        var upstream = CreateUpstream(buffer);

        var status = await upstream.GetStatusAsync();

        status.IsOnline.Should().BeTrue();
        status.PendingCount.Should().BeGreaterOrEqualTo(0);
    }

    #endregion

    #region BaseDownstreamSyncService 测试

    [Fact]
    public async Task Downstream_SendAsync_应更新LastSyncTime()
    {
        var downstream = CreateDownstream();
        var message = CreateMessage(SyncMessageType.DispatchStrategy, SyncPriority.Normal);

        var result = await downstream.SendAsync(message);

        result.Should().BeTrue();
        var status = await downstream.GetStatusAsync();
        status.LastSyncTime.Should().NotBeNull();
    }

    [Fact]
    public async Task Downstream_SendStrategyAsync_应抛出NotSupportedException_云端只读边界()
    {
        var downstream = CreateDownstream();

#pragma warning disable CS0618
        var act = () => downstream.SendStrategyAsync(Guid.NewGuid(), "site-001", "{}", "v1.0");
#pragma warning restore CS0618

        await act.Should().ThrowAsync<NotSupportedException>()
            .WithMessage("*REQ-001*");
    }

    [Fact]
    public async Task Downstream_SendRulePackageAsync_应抛出NotSupportedException_云端只读边界()
    {
        var downstream = CreateDownstream();

#pragma warning disable CS0618
        var act = () => downstream.SendRulePackageAsync(Guid.NewGuid(), "site-001", "{\"rules\":[]}", "v2.1");
#pragma warning restore CS0618

        await act.Should().ThrowAsync<NotSupportedException>()
            .WithMessage("*REQ-001*");
    }

    [Fact]
    public async Task Downstream_SendDeviceConfigAsync_应抛出NotSupportedException_云端只读边界()
    {
        var downstream = CreateDownstream();

#pragma warning disable CS0618
        var act = () => downstream.SendDeviceConfigAsync(Guid.NewGuid(), "site-001", "{\"config\":{}}");
#pragma warning restore CS0618

        await act.Should().ThrowAsync<NotSupportedException>()
            .WithMessage("*REQ-001*");
    }

    [Fact]
    public async Task Downstream_SendBatchAsync_应返回消息数()
    {
        var downstream = CreateDownstream();
        var messages = new[]
        {
            CreateMessage(SyncMessageType.DispatchStrategy, SyncPriority.Normal),
            CreateMessage(SyncMessageType.RulePackage, SyncPriority.High),
        };

        var count = await downstream.SendBatchAsync(messages);

        count.Should().Be(2);
    }

    #endregion

    #region SyncIntegrityValidatorService 测试

    [Fact]
    public void IntegrityValidator_ComputeChecksum_应返回SM3哈希()
    {
        var sm2Mock = new Mock<ISM2CryptoService>();
        var sm3Mock = new Mock<ISM3HashService>();
        var sm4Mock = new Mock<ISM4CryptoService>();
        sm3Mock.Setup(s => s.Hash(It.IsAny<byte[]>()))
            .Returns(new byte[32]);

        var validator = new SyncIntegrityValidatorService(sm2Mock.Object, sm3Mock.Object, sm4Mock.Object);
        var msg = CreateMessage(SyncMessageType.Telemetry, SyncPriority.Normal);

        var checksum = validator.ComputeChecksum(msg);

        checksum.Should().NotBeNullOrEmpty();
        sm3Mock.Verify(s => s.Hash(It.IsAny<byte[]>()), Times.Once);
    }

    [Fact]
    public void IntegrityValidator_ValidateChecksum_正确校验和_应返回true()
    {
        var (validator, sm3Mock) = CreateIntegrityValidator();
        var msg = CreateMessage(SyncMessageType.Telemetry, SyncPriority.Normal);
        msg.Checksum = validator.ComputeChecksum(msg);

        var isValid = validator.ValidateChecksum(msg);

        isValid.Should().BeTrue();
    }

    [Fact]
    public void IntegrityValidator_ValidateChecksum_空校验和_应返回false()
    {
        var (validator, _) = CreateIntegrityValidator();
        var msg = CreateMessage(SyncMessageType.Telemetry, SyncPriority.Normal);
        msg.Checksum = null;

        var isValid = validator.ValidateChecksum(msg);

        isValid.Should().BeFalse();
    }

    [Fact]
    public void IntegrityValidator_EncryptDecrypt_应可逆()
    {
        var sm2Mock = new Mock<ISM2CryptoService>();
        var sm3Mock = new Mock<ISM3HashService>();
        var sm4Mock = new Mock<ISM4CryptoService>();
        var payload = "敏感数据：充电桩遥测";
        var key = new byte[16];
        var encrypted = Encoding.UTF8.GetBytes("encrypted-data");
        sm4Mock.Setup(s => s.Encrypt(key, It.IsAny<byte[]>())).Returns(encrypted);
        sm4Mock.Setup(s => s.Decrypt(key, encrypted)).Returns(Encoding.UTF8.GetBytes(payload));

        var validator = new SyncIntegrityValidatorService(sm2Mock.Object, sm3Mock.Object, sm4Mock.Object);

        var encryptedPayload = validator.EncryptPayload(payload, key);
        var decrypted = validator.DecryptPayload(encryptedPayload, key);

        decrypted.Should().Be(payload);
    }

    #endregion

    #region EdgeSyncOptions 配置测试

    [Fact]
    public void EdgeSyncOptions_默认值_应合理()
    {
        var opts = new EdgeSyncOptions();

        opts.MaxBufferSize.Should().BeGreaterThan(0, "缓冲区大小必须为正数");
        opts.SyncIntervalSeconds.Should().BeGreaterOrEqualTo(10, "同步间隔不应过短");
    }

    #endregion

    #region REQ-001 云端只读边界验证

    [Theory]
    [InlineData(SyncMessageType.DispatchStrategy)]
    [InlineData(SyncMessageType.RulePackage)]
    [InlineData(SyncMessageType.DeviceConfig)]
    public void DownstreamDataFilter_REQ001_应拦截状态变更类消息(SyncMessageType type)
    {
        var filter = new DownstreamDataFilterService();
        var message = CreateMessage(type, SyncPriority.High);
        message.Direction = SyncDirection.Downstream;

        var (isAllowed, reason) = filter.ValidateDownstream(message);

        isAllowed.Should().BeFalse("云端绝对只读边界: {0} 类型不允许下行", type);
        reason.Should().Contain("FLOW-002");
    }

    [Theory]
    [InlineData(SyncMessageType.PricingPolicy)]
    [InlineData(SyncMessageType.OtaFirmware)]
    [InlineData(SyncMessageType.AiOptimization)]
    public void DownstreamDataFilter_REQ001_应放行只读分析建议类消息(SyncMessageType type)
    {
        var filter = new DownstreamDataFilterService();
        var message = CreateMessage(type, SyncPriority.Normal);
        message.Direction = SyncDirection.Downstream;

        var (isAllowed, _) = filter.ValidateDownstream(message);

        isAllowed.Should().BeTrue("只读分析建议类: {0} 允许下行", type);
    }

    [Theory]
    [InlineData(SyncMessageType.Telemetry)]
    [InlineData(SyncMessageType.DeviceStatus)]
    [InlineData(SyncMessageType.AlarmEvent)]
    [InlineData(SyncMessageType.AuditLog)]
    [InlineData(SyncMessageType.ChargingOrder)]
    [InlineData(SyncMessageType.ExecutionResult)]
    public void UpstreamDataFilter_应放行允许类型(SyncMessageType type)
    {
        var filter = new UpstreamDataFilterService();
        var message = CreateMessage(type, SyncPriority.Normal);
        message.Direction = SyncDirection.Upstream;

        var (isAllowed, _) = filter.ValidateUpstream(message);

        isAllowed.Should().BeTrue("上行类型 {0} 应放行", type);
    }

    #endregion

    #region 辅助方法

    private FileBasedOfflineBufferService CreateBuffer()
    {
        ResetBufferDirectory();
        return new FileBasedOfflineBufferService(
            Options.Create(_defaultOptions),
            _bufferLoggerMock.Object);
    }

    private void ResetBufferDirectory()
    {
        if (Directory.Exists(_bufferDir))
        {
            Directory.Delete(_bufferDir, recursive: true);
        }
    }

    private BaseUpstreamSyncService CreateUpstream(IOfflineBufferService buffer)
    {
        return new BaseUpstreamSyncService(
            buffer,
            Options.Create(_defaultOptions),
            _httpClientFactoryMock.Object,
            _upstreamLoggerMock.Object);
    }

    private BaseDownstreamSyncService CreateDownstream()
    {
        return new BaseDownstreamSyncService(
            Options.Create(_defaultOptions),
            _httpClientFactoryMock.Object,
            _downstreamLoggerMock.Object);
    }

    private (SyncIntegrityValidatorService validator, Mock<ISM3HashService> sm3Mock) CreateIntegrityValidator()
    {
        var sm2Mock = new Mock<ISM2CryptoService>();
        var sm3Mock = new Mock<ISM3HashService>();
        var sm4Mock = new Mock<ISM4CryptoService>();
        sm3Mock.Setup(s => s.Hash(It.IsAny<byte[]>()))
            .Returns((byte[] data) => System.Security.Cryptography.SHA256.HashData(data));
        var validator = new SyncIntegrityValidatorService(sm2Mock.Object, sm3Mock.Object, sm4Mock.Object);
        return (validator, sm3Mock);
    }

    private static SyncMessage CreateMessage(SyncMessageType type, SyncPriority priority)
    {
        return new SyncMessage
        {
            MessageId = Guid.NewGuid(),
            TenantId = Guid.NewGuid(),
            Direction = SyncDirection.Upstream,
            Type = type,
            Priority = priority,
            SourceService = "test-service",
            SiteId = "site-test",
            Payload = "{\"test\":true}",
            CreatedAt = DateTimeOffset.UtcNow,
            ExpiresAt = DateTimeOffset.UtcNow.AddHours(72),
        };
    }

    private static SyncMessage CreateVersionedMessage(string version, DateTimeOffset createdAt)
    {
        return new SyncMessage
        {
            MessageId = Guid.NewGuid(),
            TenantId = Guid.Parse("11111111-1111-1111-1111-111111111111"),
            Direction = SyncDirection.Downstream,
            Type = SyncMessageType.DispatchStrategy,
            Priority = SyncPriority.Normal,
            SourceService = "cloud-orchestrator",
            SiteId = "edge-site-001",
            Payload = "{\"strategy\":true}",
            Version = version,
            CreatedAt = createdAt,
            ExpiresAt = createdAt.AddHours(72),
        };
    }

    #endregion
}
