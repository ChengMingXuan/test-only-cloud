using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.Common;

/// <summary>
/// V3.2.0 合并能源服务、安全增强、证书轮转等关键特性的源码级集成回归测试。
/// 验证：Operations 合并(EnergyEff+MultiEnergy+SafeControl)、Trading 合并(ElecTrade+CarbonTrade+DemandResp)、
/// 安全中间件、敏感数据加密接口、证书轮转、绿电碳联动、权限迁移脚本、EventSourcing 清理。
/// </summary>
public class V320ConsolidatedTests
{
    private static readonly string RepoRoot = FindRepoRoot();

    #region Operations 合并验证

    [Fact]
    public void OperationsProgram_ShouldRegisterEnergyEffModule()
    {
        var content = ReadRepoFile("JGSY.AGI.EnergyServices.Operations", "Program.cs");

        content.Should().Contain("MeterConfig", "Operations 应注册 EnergyEff 的 MeterConfig");
        content.Should().Contain("Consumption", "Operations 应注册 EnergyEff 的 Consumption");
        content.Should().Contain("EfficiencyIndex", "Operations 应注册 EnergyEff 的 EfficiencyIndex");
    }

    [Fact]
    public void OperationsProgram_ShouldRegisterMultiEnergyModule()
    {
        var content = ReadRepoFile("JGSY.AGI.EnergyServices.Operations", "Program.cs");

        content.Should().Contain("EnergyBalance", "Operations 应注册 MultiEnergy 的 EnergyBalance");
        content.Should().Contain("ConversionDevice", "Operations 应注册 MultiEnergy 的 ConversionDevice");
        content.Should().Contain("SchedulePlan", "Operations 应注册 MultiEnergy 的 SchedulePlan");
    }

    [Fact]
    public void OperationsProgram_ShouldRegisterSafeControlModule()
    {
        var content = ReadRepoFile("JGSY.AGI.EnergyServices.Operations", "Program.cs");

        content.Should().Contain("SafetyEvent", "Operations 应注册 SafeControl 的 SafetyEvent");
        content.Should().Contain("RiskAssessment", "Operations 应注册 SafeControl 的 RiskAssessment");
        content.Should().Contain("EmergencyPlan", "Operations 应注册 SafeControl 的 EmergencyPlan");
    }

    #endregion

    #region Trading 合并验证

    [Fact]
    public void TradingProgram_ShouldRegisterElecTradeModule()
    {
        var content = ReadRepoFile("JGSY.AGI.EnergyServices.Trading", "Program.cs");

        content.Should().Contain("TradingOrder", "Trading 应注册 ElecTrade 的 TradingOrder");
        content.Should().Contain("Settlement", "Trading 应注册 ElecTrade 的 Settlement");
        content.Should().Contain("MarketConfig", "Trading 应注册 ElecTrade 的 MarketConfig");
    }

    [Fact]
    public void TradingProgram_ShouldRegisterCarbonTradeModule()
    {
        var content = ReadRepoFile("JGSY.AGI.EnergyServices.Trading", "Program.cs");

        content.Should().Contain("EmissionConfig", "Trading 应注册 CarbonTrade 的 EmissionConfig");
        content.Should().Contain("EmissionRecord", "Trading 应注册 CarbonTrade 的 EmissionRecord");
        content.Should().Contain("Fulfillment", "Trading 应注册 CarbonTrade 的 Fulfillment");
    }

    [Fact]
    public void TradingProgram_ShouldRegisterDemandRespModule()
    {
        var content = ReadRepoFile("JGSY.AGI.EnergyServices.Trading", "Program.cs");

        content.Should().Contain("DRInstruction", "Trading 应注册 DemandResp 的 DRInstruction");
        content.Should().Contain("DRParticipation", "Trading 应注册 DemandResp 的 DRParticipation");
        content.Should().Contain("DRExecution", "Trading 应注册 DemandResp 的 DRExecution");
    }

    #endregion

    #region 安全增强验证

    [Fact]
    public void ISensitiveDataEncryptionService_ShouldDefineCoreEncryptionMethods()
    {
        var content = ReadRepoFile("JGSY.AGI.Common.Abstractions", "Security", "ISensitiveDataEncryptionService.cs");

        content.Should().Contain("string Encrypt(string plainText)");
        content.Should().Contain("string Decrypt(string cipherText)");
        content.Should().Contain("string Hash(string plainText)");
        content.Should().Contain("string Mask(string plainText, SensitiveDataType dataType)");
    }

    [Fact]
    public void ISensitiveDataEncryptionService_ShouldDefineSensitiveDataTypes()
    {
        var content = ReadRepoFile("JGSY.AGI.Common.Abstractions", "Security", "ISensitiveDataEncryptionService.cs");

        content.Should().Contain("Phone");
        content.Should().Contain("Email");
        content.Should().Contain("BankAccount");
        content.Should().Contain("IdCard");
    }

    [Fact]
    public void GatewaySecurityHeadersMiddleware_ShouldSetAllRequiredHeaders()
    {
        var content = ReadRepoFile("JGSY.AGI.Gateway", "Middleware", "SecurityHeadersMiddleware.cs");

        content.Should().Contain("X-Content-Type-Options", "应包含 nosniff 头");
        content.Should().Contain("X-Frame-Options", "应包含 X-Frame-Options");
        content.Should().Contain("Referrer-Policy", "应包含 Referrer-Policy");
        content.Should().Contain("Permissions-Policy", "应包含 Permissions-Policy");
        content.Should().Contain("Content-Security-Policy", "应包含 CSP");
    }

    [Fact]
    public void HostingSecurityHeadersMiddleware_ShouldExist()
    {
        var content = ReadRepoFile("JGSY.AGI.Common.Hosting", "Security", "SecurityHeadersMiddleware.cs");

        content.Should().Contain("SecurityHeadersMiddleware");
        content.Should().Contain("InvokeAsync");
    }

    #endregion

    #region 证书轮转验证

    [Fact]
    public void CertificateRotationController_ShouldHaveStatusEndpoint()
    {
        var content = ReadRepoFile("JGSY.AGI.Observability", "Monitor", "Api", "CertificateRotationController.cs");

        content.Should().Contain("[Route(\"api/monitor/service-mesh/certificate-rotation\")]");
        content.Should().Contain("GetStatus");
        content.Should().Contain("[Authorize]");
    }

    [Fact]
    public void DaprCertificateRotationService_ShouldImplementBackgroundService()
    {
        var content = ReadRepoFile("JGSY.AGI.Common.Auth", "Security", "DaprCertificateRotationService.cs");

        content.Should().Contain("BackgroundService");
        content.Should().Contain("IManagedCertificateRotationService");
    }

    #endregion

    #region 绿电碳联动验证

    [Fact]
    public void GreenPowerLinkageService_ShouldHaveCalculateCarbonOffsetAsync()
    {
        var content = ReadRepoFile("JGSY.AGI.EnergyServices.Trading", "Modules", "ElecTrade", "Business", "GreenPowerLinkageService.cs");

        content.Should().Contain("CalculateCarbonOffsetAsync");
        content.Should().Contain("GreenPowerCarbonOffsetResult");
        content.Should().Contain("IGreenPowerLinkageService");
    }

    [Fact]
    public void GreenPowerLinkageService_ShouldUseCarbonEmissionFactor()
    {
        var content = ReadRepoFile("JGSY.AGI.EnergyServices.Trading", "Modules", "ElecTrade", "Business", "GreenPowerLinkageService.cs");

        content.Should().Contain("0.5810", "应使用中国电网平均排放替代因子 0.5810 tCO2/MWh");
    }

    #endregion

    #region 权限迁移脚本验证

    [Theory]
    [InlineData("009_iotcloudai_chat_permissions.sql", "iotcloudai")]
    [InlineData("010_blockchain_failover_permissions.sql", "blockchain")]
    [InlineData("011_v31_security_permissions.sql", "security")]
    [InlineData("012_three_role_separation_permissions.sql", "three_role")]
    public void PermissionMigration_ShouldExistAndBeIdempotent(string fileName, string keyword)
    {
        var content = ReadRepoFile("JGSY.AGI.Permission", "Data", "Migrations", fileName);

        content.Should().Contain("ON CONFLICT DO NOTHING", $"迁移脚本 {fileName} 应是幂等的");
        content.Should().Contain(keyword, $"迁移脚本 {fileName} 应包含相关权限码");
    }

    [Fact]
    public void PermissionMigration012_ShouldDefineThreeRoleSeparation()
    {
        var content = ReadRepoFile("JGSY.AGI.Permission", "Data", "Migrations", "012_three_role_separation_permissions.sql");

        content.Should().Contain("CREATE SCHEMA IF NOT EXISTS permission");
    }

    #endregion

    #region EventSourcing 清理验证

    [Fact]
    public void ChargingOrderEventSourcingController_ShouldNotExist()
    {
        var searchDir = Path.Combine(RepoRoot, "JGSY.AGI.Charging");
        if (!Directory.Exists(searchDir))
        {
            // 如果 Charging 目录不存在，测试自动通过
            return;
        }

        var files = Directory.GetFiles(searchDir, "ChargingOrderEventSourcingController.cs", SearchOption.AllDirectories);
        files.Should().BeEmpty("EventSourcing 控制器应已在 V3.2.0 中移除");
    }

    [Fact]
    public void ChargingProject_ShouldNotReferenceEventSourcing()
    {
        var projectDir = Path.Combine(RepoRoot, "JGSY.AGI.Charging");
        if (!Directory.Exists(projectDir))
            return;

        var csFiles = Directory.GetFiles(projectDir, "*.cs", SearchOption.AllDirectories);
        foreach (var file in csFiles)
        {
            var content = File.ReadAllText(file);
            content.Should().NotContain("EventSourcing",
                $"文件 {Path.GetFileName(file)} 不应包含 EventSourcing 引用");
        }
    }

    #endregion

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
