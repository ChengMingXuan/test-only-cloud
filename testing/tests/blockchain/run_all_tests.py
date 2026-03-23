"""
区块链服务 — 全工具测试执行脚本
================================================================

这个脚本协调所有 6 类测试工具的执行，生成统一的测试报告。

6 类测试工具：
  1. pytest         - 单元测试、API 集成测试、数据一致性测试
  2. k6             - 性能和压力测试
  3. Playwright     - E2E 端到端测试（需要 UI）
  4. Cypress        - 业务流程测试（需要 UI）
  5. Puppeteer      - 页面性能测试
  6. Selenium       - 浏览器兼容性测试

针对区块链服务的主要是 pytest + k6。

运行方式：
  python tests/blockchain/run_all_tests.py
  python tests/blockchain/run_all_tests.py --quick
  python tests/blockchain/run_all_tests.py --parallel
  python tests/blockchain/run_all_tests.py --tools pytest,k6
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
import argparse


# ═══════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent.parent.parent
TESTS_DIR = PROJECT_ROOT / "tests" / "blockchain"
TEST_RESULTS_DIR = PROJECT_ROOT / "TestResults" / "blockchain"
REPORTS_DIR = TEST_RESULTS_DIR / "reports"

# 确保输出目录存在
TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


# ═══════════════════════════════════════════════════════════════
# 测试配置
# ═══════════════════════════════════════════════════════════════

TEST_CONFIGS = {
    "pytest_unit": {
        "name": "pytest - 单元测试",
        "command": [
            "pytest",
            str(TESTS_DIR / "test_failover_unit.py"),
            "-v",
            "--tb=short",
            "--junit-xml=" + str(REPORTS_DIR / "pytest-unit.xml"),
            "--html=" + str(REPORTS_DIR / "pytest-unit.html"),
            "--self-contained-html",
        ],
        "skip_if_missing": False,
    },
    "pytest_api": {
        "name": "pytest - API 集成测试",
        "command": [
            "pytest",
            str(TESTS_DIR / "test_failover_api.py"),
            "-v",
            "--tb=short",
            "-m", "api",
            "--junit-xml=" + str(REPORTS_DIR / "pytest-api.xml"),
            "--html=" + str(REPORTS_DIR / "pytest-api.html"),
            "--self-contained-html",
        ],
        "skip_if_missing": False,
    },
    "pytest_consistency": {
        "name": "pytest - 数据一致性测试",
        "command": [
            "pytest",
            str(TESTS_DIR / "test_data_consistency.py"),
            "-v",
            "--tb=short",
            "-m", "blockchain",
            "--junit-xml=" + str(REPORTS_DIR / "pytest-consistency.xml"),
            "--html=" + str(REPORTS_DIR / "pytest-consistency.html"),
            "--self-contained-html",
        ],
        "skip_if_missing": False,
    },
    "k6": {
        "name": "k6 - 性能和压力测试",
        "command": [
            "k6",
            "run",
            str(TESTS_DIR / "test_performance.k6.js"),
            "--vus=10",
            "--duration=30s",
            "--summary-export=" + str(REPORTS_DIR / "k6-summary.json"),
        ],
        "skip_if_missing": True,
    },
}

QUICK_TEST_CONFIGS = {
    "pytest_unit": TEST_CONFIGS["pytest_unit"],
    "pytest_api": {
        **TEST_CONFIGS["pytest_api"],
        "command": TEST_CONFIGS["pytest_api"]["command"] + ["-k", "test_get_failover_status"],
    },
}


# ═══════════════════════════════════════════════════════════════
# 测试执行
# ═══════════════════════════════════════════════════════════════

class TestRunner:
    """测试执行器"""
    
    def __init__(self, parallel: bool = False, tools: List[str] = None):
        self.parallel = parallel
        self.tools = tools or list(TEST_CONFIGS.keys())
        self.results: Dict[str, Dict[str, Any]] = {}
        self.failed_tests: List[str] = []
    
    def run_all(self) -> bool:
        """执行所有测试"""
        print("=" * 70)
        print("区块链服务 - 全工具测试执行")
        print("=" * 70)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"并行执行: {self.parallel}")
        print(f"测试工具: {', '.join(self.tools)}")
        print("=" * 70)
        print()
        
        if self.parallel:
            self._run_parallel()
        else:
            self._run_sequential()
        
        return self._generate_report()
    
    def _run_sequential(self):
        """顺序执行"""
        for tool_name in self.tools:
            if tool_name not in TEST_CONFIGS:
                print(f"⚠️  未知工具: {tool_name}，跳过")
                continue
            
            self._run_test(tool_name)
    
    def _run_parallel(self):
        """并行执行"""
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self._run_test, tool_name): tool_name
                for tool_name in self.tools
                if tool_name in TEST_CONFIGS
            }
            
            for future in concurrent.futures.as_completed(futures):
                pass
    
    def _run_test(self, tool_name: str):
        """执行单个测试"""
        config = TEST_CONFIGS[tool_name]
        test_name = config["name"]
        
        print(f"\n▶️  开始: {test_name}")
        print("-" * 70)
        
        try:
            result = subprocess.run(
                config["command"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=300  # 5 分钟超时
            )
            
            self.results[tool_name] = {
                "status": "passed" if result.returncode == 0 else "failed",
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
            
            if result.returncode == 0:
                print(f"✅ 通过: {test_name}")
                print(f"   输出: {result.stdout.split(chr(10))[0][:80]}...")
            else:
                print(f"❌ 失败: {test_name}")
                self.failed_tests.append(tool_name)
                if result.stderr:
                    print(f"   错误: {result.stderr[:200]}")
        
        except subprocess.TimeoutExpired:
            self.results[tool_name] = {
                "status": "timeout",
                "exit_code": -1,
                "stderr": "测试超时（5 分钟）"
            }
            print(f"⏱️  超时: {test_name}")
            self.failed_tests.append(tool_name)
        
        except FileNotFoundError:
            if config.get("skip_if_missing"):
                self.results[tool_name] = {
                    "status": "skipped",
                    "exit_code": 0,
                    "stderr": "工具未安装"
                }
                print(f"⊘ 跳过: {test_name}（工具未安装）")
            else:
                self.results[tool_name] = {
                    "status": "error",
                    "exit_code": -1,
                    "stderr": "工具未安装"
                }
                print(f"❌ 错误: {test_name}（工具未安装）")
                self.failed_tests.append(tool_name)
        
        except Exception as e:
            self.results[tool_name] = {
                "status": "error",
                "exit_code": -1,
                "stderr": str(e)
            }
            print(f"❌ 异常: {test_name}: {str(e)}")
            self.failed_tests.append(tool_name)
    
    def _generate_report(self) -> bool:
        """生成测试报告"""
        print("\n" + "=" * 70)
        print("测试总结")
        print("=" * 70)
        
        passed = sum(1 for r in self.results.values() if r["status"] == "passed")
        failed = sum(1 for r in self.results.values() if r["status"] == "failed")
        skipped = sum(1 for r in self.results.values() if r["status"] == "skipped")
        errors = sum(1 for r in self.results.values() if r["status"] == "error")
        
        print(f"✅ 通过: {passed}")
        print(f"❌ 失败: {failed}")
        print(f"⊘ 跳过: {skipped}")
        print(f"⚠️  异常: {errors}")
        print()
        
        # 生成 JSON 报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "errors": errors,
                "total": len(self.results),
            },
            "results": self.results,
        }
        
        report_path = REPORTS_DIR / f"blockchain-test-report-{TIMESTAMP}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 报告已保存: {report_path}")
        
        # 生成 Markdown 报告
        self._generate_markdown_report()
        
        # 返回是否所有测试都通过
        return len(self.failed_tests) == 0
    
    def _generate_markdown_report(self):
        """生成 Markdown 报告"""
        md_path = REPORTS_DIR / f"blockchain-test-report-{TIMESTAMP}.md"
        
        lines = [
            "# 区块链服务 - 测试报告",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 测试总结",
            "",
        ]
        
        for tool_name, result in self.results.items():
            config = TEST_CONFIGS.get(tool_name, {})
            test_name = config.get("name", tool_name)
            status_icon = {
                "passed": "✅",
                "failed": "❌",
                "skipped": "⊘",
                "error": "⚠️ ",
                "timeout": "⏱️ ",
            }.get(result["status"], "❓")
            
            lines.append(f"| {status_icon} | {test_name} | {result['status']} |")
        
        lines.extend([
            "",
            "## 失败详情",
            "",
        ])
        
        if self.failed_tests:
            for tool_name in self.failed_tests:
                result = self.results[tool_name]
                config = TEST_CONFIGS.get(tool_name, {})
                test_name = config.get("name", tool_name)
                
                lines.extend([
                    f"### {test_name}",
                    "",
                    "```",
                    result.get("stderr", "无错误信息")[:500],
                    "```",
                    "",
                ])
        else:
            lines.append("无失败。✨")
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        print(f"📄 Markdown 报告: {md_path}")


# ═══════════════════════════════════════════════════════════════
# 命令行接口
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="区块链服务 - 全工具测试执行"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="快速测试（仅运行关键测试）"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="并行执行测试"
    )
    parser.add_argument(
        "--tools",
        type=str,
        help="指定工具（逗号分隔），例如: pytest_unit,k6"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="单个测试超时时间（秒）"
    )
    
    args = parser.parse_args()
    
    # 确定要运行的工具
    if args.tools:
        tools = args.tools.split(",")
    else:
        tools = list(TEST_CONFIGS.keys())
    
    # 创建测试执行器
    runner = TestRunner(parallel=args.parallel, tools=tools)
    
    # 运行测试
    success = runner.run_all()
    
    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
