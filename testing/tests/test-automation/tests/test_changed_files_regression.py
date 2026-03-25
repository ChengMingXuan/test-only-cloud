import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


def read_repo_file(*parts: str) -> str:
    path = REPO_ROOT.joinpath(*parts)
    assert path.exists(), f"文件不存在: {path}"
    return path.read_text(encoding="utf-8")


def test_appsettings_should_not_contain_deprecated_default_secrets():
    config_files = [
        path
        for path in REPO_ROOT.glob("JGSY.AGI.*/appsettings.json")
        if path.is_file()
    ]
    template_file = REPO_ROOT / "deploy" / "configs" / "templates" / "appsettings.Production.template.json"
    if template_file.exists():
        config_files.append(template_file)

    assert config_files, "应至少找到一个配置文件"

    forbidden = ["P@ssw0rd", "jgsy_redis_2024", "jgsy_rabbitmq_2024"]
    for config_file in config_files:
        content = config_file.read_text(encoding="utf-8")
        for secret in forbidden:
            assert secret not in content, f"{config_file} 仍包含默认密钥 {secret}"


def test_gateway_program_should_enforce_cors_and_https_metadata():
    content = read_repo_file("JGSY.AGI.Gateway", "Program.cs")

    assert "filterLocalhostOrigins" in content
    assert "origins.Where(o => !o.Contains(\"localhost\", StringComparison.OrdinalIgnoreCase)).ToArray()" in content
    assert "必须显式配置 Cors:AllowedOrigins 或 CORS_ALLOWED_ORIGINS，禁止使用 localhost 回退默认值" in content
    assert "options.RequireHttpsMetadata = configuration.GetValue<bool>(\"SecuritySwitches:RequireHttpsMetadata\")" in content


def test_audit_middleware_should_treat_download_as_export_and_sensitive():
    content = read_repo_file("JGSY.AGI.Common.Auth", "Security", "Audit", "AuditMiddleware.cs")

    assert 'if (path.Contains("/download", StringComparison.OrdinalIgnoreCase))' in content
    assert "return AuditAction.Export;" in content
    assert "var isSensitive = IsSensitivePath(path) || action == AuditAction.Export;" in content


def test_real_name_auth_service_should_use_configured_key_instead_of_hardcoded_secret():
    content = read_repo_file("JGSY.AGI.Identity", "User", "Business", "RealNameAuthService.cs")

    assert 'configuration["Security:RealNameAuth:EncryptionKey"]' in content
    assert "Convert.FromBase64String(keyString)" in content
    assert "if (_encryptionKey.Length != 32)" in content
    assert "JGSY_AGI_REALNAME_AUTH_KEY_2024!" not in content


def test_wallet_service_should_encrypt_bank_account_before_write():
    content = read_repo_file("JGSY.AGI.Account", "Service", "WalletService.cs")

    assert "ISensitiveDataEncryptionService?" in content
    assert "AccountInfo = _encryption != null ? _encryption.Encrypt(bankAccount) : bankAccount" in content


def test_trade_settlement_saga_should_enforce_tax_rate_and_idempotency():
    content = read_repo_file("JGSY.AGI.EnergyServices.Trading", "Modules", "ElecTrade", "Services", "TradeSettlementSagaService.cs")

    assert 'configuration.GetValue<decimal?>("ElecTrade:Settlement:TaxRate")' in content
    assert "必须配置 ElecTrade:Settlement:TaxRate" in content
    assert "if (_taxRate < 0 || _taxRate > 1)" in content
    assert 'if (existing.Status == "processing")' in content
    assert "[AUDIT][DEGRADED]" in content
    assert 'GetValue<decimal>("ElecTrade:Settlement:TaxRate", 0.13m)' not in content


def test_orchestrator_should_use_health_precheck_beijing_time_and_timeout():
    content = read_repo_file("JGSY.AGI.EnergyCore.Orchestrator", "Business", "SehsDispatchOrchestrator.cs")

    assert 'CheckSubsystemHealthAsync("pvessc"' in content
    assert 'CheckSubsystemHealthAsync("vpp"' in content
    assert "CancellationTokenSource(TimeSpan.FromSeconds(30))" in content
    assert "Task.WhenAll(pvesscTask, vppTask, mgTask).WaitAsync(cts.Token)" in content
    assert 'TimeZoneInfo.FindSystemTimeZoneById("Asia/Shanghai")' in content
    assert "if (!pvesscHealthy && !vppHealthy && !mgHealthy)" in content


def test_vpp_capability_level_should_promote_carbon_trade_to_l1():
    content = read_repo_file("JGSY.AGI.EnergyCore.VPP", "Business", "VppService.cs")

    assert "if (gridDispatch || carbonTrade) return 1;" in content
    assert "if (elecTrade && gridDispatch) return 2;" in content
    assert "if (carbonTrade && aiOptimize && elecTrade && gridDispatch) return 3;" in content


def test_role_inheritance_batch_delete_should_use_any_ids_statement():
    content = read_repo_file("JGSY.AGI.Permission", "Business", "RoleInheritanceService.cs")

    assert "WHERE id = ANY(@Ids) AND tenant_id = @TenantId AND delete_at IS NULL" in content
    assert len(re.findall(r"BatchDeleteInheritanceAsync", content)) == 1


def test_pvessc_soh_service_should_mark_offline_devices():
    service_content = read_repo_file("JGSY.AGI.EnergyCore.PVESSC", "Business", "PvesscSohService.cs")
    dto_content = read_repo_file("JGSY.AGI.EnergyCore.PVESSC", "Models", "PvesscSohDtos.cs")

    assert "private const int HeartbeatTimeoutMinutes = 10;" in service_content
    assert "TotalMinutes > HeartbeatTimeoutMinutes" in service_content
    assert "IsOffline = isOffline" in service_content
    assert "public bool IsOffline { get; set; }" in dto_content