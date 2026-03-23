using System.Text;
using FluentAssertions;
using JGSY.AGI.Common.Core.Crypto;
using JGSY.AGI.Common.Core.Security.Offline;
using JGSY.AGI.Common.Hosting.Security;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Moq;
using Xunit;

namespace JGSY.AGI.Test.Common.Compliance;

/// <summary>
/// 离线认证服务测试
/// 合规项：DEPLOY-009 / AUTH-007 / AUTH-008 / GB/T 36572
/// 覆盖：离线 JWT 验证、密钥缓存持久化、SM2 指令签名/验签
/// </summary>
public class OfflineAuthServiceTests : IDisposable
{
    private readonly string _keyCacheDir;
    private readonly Mock<ILogger<OfflineJwtValidatorService>> _validatorLoggerMock;
    private readonly Mock<ILogger<FileBasedKeyCache>> _keyCacheLoggerMock;
    private readonly OfflineAuthOptions _defaultOptions;

    public OfflineAuthServiceTests()
    {
        _keyCacheDir = Path.Combine(Path.GetTempPath(), $"keycache-test-{Guid.NewGuid():N}");
        _validatorLoggerMock = new Mock<ILogger<OfflineJwtValidatorService>>();
        _keyCacheLoggerMock = new Mock<ILogger<FileBasedKeyCache>>();
        _defaultOptions = new OfflineAuthOptions
        {
            KeyCachePath = _keyCacheDir,
            JwtSecretKey = "test-secret-key-for-unit-testing-minimum-32-bytes!",
            JwtIssuer = "test-issuer",
            JwtAudience = "test-audience",
        };
    }

    public void Dispose()
    {
        if (Directory.Exists(_keyCacheDir))
            Directory.Delete(_keyCacheDir, recursive: true);
    }

    #region FileBasedKeyCache 测试

    [Fact]
    public async Task KeyCache_CacheKey_应持久化到文件()
    {
        var cache = CreateKeyCache();
        var keyData = Encoding.UTF8.GetBytes("test-key-material");

        await cache.CacheKeyAsync("key-001", keyData, DateTimeOffset.UtcNow.AddDays(90));

        var files = Directory.GetFiles(_keyCacheDir, "*.key.json");
        files.Should().HaveCount(1);
    }

    [Fact]
    public async Task KeyCache_GetKey_应返回之前缓存的密钥()
    {
        var cache = CreateKeyCache();
        var keyData = Encoding.UTF8.GetBytes("my-secret-key");

        await cache.CacheKeyAsync("key-002", keyData, DateTimeOffset.UtcNow.AddDays(30));
        var retrieved = await cache.GetKeyAsync("key-002");

        retrieved.Should().NotBeNull();
        retrieved.Should().Equal(keyData);
    }

    [Fact]
    public async Task KeyCache_GetKey_不存在的KeyId_应返回null()
    {
        var cache = CreateKeyCache();

        var result = await cache.GetKeyAsync("nonexistent");

        result.Should().BeNull();
    }

    [Fact]
    public async Task KeyCache_GetAllValidKeys_应返回所有缓存密钥()
    {
        var cache = CreateKeyCache();
        await cache.CacheKeyAsync("key-a", new byte[] { 1, 2, 3 }, DateTimeOffset.UtcNow.AddDays(30));
        await cache.CacheKeyAsync("key-b", new byte[] { 4, 5, 6 }, DateTimeOffset.UtcNow.AddDays(60));

        var allKeys = await cache.GetAllValidKeysAsync();

        allKeys.Should().HaveCount(2);
    }

    [Fact]
    public async Task KeyCache_PurgeExpired_应清除过期超过7天的密钥()
    {
        var cache = CreateKeyCache();
        // 缓存一个已过期的密钥（手动写入过期文件）
        var expiredEntry = new { KeyId = "expired-key", KeyMaterial = new byte[] { 1 }, CachedAt = DateTimeOffset.UtcNow.AddDays(-100), ExpiresAt = DateTimeOffset.UtcNow.AddDays(-10) };
        var json = System.Text.Json.JsonSerializer.Serialize(expiredEntry);
        await File.WriteAllTextAsync(Path.Combine(_keyCacheDir, "expired-key.key.json"), json);

        await cache.PurgeExpiredAsync();

        File.Exists(Path.Combine(_keyCacheDir, "expired-key.key.json")).Should().BeFalse();
    }

    [Fact]
    public async Task KeyCache_文件路径应防注入_特殊字符被替换()
    {
        var cache = CreateKeyCache();

        await cache.CacheKeyAsync("../../../etc/passwd", new byte[] { 1 }, DateTimeOffset.UtcNow.AddDays(30));

        // 不应在 _keyCacheDir 之外创建文件
        var files = Directory.GetFiles(_keyCacheDir, "*.key.json");
        files.Should().HaveCount(1);
        Path.GetDirectoryName(files[0]).Should().Be(_keyCacheDir);
    }

    #endregion

    #region OfflineJwtValidatorService 测试

    [Fact]
    public void JwtValidator_有JwtSecretKey_IsOfflineValidationAvailable应为true()
    {
        var (validator, _) = CreateValidator(_defaultOptions);

        validator.IsOfflineValidationAvailable.Should().BeTrue();
    }

    [Fact]
    public void JwtValidator_无JwtSecretKey_IsOfflineValidationAvailable应为false()
    {
        var opts = new OfflineAuthOptions
        {
            KeyCachePath = _keyCacheDir,
            JwtSecretKey = string.Empty,
        };
        var (validator, _) = CreateValidator(opts);

        validator.IsOfflineValidationAvailable.Should().BeFalse();
    }

    [Fact]
    public async Task JwtValidator_ValidateToken_有效Token应返回ClaimsPrincipal()
    {
        var (validator, _) = CreateValidator(_defaultOptions);
        var token = GenerateTestJwt(_defaultOptions);

        var principal = await validator.ValidateTokenAsync(token);

        principal.Should().NotBeNull();
        principal!.Identity!.IsAuthenticated.Should().BeTrue();
    }

    [Fact]
    public async Task JwtValidator_ValidateToken_过期Token应返回null()
    {
        var (validator, _) = CreateValidator(_defaultOptions);
        var token = GenerateTestJwt(_defaultOptions, expiresInMinutes: -5);

        var principal = await validator.ValidateTokenAsync(token);

        principal.Should().BeNull();
    }

    [Fact]
    public async Task JwtValidator_ValidateToken_无效签名应返回null()
    {
        var (validator, _) = CreateValidator(_defaultOptions);
        var wrongOpts = new OfflineAuthOptions
        {
            JwtSecretKey = "completely-different-key-for-testing-wrong-signature!",
            JwtIssuer = _defaultOptions.JwtIssuer,
            JwtAudience = _defaultOptions.JwtAudience,
        };
        var token = GenerateTestJwt(wrongOpts);

        var principal = await validator.ValidateTokenAsync(token);

        principal.Should().BeNull();
    }

    [Fact]
    public async Task JwtValidator_RefreshKeyCache_应更新本地密钥缓存()
    {
        var (validator, cache) = CreateValidator(_defaultOptions);

        await validator.RefreshKeyCacheAsync();

        var key = await cache.GetKeyAsync("jwt-signing-key");
        key.Should().NotBeNull();
    }

    [Fact]
    public void JwtValidator_GetKeyCacheStatus_应返回有效状态()
    {
        var (validator, _) = CreateValidator(_defaultOptions);

        var status = validator.GetKeyCacheStatus();

        status.IsValid.Should().BeTrue();
        status.CachedKeyCount.Should().BeGreaterOrEqualTo(1);
    }

    #endregion

    #region LocalCommandSignerService 测试

    [Fact]
    public async Task CommandSigner_SignAndVerify_签名后验签应成功()
    {
        var sm2Mock = new Mock<ISM2CryptoService>();
        var fakeSignature = new byte[] { 1, 2, 3, 4, 5 };
        sm2Mock.Setup(s => s.GenerateKeyPair()).Returns((PrivateKey: new byte[] { 10 }, PublicKey: new byte[] { 20 }));
        sm2Mock.Setup(s => s.Sign(It.IsAny<byte[]>(), It.IsAny<byte[]>())).Returns(fakeSignature);
        sm2Mock.Setup(s => s.Verify(It.IsAny<byte[]>(), It.IsAny<byte[]>(), It.IsAny<byte[]>())).Returns(true);
        var logger = new Mock<ILogger<LocalCommandSignerService>>();

        var signer = new LocalCommandSignerService(sm2Mock.Object, logger.Object);
        var commandData = Encoding.UTF8.GetBytes("设备控制指令");

        var sig = await signer.SignCommandAsync("cmd-001", commandData);

        sig.Should().NotBeNull();
        sig.CommandId.Should().Be("cmd-001");
        sig.Algorithm.Should().Be("SM2");
        sig.SignatureBytes.Should().Equal(fakeSignature);

        var isValid = await signer.VerifyCommandSignatureAsync("cmd-001", commandData, sig);
        isValid.Should().BeTrue();
    }

    [Fact]
    public void CommandSigner_GetSigningKeyStatus_应返回可用状态()
    {
        var sm2Mock = new Mock<ISM2CryptoService>();
        sm2Mock.Setup(s => s.GenerateKeyPair()).Returns((PrivateKey: new byte[] { 10 }, PublicKey: new byte[] { 20 }));
        var logger = new Mock<ILogger<LocalCommandSignerService>>();

        var signer = new LocalCommandSignerService(sm2Mock.Object, logger.Object);

        var status = signer.GetSigningKeyStatus();

        status.IsAvailable.Should().BeTrue();
        status.Algorithm.Should().Be("SM2");
        status.KeyId.Should().NotBeNullOrEmpty();
    }

    #endregion

    #region OfflineAuthOptions 配置测试

    [Fact]
    public void OfflineAuthOptions_默认值_应合理()
    {
        var opts = new OfflineAuthOptions();

        opts.RefreshIntervalSeconds.Should().BeGreaterOrEqualTo(3600, "密钥刷新间隔至少 1 小时");
        opts.KeyCachePath.Should().NotBeNullOrEmpty();
    }

    #endregion

    #region 辅助方法

    private FileBasedKeyCache CreateKeyCache()
    {
        return new FileBasedKeyCache(
            Options.Create(_defaultOptions),
            _keyCacheLoggerMock.Object);
    }

    private (OfflineJwtValidatorService validator, FileBasedKeyCache cache) CreateValidator(OfflineAuthOptions opts)
    {
        var cache = new FileBasedKeyCache(Options.Create(opts), _keyCacheLoggerMock.Object);
        var validator = new OfflineJwtValidatorService(
            cache,
            Options.Create(opts),
            _validatorLoggerMock.Object);
        return (validator, cache);
    }

    private static string GenerateTestJwt(OfflineAuthOptions opts, int expiresInMinutes = 60)
    {
        var keyBytes = Encoding.UTF8.GetBytes(opts.JwtSecretKey);
        var securityKey = new Microsoft.IdentityModel.Tokens.SymmetricSecurityKey(keyBytes);
        var credentials = new Microsoft.IdentityModel.Tokens.SigningCredentials(
            securityKey, Microsoft.IdentityModel.Tokens.SecurityAlgorithms.HmacSha256);

        var claims = new[]
        {
            new System.Security.Claims.Claim(System.Security.Claims.ClaimTypes.Name, "test-user"),
            new System.Security.Claims.Claim("tenant_id", Guid.NewGuid().ToString()),
        };

        // 确保 notBefore 始终在 expires 之前
        var now = DateTime.UtcNow;
        var notBefore = expiresInMinutes > 0 ? now.AddMinutes(-1) : now.AddMinutes(expiresInMinutes - 1);
        var expires = now.AddMinutes(expiresInMinutes);

        var token = new System.IdentityModel.Tokens.Jwt.JwtSecurityToken(
            issuer: opts.JwtIssuer,
            audience: opts.JwtAudience,
            claims: claims,
            notBefore: notBefore,
            expires: expires,
            signingCredentials: credentials);

        return new System.IdentityModel.Tokens.Jwt.JwtSecurityTokenHandler().WriteToken(token);
    }

    #endregion
}
