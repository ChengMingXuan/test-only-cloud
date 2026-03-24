using System.Text.Json;
using System.Text.RegularExpressions;
using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.Common;

/// <summary>
/// SecuritySwitches 配置合规 - 集成回归测试（v2.5）
/// 验证：本地即生产、配置文件完整性、代码模式正确性、Prod 一致性
/// </summary>
public class SecuritySwitchesConfigTests
{
    private static readonly string RepoRoot = FindRepoRoot();

    /// <summary>26 个后端微服务</summary>
    private static readonly string[] Services =
    {
        "Account", "Analytics", "Blockchain", "Charging",
        "ContentPlatform", "Device", "DigitalTwin",
        "EnergyCore.MicroGrid", "EnergyCore.Orchestrator",
        "EnergyCore.PVESSC", "EnergyCore.VPP",
        "EnergyServices.Operations", "EnergyServices.Trading",
        "Gateway", "Identity", "Ingestion", "IotCloudAI",
        "Observability", "Permission", "RuleEngine",
        "Settlement", "Simulator", "Station", "Storage",
        "Tenant", "WorkOrder",
    };

    /// <summary>11 个 SecuritySwitches 标准开关</summary>
    private static readonly string[] AllSwitches =
    {
        "UseHttps", "ForceHttpsRedirection", "RequireHttpsMetadata", "HstsEnabled",
        "DbEnableSsl", "RedisEnableSsl", "RedisUseAcl",
        "Sm4Enabled", "KeyRotationEnabled", "SessionControlEnabled", "MtlsEnabled",
    };

    private static readonly string[] HttpsSwitches =
    {
        "UseHttps", "ForceHttpsRedirection", "RequireHttpsMetadata", "HstsEnabled",
    };

    // ==================== 1. 环境配置文件存在性 ====================

    [Theory]
    [MemberData(nameof(GetServices))]
    public void DevelopmentJson_ShouldNotExist(string service)
    {
        var path = Path.Combine(RepoRoot, $"JGSY.AGI.{service}", "appsettings.Development.json");
        File.Exists(path).Should().BeFalse($"{service} 不应存在 appsettings.Development.json");
    }

    [Theory]
    [MemberData(nameof(GetServices))]
    public void ProductionJson_ShouldExist(string service)
    {
        var path = Path.Combine(RepoRoot, $"JGSY.AGI.{service}", "appsettings.Production.json");
        File.Exists(path).Should().BeTrue($"{service} 应存在 appsettings.Production.json");
    }

    // ==================== 2. Prod 配置 HTTPS=true ====================

    [Theory]
    [MemberData(nameof(GetServices))]
    public void ProductionJson_HttpsSwitches_ShouldBeTrue(string service)
    {
        var path = Path.Combine(RepoRoot, $"JGSY.AGI.{service}", "appsettings.Production.json");
        var json = JsonDocument.Parse(File.ReadAllText(path));
        var ss = json.RootElement.GetProperty("SecuritySwitches");

        foreach (var sw in HttpsSwitches)
        {
            ss.GetProperty(sw).GetBoolean().Should().BeTrue($"{service} Prod: {sw} 应为 true");
        }
    }

    // ==================== 3. Security.json 基线 ====================

    [Fact]
    public void SecurityJson_ShouldContainAll11Switches()
    {
        var path = Path.Combine(RepoRoot, "JGSY.AGI.Common.Hosting", "appsettings.Security.json");
        File.Exists(path).Should().BeTrue("appsettings.Security.json 应存在");

        var json = JsonDocument.Parse(File.ReadAllText(path));
        var ss = json.RootElement.GetProperty("SecuritySwitches");

        foreach (var sw in AllSwitches)
        {
            ss.TryGetProperty(sw, out _).Should().BeTrue($"Security.json 应包含 {sw}");
        }
    }

    // ==================== 4. SecuritySwitchesOptions 类 ====================

    [Fact]
    public void SecuritySwitchesOptions_ShouldContainAll11Properties()
    {
        var content = ReadRepoFile("JGSY.AGI.Common.Auth", "Security", "SecuritySwitchesOptions.cs");

        foreach (var sw in AllSwitches)
        {
            content.Should().Contain(sw, $"SecuritySwitchesOptions 应包含属性 {sw}");
        }

        content.Should().Contain("SectionName", "应包含 SectionName 常量");
    }

    // ==================== 5. 代码模式正确性 ====================

    [Fact]
    public void JwtExtensions_ShouldUseConfigDriven_RequireHttpsMetadata()
    {
        var content = ReadRepoFile("JGSY.AGI.Common.Auth", "Authentication", "JwtAuthenticationExtensions.cs");

        content.Should().Contain("SecuritySwitches:RequireHttpsMetadata",
            "应读取 SecuritySwitches:RequireHttpsMetadata 配置");
        content.Should().NotContain("RequireHttpsMetadata = true",
            "不应硬编码 RequireHttpsMetadata = true");
    }

    [Fact]
    public void GatewayProgram_ShouldUseSecuritySwitches()
    {
        var content = ReadRepoFile("JGSY.AGI.Gateway", "Program.cs");

        content.Should().Contain("SecuritySwitches:ForceHttpsRedirection");
        content.Should().Contain("SecuritySwitches:HstsEnabled");
        content.Should().Contain("SecuritySwitches:RequireHttpsMetadata");
    }

    [Fact]
    public void GatewaySecurityHeadersMiddleware_ShouldBeConditional()
    {
        var content = ReadRepoFile("JGSY.AGI.Gateway", "Middleware", "SecurityHeadersMiddleware.cs");

        content.Should().Contain("IConfiguration", "应注入 IConfiguration");
        content.Should().Contain("HstsEnabled", "应检查 HstsEnabled 开关");
    }

    [Fact]
    public void CommonSecurityHeadersMiddleware_ShouldBeConditional()
    {
        var content = ReadRepoFile("JGSY.AGI.Common.Hosting", "Security", "SecurityHeadersMiddleware.cs");

        content.Should().Contain("IConfiguration", "应注入 IConfiguration");
        content.Should().Contain("HstsEnabled", "应检查 HstsEnabled 开关");
    }

    [Fact]
    public void SecurityServiceExtensions_ShouldRegisterOptions()
    {
        var content = ReadRepoFile("JGSY.AGI.Common.Hosting", "Extensions", "SecurityServiceExtensions.cs");

        content.Should().Contain("SecuritySwitchesOptions", "应注册 SecuritySwitchesOptions");
    }

    // ==================== 6. 无硬编码密码 ====================

    [Theory]
    [MemberData(nameof(GetServices))]
    public void AppSettings_ShouldNotContainWeakPasswords(string service)
    {
        var path = Path.Combine(RepoRoot, $"JGSY.AGI.{service}", "appsettings.json");
        if (!File.Exists(path)) return;

        var content = File.ReadAllText(path);
        var forbidden = new[] { "P@ssw0rd", "jgsy_redis_2024", "jgsy_rabbitmq_2024" };

        foreach (var secret in forbidden)
        {
            content.Should().NotContain(secret, $"{service}/appsettings.json 不应包含弱密码 {secret}");
        }
    }

    // ==================== 7. Prod Swagger 配置 ====================

    [Theory]
    [MemberData(nameof(GetServices))]
    public void ProductionJson_SwaggerDisabled(string service)
    {
        var path = Path.Combine(RepoRoot, $"JGSY.AGI.{service}", "appsettings.Production.json");
        var json = JsonDocument.Parse(File.ReadAllText(path));

        json.RootElement.GetProperty("Swagger").GetProperty("Enabled").GetBoolean()
            .Should().BeFalse($"{service} Prod: Swagger.Enabled 应为 false");
    }

    // ==================== Helpers ====================

    public static IEnumerable<object[]> GetServices()
        => Services.Select(s => new object[] { s });

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
                return current.FullName;
            current = current.Parent;
        }
        throw new InvalidOperationException("未找到仓库根目录 AIOPS.sln");
    }
}
