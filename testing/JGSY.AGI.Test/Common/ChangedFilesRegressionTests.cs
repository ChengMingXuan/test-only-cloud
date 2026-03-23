using System.Text.RegularExpressions;
using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.Common;

/// <summary>
/// 当前未提交改动的源码级回归测试。
/// 仅验证本轮修复承诺的关键行为，避免业务代码回退时无感失效。
/// </summary>
public class ChangedFilesRegressionTests
{
    private static readonly string RepoRoot = FindRepoRoot();

    [Fact]
    public void AppSettings_ShouldNotContainDeprecatedDefaultSecrets()
    {
        var configFiles = Directory
            .GetDirectories(RepoRoot, "JGSY.AGI.*", SearchOption.TopDirectoryOnly)
            .Select(dir => Path.Combine(dir, "appsettings.json"))
            .Where(File.Exists)
            .Append(Path.Combine(RepoRoot, "docker", "config", "templates", "appsettings.Production.template.json"))
            .ToList();

        configFiles.Should().NotBeEmpty("仓库中应存在待验证的配置文件");

        var forbiddenSecrets = new[]
        {
            "P@ssw0rd",
            "jgsy_redis_2024",
            "jgsy_rabbitmq_2024"
        };

        foreach (var file in configFiles)
        {
            var content = File.ReadAllText(file);
            foreach (var secret in forbiddenSecrets)
            {
                content.Should().NotContain(secret, $"{Path.GetFileName(file)} 不应再保留默认密钥 {secret}");
            }
        }
    }

    [Fact]
    public void GatewayProgram_ShouldEnforceCorsAndHttpsMetadata()
    {
        var content = ReadRepoFile("JGSY.AGI.Gateway", "Program.cs");

        content.Should().Contain("var nonLocalhostOrigins = origins.Where(o => !o.Contains(\"localhost\", StringComparison.OrdinalIgnoreCase)).ToArray();");
        content.Should().Contain("throw new InvalidOperationException(\"必须显式配置 Cors:AllowedOrigins 或 CORS_ALLOWED_ORIGINS，禁止使用 localhost 回退默认值\")");
        content.Should().Contain("SecuritySwitches:RequireHttpsMetadata");
    }

    [Fact]
    public void AuditMiddleware_ShouldTreatDownloadAsSensitiveExport()
    {
        var content = ReadRepoFile("JGSY.AGI.Common.Auth", "Security", "Audit", "AuditMiddleware.cs");

        content.Should().Contain("if (path.Contains(\"/download\", StringComparison.OrdinalIgnoreCase))");
        content.Should().Contain("return AuditAction.Export;");
        content.Should().Contain("var isSensitive = IsSensitivePath(path) || action == AuditAction.Export;");
    }

    [Fact]
    public void RealNameAuthService_ShouldLoadConfiguredEncryptionKey()
    {
        var content = ReadRepoFile("JGSY.AGI.Identity", "User", "Business", "RealNameAuthService.cs");

        content.Should().Contain("configuration[\"Security:RealNameAuth:EncryptionKey\"]");
        content.Should().Contain("Convert.FromBase64String(keyString)");
        content.Should().Contain("if (_encryptionKey.Length != 32)");
        content.Should().NotContain("JGSY_AGI_REALNAME_AUTH_KEY_2024!");
    }

    [Fact]
    public void WalletService_ShouldEncryptBankAccountBeforePersistence()
    {
        var content = ReadRepoFile("JGSY.AGI.Account", "Service", "WalletService.cs");

        content.Should().Contain("ISensitiveDataEncryptionService?");
        content.Should().Contain("AccountInfo = _encryption != null ? _encryption.Encrypt(bankAccount) : bankAccount");
    }

    [Fact]
    public void TradeSettlementSagaService_ShouldRequireTaxRate_AndProtectIdempotency()
    {
        var content = ReadRepoFile("JGSY.AGI.EnergyServices.Trading", "Modules", "ElecTrade", "Services", "TradeSettlementSagaService.cs");

        content.Should().Contain("configuration.GetValue<decimal?>(\"ElecTrade:Settlement:TaxRate\")");
        content.Should().Contain("必须配置 ElecTrade:Settlement:TaxRate");
        content.Should().Contain("if (_taxRate < 0 || _taxRate > 1)");
        content.Should().Contain("if (existing.Status == \"processing\")");
        content.Should().Contain("[AUDIT][DEGRADED]");
        content.Should().NotContain("GetValue<decimal>(\"ElecTrade:Settlement:TaxRate\", 0.13m)");
    }

    [Fact]
    public void Orchestrator_ShouldUseHealthPrecheck_BeijingTime_AndTimeout()
    {
        var content = ReadRepoFile("JGSY.AGI.EnergyCore.Orchestrator", "Business", "SehsDispatchOrchestrator.cs");

        content.Should().Contain("CheckSubsystemHealthAsync(\"pvessc\"");
        content.Should().Contain("CheckSubsystemHealthAsync(\"vpp\"");
        content.Should().Contain("CancellationTokenSource(TimeSpan.FromSeconds(30))");
        content.Should().Contain("Task.WhenAll(pvesscTask, vppTask, mgTask).WaitAsync(cts.Token)");
        content.Should().Contain("TimeZoneInfo.FindSystemTimeZoneById(\"Asia/Shanghai\")");
        content.Should().Contain("if (!pvesscHealthy && !vppHealthy && !mgHealthy)");
    }

    [Theory]
    [InlineData(false, false, false, false, 0)]
    [InlineData(false, false, true, false, 1)]
    [InlineData(true, false, false, false, 1)]
    [InlineData(true, true, false, false, 2)]
    [InlineData(true, true, true, true, 3)]
    public void VppCapabilityLevel_ShouldReflectCarbonTradeUpgrade(
        bool gridDispatch,
        bool elecTrade,
        bool carbonTrade,
        bool aiOptimize,
        short expectedLevel)
    {
        var actual = global::JGSY.AGI.VPP.Business.VppService.DetectCapabilityLevel(
            gridDispatch,
            elecTrade,
            carbonTrade,
            aiOptimize);

        actual.Should().Be(expectedLevel);
    }

    [Fact]
    public void RoleInheritanceService_ShouldUseSingleBatchDeleteStatement()
    {
        var content = ReadRepoFile("JGSY.AGI.Permission", "Business", "RoleInheritanceService.cs");

        content.Should().Contain("WHERE id = ANY(@Ids) AND tenant_id = @TenantId AND delete_at IS NULL");
        Regex.Matches(content, "BatchDeleteInheritanceAsync", RegexOptions.CultureInvariant).Should().HaveCount(1);
    }

    [Fact]
    public void PvesscSohService_ShouldDetectOfflineHeartbeatAndExposeResult()
    {
        var serviceContent = ReadRepoFile("JGSY.AGI.EnergyCore.PVESSC", "Business", "PvesscSohService.cs");
        var dtoContent = ReadRepoFile("JGSY.AGI.EnergyCore.PVESSC", "Models", "PvesscSohDtos.cs");

        serviceContent.Should().Contain("private const int HeartbeatTimeoutMinutes = 10;");
        serviceContent.Should().Contain("TotalMinutes > HeartbeatTimeoutMinutes");
        serviceContent.Should().Contain("IsOffline = isOffline");
        dtoContent.Should().Contain("public bool IsOffline { get; set; }");
    }

    private static string ReadRepoFile(params string[] parts)
    {
        var path = Path.Combine(new[] { RepoRoot }.Concat(parts).ToArray());
        File.Exists(path).Should().BeTrue($"测试依赖文件应存在: {path}");
        return File.ReadAllText(path);
    }

    private static string FindRepoRoot()
    {
        var current = new DirectoryInfo(AppContext.BaseDirectory);
        while (current != null)
        {
            if (File.Exists(Path.Combine(current.FullName, "AIOPS.sln")))
            {
                return current.FullName;
            }

            current = current.Parent;
        }

        throw new InvalidOperationException("未找到仓库根目录 AIOPS.sln");
    }
}