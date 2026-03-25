╔════════════════════════════════════════════════════════════════════════════════╗
║                   区块链故障转移测试套件 - 快速参考卡（2026-03-12）           ║
║                                                                                ║
║             📚 完整覆盖：同链故障转移 + 跨链灾备 + 数据一致性保证               ║
╚════════════════════════════════════════════════════════════════════════════════╝


┌─────────────────────────────────────────────────────────────────────────────────┐
│ 🎯 快速开始                                                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Linux / Mac:                                                                   │
│    cd $WORKSPACE/tests/blockchain                                               │
│    ./run-tests.sh quick              # 快速（2 分钟）                           │
│    ./run-tests.sh all                # 完整（8-10 分钟）                        │
│                                                                                 │
│  Windows PowerShell:                                                            │
│    cd tests\blockchain                                                        │
│    .\run-tests.ps1 quick              # 快速                                    │
│    .\run-tests.ps1 all -Parallel      # 并行完整                                │
│                                                                                 │
│  Python 交互（通用）:                                                           │
│    python run_all_tests.py            # 默认顺序                                │
│    python run_all_tests.py --parallel # 并行                                    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│ 📂 测试文件清单（7 个）                                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ✅ test_failover_unit.py             66+ 用例  15.3 KB  单元测试（Mock）        │
│  ✅ test_failover_api.py              23+ 用例  13.8 KB  API 集成测试            │
│  ✅ test_data_consistency.py          24+ 用例  17.2 KB  WAL / 幂等 / 同步        │
│  ✅ test_performance.k6.js            5 场景    10.6 KB  性能 / 压力测试         │
│  ✅ run_all_tests.py                  支持脚本  15.4 KB  执行编排器              │
│  ✅ run-tests.sh                      支持脚本  8.5 KB   Bash 包装               │
│  ✅ run-tests.ps1                     支持脚本  12.3 KB  PowerShell 包装         │
│  ✅ TEST_PLAN.md                      规范文档  42.6 KB  详细测试计划            │
│  ✅ README.md                         参考卡    18.9 KB  快速参考                │
│  ✅ QUICKREF.md                       此文件    当前文件 超快速查询              │
│                                                                                 │
│  📊 总大小: ~120 KB | 总代码行: ~3500 行 | 项目占用: 约 10GB（含依赖）            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│ 🚀 常用命令（复制即粘贴）                                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ## 🧪 pytest 单元测试                                                          │
│  pytest test_failover_unit.py -v              # 详细日志                        │
│  pytest test_failover_unit.py::TestSameChainFailover -v  # 指定测试类         │
│  pytest test_failover_unit.py -k node1 -v    # 运行包含 "node1" 的用例        │
│                                                                                 │
│  ## 🔌 pytest API 测试（需要服务运行）                                          │
│  pytest test_failover_api.py -v               # 所有 API 测试                  │
│  pytest test_failover_api.py -m api -v        # 仅 API 标记的测试              │
│  pytest test_failover_api.py::test_chain_switch_concurrent -vvs  # 详细        │
│                                                                                 │
│  ## 📊 pytest 数据一致性                                                        │
│  pytest test_data_consistency.py -v           # 所有一致性测试                 │
│  pytest test_data_consistency.py -m blockchain -v  # 仅区块链标记             │
│                                                                                 │
│  ## ⚡ k6 性能测试                                                              │
│  k6 run test_performance.k6.js --vus=10 --duration=30s    # 基准（10 用户）   │
│  k6 run test_performance.k6.js --vus=100 --duration=5m    # 压力（100 用户）  │
│  k6 run test_performance.k6.js --vus=1 --duration=10s     # 热身（1 用户）    │
│                                                                                 │
│  ## 📈 覆盖率和报告                                                             │
│  pytest tests/blockchain/ --cov=JGSY.AGI.Blockchain \\                         │
│    --cov-report=html --cov-report=term                    # HTML 覆盖率报告   │
│  pytest test_failover_unit.py --html=report.html \\                            │
│    --self-contained-html                      # 独立 HTML 报告                │
│                                                                                 │
│  ## 🔍 调试和故障排除                                                           │
│  pytest test_failover_api.py --tb=long -vvv  # 长堆栈跟踪                      │
│  pytest test_failover_unit.py -s              # 显示 print() 输出              │
│  k6 run test_performance.k6.js --linger       # 保留 VU 进程（调试）           │
│                                                                                 │
│  ## 🧹 清理                                                                    │
│  rm -rf .pytest_cache __pycache__ htmlcov    # Unix/Mac                       │
│  rmdir /s /q .pytest_cache __pycache__        # Windows                        │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│ 📋 测试模式速查表                                                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  模式              脚本命令                     耗时      依赖              │
│  ───────────────────────────────────────────────────────────────────────────  │
│  快速              ./run-tests.sh quick       2 分钟    pytest               │
│  单元              ./run-tests.sh unit        1 分钟    pytest               │
│  API               ./run-tests.sh api         2 分钟    pytest + 服务        │
│  一致性            ./run-tests.sh consistency 1 分钟    pytest               │
│  性能              ./run-tests.sh performance 3 分钟    k6 + 服务            │
│  完整              ./run-tests.sh all         8-10分钟  pytest + k6 + 服务   │
│  并行              ./run-tests.sh all -j4    8-10分钟  所有 + 并行工作器   │
│                                                                                 │
|  ───────────────────────────────────────────────────────────────────────────  │
│  默认值: mode='quick', parallel=False, tool=all                               │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│ 🎓 pytest 技巧速查                                                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ## 标记（Markers）                                                             │
│  pytest test_*.py -m p0                       # 仅 P0 优先级用例               │
│  pytest test_*.py -m "not slow"               # 排除慢速测试                   │
│  pytest test_*.py -m "blockchain or p0"      # P0 或区块链标记的               │
│                                                                                 │
│  ## 参数化                                                                      │
│  pytest test_failover_unit.py::test_switch_to_chain \\                        │
│    --co -q                                    # 显示所有参数化组合             │
│                                                                                 │
│  ## 并行执行（需要 pytest-xdist）                                               │
│  pytest test_*.py -n auto                     # 自动检测 CPU 数                │
│  pytest test_*.py -n 4                        # 使用 4 个 worker               │
│                                                                                 │
│  ## 监听文件变化（需要 pytest-watch）                                           │
│  ptw test_failover_*.py -- -v                # 文件变化自动重跑               │
│                                                                                 │
│  ## 失败时立即停止                                                              │
│  pytest test_*.py -x                          # 第一个失败停止                 │
│  pytest test_*.py -x --lf                     # 仅重跑上次失败的               │
│  pytest test_*.py --maxfail=3                 # 3 次失败后停止                 │
│                                                                                 │
│  ## 生成报告                                                                    │
│  pytest test_*.py --tb=short                  # 简短堆栈                       │
│  pytest test_*.py -ra                         # 显示所有测试摘要               │
│  pytest test_*.py -q                          # 简洁输出                       │
│                                                                                 │
│  ## 时间统计                                                                    │
│  pytest test_*.py --durations=10              # 10 个最慢的测试                │
│  pytest test_*.py --durations=0               # 所有测试排序by耗时             │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│ ⚙️ 环境变量（高级）                                                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ## API 测试配置                                                                │
│  export BLOCKCHAIN_SERVICE_URL=http://localhost:8021                           │
│  export API_TIMEOUT=10                        # 秒                             │
│  export API_RETRY_COUNT=3                     # 重试次数                       │
│  export API_JWT_TOKEN=<token>                 # JWT 令牌（可选）                │
│                                                                                 │
│  ## 数据库配置（集成测试）                                                      │
│  export POSTGRES_HOST=localhost                                                │
│  export POSTGRES_PORT=5432                                                     │
│  export POSTGRES_USER=postgres                                                 │
│  export POSTGRES_PASSWORD=postgres                                              │
│  export POSTGRES_DB=jgsy_blockchain                                            │
│                                                                                 │
│  ## k6 配置                                                                     │
│  export K6_VUS=50                             # 虚拟用户数                     │
│  export K6_DURATION=5m                        # 持续时间                       │
│  export K6_QUIET=true                         # 简洁输出                       │
│                                                                                 │
│  ## pytest 配置                                                                 │
│  export PYTEST_LOGLEVEL=DEBUG                 # 日志级别                       │
│  export PYTEST_TIMEOUT=30                     # 用例超时（秒）                 │
│                                                                                 │
│  示例（Linux/Mac）:                                                             │
│  export BLOCKCHAIN_SERVICE_URL=http://localhost:8021 && \\                     │
│    pytest test_failover_api.py -v                                              │
│                                                                                 │
│  示例（PowerShell）:                                                            │
│  $env:BLOCKCHAIN_SERVICE_URL="http://localhost:8021"                           │
│  pytest test_failover_api.py -v                                                │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│ 🔧 前置条件和故障排查                                                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ❓ 问题: "ModuleNotFoundError: No module named 'pytest'"                       │
│  ✅ 解决:                                                                       │
│    pip install pytest pytest-asyncio pytest-html pytest-xdist                  │
│    pip install httpx k6 requests mock                                          │
│                                                                                 │
│  ❓ 问题: "ConnectionError: Cannot connect to http://localhost:8021"           │
│  ✅ 解决:                                                                       │
│    docker-compose up blockchain postgres redis -d                              │
│    sleep 10                                                                     │
│    pytest test_failover_api.py -v                                              │
│                                                                                 │
│  ❓ 问题: "k6: command not found"                                               │
│  ✅ 解决:                                                                       │
│    # Linux (Ubuntu/Debian)                                                     │
│    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 \\              │
│      --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69                      │
│    echo "deb https://dl.k6.io/deb stable main" | sudo tee \\                   │
│      /etc/apt/sources.list.d/k6-stable.list                                    │
│    sudo apt-get update && sudo apt-get install k6                              │
│                                                                                 │
│    # Mac                                                                        │
│    brew install k6                                                              │
│                                                                                 │
│    # Windows (Chocolatey)                                                      │
│    choco install k6                                                             │
│                                                                                 │
│  ❓ 问题: "Test failed with timeout"                                            │
│  ✅ 解决:                                                                       │
│    pytest test_failover_api.py --timeout=60 -v                                 │
│    (或增加环境变量: export PYTEST_TIMEOUT=60)                                  │
│                                                                                 │
│  ❓ 问题: "Database connection refused"                                         │
│  ✅ 解决:                                                                       │
│    # 确保 PostgreSQL 运行                                                      │
│    docker-compose ps postgres                                                  │
│    docker-compose up postgres -d && sleep 5                                    │
│    # 定位连接字符串                                                             │
│    psql -h localhost -U postgres -c "SELECT version();"                        │
│                                                                                 │
│  ❓ 问题: "Permission denied: ./run-tests.sh" (Linux)                           │
│  ✅ 解决:                                                                       │
│    chmod +x run-tests.sh                                                       │
│    ./run-tests.sh quick                                                        │
│                                                                                 │
│  ❓ 问题: "PowerShell script execution disabled" (Windows)                      │
│  ✅ 解决:                                                                       │
│    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser        │
│    .\run-tests.ps1 quick                                                       │
│                                                                                 │
│  ✅ 健康检查:                                                                   │
│    pytest --version              # pytest 是否可用                             │
│    k6 version                    # k6 是否可用                                 │
│    docker ps                     # Docker 是否运行                             │
│    curl http://localhost:8021/api/blockchain/health  # 服务是否启动           │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│ 📊 性能基准（预期值）                                                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  操作                  50%        95%        99%        失败率     并发        │
│  ────────────────────────────────────────────────────────────────────────────  │
│  获取状态              60ms      150ms      200ms       <1%       10 VU       │
│  链切换                300ms     800ms     1200ms       <5%       10 VU       │
│  节点切换              200ms     700ms     1000ms       <3%       10 VU       │
│  重置                  150ms     500ms      800ms       <2%       10 VU       │
│  健康检查              30ms      100ms      150ms       <1%       10 VU       │
│  ────────────────────────────────────────────────────────────────────────────  │
│  压力测试（100 VU）                                                            │
│  同时故障转移          1000ms+   2000ms+   3000ms+      <10%      100 VU      │
│  内存占用              <200MB (稳定 5 分钟)                                    │
│  CPU 占用              <50% (单核)                                             │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│ 📚 文档导航                                                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  文件                        内容                       何时阅读              │
│  ─────────────────────────────────────────────────────────────────────────── │
│  README.md                   完整参考                   第一次使用            │
│  QUICKREF.md                 本文件（快速查询）        查找具体命令          │
│  TEST_PLAN.md                详细用例清单               理解测试覆盖范围      │
│  test_failover_unit.py       单元测试源码               学习测试模式          │
│  test_failover_api.py        API 测试源码               理解 API 测试        │
│  test_data_consistency.py    一致性测试源码             理解数据验证          │
│  test_performance.k6.js      性能测试源码               运行性能检查          │
│  run_all_tests.py            Python 执行脚本            编程自动化            │
│  run-tests.sh                Bash 脚本（Unix）          Linux/Mac 快速启动    │
│  run-tests.ps1               PowerShell 脚本（Win）     Windows 快速启动      │
│                                                                                 │
│  链接:                                                                          │
│  - 区块链架构: ../../../JGSY.AGI.Blockchain/README.md                          │
│  - 故障转移源码: ../../../JGSY.AGI.Blockchain/Services/ChainFailoverManager.cs │
│  - 常规测试规范: ../../../docs/04-开发规范/自动化测试标准手册.md               │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│ ✅ 验收清单（发布前）                                                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  [ ] 1. 依赖安装检查                                                            │
│        pip install pytest pytest-asyncio httpx pytest-html                     │
│        brew install k6  或  choco install k6                                   │
│                                                                                 │
│  [ ] 2. 快速冒烟测试（2 分钟）                                                  │
│        ./run-tests.sh quick                                                    │
│        ✅ 通过: 66 单元测试 → 100% 通过                                         │
│                                                                                 │
│  [ ] 3. API 集成测试（确保服务运行）                                            │
│        docker-compose up blockchain postgres redis -d                          │
│        ./run-tests.sh api                                                      │
│        ✅ 通过: 23 API 用例 → 100% 通过                                         │
│                                                                                 │
│  [ ] 4. 数据一致性验证                                                          │
│        ./run-tests.sh consistency                                              │
│        ✅ 通过: 24 一致性用例 → 100% 通过                                       │
│                                                                                 │
│  [ ] 5. 性能基准验证                                                            │
│        ./run-tests.sh performance                                              │
│        ✅ 通过: P95 < 500ms, P99 < 1s, 失败率 < 5%                             │
│                                                                                 │
│  [ ] 6. 完整测试运行（8-10 分钟）                                               │
│        ./run-tests.sh all                                                      │
│        ✅ 通过: 120+ 总用例 → 100% 通过                                         │
│                                                                                 │
│  [ ] 7. 覆盖率报告生成                                                          │
│        pytest tests/blockchain/ --cov=JGSY.AGI.Blockchain \\                  │
│          --cov-report=html --cov-report=term-missing                           │
│        ✅ 覆盖率 > 90% 代码行                                                   │
│                                                                                 │
│  [ ] 8. 无遗留问题                                                              │
│        cat TestResults/blockchain/reports/*.md                                 │
│        ✅ 0 个错误、0 个警告、0 个跳过的用例                                    │
│                                                                                 │
│  所有 8 项通过 → ✅ 可上线发布                                                  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│ 🆚 对比参考：单机 vs 分布式测试                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  维度          单机测试（本地）              分布式测试（Docker）              │
│  ─────────────────────────────────────────────────────────────────────────── │
│  启动时间      <1 分钟                      3-5 分钟（镜像 pull）             │
│  环境一致性    ≤80%（取决于 OS）            ~99% (容器化)                     │
│  费用          免费                         AWS/GCP ~$100/月                  │
│  调试难度      简单（本地）                 复杂（远程 logs）                 │
│  覆盖范围      单节点                       多节点网络                        │
│  推荐          开发/快速验证                CI/CD/预发布                      │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘


╔════════════════════════════════════════════════════════════════════════════════╗
║                              最后一步：执行测试                                  ║
║                                                                                  ║
║  $ cd tests/blockchain                                                         ║
║  $ ./run-tests.sh all              # Linux/Mac                                 ║
║  $ .\run-tests.ps1 all -Parallel   # Windows PowerShell                        ║
║                                                                                  ║
║  或                                                                              ║
║                                                                                  ║
║  $ python run_all_tests.py --parallel                                          ║
║                                                                                  ║
║  预期: 120+ 用例, 8-10 分钟, 100% 通过 ✅                                        ║
║                                                                                  ║
║  问题？见上面的 🔧 故障排查 部分                                                 ║
║                                                                                  ║
╚════════════════════════════════════════════════════════════════════════════════╝


版本: 1.0.0
日期: 2026-03-12
维护: GitHub Copilot + JGSY.AGI 团队
许可: 内部使用
