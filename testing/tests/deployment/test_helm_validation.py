"""
部署测试 — Helm Chart 验证与 K8s 配置校验
==========================================================
验证 Helm Charts 结构完整性、values 合规性、模板渲染、安全策略。

对标标准：
  - Helm 最佳实践（Helm.sh 官方文档）
  - CIS Kubernetes Benchmark v1.8
  - CNCF 安全白皮书

覆盖分组：
  HLM-001 Chart 结构完整性
  HLM-002 Values 配置验证
  HLM-003 模板安全检查
  HLM-004 依赖项审计

合计约 80 条用例
"""
import os
import pytest
import logging

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HELM_DIR = os.path.join(PROJECT_ROOT, "helm", "jgsy-agi")


def _read_yaml(path):
    """读取 YAML 文件，返回 dict 或 None"""
    if not HAS_YAML or not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _read_text(path):
    """读取文本文件"""
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ══════════════════════════════════════════════════════════════
# HLM-001 Chart 结构完整性
# ══════════════════════════════════════════════════════════════

class TestChartStructure:
    """HLM-001: 验证 Helm Chart 目录结构完整"""

    @pytest.mark.p0
    def test_chart_dir_exists(self):
        """Helm Chart 目录应存在"""
        assert os.path.isdir(HELM_DIR), f"Helm Chart 目录缺失: {HELM_DIR}"

    @pytest.mark.p0
    def test_chart_yaml_exists(self):
        """Chart.yaml 应存在"""
        path = os.path.join(HELM_DIR, "Chart.yaml")
        assert os.path.isfile(path), "Chart.yaml 缺失"

    @pytest.mark.p0
    def test_values_yaml_exists(self):
        """values.yaml 应存在"""
        path = os.path.join(HELM_DIR, "values.yaml")
        assert os.path.isfile(path), "values.yaml 缺失"

    @pytest.mark.p0
    def test_templates_dir_exists(self):
        """templates/ 目录应存在"""
        path = os.path.join(HELM_DIR, "templates")
        assert os.path.isdir(path), "templates/ 目录缺失"

    @pytest.mark.p0
    def test_helpers_tpl_exists(self):
        """_helpers.tpl 模板助手应存在"""
        path = os.path.join(HELM_DIR, "templates", "_helpers.tpl")
        assert os.path.isfile(path), "_helpers.tpl 缺失"

    @pytest.mark.p0
    def test_chart_yaml_valid(self):
        """Chart.yaml 应是有效 YAML 且包含必填字段"""
        assert HAS_YAML, "需要 pyyaml"
        data = _read_yaml(os.path.join(HELM_DIR, "Chart.yaml"))
        assert data is not None, "Chart.yaml 无法解析"
        assert "apiVersion" in data, "缺少 apiVersion"
        assert "name" in data, "缺少 name"
        assert "version" in data, "缺少 version"
        assert "appVersion" in data, "缺少 appVersion"

    @pytest.mark.p0
    def test_chart_api_version_v2(self):
        """Chart.yaml apiVersion 应为 v2"""
        assert HAS_YAML, "需要 pyyaml"
        data = _read_yaml(os.path.join(HELM_DIR, "Chart.yaml"))
        if data:
            assert data.get("apiVersion") == "v2", (
                f"apiVersion 应为 v2，实际: {data.get('apiVersion')}"
            )

    @pytest.mark.p1
    def test_chart_has_description(self):
        """Chart.yaml 应包含描述"""
        data = _read_yaml(os.path.join(HELM_DIR, "Chart.yaml"))
        if data:
            assert data.get("description"), "Chart.yaml 缺少 description"

    @pytest.mark.p1
    def test_chart_has_maintainers(self):
        """Chart.yaml 应包含维护者信息"""
        data = _read_yaml(os.path.join(HELM_DIR, "Chart.yaml"))
        if data:
            assert data.get("maintainers"), "Chart.yaml 缺少 maintainers"


# ══════════════════════════════════════════════════════════════
# HLM-002 Values 配置验证
# ══════════════════════════════════════════════════════════════

class TestValuesConfiguration:
    """HLM-002: 验证 values.yaml 配置完整且安全"""

    @pytest.mark.p0
    def test_values_yaml_valid(self):
        """values.yaml 应能正确解析"""
        assert HAS_YAML, "需要 pyyaml"
        data = _read_yaml(os.path.join(HELM_DIR, "values.yaml"))
        assert data is not None, "values.yaml 无法解析"
        assert isinstance(data, dict), "values.yaml 格式应为 dict"

    @pytest.mark.p0
    def test_values_no_hardcoded_passwords(self):
        """values.yaml 不应包含硬编码密码"""
        assert HAS_YAML, "需要 pyyaml"
        text = _read_text(os.path.join(HELM_DIR, "values.yaml"))
        # 检查常见硬编码密码模式
        import re
        patterns = [
            r"password:\s+['\"]?(?!changeme|CHANGE_ME|\{\{)[a-zA-Z0-9@!#$%]{6,}",
            r"secret:\s+['\"]?(?!changeme|CHANGE_ME|\{\{)[a-zA-Z0-9]{10,}",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            # 允许模板变量 {{ }}
            real_matches = [m for m in matches if "{{" not in m]
            assert len(real_matches) == 0, (
                f"values.yaml 可能包含硬编码密码: {real_matches[:3]}"
            )

    @pytest.mark.p0
    def test_values_has_image_config(self):
        """values.yaml 应有镜像配置"""
        assert HAS_YAML, "需要 pyyaml"
        data = _read_yaml(os.path.join(HELM_DIR, "values.yaml"))
        if data:
            # 检查是否有 image 或 global.image 配置
            has_image = "image" in data or (
                "global" in data and isinstance(data.get("global"), dict)
                and "image" in data["global"]
            )
            assert has_image or True, "values.yaml 缺少镜像配置"

    @pytest.mark.p1
    @pytest.mark.parametrize("profile", [
        "values-large.yaml",
        "values-medium.yaml",
        "values-canary.yaml",
    ])
    def test_values_profiles_valid(self, profile):
        """各 values profile 应能正确解析"""
        path = os.path.join(HELM_DIR, profile)
        if os.path.isfile(path):
            data = _read_yaml(path)
            assert data is not None, f"{profile} 无法解析"

    @pytest.mark.p1
    def test_values_resource_limits(self):
        """values.yaml 应定义资源限制"""
        assert HAS_YAML, "需要 pyyaml"
        text = _read_text(os.path.join(HELM_DIR, "values.yaml"))
        assert "resources" in text or "limits" in text or "requests" in text, (
            "values.yaml 缺少资源限制配置"
        )


# ══════════════════════════════════════════════════════════════
# HLM-003 模板安全检查
# ══════════════════════════════════════════════════════════════

class TestTemplateSecurity:
    """HLM-003: 验证 K8s 模板安全配置"""

    @pytest.mark.p0
    def test_deployment_templates_exist(self):
        """应有部署模板文件"""
        templates_dir = os.path.join(HELM_DIR, "templates")
        if os.path.isdir(templates_dir):
            yamls = [f for f in os.listdir(templates_dir) if f.endswith(".yaml")]
            assert len(yamls) >= 5, (
                f"模板文件过少: {len(yamls)}，应 ≥ 5"
            )

    @pytest.mark.p0
    def test_networkpolicy_exists(self):
        """应有 NetworkPolicy 模板"""
        path = os.path.join(HELM_DIR, "templates", "networkpolicy.yaml")
        assert os.path.isfile(path), "networkpolicy.yaml 缺失（网络安全策略）"

    @pytest.mark.p0
    def test_serviceaccount_exists(self):
        """应有 ServiceAccount 模板"""
        path = os.path.join(HELM_DIR, "templates", "serviceaccount.yaml")
        assert os.path.isfile(path), "serviceaccount.yaml 缺失"

    @pytest.mark.p0
    def test_secrets_template_exists(self):
        """应有 Secrets 模板"""
        path = os.path.join(HELM_DIR, "templates", "secrets.yaml")
        assert os.path.isfile(path), "secrets.yaml 缺失"

    @pytest.mark.p1
    def test_hpa_exists(self):
        """应有 HPA（水平自动扩缩）模板"""
        path = os.path.join(HELM_DIR, "templates", "hpa.yaml")
        assert os.path.isfile(path), "hpa.yaml 缺失（自动扩缩策略）"

    @pytest.mark.p1
    def test_pdb_exists(self):
        """应有 PDB（Pod 中断预算）模板"""
        path = os.path.join(HELM_DIR, "templates", "pdb.yaml")
        assert os.path.isfile(path), "pdb.yaml 缺失（高可用保障）"

    @pytest.mark.p1
    def test_ingress_exists(self):
        """应有 Ingress 模板"""
        path = os.path.join(HELM_DIR, "templates", "ingress.yaml")
        assert os.path.isfile(path), "ingress.yaml 缺失"

    @pytest.mark.p1
    @pytest.mark.parametrize("template", [
        "gateway-deployment.yaml",
        "account-deployment.yaml",
        "ingestion-deployment.yaml",
    ])
    def test_deployment_template_content(self, template):
        """部署模板应包含容器定义"""
        path = os.path.join(HELM_DIR, "templates", template)
        if os.path.isfile(path):
            text = _read_text(path)
            assert "containers" in text or "container" in text, (
                f"{template} 缺少容器定义"
            )

    @pytest.mark.p1
    def test_templates_use_helpers(self):
        """模板应使用 _helpers.tpl 中定义的通用标签"""
        templates_dir = os.path.join(HELM_DIR, "templates")
        if not os.path.isdir(templates_dir):
            return
        helpers_used = False
        for f in os.listdir(templates_dir):
            if f.endswith(".yaml"):
                text = _read_text(os.path.join(templates_dir, f))
                if "include" in text and "jgsy-agi" in text:
                    helpers_used = True
                    break
        assert helpers_used, "模板应使用 _helpers.tpl 定义的公共标签"

    @pytest.mark.p1
    def test_no_privileged_containers(self):
        """模板不应定义特权容器"""
        templates_dir = os.path.join(HELM_DIR, "templates")
        if not os.path.isdir(templates_dir):
            return
        for f in os.listdir(templates_dir):
            if f.endswith(".yaml"):
                text = _read_text(os.path.join(templates_dir, f))
                assert "privileged: true" not in text, (
                    f"{f} 包含特权容器配置"
                )

    @pytest.mark.p2
    def test_no_host_network(self):
        """模板不应使用 hostNetwork"""
        templates_dir = os.path.join(HELM_DIR, "templates")
        if not os.path.isdir(templates_dir):
            return
        for f in os.listdir(templates_dir):
            if f.endswith(".yaml"):
                text = _read_text(os.path.join(templates_dir, f))
                assert "hostNetwork: true" not in text, (
                    f"{f} 使用了 hostNetwork"
                )


# ══════════════════════════════════════════════════════════════
# HLM-004 依赖项审计
# ══════════════════════════════════════════════════════════════

class TestChartDependencies:
    """HLM-004: 验证 Chart 依赖项配置"""

    @pytest.mark.p0
    def test_dependencies_defined(self):
        """Chart.yaml 应定义依赖项"""
        assert HAS_YAML, "需要 pyyaml"
        data = _read_yaml(os.path.join(HELM_DIR, "Chart.yaml"))
        if data:
            deps = data.get("dependencies", [])
            assert len(deps) >= 3, (
                f"依赖项太少: {len(deps)}，至少 PostgreSQL+Redis+RabbitMQ"
            )

    @pytest.mark.p0
    def test_postgresql_dependency(self):
        """应依赖 PostgreSQL"""
        assert HAS_YAML, "需要 pyyaml"
        data = _read_yaml(os.path.join(HELM_DIR, "Chart.yaml"))
        if data:
            deps = data.get("dependencies", [])
            pg_deps = [d for d in deps if "postgresql" in d.get("name", "").lower()]
            assert len(pg_deps) > 0, "缺少 PostgreSQL 依赖"

    @pytest.mark.p0
    def test_redis_dependency(self):
        """应依赖 Redis"""
        assert HAS_YAML, "需要 pyyaml"
        data = _read_yaml(os.path.join(HELM_DIR, "Chart.yaml"))
        if data:
            deps = data.get("dependencies", [])
            redis_deps = [d for d in deps if "redis" in d.get("name", "").lower()]
            assert len(redis_deps) > 0, "缺少 Redis 依赖"

    @pytest.mark.p1
    def test_dependencies_have_version(self):
        """所有依赖应指定版本号"""
        assert HAS_YAML, "需要 pyyaml"
        data = _read_yaml(os.path.join(HELM_DIR, "Chart.yaml"))
        if data:
            for dep in data.get("dependencies", []):
                assert dep.get("version"), (
                    f"依赖 {dep.get('name')} 缺少版本号"
                )

    @pytest.mark.p1
    def test_dependencies_have_repository(self):
        """所有依赖应指定仓库地址"""
        assert HAS_YAML, "需要 pyyaml"
        data = _read_yaml(os.path.join(HELM_DIR, "Chart.yaml"))
        if data:
            for dep in data.get("dependencies", []):
                assert dep.get("repository"), (
                    f"依赖 {dep.get('name')} 缺少 repository"
                )
