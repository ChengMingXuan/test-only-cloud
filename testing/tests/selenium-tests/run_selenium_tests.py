"""
Selenium 浏览器兼容性测试 — 完整执行脚本

执行步骤：
  1. 启动 Mock HTTP 服务器（模拟前端页面）
  2. 并行运行 generated/ 下全部 4116 条测试 (pytest-xdist -n 4)
  3. 保存 JUnit XML 至 junit.xml
  4. 关闭 Mock 服务器
  5. 输出结果摘要

用法：
  python run_selenium_tests.py [--workers N] [--files-limit N]
"""
import sys, os, subprocess, time, argparse
from pathlib import Path

ROOT = Path(__file__).parent
os.environ.setdefault("WDM_LOCAL", "1")

# 添加 mock_server 模块到路径
sys.path.insert(0, str(ROOT))
from mock_server import MockServer


def main():
    ap = argparse.ArgumentParser(description="运行 Selenium 兼容性测试")
    ap.add_argument("--workers", type=int, default=4, help="并行 xdist workers (默认 4)")
    ap.add_argument("--files-limit", type=int, default=0, help="仅运行前 N 个测试文件（0=全部）")
    ap.add_argument("--timeout", type=int, default=20, help="每个测试超时秒数（默认 20）")
    args = ap.parse_args()

    # 1. 启动 Mock 服务器
    srv = MockServer()
    srv.start()
    base_url = srv.base_url
    print(f"✅ Mock 服务器已启动: {base_url}")
    os.environ["TEST_BASE_URL"] = base_url

    # 2. 构建测试文件列表（包含 supplement 子目录）
    gen_dir = ROOT / "tests" / "generated"
    all_files = sorted(gen_dir.rglob("test_*.py"))
    if args.files_limit and args.files_limit > 0:
        all_files = all_files[: args.files_limit]
    print(f"📂 测试文件数: {len(all_files)}")

    # 确保 JUnit 目录存在
    junit_path = ROOT / "junit.xml"
    report_path = ROOT / "selenium-report.html"

    # 3. 运行 pytest
    cmd = [
        sys.executable, "-m", "pytest",
        *[str(f) for f in all_files],
        f"--timeout={args.timeout}",
        f"--junitxml={junit_path}",
        "-q",
        "--tb=no",
        "-W", "ignore::pytest.PytestUnknownMarkWarning",
        "-W", "ignore::DeprecationWarning",
        "--override-ini=testpaths=",  # 覆盖 pytest.ini 的 testpaths
        "--override-ini=addopts=",    # 覆盖 pytest.ini 的 addopts（避免重复 -q 等）
    ]

    print(f"🚀 启动 pytest (workers={args.workers}, timeout={args.timeout}s)...")
    start_ts = time.time()

    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=False)

    elapsed = time.time() - start_ts
    exit_code = proc.returncode

    # 4. 停止 Mock 服务器
    srv.stop()
    print(f"\n⏱  总耗时: {elapsed:.1f}s")

    # 5. 输出结果摘要
    if junit_path.exists():
        import xml.etree.ElementTree as ET
        try:
            tree = ET.parse(junit_path)
            root = tree.getroot()
            ts = root.find("testsuite") or root
            total = int(ts.get("tests", 0))
            failed = int(ts.get("failures", 0)) + int(ts.get("errors", 0))
            skipped = int(ts.get("skipped", 0))
            passed = total - failed - skipped
            pct = (passed / total * 100) if total else 0
            print(f"\n📊 结果：总计={total}, 通过={passed}, 失败={failed}, 跳过={skipped}, 通过率={pct:.1f}%")
        except Exception as e:
            print(f"⚠  解析 JUnit XML 失败: {e}")
    else:
        print("❌ junit.xml 未生成")

    print(f"\n{'✅' if exit_code == 0 else '❌'} pytest 退出码: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
