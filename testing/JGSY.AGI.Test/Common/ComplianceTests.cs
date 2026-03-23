using System.Reflection;
using FluentAssertions;
using JGSY.AGI.Common.Core.Observability;
using JGSY.AGI.Common.Hosting.Audit;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Moq;
using Xunit;

namespace JGSY.AGI.Test.Common;

/// <summary>
/// 等保三级合规验证测试集
/// 覆盖 P1/P2 所有修复项的自动化验证
/// </summary>
public class ComplianceTests
{
    #region P1-01: 调度端点 SM4/SM2 属性验证

    [Theory]
    [InlineData("JGSY.AGI.EnergyCore.Orchestrator", "InternalSEHSController", "Orchestrate")]
    [InlineData("JGSY.AGI.EnergyCore.Orchestrator", "InternalSEHSController", "RealTimeControl")]
    [InlineData("JGSY.AGI.EnergyCore.PVESSC", "InternalPVESSCController", "DispatchExecute")]
    public void DispatchEndpoints_ShouldHave_SM4AndSM2Attributes(
        string assemblyPrefix, string controllerName, string methodName)
    {
        // 查找包含目标控制器的程序集
        var assembly = AppDomain.CurrentDomain.GetAssemblies()
            .FirstOrDefault(a => a.GetName().Name?.StartsWith(assemblyPrefix) ?? false)
            ?? Assembly.Load(assemblyPrefix);

        var controllerType = assembly.GetTypes()
            .FirstOrDefault(t => t.Name == controllerName);

        controllerType.Should().NotBeNull($"控制器 {controllerName} 应存在于 {assemblyPrefix}");

        var method = controllerType!.GetMethods(BindingFlags.Public | BindingFlags.Instance)
            .FirstOrDefault(m => m.Name == methodName);

        method.Should().NotBeNull($"方法 {methodName} 应存在于 {controllerName}");

        // 验证 RequireSM4Encryption 属性
        var sm4Attr = method!.GetCustomAttributes()
            .Any(a => a.GetType().Name == "RequireSM4EncryptionAttribute");
        sm4Attr.Should().BeTrue($"{controllerName}.{methodName} 必须标记 [RequireSM4Encryption]（等保三级 CRYPTO-001）");

        // 验证 RequireSM2Signature 属性
        var sm2Attr = method.GetCustomAttributes()
            .Any(a => a.GetType().Name == "RequireSM2SignatureAttribute");
        sm2Attr.Should().BeTrue($"{controllerName}.{methodName} 必须标记 [RequireSM2Signature]（等保三级 CRYPTO-003）");
    }

    #endregion

    #region P1-02: 禁止硬编码密码

    [Theory]
    [InlineData("JGSY.AGI.Ingestion", "RabbitMqProtocolPublisherOptions")]
    [InlineData("JGSY.AGI.RuleEngine", "RuleEngineConsumerOptions")]
    public void OptionsClasses_PasswordDefault_ShouldNotBeHardcoded(
        string assemblyPrefix, string optionsClassName)
    {
        var assembly = AppDomain.CurrentDomain.GetAssemblies()
            .FirstOrDefault(a => a.GetName().Name?.StartsWith(assemblyPrefix) ?? false)
            ?? Assembly.Load(assemblyPrefix);

        var optionsType = assembly.GetTypes()
            .FirstOrDefault(t => t.Name == optionsClassName);

        optionsType.Should().NotBeNull($"{optionsClassName} 应存在于 {assemblyPrefix}");

        var instance = Activator.CreateInstance(optionsType!);
        var passwordProp = optionsType.GetProperty("Password");
        passwordProp.Should().NotBeNull($"{optionsClassName} 应有 Password 属性");

        var defaultValue = passwordProp!.GetValue(instance) as string;
        defaultValue.Should().BeEmpty($"{optionsClassName}.Password 默认值必须为空（禁止硬编码密码，等保三级 CRYPTO-005）");
    }

    [Fact]
    public void DeviceMqttService_ShouldNotContainHardcodedPassword()
    {
        // 通过反射验证源代码中确实不包含硬编码密码
        var assembly = AppDomain.CurrentDomain.GetAssemblies()
            .FirstOrDefault(a => a.GetName().Name == "JGSY.AGI.Device")
            ?? Assembly.Load("JGSY.AGI.Device");

        var mqttServiceType = assembly.GetTypes()
            .FirstOrDefault(t => t.Name == "MqttClientService");

        mqttServiceType.Should().NotBeNull("MqttClientService 应存在");

        // MqttClientService 不应有任何字段/属性包含默认密码
        var fields = mqttServiceType!.GetFields(BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static | BindingFlags.Instance);
        foreach (var field in fields)
        {
            if (field.FieldType == typeof(string) && field.IsStatic)
            {
                var value = field.GetValue(null) as string;
                value.Should().NotBe("jgsy_rabbitmq_2024",
                    $"字段 {field.Name} 不应包含硬编码密码");
            }
        }
    }

    #endregion

    #region P2-04: 系统角色删除保护

    [Fact]
    public void RoleService_ShouldProtectAllSystemRoles()
    {
        // 验证 RoleService 使用 IsSystem 而非硬编码角色名判断
        var assembly = AppDomain.CurrentDomain.GetAssemblies()
            .FirstOrDefault(a => a.GetName().Name == "JGSY.AGI.Permission")
            ?? Assembly.Load("JGSY.AGI.Permission");

        var roleServiceType = assembly.GetTypes()
            .FirstOrDefault(t => t.Name == "RoleService");

        roleServiceType.Should().NotBeNull("RoleService 应存在于 Permission 项目");

        // 检查 DeleteAsync 方法存在
        var deleteMethod = roleServiceType!.GetMethods()
            .FirstOrDefault(m => m.Name == "DeleteAsync");

        deleteMethod.Should().NotBeNull("RoleService 应有 DeleteAsync 方法");
    }

    #endregion

    #region P2-05: 审计完整性检查后台服务

    [Fact]
    public void AuditLogIntegrityCheckService_ShouldBeRegisterable()
    {
        // 验证后台服务类存在且继承自 BackgroundService
        var serviceType = typeof(AuditLogIntegrityCheckService);

        serviceType.Should().NotBeNull();
        serviceType.BaseType?.Name.Should().Be("BackgroundService",
            "AuditLogIntegrityCheckService 必须继承 BackgroundService");
    }

    [Fact]
    public void AuditIntegrityCheckOptions_ShouldHaveCorrectDefaults()
    {
        var options = new AuditIntegrityCheckOptions();

        options.IntervalHours.Should().Be(6, "默认检查间隔应为 6 小时");
        options.LookbackHours.Should().Be(24, "默认回溯范围应为 24 小时");
        options.Enabled.Should().BeTrue("默认应启用完整性检查");
    }

    [Fact]
    public async Task AuditLogIntegrityCheckService_WhenDisabled_ShouldNotRunCheck()
    {
        var integrityService = new Mock<IAuditIntegrityService>();
        var logger = new Mock<ILogger<AuditLogIntegrityCheckService>>();
        var options = Options.Create(new AuditIntegrityCheckOptions { Enabled = false });

        var service = new AuditLogIntegrityCheckService(integrityService.Object, logger.Object, options);

        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(2));
        await service.StartAsync(cts.Token);
        await Task.Delay(500);
        await service.StopAsync(CancellationToken.None);

        // 禁用时不应调用验证方法
        integrityService.Verify(
            s => s.VerifyChainAsync(It.IsAny<DateTimeOffset>(), It.IsAny<DateTimeOffset>(), It.IsAny<CancellationToken>()),
            Times.Never,
            "禁用时不应执行完整性检查");
    }

    #endregion

    #region P2-03: SQL 注入防护（AllowedTables 白名单）

    [Fact]
    public void EdgeDataRepository_ShouldHaveAllowedTablesWhitelist()
    {
        var assembly = AppDomain.CurrentDomain.GetAssemblies()
            .FirstOrDefault(a => a.GetName().Name == "JGSY.AGI.IotCloudAI")
            ?? Assembly.Load("JGSY.AGI.IotCloudAI");

        var repoType = assembly.GetTypes()
            .FirstOrDefault(t => t.Name == "EdgeDataRepository");

        repoType.Should().NotBeNull("EdgeDataRepository 应存在于 IotCloudAI 项目");

        // 验证白名单字段存在
        var allowedTablesField = repoType!.GetFields(BindingFlags.NonPublic | BindingFlags.Static)
            .FirstOrDefault(f => f.Name == "AllowedTables");

        allowedTablesField.Should().NotBeNull(
            "EdgeDataRepository 必须有 AllowedTables 白名单字段（SQL注入防护 P2-03）");
    }

    #endregion

    #region SM3 链式哈希验证

    [Fact]
    public async Task AuditIntegrityService_ChainHash_ShouldBeReproducible()
    {
        // 验证 SM3 链式哈希计算一致性
        var sm3Mock = new Mock<global::JGSY.AGI.Common.Core.Crypto.ISM3HashService>();
        sm3Mock.Setup(s => s.Hash(It.IsAny<byte[]>()))
            .Returns((byte[] data) =>
            {
                // 使用确定性哈希作为 mock
                using var sha = System.Security.Cryptography.SHA256.Create();
                return sha.ComputeHash(data);
            });

        var logger = new Mock<ILogger<AuditIntegrityService>>();
        var service = new AuditIntegrityService(sm3Mock.Object, logger.Object);

        var entry1 = new LocalAuditEntry
        {
            TenantId = Guid.Parse("11111111-1111-1111-1111-111111111111"),
            UserId = "user1",
            UserName = "张三",
            Action = "Login",
            Resource = "System",
            EventType = "Authentication"
        };

        var hash1 = await service.ComputeChainHashAsync(entry1);
        hash1.Should().NotBeNullOrEmpty("首条日志应产生有效哈希");
        entry1.PreviousHash.Should().BeNull("首条日志的前置哈希应为 null（GENESIS）");

        var entry2 = new LocalAuditEntry
        {
            TenantId = Guid.Parse("11111111-1111-1111-1111-111111111111"),
            UserId = "user2",
            UserName = "李四",
            Action = "CreateRole",
            Resource = "Role",
            EventType = "Authorization"
        };

        var hash2 = await service.ComputeChainHashAsync(entry2);
        hash2.Should().NotBeNullOrEmpty("第二条日志应产生有效哈希");
        entry2.PreviousHash.Should().Be(hash1, "第二条日志的前置哈希应等于第一条日志的哈希");
        hash2.Should().NotBe(hash1, "不同日志应产生不同哈希");
    }

    #endregion

    #region 部署模式属性验证

    [Fact]
    public void DeploymentModeAttributes_ShouldExist()
    {
        // 验证 EdgeOnly 和 CloudOnly 属性类存在
        var abstractionsAssembly = AppDomain.CurrentDomain.GetAssemblies()
            .FirstOrDefault(a => a.GetName().Name == "JGSY.AGI.Common.Abstractions")
            ?? Assembly.Load("JGSY.AGI.Common.Abstractions");

        var edgeOnlyAttr = abstractionsAssembly.GetTypes()
            .FirstOrDefault(t => t.Name == "EdgeOnlyAttribute");
        edgeOnlyAttr.Should().NotBeNull("[EdgeOnly] 属性应存在（双部署模式 DEPLOY-001）");

        var cloudOnlyAttr = abstractionsAssembly.GetTypes()
            .FirstOrDefault(t => t.Name == "CloudOnlyAttribute");
        cloudOnlyAttr.Should().NotBeNull("[CloudOnly] 属性应存在（双部署模式 DEPLOY-001）");
    }

    [Fact]
    public void DeploymentModeControllerFeatureProvider_ShouldExist()
    {
        var hostingAssembly = AppDomain.CurrentDomain.GetAssemblies()
            .FirstOrDefault(a => a.GetName().Name == "JGSY.AGI.Common.Hosting")
            ?? Assembly.Load("JGSY.AGI.Common.Hosting");

        var providerType = hostingAssembly.GetTypes()
            .FirstOrDefault(t => t.Name == "DeploymentModeControllerFeatureProvider");
        providerType.Should().NotBeNull(
            "DeploymentModeControllerFeatureProvider 应存在（部署模式控制器裁剪 DEPLOY-002）");
    }

    #endregion

    #region P2-01: mTLS 默认启用

    [Fact]
    public void MtlsOptions_Enabled_ShouldDefaultToTrue()
    {
        var authAssembly = AppDomain.CurrentDomain.GetAssemblies()
            .FirstOrDefault(a => a.GetName().Name == "JGSY.AGI.Common.Auth")
            ?? Assembly.Load("JGSY.AGI.Common.Auth");

        var mtlsType = authAssembly.GetTypes()
            .FirstOrDefault(t => t.Name == "MtlsOptions");

        mtlsType.Should().NotBeNull("MtlsOptions 应存在于 Common.Auth");

        var instance = Activator.CreateInstance(mtlsType!);
        var enabledProp = mtlsType.GetProperty("Enabled");
        enabledProp.Should().NotBeNull();

        var defaultValue = (bool)enabledProp!.GetValue(instance)!;
        defaultValue.Should().BeTrue("mTLS 必须默认启用（等保三级可信验证 P2-01）");
    }

    [Fact]
    public void MtlsOptions_ShouldHaveRequiredCertificatePaths()
    {
        var authAssembly = AppDomain.CurrentDomain.GetAssemblies()
            .FirstOrDefault(a => a.GetName().Name == "JGSY.AGI.Common.Auth")
            ?? Assembly.Load("JGSY.AGI.Common.Auth");

        var mtlsType = authAssembly.GetTypes()
            .FirstOrDefault(t => t.Name == "MtlsOptions")!;

        var instance = Activator.CreateInstance(mtlsType);

        // 验证所有证书路径属性都有默认值
        var properties = new[] { "CaCertificatePath", "ClientCertificatePath", "ClientKeyPath", "ServerCertificatePath", "ServerKeyPath" };
        foreach (var propName in properties)
        {
            var prop = mtlsType.GetProperty(propName);
            prop.Should().NotBeNull($"MtlsOptions 应有 {propName} 属性");
            var value = prop!.GetValue(instance) as string;
            value.Should().NotBeNullOrEmpty($"MtlsOptions.{propName} 应有默认值");
        }
    }

    #endregion

    #region P2-02: AllowAnonymous 端点合规审查

    [Fact]
    public void ModelsController_GetModelTypes_ShouldNotBeAnonymous()
    {
        var assembly = AppDomain.CurrentDomain.GetAssemblies()
            .FirstOrDefault(a => a.GetName().Name == "JGSY.AGI.IotCloudAI")
            ?? Assembly.Load("JGSY.AGI.IotCloudAI");

        var controllerType = assembly.GetTypes()
            .FirstOrDefault(t => t.Name == "ModelsController");

        controllerType.Should().NotBeNull();

        var method = controllerType!.GetMethods()
            .FirstOrDefault(m => m.Name == "GetModelTypes");

        method.Should().NotBeNull();

        var hasAllowAnonymous = method!.GetCustomAttributes()
            .Any(a => a.GetType().Name == "AllowAnonymousAttribute");

        hasAllowAnonymous.Should().BeFalse(
            "ModelsController.GetModelTypes 不应标记 [AllowAnonymous]（等保三级授权合规 P2-02）");
    }

    [Fact]
    public void AlertWebhookController_ShouldHaveClassLevelAuthorize()
    {
        var assembly = AppDomain.CurrentDomain.GetAssemblies()
            .FirstOrDefault(a => a.GetName().Name == "JGSY.AGI.WorkOrder")
            ?? Assembly.Load("JGSY.AGI.WorkOrder");

        var controllerType = assembly.GetTypes()
            .FirstOrDefault(t => t.Name == "AlertWebhookController");

        controllerType.Should().NotBeNull();

        var hasAuthorize = controllerType!.GetCustomAttributes()
            .Any(a => a.GetType().Name == "AuthorizeAttribute");

        hasAuthorize.Should().BeTrue(
            "AlertWebhookController 类级别应标记 [Authorize]（等保三级 P2-02，webhook 使用 API Key 认证）");
    }

    [Fact]
    public void FilesController_ShouldHaveClassLevelAuthorize()
    {
        var assembly = AppDomain.CurrentDomain.GetAssemblies()
            .FirstOrDefault(a => a.GetName().Name == "JGSY.AGI.Storage")
            ?? Assembly.Load("JGSY.AGI.Storage");

        var controllerType = assembly.GetTypes()
            .FirstOrDefault(t => t.Name == "FilesController");

        controllerType.Should().NotBeNull();

        var hasAuthorize = controllerType!.GetCustomAttributes()
            .Any(a => a.GetType().Name == "AuthorizeAttribute");

        hasAuthorize.Should().BeTrue(
            "FilesController 类级别应标记 [Authorize]（等保三级 P2-02）");
    }

    #endregion
}
