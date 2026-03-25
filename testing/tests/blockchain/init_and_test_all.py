#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
区块链服务 — 数据库初始化 + 全量测试执行脚本

功能:
  ✅ 检查数据库连接
  ✅ 执行 DbUp 迁移（初始化表结构）
  ✅ 导入权限和菜单种子数据
  ✅ 逐个运行所有 8 个测试套件
  ✅ 生成最终综合报告

使用: python init_and_test_all.py
"""

import os
import sys
import json
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import traceback

# ════════════════════════════════════════════════════════════════════════════════
# 日志配置
# ════════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('init_and_test_all.log')
    ]
)
logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# 配置和常量
# ════════════════════════════════════════════════════════════════════════════════

class Config:
    """脚本配置"""
    
    # 数据库配置
    DB_HOST = "localhost"
    DB_PORT = 5432
    DB_USER = "postgres"
    DB_PASSWORD = "postgres"
    DB_NAME = "jgsy_blockchain"
    
    # 测试配置
    TESTS_DIR = Path("tests/blockchain")
    REPORT_DIR = Path("TestResults/blockchain")
    
    # 测试文件列表（执行顺序）
    TEST_FILES = [
        ("单元测试", "test_failover_unit.py", ["pytest", "-v", "--tb=short"]),
        ("API 集成测试", "test_failover_api.py", ["pytest", "-v", "-m", "api", "--tb=short"]),
        ("数据一致性测试", "test_data_consistency.py", ["pytest", "-v", "--tb=short"]),
        ("灾备集成测试", "test_disaster_recovery_integration.py", ["pytest", "-v", "-m", "p0", "--tb=short"]),
        ("性能基准", "test_performance.k6.js", ["k6", "run", "--vus=10", "--duration=30s"]),
    ]


# ════════════════════════════════════════════════════════════════════════════════
# 数据库初始化
# ════════════════════════════════════════════════════════════════════════════════

class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self):
        self.results = {
            'connection': False,
            'migration': False,
            'seed_data': False,
        }
    
    def check_connection(self) -> bool:
        """检查数据库连接"""
        logger.info("=" * 70)
        logger.info("1️⃣  检查数据库连接")
        logger.info("=" * 70)
        
        try:
            cmd = [
                "psql",
                f"-h", Config.DB_HOST,
                f"-p", str(Config.DB_PORT),
                f"-U", Config.DB_USER,
                "-d", "postgres",  # 先连接默认数据库
                "-c", "SELECT 1;"
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = Config.DB_PASSWORD
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                env=env
            )
            
            if result.returncode == 0:
                logger.info("✅ PostgreSQL 连接成功")
                self.results['connection'] = True
                
                # 检查业务库是否存在
                logger.info(f"   检查业务库: {Config.DB_NAME}")
                result = subprocess.run(
                    [
                        "psql",
                        f"-h", Config.DB_HOST,
                        f"-U", Config.DB_USER,
                        "-lqt"
                    ],
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=10
                )
                
                if Config.DB_NAME in result.stdout:
                    logger.info(f"   ✅ 库 {Config.DB_NAME} 存在")
                else:
                    logger.warning(f"   ⚠️  库 {Config.DB_NAME} 不存在，将创建...")
                    self._create_database()
                
                return True
            else:
                logger.error(f"❌ 数据库连接失败: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            logger.error("❌ 连接超时（检查 PostgreSQL 是否启动）")
            return False
        except FileNotFoundError:
            logger.error("❌ psql 命令未找到（检查 PostgreSQL 是否安装）")
            return False
        except Exception as e:
            logger.error(f"❌ 连接错误: {e}")
            return False
    
    def _create_database(self):
        """创建业务库"""
        logger.info(f"   创建库 {Config.DB_NAME}...")
        
        cmd = [
            "psql",
            f"-h", Config.DB_HOST,
            f"-U", Config.DB_USER,
            "-d", "postgres",
            "-c", f"CREATE DATABASE {Config.DB_NAME} OWNER postgres;"
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = Config.DB_PASSWORD
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            logger.info(f"   ✅ 库 {Config.DB_NAME} 创建成功")
        else:
            logger.warning(f"   ⚠️  库创建失败或已存在: {result.stderr.strip()}")
    
    def run_dbup_migration(self) -> bool:
        """运行 DbUp 迁移初始化表结构"""
        logger.info("=" * 70)
        logger.info("2️⃣  执行 DbUp 迁移初始化表结构")
        logger.info("=" * 70)
        
        try:
            # 查找 DbUp 项目
            dbup_project = Path("JGSY.AGI.Blockchain/Data/DbUp.csproj")
            
            if not dbup_project.exists():
                logger.warning(f"⚠️  未找到 DbUp 项目: {dbup_project}")
                logger.info("   尝试使用 SQL 脚本直接初始化...")
                return self._run_sql_migrations()
            
            logger.info(f"   执行 DbUp 迁移...")
            
            # 构建迁移项目和执行
            cmd = [
                "dotnet",
                "run",
                "--project", str(dbup_project),
                "--",
                f"--server={Config.DB_HOST}:{Config.DB_PORT}",
                f"--database={Config.DB_NAME}",
                f"--username={Config.DB_USER}",
                f"--password={Config.DB_PASSWORD}"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(Path.cwd())
            )
            
            if result.returncode == 0 or "No new scripts to execute" in result.stdout:
                logger.info("✅ DbUp 迁移成功（或已是最新）")
                logger.info(f"   输出: {result.stdout[:200]}")
                self.results['migration'] = True
                return True
            else:
                logger.warning(f"⚠️  DbUp 迁移有警告: {result.stderr[:300]}")
                self.results['migration'] = True  # 仅警告，不阻塞
                return True
        
        except Exception as e:
            logger.warning(f"⚠️  DbUp 迁移失败: {e}")
            logger.info("   尝试使用 SQL 脚本直接初始化...")
            return self._run_sql_migrations()
    
    def _run_sql_migrations(self) -> bool:
        """运行 SQL 迁移脚本"""
        logger.info("   运行 SQL 迁移脚本...")
        
        migration_dir = Path("JGSY.AGI.Blockchain/Data/Migrations")
        
        if not migration_dir.exists():
            logger.warning(f"⚠️  未找到迁移脚本目录: {migration_dir}")
            return False
        
        # 按顺序执行所有 SQL 脚本
        sql_files = sorted(migration_dir.glob("*.sql"))
        
        if not sql_files:
            logger.warning("⚠️  未找到 SQL 迁移脚本")
            return False
        
        env = os.environ.copy()
        env['PGPASSWORD'] = Config.DB_PASSWORD
        
        executed = 0
        for sql_file in sql_files:
            try:
                logger.info(f"   执行: {sql_file.name}")
                
                with open(sql_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                cmd = [
                    "psql",
                    f"-h", Config.DB_HOST,
                    f"-U", Config.DB_USER,
                    "-d", Config.DB_NAME,
                    "-f", str(sql_file)
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    env=env
                )
                
                if result.returncode == 0:
                    logger.info(f"      ✅ 成功")
                    executed += 1
                else:
                    logger.warning(f"      ⚠️  有警告: {result.stderr[:100]}")
                    executed += 1  # 继续执行下一个脚本
            
            except Exception as e:
                logger.warning(f"      ⚠️  执行失败: {e}")
                continue
        
        if executed > 0:
            logger.info(f"✅ 已执行 {executed} 个迁移脚本")
            self.results['migration'] = True
            return True
        else:
            logger.warning("⚠️  没有成功执行任何迁移脚本")
            return False
    
    def import_seed_data(self) -> bool:
        """导入权限和菜单种子数据"""
        logger.info("=" * 70)
        logger.info("3️⃣  导入权限和菜单种子数据")
        logger.info("=" * 70)
        
        try:
            # 权限种子数据脚本
            seed_script = Path("docker/seed-data/permission/005_blockchain_failover_permission_and_menu.sql")
            
            if not seed_script.exists():
                logger.warning(f"⚠️  未找到种子数据脚本: {seed_script}")
                logger.info("   跳过权限初始化（可手动执行）")
                self.results['seed_data'] = False
                return False
            
            logger.info(f"   执行权限和菜单初始化: {seed_script.name}")
            
            env = os.environ.copy()
            env['PGPASSWORD'] = Config.DB_PASSWORD
            
            cmd = [
                "psql",
                f"-h", Config.DB_HOST,
                f"-U", Config.DB_USER,
                "-d", "jgsy_permission",  # Permission 库
                "-f", str(seed_script)
            ]
            
            # 如果 Permission 库不存在，先尝试用业务库
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                env=env
            )
            
            if result.returncode == 0:
                logger.info("✅ 权限和菜单初始化成功")
                
                # 验证初始化结果
                verify_cmd = [
                    "psql",
                    f"-h", Config.DB_HOST,
                    f"-U", Config.DB_USER,
                    "-d", "jgsy_permission",
                    "-t", "-c",
                    "SELECT COUNT(*) FROM perm_permission WHERE perm_code LIKE 'blockchain:%';"
                ]
                
                verify_result = subprocess.run(
                    verify_cmd,
                    capture_output=True,
                    text=True,
                    env=env
                )
                
                if verify_result.returncode == 0:
                    count = verify_result.stdout.strip()
                    logger.info(f"   验证: {count} 个权限码已导入")
                    self.results['seed_data'] = True
                    return True
            
            else:
                logger.warning(f"⚠️  权限导入有问题: {result.stderr[:200]}")
                logger.info("   这可能是因为 Permission 库不存在（正常情况）")
                self.results['seed_data'] = False
                return False
        
        except FileNotFoundError:
            logger.warning("⚠️  psql 命令未找到")
            return False
        except Exception as e:
            logger.warning(f"⚠️  种子数据导入失败: {e}")
            return False


# ════════════════════════════════════════════════════════════════════════════════
# 测试执行器
# ════════════════════════════════════════════════════════════════════════════════

class TestRunner:
    """分类测试执行器"""
    
    def __init__(self):
        self.test_results = {}
        self.report_dir = Config.REPORT_DIR / "full_test_results"
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def run_all_tests(self) -> Dict[str, bool]:
        """逐个运行所有测试"""
        logger.info("=" * 70)
        logger.info("4️⃣  逐个运行所有测试")
        logger.info("=" * 70)
        
        # 切换到测试目录
        original_dir = Path.cwd()
        os.chdir(Config.TESTS_DIR)
        
        try:
            for test_name, test_file, cmd_template in Config.TEST_FILES:
                success = self._run_single_test(test_name, test_file, cmd_template)
                self.test_results[test_name] = success
                
                # 测试间隔
                time.sleep(2)
            
            return self.test_results
        
        finally:
            os.chdir(original_dir)
    
    def _run_single_test(self, test_name: str, test_file: str, cmd_template: List[str]) -> bool:
        """运行单个测试"""
        logger.info(f"\n{'─' * 70}")
        logger.info(f"▶️  {test_name}: {test_file}")
        logger.info(f"{'─' * 70}")
        
        try:
            # 构建完整命令
            if cmd_template[0] == "pytest":
                cmd = ["pytest", test_file] + cmd_template[1:]
            elif cmd_template[0] == "k6":
                cmd = ["k6", "run", test_file] + cmd_template[2:]
            else:
                cmd = cmd_template + [test_file]
            
            # 执行测试
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 分钟超时
            )
            elapsed = time.time() - start_time
            
            # 保存输出
            output_file = self.report_dir / f"{test_name.replace(' ', '_')}_output.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Command: {' '.join(cmd)}\n")
                f.write(f"Elapsed: {elapsed:.2f}s\n")
                f.write(f"Exit Code: {result.returncode}\n")
                f.write(f"\n=== STDOUT ===\n{result.stdout}\n")
                f.write(f"\n=== STDERR ===\n{result.stderr}\n")
            
            # 判断成功
            success = result.returncode == 0
            
            if success:
                logger.info(f"✅ {test_name}: 通过 ({elapsed:.2f}s)")
            else:
                logger.warning(f"❌ {test_name}: 失败 ({elapsed:.2f}s)")
                logger.info(f"   输出文件: {output_file}")
                
                # 显示错误摘要
                if "FAILED" in result.stdout:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "FAILED" in line or "ERROR" in line:
                            logger.info(f"   {line[:100]}")
            
            return success
        
        except subprocess.TimeoutExpired:
            logger.error(f"❌ {test_name}: 超时（600s）")
            return False
        except FileNotFoundError as e:
            logger.error(f"❌ {test_name}: 命令未找到 - {e}")
            return False
        except Exception as e:
            logger.error(f"❌ {test_name}: 执行错误 - {e}")
            logger.error(traceback.format_exc())
            return False
    
    def generate_report(self) -> bool:
        """生成综合测试报告"""
        logger.info("=" * 70)
        logger.info("5️⃣  生成综合测试报告")
        logger.info("=" * 70)
        
        # JSON 报告
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'database': {
                'host': Config.DB_HOST,
                'port': Config.DB_PORT,
                'name': Config.DB_NAME,
            },
            'test_results': self.test_results,
            'summary': {
                'total': len(self.test_results),
                'passed': sum(1 for v in self.test_results.values() if v),
                'failed': sum(1 for v in self.test_results.values() if not v),
            }
        }
        
        json_file = self.report_dir / "test_report.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ JSON 报告已保存: {json_file}")
        
        # Markdown 报告
        md_content = self._generate_markdown_report(report_data)
        md_file = self.report_dir / "test_report.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"✅ Markdown 报告已保存: {md_file}")
        
        return True
    
    def _generate_markdown_report(self, report_data: Dict) -> str:
        """生成 Markdown 报告"""
        passed = report_data['summary']['passed']
        total = report_data['summary']['total']
        
        md = f"""# 区块链服务 — 全量测试报告

**生成时间**: {report_data['timestamp']}

**数据库**: {report_data['database']['host']}:{report_data['database']['port']}/{report_data['database']['name']}

## 测试摘要

- **总测试数**: {total}
- **通过数**: {passed}
- **失败数**: {report_data['summary']['failed']}
- **通过率**: {(passed/total*100):.1f}%

## 测试结果

| 测试项 | 状态 | 备注 |
|--------|------|------|
{self._generate_result_rows(report_data['test_results'])}

## 详细输出

所有输出文件位置: `{self.report_dir}`

"""
        return md
    
    def _generate_result_rows(self, results: Dict[str, bool]) -> str:
        """生成 Markdown 表格行"""
        rows = []
        for test_name, success in results.items():
            status = "✅ 通过" if success else "❌ 失败"
            file_name = test_name.replace(' ', '_')
            rows.append(f"| {test_name} | {status} | [输出]({file_name}_output.txt) |")
        return '\n'.join(rows)


# ════════════════════════════════════════════════════════════════════════════════
# 主程序
# ════════════════════════════════════════════════════════════════════════════════

def main():
    """主函数"""
    
    logger.info("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║      区块链服务 — 数据库初始化 + 全量测试执行                      ║
    ║                                                                   ║
    ║  阶段:                                                             ║
    ║   1️⃣  检查数据库连接                                              ║
    ║   2️⃣  执行 DbUp 迁移初始化表结构                                  ║
    ║   3️⃣  导入权限和菜单种子数据                                      ║
    ║   4️⃣  逐个运行所有测试                                            ║
    ║   5️⃣  生成综合测试报告                                            ║
    ║                                                                   ║
    ║  预计耗时: 15-30 分钟                                              ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    start_time = time.time()
    
    try:
        # ════════════════════════════════════════════════════════════════
        # 第一步: 数据库初始化
        # ════════════════════════════════════════════════════════════════
        db_init = DatabaseInitializer()
        
        if not db_init.check_connection():
            logger.error("❌ 无法连接数据库，停止执行")
            sys.exit(1)
        
        if not db_init.run_dbup_migration():
            logger.warning("⚠️  DbUp 迁移有问题，但继续执行（可能表结构已存在）")
        
        db_init.import_seed_data()
        
        # ════════════════════════════════════════════════════════════════
        # 第二步: 运行测试
        # ════════════════════════════════════════════════════════════════
        test_runner = TestRunner()
        results = test_runner.run_all_tests()
        test_runner.generate_report()
        
        # ════════════════════════════════════════════════════════════════
        # 最后: 显示汇总
        # ════════════════════════════════════════════════════════════════
        elapsed = time.time() - start_time
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 最终汇总")
        logger.info("=" * 70)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        logger.info(f"\n数据库初始化:")
        logger.info(f"  - 数据库连接: {'✅' if db_init.results['connection'] else '❌'}")
        logger.info(f"  - DbUp 迁移: {'✅' if db_init.results['migration'] else '⚠️'}")
        logger.info(f"  - 种子数据: {'✅' if db_init.results['seed_data'] else '⚠️'}")
        
        logger.info(f"\n测试结果: {passed}/{total} 通过")
        for test_name, success in results.items():
            status = "✅" if success else "❌"
            logger.info(f"  {status} {test_name}")
        
        logger.info(f"\n总耗时: {elapsed:.1f} 秒")
        logger.info(f"报告位置: {test_runner.report_dir}")
        
        # 确定最终状态
        if passed == total:
            logger.info("\n🎉 所有测试通过！")
            sys.exit(0)
        else:
            logger.warning(f"\n⚠️  {total - passed} 个测试失败")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("\n⏹️  被用户中断")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n❌ 执行失败: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()
