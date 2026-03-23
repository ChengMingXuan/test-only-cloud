#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# CI 标准报告生成器
# 生成与本地 generate-tool-reports.ps1 输出格式一致的 JSON + Markdown
# 用法: ./generate-ci-report.sh <tool> <xml_or_output> [options]
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

TOOL="${1:?用法: $0 <tool> [选项...]}"
shift

# 默认参数
XML_FILE=""
OUTPUT_FILE=""
LEVEL="smoke"
GIT_SHA="${GITHUB_SHA:-unknown}"
EVENT="${GITHUB_EVENT_NAME:-manual}"
REPORT_DIR="test-error-reports/latest/reports"

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --xml) XML_FILE="$2"; shift 2 ;;
    --output) OUTPUT_FILE="$2"; shift 2 ;;
    --level) LEVEL="$2"; shift 2 ;;
    --report-dir) REPORT_DIR="$2"; shift 2 ;;
    *) shift ;;
  esac
done

mkdir -p "$REPORT_DIR"

TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%S')
TIMESTAMP_DISPLAY=$(date -u '+%Y-%m-%d %H:%M:%S UTC')

# ─── 工具元信息 ───
declare -A DISPLAY_NAMES=(
  [pytest]="pytest（API功能测试）"
  [cypress]="Cypress（UI交互测试）"
  [playwright]="Playwright（E2E端到端测试）"
  [puppeteer]="Puppeteer（渲染/性能测试）"
  [selenium]="Selenium（浏览器兼容性测试）"
  [k6]="k6（性能压测）"
  [integration]="集成测试（C# xUnit）"
)

declare -A ICONS=(
  [pytest]="🐍" [cypress]="🌲" [playwright]="🎭"
  [puppeteer]="🤖" [selenium]="🔬" [k6]="⚡" [integration]="🔧"
)

declare -A STANDARD_CASES=(
  [pytest]=57774 [cypress]=9877 [playwright]=11093
  [puppeteer]=8137 [selenium]=6540 [k6]=3651 [integration]=1999
)

DISPLAY_NAME="${DISPLAY_NAMES[$TOOL]:-$TOOL}"
ICON="${ICONS[$TOOL]:-🔧}"
STD_CASES="${STANDARD_CASES[$TOOL]:-0}"

# ─── 解析测试结果 ───
TOTAL=0; PASSED=0; FAILED=0; SKIPPED=0; ERRORS=0; DURATION=0

# 方法1：从 JUnit XML 解析（pytest、selenium、integration）
if [ -n "$XML_FILE" ] && [ -f "$XML_FILE" ]; then
  TOTAL=$(grep -oP 'tests="\K[0-9]+' "$XML_FILE" | head -1 || echo "0")
  FAILURES=$(grep -oP 'failures="\K[0-9]+' "$XML_FILE" | head -1 || echo "0")
  ERRORS=$(grep -oP 'errors="\K[0-9]+' "$XML_FILE" | head -1 || echo "0")
  SKIPPED=$(grep -oP 'skipped="\K[0-9]+' "$XML_FILE" | head -1 || echo "0")
  DURATION=$(grep -oP 'time="\K[0-9.]+' "$XML_FILE" | head -1 || echo "0")
  FAILED=$((FAILURES + ERRORS))
  PASSED=$((TOTAL - FAILED - SKIPPED))
  [ "$PASSED" -lt 0 ] && PASSED=0
fi

# 方法2：从输出文本估算（Cypress、Playwright、Puppeteer、k6）
if [ "$TOTAL" -eq 0 ] && [ -n "$OUTPUT_FILE" ] && [ -f "$OUTPUT_FILE" ]; then
  case "$TOOL" in
    cypress)
      PASSED=$(grep -cE '✓|passing' "$OUTPUT_FILE" 2>/dev/null || echo "0")
      FAILED=$(grep -cE '✗|failing' "$OUTPUT_FILE" 2>/dev/null || echo "0")
      TOTAL=$((PASSED + FAILED))
      ;;
    playwright)
      # Playwright: "X passed", "Y failed", "Z skipped"
      PASSED=$(grep -oP '\d+(?= passed)' "$OUTPUT_FILE" | tail -1 || echo "0")
      FAILED=$(grep -oP '\d+(?= failed)' "$OUTPUT_FILE" | tail -1 || echo "0")
      SKIPPED=$(grep -oP '\d+(?= skipped)' "$OUTPUT_FILE" | tail -1 || echo "0")
      [ -z "$PASSED" ] && PASSED=0
      [ -z "$FAILED" ] && FAILED=0
      [ -z "$SKIPPED" ] && SKIPPED=0
      TOTAL=$((PASSED + FAILED + SKIPPED))
      ;;
    puppeteer)
      # Jest: "Tests: X passed, Y failed, Z total"
      TOTAL=$(grep -oP 'Tests:\s+.*?(\d+)\s+total' "$OUTPUT_FILE" | grep -oP '\d+(?=\s+total)' | tail -1 || echo "0")
      PASSED=$(grep -oP '\d+(?= passed)' "$OUTPUT_FILE" | tail -1 || echo "0")
      FAILED=$(grep -oP '\d+(?= failed)' "$OUTPUT_FILE" | tail -1 || echo "0")
      [ -z "$TOTAL" ] && TOTAL=0
      [ -z "$PASSED" ] && PASSED=0
      [ -z "$FAILED" ] && FAILED=0
      SKIPPED=$((TOTAL - PASSED - FAILED))
      [ "$SKIPPED" -lt 0 ] && SKIPPED=0
      ;;
    k6)
      # k6: 从 summary JSON 解析 checks
      K6_SUMMARY="TestResults/k6-summary.json"
      if [ -f "$K6_SUMMARY" ]; then
        PASSED=$(python3 -c "import json; d=json.load(open('$K6_SUMMARY')); print(d.get('metrics',{}).get('checks',{}).get('values',{}).get('passes',0))" 2>/dev/null || echo "0")
        FAILED=$(python3 -c "import json; d=json.load(open('$K6_SUMMARY')); print(d.get('metrics',{}).get('checks',{}).get('values',{}).get('fails',0))" 2>/dev/null || echo "0")
        TOTAL=$((PASSED + FAILED))
      else
        PASSED=$(grep -cE '✓|✗' "$OUTPUT_FILE" 2>/dev/null || echo "0")
        TOTAL=$PASSED
      fi
      ;;
  esac
fi

# 计算通过率
if [ "$TOTAL" -gt 0 ]; then
  PASS_RATE=$(python3 -c "print(round($PASSED / $TOTAL * 100, 2))" 2>/dev/null || echo "0")
else
  PASS_RATE=0
fi

# 判断状态
if [ "$FAILED" -eq 0 ] && [ "$TOTAL" -gt 0 ]; then
  STATUS_TEXT="✅ 全部通过"
  CAN_RELEASE=true
  GATE_TEXT="全部通过 - 可发布"
elif [ "$TOTAL" -eq 0 ]; then
  STATUS_TEXT="⚠️ 未执行"
  CAN_RELEASE=false
  GATE_TEXT="未收集到测试结果"
else
  STATUS_TEXT="❌ 有失败 ($FAILED)"
  CAN_RELEASE=false
  GATE_TEXT="存在失败用例 - 不可发布"
fi

# 提取失败详情
FAILURE_DETAILS=""
if [ "$FAILED" -gt 0 ] && [ -n "$OUTPUT_FILE" ] && [ -f "$OUTPUT_FILE" ]; then
  FAILURE_DETAILS=$(grep -A 3 "FAILED\|FAIL\|Error\|✗\|✘\|AssertionError\|assert" "$OUTPUT_FILE" 2>/dev/null | head -200 || true)
fi

# ─── 生成 JSON 报告（与本地 generate-tool-reports.ps1 格式一致）───
MEASUREMENT_MODE="cases"
[ "$TOOL" = "k6" ] && MEASUREMENT_MODE="checks"

cat > "$REPORT_DIR/${TOOL}-report.json" << JSONEOF
{
  "tool": "$TOOL",
  "displayName": "$DISPLAY_NAME",
  "icon": "$ICON",
  "standardCases": $STD_CASES,
  "summary": {
    "total": $TOTAL,
    "passed": $PASSED,
    "failed": $FAILED,
    "skipped": $SKIPPED,
    "passRate": $PASS_RATE,
    "duration_s": $DURATION,
    "timestamp": "$TIMESTAMP",
    "source": "GitHub Actions CI ($LEVEL)",
    "measurementMode": "$MEASUREMENT_MODE",
    "comparableTotal": $TOTAL,
    "executedFiles": 0
  },
  "gateStatus": {
    "canRelease": $CAN_RELEASE,
    "statusText": "$GATE_TEXT"
  },
  "ci": {
    "gitCommit": "$GIT_SHA",
    "eventName": "$EVENT",
    "testLevel": "$LEVEL",
    "runnerOS": "ubuntu-latest",
    "timestamp": "$TIMESTAMP_DISPLAY"
  },
  "fileCount": 0,
  "files": [],
  "failures": []
}
JSONEOF

# ─── 生成 Markdown 报告（与本地格式一致）───
cat > "$REPORT_DIR/${TOOL}-report.md" << MDEOF
# $ICON $DISPLAY_NAME — 测试报告

> 来源：GitHub Actions CI | 级别：$LEVEL | $TIMESTAMP_DISPLAY

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | $STD_CASES |
| 实际执行 | $TOTAL |
| ✅ 通过 | $PASSED |
| ❌ 失败 | $FAILED |
| ⏭️ 跳过 | $SKIPPED |
| 通过率 | ${PASS_RATE}% |
| 耗时(s) | $DURATION |

## 发布门禁

- **状态**：$STATUS_TEXT
- **结论**：$GATE_TEXT

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | \`$GIT_SHA\` |
| 触发方式 | $EVENT |
| 运行环境 | ubuntu-latest |
| 测试级别 | $LEVEL |
MDEOF

if [ -n "$FAILURE_DETAILS" ]; then
  cat >> "$REPORT_DIR/${TOOL}-report.md" << FAILEOF

## 失败详情

\`\`\`
$FAILURE_DETAILS
\`\`\`
FAILEOF
fi

echo "✅ 已生成 $REPORT_DIR/${TOOL}-report.{json,md}"
