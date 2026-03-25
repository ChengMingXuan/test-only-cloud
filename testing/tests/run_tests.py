"""
运行测试入口脚本
==================
支持按模块、优先级、类型运行测试
"""
import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def run_cmd(cmd: list[str], desc: str):
    print(f"\n{'='*60}")
    print(f"  {desc}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, cwd=BASE_DIR)
    return result.returncode


def main():
    if len(sys.argv) < 2:
        print("""
用法: python run_tests.py <命令>

命令列表:
  smoke           烟雾测试（P0 核心流程）
  api             全部 API 测试
  e2e             全部 E2E 页面测试
  security        安全测试
  tenant          多租户隔离测试
  db              数据库验证测试
  all             全量测试
  report          生成 HTML 报告
  allure          生成 Allure 报告
  identity        Identity 服务测试
  charging        Charging 服务测试

  k6-smoke        K6 烟雾测试
  k6-load         K6 负载测试
  k6-stress       K6 压力测试
  k6-concurrency  K6 充电并发测试
  k6-idempotency  K6 幂等性测试
  k6-stability    K6 72h 稳定性
        """)
        return 1

    cmd = sys.argv[1]
    extra = sys.argv[2:] if len(sys.argv) > 2 else []

    pytest_base = [sys.executable, "-m", "pytest", "-v", "--tb=short"]
    k6_base = ["k6", "run"]

    commands = {
        # ── PyTest ──
        "smoke":    pytest_base + ["-m", "smoke or p0", "tests/"] + extra,
        "api":      pytest_base + ["tests/api/"] + extra,
        "e2e":      pytest_base + ["-m", "e2e", "tests/e2e/"] + extra,
        "security": pytest_base + ["-m", "security", "tests/security/"] + extra,
        "tenant":   pytest_base + ["-m", "tenant_isolation", "tests/api/test_tenant_isolation.py"] + extra,
        "db":       pytest_base + ["-m", "db_verify", "tests/"] + extra,
        "all":      pytest_base + ["tests/"] + extra,
        "report":   pytest_base + ["tests/", "--html=reports/test-report.html",
                                    "--self-contained-html"] + extra,
        "allure":   pytest_base + ["tests/", "--alluredir=reports/allure-results"] + extra,
        "identity": pytest_base + ["tests/api/test_identity/"] + extra,
        "charging": pytest_base + ["tests/api/test_charging/"] + extra,

        # ── K6 ──
        "k6-smoke":        k6_base + ["k6/scenarios/smoke-test.js"],
        "k6-load":         k6_base + ["k6/scenarios/load-test.js"],
        "k6-stress":       k6_base + ["k6/scenarios/stress-test.js"],
        "k6-concurrency":  k6_base + ["-e", "SCENARIO=concurrency",
                                       "k6/scenarios/charging-concurrency-test.js"],
        "k6-idempotency":  k6_base + ["-e", "SCENARIO=idempotency",
                                       "k6/scenarios/charging-concurrency-test.js"],
        "k6-stability":    k6_base + ["-e", "SCENARIO=stability",
                                       "k6/scenarios/charging-concurrency-test.js"],
    }

    if cmd not in commands:
        print(f"未知命令: {cmd}")
        return 1

    return run_cmd(commands[cmd], cmd)


if __name__ == "__main__":
    sys.exit(main())
