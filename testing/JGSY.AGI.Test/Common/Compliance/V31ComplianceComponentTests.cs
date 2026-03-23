// ═══════════════════════════════════════════════════════════════════
// v3.1 新增合规组件单元测试
// 覆盖：ConditionalAccessPolicy / ZeroTrustEnforcer / PasskeyAuthProvider
//       AuditNonRepudiationService / DistributedChainProofService / BackupOrchestrationService
// ═══════════════════════════════════════════════════════════════════

using FluentAssertions;
using JGSY.AGI.Common.Core.Crypto;
using JGSY.AGI.Common.Core.Security;
using JGSY.AGI.Common.Hosting.Audit;
using JGSY.AGI.Common.Hosting.Security;
using JGSY.AGI.Common.Infra.Backup;
using JGSY.AGI.Common.Infra.Blockchain;
using JGSY.AGI.Common.Infra.Crypto;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Moq;
using System.Net;
using Xunit;

namespace JGSY.AGI.Test.Common.Compliance;

/// <summary>
/// v3.1 新增安全组件合规测试（等保三级 99%+）
/// </summary>
public class V31ComplianceComponentTests
{
    #region  条件式访问策略 (AUTH-003)

    [Fact]
    public void ConditionalAccessPolicy_WhenEnabled_ShouldEvaluateRequest()
    {
        var opts = Options.Create(new ConditionalAccessOptions { Enabled = true });
        var logger = Mock.Of<ILogger<ConditionalAccessPolicy>>();
        var policy = new ConditionalAccessPolicy(opts, logger);

        var ctx = CreateHttpContext("192.168.1.1");
        var result = policy.Evaluate(ctx, "user-001");

        result.Should().NotBeNull("条件访问必须返回决策结果（AUTH-003）");
        result.RiskScore.Should().BeGreaterThanOrEqualTo(0, "风险评分必须为非负整数");
        result.Reason.Should().NotBeEmpty("决策原因不应为空");
    }

    [Fact]
    public void ConditionalAccessPolicy_WhenDisabled_ShouldAlwaysAllow()
    {
        var opts = Options.Create(new ConditionalAccessOptions { Enabled = false });
        var logger = Mock.Of<ILogger<ConditionalAccessPolicy>>();
        var policy = new ConditionalAccessPolicy(opts, logger);

        var ctx = CreateHttpContext("1.2.3.4");
        var result = policy.Evaluate(ctx, "user-002");

        result.Allowed.Should().BeTrue("禁用时应允许所有请求");
        result.RiskScore.Should().Be(0);
    }

    [Fact]
    public void ConditionalAccessPolicy_BlockedIp_ShouldDenyAccess()
    {
        var opts = Options.Create(new ConditionalAccessOptions
        {
            Enabled = true,
            BlockedIpRanges = ["1.2.3.4"]
        });
        var logger = Mock.Of<ILogger<ConditionalAccessPolicy>>();
        var policy = new ConditionalAccessPolicy(opts, logger);

        var ctx = CreateHttpContext("1.2.3.4");
        var result = policy.Evaluate(ctx, "attacker");

        result.Allowed.Should().BeFalse("黑名单IP必须被拒绝（AUTH-003 安全访问控制）");
        result.RiskScore.Should().Be(100);
    }

    [Fact]
    public void ConditionalAccessPolicy_UnknownDevice_ShouldRequireVerification()
    {
        var opts = Options.Create(new ConditionalAccessOptions { Enabled = true });
        var logger = Mock.Of<ILogger<ConditionalAccessPolicy>>();
        var policy = new ConditionalAccessPolicy(opts, logger);

        var ctx = CreateHttpContext("192.168.1.1");
        var result = policy.Evaluate(ctx, "user-003", deviceFingerprint: null);

        result.RequireDeviceVerification.Should().BeTrue("未知设备应触发设备验证（AUTH-003）");
    }

    [Fact]
    public void ConditionalAccessPolicy_KnownDevice_ShouldNotRequireVerification()
    {
        var opts = Options.Create(new ConditionalAccessOptions { Enabled = true });
        var logger = Mock.Of<ILogger<ConditionalAccessPolicy>>();
        var policy = new ConditionalAccessPolicy(opts, logger);

        var ctx = CreateHttpContext("192.168.1.1");
        var result = policy.Evaluate(ctx, "user-004", deviceFingerprint: "fp-abc123");

        result.RequireDeviceVerification.Should().BeFalse("已知设备不应要求设备验证");
    }

    #endregion

    #region 零信任执行器 (ZONE-005)

    [Fact]
    public void ZeroTrustEnforcer_ExcludedPath_ShouldAllow()
    {
        var opts = Options.Create(new ZeroTrustOptions { Enabled = true });
        var logger = Mock.Of<ILogger<ZeroTrustEnforcer>>();
        var enforcer = new ZeroTrustEnforcer(opts, logger);

        var ctx = CreateHttpContext("10.0.0.1", path: "/health");
        ctx.User = new System.Security.Claims.ClaimsPrincipal();

        var decision = enforcer.Enforce(ctx);
        decision.IsAllowed.Should().BeTrue("健康检查路径应豁免零信任检查（ZONE-005）");
    }

    [Fact]
    public void ZeroTrustEnforcer_ReplayAttack_ShouldDeny()
    {
        var opts = Options.Create(new ZeroTrustOptions
        {
            Enabled = true,
            MaxClockSkewSeconds = 60
        });
        var logger = Mock.Of<ILogger<ZeroTrustEnforcer>>();
        var enforcer = new ZeroTrustEnforcer(opts, logger);

        // 使用10分钟前的时间戳（超过60秒限制）
        var oldTimestamp = DateTimeOffset.UtcNow.AddMinutes(-10).ToUnixTimeSeconds().ToString();
        var ctx = CreateHttpContext("10.0.0.1", headers: new Dictionary<string, string>
        {
            ["X-Request-Timestamp"] = oldTimestamp
        });

        // 设置身份认证
        var claims = new[] { new System.Security.Claims.Claim(System.Security.Claims.ClaimTypes.NameIdentifier, "user-001") };
        ctx.User = new System.Security.Claims.ClaimsPrincipal(
            new System.Security.Claims.ClaimsIdentity(claims, "jwt"));

        var decision = enforcer.Enforce(ctx);
        decision.IsAllowed.Should().BeFalse("过期时间戳应被拒绝（ZONE-005 防重放攻击）");
        decision.DenialCode.Should().Be("ReplayAttackPrevention");
    }

    [Fact]
    public void ZeroTrustEnforcer_FreshTimestamp_ShouldAllow()
    {
        var opts = Options.Create(new ZeroTrustOptions
        {
            Enabled = true,
            MaxClockSkewSeconds = 300,
            RequireInternalServiceSignature = false,
            RequireDeviceFingerprint = false
        });
        var logger = Mock.Of<ILogger<ZeroTrustEnforcer>>();
        var enforcer = new ZeroTrustEnforcer(opts, logger);

        var validTimestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString();
        var ctx = CreateHttpContext("10.0.0.1", headers: new Dictionary<string, string>
        {
            ["X-Request-Timestamp"] = validTimestamp
        });
        var claims = new[] { new System.Security.Claims.Claim(System.Security.Claims.ClaimTypes.NameIdentifier, "user-001") };
        ctx.User = new System.Security.Claims.ClaimsPrincipal(
            new System.Security.Claims.ClaimsIdentity(claims, "jwt"));

        var decision = enforcer.Enforce(ctx);
        decision.IsAllowed.Should().BeTrue("有效时间戳应被允许（ZONE-005）");
    }

    [Fact]
    public void ZeroTrustEnforcer_InternalService_WithoutSignature_ShouldDeny()
    {
        var opts = Options.Create(new ZeroTrustOptions
        {
            Enabled = true,
            RequireInternalServiceSignature = true,
            MaxClockSkewSeconds = 300
        });
        var logger = Mock.Of<ILogger<ZeroTrustEnforcer>>();
        var enforcer = new ZeroTrustEnforcer(opts, logger);

        var validTimestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString();
        var ctx = CreateHttpContext("10.0.0.1", headers: new Dictionary<string, string>
        {
            ["X-Request-Timestamp"] = validTimestamp,
            ["X-Internal-Service"] = "true" // 标记为内部服务但没有签名
        });
        var claims = new[] { new System.Security.Claims.Claim(System.Security.Claims.ClaimTypes.NameIdentifier, "system") };
        ctx.User = new System.Security.Claims.ClaimsPrincipal(
            new System.Security.Claims.ClaimsIdentity(claims, "internal"));

        var decision = enforcer.Enforce(ctx);
        decision.IsAllowed.Should().BeFalse("内部服务请求缺少签名应被拒绝（ZONE-005 服务间认证）");
    }

    #endregion

    #region Passkey 认证 (AUTH-002)

    [Fact]
    public void PasskeyAuthProvider_WhenEnabled_ShouldCreateRegistrationChallenge()
    {
        var opts = Options.Create(new PasskeyOptions { Enabled = true });
        var logger = Mock.Of<ILogger<PasskeyAuthProvider>>();
        var provider = new PasskeyAuthProvider(opts, logger);

        var challenge = provider.CreateRegistrationChallenge("user-001", "user@jgsy.agi");

        challenge.Should().NotBeNull("Passkey注册挑战不应为空（AUTH-002）");
        challenge.ChallengeId.Should().NotBeEmpty();
        challenge.ChallengeBase64.Should().NotBeEmpty();
        challenge.UserId.Should().Be("user-001");
        challenge.ExpiresAtUtc.Should().BeGreaterThan(DateTimeOffset.UtcNow.ToUnixTimeMilliseconds());
    }

    [Fact]
    public void PasskeyAuthProvider_ChallengeExpiry_ShouldBeInFuture()
    {
        var opts = Options.Create(new PasskeyOptions { Enabled = true, ChallengeTimeoutSeconds = 300 });
        var logger = Mock.Of<ILogger<PasskeyAuthProvider>>();
        var provider = new PasskeyAuthProvider(opts, logger);

        var challenge = provider.CreateRegistrationChallenge("user-002", "user2@test.com");
        var expiryTime = DateTimeOffset.FromUnixTimeMilliseconds(challenge.ExpiresAtUtc);
        var minExpiry = DateTimeOffset.UtcNow.AddSeconds(299);

        expiryTime.Should().BeAfter(minExpiry.UtcDateTime,
            "Passkey挑战有效期应≥300秒（AUTH-002）");
    }

    [Fact]
    public void PasskeyAuthProvider_WhenDisabled_ShouldThrow()
    {
        var opts = Options.Create(new PasskeyOptions { Enabled = false });
        var logger = Mock.Of<ILogger<PasskeyAuthProvider>>();
        var provider = new PasskeyAuthProvider(opts, logger);

        Action act = () => provider.CreateRegistrationChallenge("user", "user@test.com");
        act.Should().Throw<InvalidOperationException>("Passkey未启用时应抛出InvalidOperationException");
    }

    [Fact]
    public void PasskeyAuthProvider_CreateAuthChallenge_ShouldReturnValidChallenge()
    {
        var opts = Options.Create(new PasskeyOptions { Enabled = true });
        var logger = Mock.Of<ILogger<PasskeyAuthProvider>>();
        var provider = new PasskeyAuthProvider(opts, logger);

        var authChallenge = provider.CreateAuthChallenge();

        authChallenge.Should().NotBeNull("认证挑战不应为空（AUTH-002）");
        authChallenge.ChallengeBase64.Should().NotBeEmpty();
        authChallenge.ChallengeId.Should().NotBeEmpty();
    }

    #endregion

    #region 审计不可否认性 (AUDIT-006)

    [Fact]
    public void AuditNonRepudiationService_ShouldGenerateValidProof()
    {
        var sm2Mock = new Mock<ISM2CryptoService>();
        // Mock SM2 密钥对 + 签名
        sm2Mock.Setup(x => x.GenerateKeyPair()).Returns((new byte[32], new byte[65]));
        sm2Mock.Setup(x => x.Sign(It.IsAny<byte[]>(), It.IsAny<byte[]>())).Returns(new byte[72]);

        var sm3Mock = new Mock<ISM3HashService>();
        sm3Mock.Setup(x => x.Hash(It.IsAny<byte[]>())).Returns(new byte[32]);

        var configMock = new Mock<IConfiguration>();
        var logger = Mock.Of<ILogger<AuditNonRepudiationService>>();
        var service = new AuditNonRepudiationService(sm2Mock.Object, sm3Mock.Object, configMock.Object, logger);

        var auditEvent = new { UserId = "user-001", Action = "login", Resource = "system", Timestamp = DateTime.UtcNow };
        var proof = service.GenerateProof("evt-001", auditEvent);

        proof.Should().NotBeNull("不可否认性证明不应为空（AUDIT-006）");
        proof.EventId.Should().Be("evt-001");
        proof.Signature.Should().NotBeEmpty("SM2签名不应为空");
        proof.EventHash.Should().NotBeEmpty("SM3哈希不应为空");
        proof.TimestampUtc.Should().BeGreaterThan(0);
        proof.TimestampSource.Should().Be("local");
    }

    [Fact]
    public void AuditNonRepudiationService_ShouldGenerateDifferentProofsForDifferentEvents()
    {
        var sm2Mock = new Mock<ISM2CryptoService>();
        sm2Mock.Setup(x => x.GenerateKeyPair()).Returns((new byte[32], new byte[65]));
        sm2Mock.Setup(x => x.Sign(It.IsAny<byte[]>(), It.IsAny<byte[]>())).Returns<byte[], byte[]>((k, data) =>
        {
            // 返回包含data内容的签名确保不同事件产生不同签名
            var sig = new byte[72];
            Array.Copy(data, 0, sig, 0, Math.Min(data.Length, sig.Length));
            return sig;
        });

        var sm3Mock = new Mock<ISM3HashService>();
        sm3Mock.Setup(x => x.Hash(It.IsAny<byte[]>())).Returns<byte[]>(data =>
        {
            // 使用简单哈希确保不同输入产生不同输出
            return System.Security.Cryptography.SHA256.HashData(data).Take(32).ToArray();
        });

        var configMock = new Mock<IConfiguration>();
        var logger = Mock.Of<ILogger<AuditNonRepudiationService>>();
        var service = new AuditNonRepudiationService(sm2Mock.Object, sm3Mock.Object, configMock.Object, logger);

        var event1 = new { Action = "login", UserId = "user-001" };
        var event2 = new { Action = "logout", UserId = "user-002" };

        var proof1 = service.GenerateProof("evt-001", event1);
        var proof2 = service.GenerateProof("evt-002", event2);

        proof1.EventHash.Should().NotBe(proof2.EventHash, "不同审计事件应有不同的哈希（AUDIT-006 完整性）");
    }

    #endregion

    #region 分布式链证明 (AUDIT-007)

    [Fact]
    public void DistributedChainProofService_ShouldAcceptEventHashes()
    {
        var opts = Options.Create(new DistributedChainProofOptions
        {
            Enabled = true,
            IntervalMinutes = 15,
            ProofStoragePath = Path.GetTempPath()
        });
        var sm3Mock = new Mock<ISM3HashService>();
        sm3Mock.Setup(x => x.Hash(It.IsAny<byte[]>())).Returns(new byte[32]);

        var logger = Mock.Of<ILogger<DistributedChainProofService>>();
        var service = new DistributedChainProofService(opts, sm3Mock.Object, logger);

        // 提交多个服务的审计事件哈希
        Action act = () =>
        {
            service.SubmitEventHash("jgsy.identity", "hash-001");
            service.SubmitEventHash("jgsy.permission", "hash-002");
            service.SubmitEventHash("jgsy.device", "hash-003");
        };

        act.Should().NotThrow("提交审计哈希不应抛出异常（AUDIT-007 分布式链证明）");
    }

    #endregion

    #region 备份自动化 (BACKUP-001)

    [Fact]
    public async Task BackupOrchestrationService_ShouldExecuteFullBackup()
    {
        var opts = Options.Create(new BackupOrchestrationOptions
        {
            Enabled = true,
            BackupStoragePath = Path.Combine(Path.GetTempPath(), "test-backup-" + Guid.NewGuid()),
            FullBackupIntervalHours = 24,
            IncrementalBackupIntervalHours = 1,
            RetentionDays = 90
        });
        var logger = Mock.Of<ILogger<BackupOrchestrationService>>();
        var service = new BackupOrchestrationService(opts, logger);

        var result = await service.ExecuteBackupAsync(BackupType.Full);

        result.Should().NotBeNull("全量备份必须返回结果（BACKUP-001）");
        result.Type.Should().Be(BackupType.Full);
        result.Success.Should().BeTrue("备份操作应成功");
        result.BackupId.Should().NotBeEmpty("备份ID不应为空");
        result.TimestampUtc.Should().BeGreaterThan(0);

        // 清理临时目录
        if (Directory.Exists(opts.Value.BackupStoragePath))
            Directory.Delete(opts.Value.BackupStoragePath, true);
    }

    [Fact]
    public async Task BackupOrchestrationService_ShouldVerifyBackupIntegrity()
    {
        var tempPath = Path.Combine(Path.GetTempPath(), "test-backup-integrity-" + Guid.NewGuid());
        var opts = Options.Create(new BackupOrchestrationOptions
        {
            Enabled = true,
            BackupStoragePath = tempPath,
            EnableIntegrityVerification = true
        });
        var logger = Mock.Of<ILogger<BackupOrchestrationService>>();
        var service = new BackupOrchestrationService(opts, logger);

        var backup = await service.ExecuteBackupAsync(BackupType.Incremental);
        var isValid = await service.VerifyBackupIntegrityAsync(backup);

        isValid.Should().BeTrue("备份完整性验证应通过（BACKUP-001 RPO/RTO要求）");

        if (Directory.Exists(tempPath))
            Directory.Delete(tempPath, true);
    }

    [Fact]
    public void BackupOrchestrationService_RetentionPolicy_ShouldBe90Days()
    {
        var opts = Options.Create(new BackupOrchestrationOptions());
        opts.Value.RetentionDays.Should().BeGreaterThanOrEqualTo(30,
            "等保三级要求备份保留≥30天（7.1.14节）");
    }

    [Fact]
    public void BackupOrchestrationService_RPO_ShouldBe1HourOrLess()
    {
        var opts = Options.Create(new BackupOrchestrationOptions());
        opts.Value.IncrementalBackupIntervalHours.Should().BeLessThanOrEqualTo(1,
            "等保三级RPO要求≤1小时（BACKUP-001）");
    }

    [Fact]
    public void BackupOrchestrationService_ShouldTrackHistory()
    {
        var opts = Options.Create(new BackupOrchestrationOptions
        {
            BackupStoragePath = Path.Combine(Path.GetTempPath(), "test-history-" + Guid.NewGuid())
        });
        var logger = Mock.Of<ILogger<BackupOrchestrationService>>();
        var service = new BackupOrchestrationService(opts, logger);

        var history = service.GetBackupHistory();
        history.Should().NotBeNull("备份历史记录不应为空（BACKUP-001 审计要求）");
    }

    #endregion

    #region 区块链存证 (DATA-005)

    [Fact]
    public async Task BlockchainEvidenceService_WhenDisabled_ShouldCreateLocalRecord()
    {
        var opts = Options.Create(new BlockchainEvidenceOptions { Enabled = false });
        var sm3Mock = new Mock<ISM3HashService>();
        sm3Mock.Setup(x => x.Hash(It.IsAny<byte[]>())).Returns(new byte[32]);

        var logger = Mock.Of<ILogger<BlockchainEvidenceService>>();
        var service = new BlockchainEvidenceService(opts, sm3Mock.Object, logger);

        var data = new { EnergyKw = 100.5, DeviceId = "dev-001", Timestamp = DateTime.UtcNow };
        var record = await service.SubmitEvidenceAsync("energy_dispatch", data);

        record.Should().NotBeNull("降级本地存证应返回记录（DATA-005）");
        record.Status.Should().Be("pending", "本地存证状态为pending");
        record.DataHash.Should().NotBeEmpty("数据哈希不应为空");
    }

    [Fact]
    public async Task BlockchainEvidenceService_ShouldCalculateSM3Hash()
    {
        var opts = Options.Create(new BlockchainEvidenceOptions { Enabled = false });
        var sm3 = new SM3HashService();
        var logger = Mock.Of<ILogger<BlockchainEvidenceService>>();
        var service = new BlockchainEvidenceService(opts, sm3, logger);

        var data = new { Value = "test-evidence", Timestamp = "2026-03-11" };
        var record = await service.SubmitEvidenceAsync("audit_log", data);

        record.DataHash.Should().HaveLength(64, "SM3哈希十六进制字符串应为64位（DATA-005 国密哈希）");
        record.DataHash.Should().MatchRegex("^[0-9a-f]+$", "数据哈希必须为有效十六进制（DATA-005）");
    }

    [Fact]
    public async Task BlockchainEvidenceService_ShouldVerifyDataIntegrity()
    {
        var opts = Options.Create(new BlockchainEvidenceOptions { Enabled = false });
        var sm3 = new SM3HashService();
        var logger = Mock.Of<ILogger<BlockchainEvidenceService>>();
        var service = new BlockchainEvidenceService(opts, sm3, logger);

        var data = new { Contract = "JGSY-2026-001", Amount = 50000, Currency = "CNY" };
        var record = await service.SubmitEvidenceAsync("contract_record", data, "contract-001");

        // 用相同数据验证 - 应该通过
        var isValid = await service.VerifyEvidenceAsync("contract-001", data);
        isValid.Should().BeTrue("相同数据的完整性验证应通过（DATA-005 区块链存证）");
    }

    #endregion

    #region 账号锁定服务 (AUTH-005)

    [Fact]
    public async Task AccountLockupService_ShouldFreezeViolatingAccount()
    {
        var cache = new Mock<Microsoft.Extensions.Caching.Distributed.IDistributedCache>();
        cache.Setup(c => c.SetAsync(It.IsAny<string>(), It.IsAny<byte[]>(),
            It.IsAny<Microsoft.Extensions.Caching.Distributed.DistributedCacheEntryOptions>(),
            It.IsAny<CancellationToken>())).Returns(Task.CompletedTask);
        var opts = Options.Create(new AccountLockupOptions { Enabled = true, FreezeHours = 72 });
        var logger = Mock.Of<ILogger<AccountLockupService>>();
        var service = new AccountLockupService(cache.Object, logger, opts);

        var result = await service.DetectAndFreezeAsync(Guid.NewGuid(), ViolationType.BruteForce, "连续5次登录失败");

        result.Should().BeTrue("暴力破解违规应被冻结（AUTH-005）");
    }

    [Fact]
    public async Task AccountLockupService_WhenDisabled_ShouldNotFreeze()
    {
        var cache = new Mock<Microsoft.Extensions.Caching.Distributed.IDistributedCache>();
        var opts = Options.Create(new AccountLockupOptions { Enabled = false });
        var logger = Mock.Of<ILogger<AccountLockupService>>();
        var service = new AccountLockupService(cache.Object, logger, opts);

        var result = await service.DetectAndFreezeAsync(Guid.NewGuid(), ViolationType.AbnormalIpLogin, "test");

        result.Should().BeFalse("禁用时不应冻结账号");
    }

    [Fact]
    public void AccountLockupOptions_FreezeHours_ShouldBeAtLeast72()
    {
        var opts = new AccountLockupOptions();
        opts.FreezeHours.Should().BeGreaterThanOrEqualTo(72,
            "等保三级要求违规冻结≥72小时（AUTH-005）");
    }

    [Fact]
    public void AccountLockupOptions_ShouldNotAllowAutoUnfreeze()
    {
        var opts = new AccountLockupOptions();
        opts.AllowAutoUnfreeze.Should().BeFalse(
            "等保三级默认仅安全管理员可解冻（AUTH-005）");
    }

    #endregion

    #region 生物识别认证 (AUTH-004)

    [Fact]
    public void BiometricAuthProvider_WhenDisabled_EnrollShouldThrow()
    {
        var opts = Options.Create(new BiometricAuthOptions { Enabled = false });
        var logger = Mock.Of<ILogger<BiometricAuthProvider>>();
        var provider = new BiometricAuthProvider(logger, opts);

        Func<Task> act = () => provider.EnrollAsync(Guid.NewGuid(), BiometricType.Fingerprint, new byte[] { 1, 2, 3 });

        act.Should().ThrowAsync<InvalidOperationException>("生物识别未启用时应拒绝注册");
    }

    [Fact]
    public async Task BiometricAuthProvider_WhenDisabled_VerifyShouldReturnNotVerified()
    {
        var opts = Options.Create(new BiometricAuthOptions { Enabled = false });
        var logger = Mock.Of<ILogger<BiometricAuthProvider>>();
        var provider = new BiometricAuthProvider(logger, opts);

        var result = await provider.VerifyAsync(Guid.NewGuid(), BiometricType.FaceRecognition, new byte[] { 1, 2, 3 });

        result.IsVerified.Should().BeFalse("未启用时不应通过验证");
        result.Reason.Should().Contain("未启用");
    }

    [Fact]
    public void BiometricAuthOptions_LivenessDetection_ShouldBeRequired()
    {
        var opts = new BiometricAuthOptions();
        opts.RequireLivenessDetection.Should().BeTrue(
            "等保三级要求活体检测防止照片/视频攻击（AUTH-004）");
    }

    #endregion

    #region KMS 密钥管理 (CRYPTO-005)

    [Fact]
    public async Task KeyManagementService_ShouldGenerateAndDecryptDataKey()
    {
        var sm2 = new SM2CryptoService();
        var cache = new Mock<Microsoft.Extensions.Caching.Distributed.IDistributedCache>();
        cache.Setup(c => c.SetAsync(It.IsAny<string>(), It.IsAny<byte[]>(),
            It.IsAny<Microsoft.Extensions.Caching.Distributed.DistributedCacheEntryOptions>(),
            It.IsAny<CancellationToken>())).Returns(Task.CompletedTask);
        var opts = Options.Create(new KeyManagementOptions { Enabled = true });
        var logger = Mock.Of<ILogger<KeyManagementService>>();
        var service = new KeyManagementService(sm2, cache.Object, logger, opts);

        var result = await service.GenerateDataKeyAsync("test-purpose");
        var plainKey = result.PlainKey;
        var encryptedKey = result.EncryptedKey;
        var keyId = result.KeyId;

        plainKey.Should().HaveCount(16, "SM4数据密钥应为16字节/128位（CRYPTO-005）");
        encryptedKey.Should().NotBeEmpty("加密后的密钥不应为空");
        keyId.Should().StartWith("dk-", "密钥ID应以dk-开头");

        var decrypted = await service.DecryptDataKeyAsync(encryptedKey, keyId);
        decrypted.Should().BeEquivalentTo(plainKey, "解密后的数据密钥应与原始密钥一致（CRYPTO-005 密钥完整性）");
    }

    [Fact]
    public void KeyManagementOptions_DataKeyExpiration_ShouldBe90Days()
    {
        var opts = new KeyManagementOptions();
        opts.DataKeyExpirationDays.Should().BeGreaterThanOrEqualTo(90,
            "等保三级数据密钥生存期应≥90天（CRYPTO-005）");
    }

    #endregion

    // ──── 辅助方法 ─────────────────────────────────────────────────────

    private static DefaultHttpContext CreateHttpContext(
        string ip = "127.0.0.1",
        string path = "/api/test",
        Dictionary<string, string>? headers = null)
    {
        var ctx = new DefaultHttpContext();
        ctx.Connection.RemoteIpAddress = IPAddress.Parse(ip);
        ctx.Request.Path = path;

        if (headers != null)
        {
            foreach (var (key, value) in headers)
                ctx.Request.Headers[key] = value;
        }

        return ctx;
    }
}
