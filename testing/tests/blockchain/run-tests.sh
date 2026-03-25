#!/bin/bash

# 区块链服务 — 测试快速运行脚本
# ============================================
# 
# 用法:
#   ./run-tests.sh                  # 运行所有测试
#   ./run-tests.sh quick            # 快速测试
#   ./run-tests.sh unit             # 仅单元测试
#   ./run-tests.sh api              # 仅 API 测试
#   ./run-tests.sh performance      # 仅性能测试
#   ./run-tests.sh all-detailed     # 完整详细测试
#

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TESTS_DIR="$PROJECT_ROOT/tests/blockchain"
RESULTS_DIR="$PROJECT_ROOT/TestResults/blockchain"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数定义
print_header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."
    
    if ! command -v pytest &> /dev/null; then
        print_error "pytest 未安装，请运行: pip install pytest pytest-html pytest-asyncio"
        exit 1
    fi
    
    print_success "pytest 已安装"
}

# 运行单元测试
run_unit_tests() {
    print_header "运行单元测试"
    pytest "$TESTS_DIR/test_failover_unit.py" -v \
        --tb=short \
        --junit-xml="$RESULTS_DIR/pytest-unit.xml" \
        --html="$RESULTS_DIR/pytest-unit.html" \
        --self-contained-html
    
    if [ $? -eq 0 ]; then
        print_success "单元测试通过"
    else
        print_error "单元测试失败"
        return 1
    fi
}

# 运行 API 集成测试
run_api_tests() {
    print_header "运行 API 集成测试"
    
    # 检查服务可用性
    if ! curl -s http://localhost:8021/api/blockchain/health > /dev/null 2>&1; then
        print_error "区块链服务不可用 (http://localhost:8021)"
        print_info "请先启动服务: docker-compose up blockchain"
        return 1
    fi
    
    pytest "$TESTS_DIR/test_failover_api.py" -v \
        --tb=short \
        --junit-xml="$RESULTS_DIR/pytest-api.xml" \
        --html="$RESULTS_DIR/pytest-api.html" \
        --self-contained-html
    
    if [ $? -eq 0 ]; then
        print_success "API 测试通过"
    else
        print_error "API 测试失败"
        return 1
    fi
}

# 运行数据一致性测试
run_consistency_tests() {
    print_header "运行数据一致性测试"
    pytest "$TESTS_DIR/test_data_consistency.py" -v \
        --tb=short \
        --junit-xml="$RESULTS_DIR/pytest-consistency.xml" \
        --html="$RESULTS_DIR/pytest-consistency.html" \
        --self-contained-html
    
    if [ $? -eq 0 ]; then
        print_success "一致性测试通过"
    else
        print_error "一致性测试失败"
        return 1
    fi
}

# 运行性能测试
run_performance_tests() {
    print_header "运行性能测试"
    
    if ! command -v k6 &> /dev/null; then
        print_error "k6 未安装，请访问: https://k6.io/docs/getting-started/installation/"
        return 1
    fi
    
    k6 run "$TESTS_DIR/test_performance.k6.js" \
        --vus=10 \
        --duration=30s \
        --summary-export="$RESULTS_DIR/k6-summary.json"
    
    if [ $? -eq 0 ]; then
        print_success "性能测试通过"
    else
        print_error "性能测试失败"
        return 1
    fi
}

# 快速测试（仅关键用例）
run_quick_tests() {
    print_header "快速测试（关键用例）"
    
    pytest "$TESTS_DIR/test_failover_unit.py" \
        -k "test_node1_available_should_use_node1 or test_node1_unavailable_should_failover_to_node2" \
        -v --tb=short
    
    if [ $? -eq 0 ]; then
        print_success "快速测试通过"
    else
        print_error "快速测试失败"
        return 1
    fi
}

# 详细测试（所有用例）
run_all_detailed_tests() {
    print_header "详细测试（所有用例）"
    
    print_info "阶段 1: 单元测试..."
    run_unit_tests || return 1
    
    print_info "阶段 2: 数据一致性测试..."
    run_consistency_tests || return 1
    
    print_info "阶段 3: API 集成测试..."
    run_api_tests || return 1
    
    print_info "阶段 4: 性能测试..."
    run_performance_tests || return 1
    
    print_success "所有详细测试通过"
}

# 生成报告
generate_reports() {
    print_header "生成测试报告"
    print_info "HTML 报告位置: $RESULTS_DIR/"
    print_info "打开浏览器查看: file://$RESULTS_DIR/pytest-unit.html"
}

# 主程序
main() {
    mkdir -p "$RESULTS_DIR"
    
    TEST_TYPE="${1:-all}"
    
    case "$TEST_TYPE" in
        quick)
            print_header "快速测试模式"
            run_quick_tests
            ;;
        unit)
            print_header "单元测试模式"
            run_unit_tests
            ;;
        api)
            print_header "API 集成测试模式"
            run_api_tests
            ;;
        consistency)
            print_header "数据一致性测试模式"
            run_consistency_tests
            ;;
        performance)
            print_header "性能测试模式"
            run_performance_tests
            ;;
        all-detailed)
            print_header "完整详细测试模式"
            run_all_detailed_tests
            ;;
        *)
            print_header "默认测试（单元 + 一致性 + 性能）"
            check_dependencies
            run_unit_tests
            run_consistency_tests
            
            # 性能测试可选（k6 可能未安装）
            if command -v k6 &> /dev/null; then
                run_performance_tests
            else
                print_info "跳过 k6 性能测试（k6 未安装）"
            fi
            ;;
    esac
    
    RESULT=$?
    echo ""
    generate_reports
    echo ""
    
    if [ $RESULT -eq 0 ]; then
        print_success "所有测试完成！"
    else
        print_error "部分测试失败"
        exit 1
    fi
}

main "$@"
