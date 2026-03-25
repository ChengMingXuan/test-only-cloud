"""
test-automation/tests 级别的 conftest
=====================================
检测项目源码是否可用（test-only-cloud 仓库中不包含 C# 源码），
若不可用则自动跳过需要源码的测试。
"""
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
HAS_PROJECT_SOURCE = (REPO_ROOT / "JGSY.AGI.Gateway").is_dir()

# 需要项目源码的测试文件模块名
_SOURCE_DEPENDENT_MODULES = {
    "test_changed_files_regression",
    "test_security_switches_config",
}


def pytest_collection_modifyitems(config, items):
    """自动跳过依赖项目源码的测试（云端 CI 无 C# 源码）"""
    if HAS_PROJECT_SOURCE:
        return
    skip_marker = pytest.mark.skip(reason="项目源码不可用（test-only-cloud 仓库不含 C# 源码）")
    for item in items:
        module_name = Path(item.fspath).stem
        if module_name in _SOURCE_DEPENDENT_MODULES:
            item.add_marker(skip_marker)
