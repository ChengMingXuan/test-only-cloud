#!/usr/bin/env python3
"""
pytest 用例数量统计汇总脚本
============================
统计 tests/ 目录下所有 test_*.py 文件的用例数量。

包含三种统计模式：
  1. 静态统计：统计 def test_ 函数数量（快速，不含参数化展开）
  2. 参数化统计：解析 @pytest.mark.parametrize 展开数量（准确）
  3. pytest --collect-only 统计：最精确但需要运行时

用法：
  python count_tests.py                   # 静态统计
  python count_tests.py --parametrized    # 含参数化展开统计
  python count_tests.py --collect         # 调用 pytest --collect-only
"""
import sys
import os
import re
import ast
from pathlib import Path

TESTS_ROOT = Path(__file__).parent


def count_static(tests_root: Path) -> dict:
    """
    静态统计：直接计数 def test_ 函数，不展开参数化。
    返回每个文件的用例数 + 总数。
    """
    results = {}
    total = 0
    test_files = sorted(tests_root.rglob("test_*.py"))
    for f in test_files:
        # 跳过 __pycache__ 和 node_modules
        if "__pycache__" in str(f) or "node_modules" in str(f):
            continue
        count = sum(
            1 for line in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            if re.match(r"\s+def test_", line)
        )
        if count > 0:
            rel = str(f.relative_to(tests_root))
            results[rel] = count
            total += count
    return {"files": results, "total": total}


def count_parametrized(tests_root: Path) -> dict:
    """
    参数化展开统计：解析 @pytest.mark.parametrize 标注。
    每个 test_ 方法的用例数 = 所有参数列表长度之积（多层 parametrize 相乘）。
    """
    results = {}
    grand_total = 0
    parametrized_total = 0
    static_total = 0

    test_files = sorted(tests_root.rglob("test_*.py"))
    for filepath in test_files:
        if "__pycache__" in str(filepath) or "node_modules" in str(filepath):
            continue
        try:
            source = filepath.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source)
        except SyntaxError:
            continue

        file_cases = 0
        file_parametrized = 0
        file_static = 0

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.name.startswith("test_"):
                continue

            # 找出该函数上所有 parametrize 装饰器
            param_counts = []
            for decorator in node.decorator_list:
                n = _extract_parametrize_count(decorator)
                if n is not None:
                    param_counts.append(n)

            if param_counts:
                expanded = 1
                for c in param_counts:
                    expanded *= c
                file_cases += expanded
                file_parametrized += expanded
            else:
                file_cases += 1
                file_static += 1

        if file_cases > 0:
            rel = str(filepath.relative_to(tests_root))
            results[rel] = {
                "total": file_cases,
                "parametrized": file_parametrized,
                "plain": file_static,
            }
            grand_total += file_cases
            parametrized_total += file_parametrized
            static_total += file_static

    return {
        "files": results,
        "total": grand_total,
        "parametrized_cases": parametrized_total,
        "plain_cases": static_total,
    }


def _extract_parametrize_count(decorator) -> int | None:
    """从 AST 装饰器节点提取 parametrize 参数个数"""
    # @pytest.mark.parametrize("name", [...])
    # @pytest.mark.parametrize("name", CONSTANT)  ← 模块级变量，尝试 eval
    if isinstance(decorator, ast.Call):
        func = decorator.func
        # pytest.mark.parametrize
        if _is_parametrize_call(func):
            args = decorator.args
            if len(args) >= 2:
                arg2 = args[1]
                if isinstance(arg2, (ast.List, ast.Tuple)):
                    return len(arg2.elts)
                # 引用模块级变量（如 ALL_API_PATHS）
                # 无法在 AST 层面直接求值，返回 None 让调用方单独处理
                return None
    return None


def _is_parametrize_call(func) -> bool:
    """检查函数调用是否是 pytest.mark.parametrize"""
    if isinstance(func, ast.Attribute):
        if func.attr == "parametrize":
            parent = func.value
            if isinstance(parent, ast.Attribute) and parent.attr == "mark":
                return True
    return False


def _count_file_with_import(filepath: Path, tests_root: Path) -> int:
    """
    对含模块级变量的文件，通过真正 import 来获取参数化数量。
    """
    import importlib.util
    # 将 tests_root 加入 sys.path
    sys_path_backup = sys.path.copy()
    sys.path.insert(0, str(tests_root.parent))
    sys.path.insert(0, str(tests_root))
    try:
        spec = importlib.util.spec_from_file_location("_tmp_mod", filepath)
        if spec is None:
            return 0
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
        count = 0
        for name in dir(mod):
            if name.startswith("test_"):
                fn = getattr(mod, name)
                marks = getattr(fn, "pytestmark", [])
                for m in marks:
                    if m.name == "parametrize" and m.args:
                        params = m.args[1] if len(m.args) > 1 else []
                        count_this = len(list(params))
                        count = max(count, count_this)
        return count
    except Exception:
        return 0
    finally:
        sys.path[:] = sys_path_backup


def collect_via_pytest(tests_root: Path) -> int:
    """
    通过 pytest --collect-only 精确统计（需要pytest已安装）。
    """
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q",
         "--ignore=selenium-tests", "--ignore=test-automation",
         str(tests_root)],
        capture_output=True, text=True, cwd=str(tests_root.parent)
    )
    # 最后一行格式: "X tests collected in Y.Zs"
    last_lines = (result.stdout + result.stderr).strip().splitlines()
    for line in reversed(last_lines):
        m = re.search(r"(\d+)\s+test[s]?\s+collected", line)
        if m:
            return int(m.group(1))
    return -1


def print_report(mode: str = "static"):
    print("=" * 70)
    print(f"  pytest 测试用例数量统计  [{mode.upper()} 模式]")
    print(f"  目标：49,755 条（3,300 API × 15 场景 + 其他文件）")
    print("=" * 70)

    if mode == "collect":
        n = collect_via_pytest(TESTS_ROOT)
        if n >= 0:
            pct = n / 49755 * 100
            print(f"\n  pytest --collect-only 统计：{n:,} 条")
            print(f"  达标率：{pct:.1f}%  （目标 49,755）")
        else:
            print("  ⚠  collect 失败，请检查依赖（pytest/conftest）")
        return

    if mode == "parametrized":
        data = count_parametrized(TESTS_ROOT)
        files = data["files"]
        total = data["total"]
        p_total = data["parametrized_cases"]
        s_total = data["plain_cases"]
    else:
        raw = count_static(TESTS_ROOT)
        files = {k: {"total": v, "parametrized": 0, "plain": v}
                 for k, v in raw["files"].items()}
        total = raw["total"]
        p_total = 0
        s_total = total

    # 按用例数降序排列
    sorted_files = sorted(files.items(), key=lambda x: x[1]["total"] if isinstance(x[1], dict) else x[1], reverse=True)

    print(f"\n{'文件':60s}  {'用例数':>8s}")
    print("-" * 70)
    file_count = 0
    for rel, info in sorted_files:
        n = info["total"] if isinstance(info, dict) else info
        print(f"  {rel:58s}  {n:>8,}")
        file_count += 1

    print("-" * 70)
    print(f"\n  文件数：{file_count}")
    print(f"  静态函数数：{s_total:,}")
    if mode == "parametrized":
        print(f"  参数化展开（AST解析）：{p_total:,}")
    print(f"\n  ★ 合计（AST解析展开）：{total:,} 条")

    target = 49755
    pct = total / target * 100
    status = "✅ 达标" if total >= target else f"❌ 差 {target - total:,} 条"
    print(f"  目标：{target:,} 条   达标率：{pct:.1f}%   {status}")

    # 说明：矩阵文件 ALL_API_PATHS = 3,300 条，×10 = 33,000
    # AST 解析无法追踪模块级变量，故显示的数值可能偏低
    # 实际用 pytest --collect-only 才能获得精确数
    print("\n  提示：矩阵文件中 ALL_API_PATHS 为运行时变量，")
    print("         AST 模式下无法展开，建议用 --collect 模式精确统计。")
    print("=" * 70)


if __name__ == "__main__":
    if "--collect" in sys.argv:
        print_report("collect")
    elif "--static" in sys.argv:
        print_report("static")
    else:
        print_report("parametrized")
