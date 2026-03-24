"""
deployment 级别的 conftest
============================
检测 Helm Chart 目录是否存在（test-only-cloud 仓库中不包含 Helm Charts），
若不存在则自动跳过部署验证测试。
"""
import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HELM_DIR = os.path.join(PROJECT_ROOT, "helm", "jgsy-agi")
HAS_HELM = os.path.isdir(HELM_DIR)


def pytest_collection_modifyitems(config, items):
    """自动跳过 Helm 部署测试（云端 CI 无 Helm Charts）"""
    if HAS_HELM:
        return
    skip_marker = pytest.mark.skip(reason="Helm Chart 目录不存在（test-only-cloud 仓库不含部署配置）")
    for item in items:
        if "deployment" in str(item.fspath):
            item.add_marker(skip_marker)
