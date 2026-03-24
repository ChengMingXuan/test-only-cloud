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
# 使用 Python 解析 XML，避免 grep|awk 管道在单行超长 XML 上失败
if [ -n "$XML_FILE" ] && [ -f "$XML_FILE" ]; then
  XML_STATS=$(python3 -c "
import xml.etree.ElementTree as ET, sys
try:
    tree = ET.parse('$XML_FILE')
    root = tree.getroot()
    total=0; failures=0; errors=0; skipped=0; duration=0.0
    # 遍历所有 <testsuite> 元素（可能有多个：xdist/per-class/per-file）
    for ts in ([root] if root.tag == 'testsuite' else root.iter('testsuite')):
        total += int(ts.get('tests', 0))
        failures += int(ts.get('failures', 0))
        errors += int(ts.get('errors', 0))
        skipped += int(ts.get('skipped', 0))
        duration += float(ts.get('time', 0))
    # 如果 root 是 <testsuites>，只取直接子 <testsuite> 避免重复计数
    if root.tag == 'testsuites':
        total=0; failures=0; errors=0; skipped=0; duration=0.0
        for ts in root.findall('testsuite'):
            total += int(ts.get('tests', 0))
            failures += int(ts.get('failures', 0))
            errors += int(ts.get('errors', 0))
            skipped += int(ts.get('skipped', 0))
            duration += float(ts.get('time', 0))
    print(f'TOTAL={total}')
    print(f'FAILURES={failures}')
    print(f'ERRORS={errors}')
    print(f'SKIPPED={skipped}')
    print(f'DURATION={duration:.1f}')
except Exception as e:
    print('TOTAL=0', file=sys.stdout)
    print('FAILURES=0', file=sys.stdout)
    print('ERRORS=0', file=sys.stdout)
    print('SKIPPED=0', file=sys.stdout)
    print('DURATION=0.0', file=sys.stdout)
    print(f'XML解析错误: {e}', file=sys.stderr)
" 2>/dev/null || printf 'TOTAL=0\nFAILURES=0\nERRORS=0\nSKIPPED=0\nDURATION=0.0\n')
  while IFS='=' read -r key value; do
    case "$key" in
      TOTAL) TOTAL="$value" ;;
      FAILURES) FAILURES="$value" ;;
      ERRORS) ERRORS="$value" ;;
      SKIPPED) SKIPPED="$value" ;;
      DURATION) DURATION="$value" ;;
    esac
  done <<< "$XML_STATS"
  FAILED=$((FAILURES + ERRORS))
  PASSED=$((TOTAL - FAILED - SKIPPED))
  [ "$PASSED" -lt 0 ] && PASSED=0
fi

# 辅助函数：去除 ANSI 转义码
strip_ansi() {
  sed 's/\x1b\[[0-9;]*[a-zA-Z]//g; s/\x1b\][^\x07]*\x07//g'
}

# 方法2：从输出文本估算（Cypress、Playwright、Puppeteer、k6）
if [ "$TOTAL" -eq 0 ] && [ -n "$OUTPUT_FILE" ] && [ -f "$OUTPUT_FILE" ]; then
  # 预处理：生成去除 ANSI 码的临时文件
  CLEAN_FILE=$(mktemp)
  strip_ansi < "$OUTPUT_FILE" > "$CLEAN_FILE"
  echo "[DEBUG] 原始输出 $(wc -l < "$OUTPUT_FILE") 行, 清理后 $(wc -l < "$CLEAN_FILE") 行" >&2

  case "$TOOL" in
    cypress)
      # Cypress 输出: "N passing", "N failing"
      PASSED=$(grep -oP '\d+(?= passing)' "$CLEAN_FILE" 2>/dev/null | tail -1 || echo "0")
      FAILED=$(grep -oP '\d+(?= failing)' "$CLEAN_FILE" 2>/dev/null | tail -1 || echo "0")
      [ -z "$PASSED" ] && PASSED=0
      [ -z "$FAILED" ] && FAILED=0
      # fallback: 数 ✓ 和 ✗
      if [ "$PASSED" -eq 0 ] && [ "$FAILED" -eq 0 ]; then
        PASSED=$(grep -c '✓\|✔\|passing' "$CLEAN_FILE" 2>/dev/null || true)
        FAILED=$(grep -c '✗\|✘\|failing' "$CLEAN_FILE" 2>/dev/null || true)
        [ -z "$PASSED" ] && PASSED=0
        [ -z "$FAILED" ] && FAILED=0
      fi
      TOTAL=$((PASSED + FAILED))
      ;;
    playwright)
      # Playwright list reporter 输出: "X passed (Ym Zs)", "Y failed", "Z skipped"
      # 也尝试匹配 JUnit XML（如果同时生成了 XML）
      PW_XML="${OUTPUT_FILE%.txt}.xml"
      [ ! -f "$PW_XML" ] && PW_XML="TestResults/playwright-results.xml"
      if [ -f "$PW_XML" ]; then
        echo "[DEBUG] 使用 Playwright JUnit XML: $PW_XML" >&2
        PW_STATS=$(python3 -c "
import xml.etree.ElementTree as ET
try:
    root = ET.parse('$PW_XML').getroot()
    t=0;f=0;e=0;s=0;d=0.0
    for ts in (root.findall('testsuite') if root.tag=='testsuites' else [root]):
        t+=int(ts.get('tests',0));f+=int(ts.get('failures',0))
        e+=int(ts.get('errors',0));s+=int(ts.get('skipped',0))
        d+=float(ts.get('time',0))
    print(f'{t} {f} {e} {s} {d:.1f}')
except: print('0 0 0 0 0.0')
" 2>/dev/null || echo "0 0 0 0 0.0")
        read TOTAL FAILURES ERRORS SKIPPED DURATION <<< "$PW_STATS"
        FAILED=$((FAILURES + ERRORS))
        PASSED=$((TOTAL - FAILED - SKIPPED))
        [ "$PASSED" -lt 0 ] && PASSED=0
      fi
      # fallback: 文本解析
      if [ "$TOTAL" -eq 0 ]; then
        PASSED=$(grep -oP '\d+(?= passed)' "$CLEAN_FILE" 2>/dev/null | tail -1 || echo "0")
        FAILED=$(grep -oP '\d+(?= failed)' "$CLEAN_FILE" 2>/dev/null | tail -1 || echo "0")
        SKIPPED=$(grep -oP '\d+(?= skipped)' "$CLEAN_FILE" 2>/dev/null | tail -1 || echo "0")
        [ -z "$PASSED" ] && PASSED=0
        [ -z "$FAILED" ] && FAILED=0
        [ -z "$SKIPPED" ] && SKIPPED=0
        TOTAL=$((PASSED + FAILED + SKIPPED))
      fi
      echo "[DEBUG] Playwright 解析结果: total=$TOTAL passed=$PASSED failed=$FAILED skipped=$SKIPPED" >&2
      ;;
    puppeteer)
      # Jest: "Tests: X passed, Y failed, Z total"
      TOTAL=$(grep -oP 'Tests:\s+.*?(\d+)\s+total' "$CLEAN_FILE" | grep -oP '\d+(?=\s+total)' | tail -1 || echo "0")
      PASSED=$(grep -oP '\d+(?= passed)' "$CLEAN_FILE" | tail -1 || echo "0")
      FAILED=$(grep -oP '\d+(?= failed)' "$CLEAN_FILE" | tail -1 || echo "0")
      [ -z "$TOTAL" ] && TOTAL=0
      [ -z "$PASSED" ] && PASSED=0
      [ -z "$FAILED" ] && FAILED=0
      SKIPPED=$((TOTAL - PASSED - FAILED))
      [ "$SKIPPED" -lt 0 ] && SKIPPED=0
      ;;
    k6)
      # k6 优先读取 summary JSON（最可靠）
      K6_SUMMARY="TestResults/k6-summary.json"
      if [ -f "$K6_SUMMARY" ]; then
        echo "[DEBUG] 使用 k6 summary JSON: $K6_SUMMARY" >&2
        PASSED=$(python3 -c "import json; d=json.load(open('$K6_SUMMARY')); print(int(d.get('metrics',{}).get('checks',{}).get('values',{}).get('passes',0)))" 2>/dev/null || echo "0")
        FAILED=$(python3 -c "import json; d=json.load(open('$K6_SUMMARY')); print(int(d.get('metrics',{}).get('checks',{}).get('values',{}).get('fails',0)))" 2>/dev/null || echo "0")
        [ -z "$PASSED" ] && PASSED=0
        [ -z "$FAILED" ] && FAILED=0
        TOTAL=$((PASSED + FAILED))
        echo "[DEBUG] k6 JSON 解析: passes=$PASSED fails=$FAILED total=$TOTAL" >&2
      fi
      # fallback: 从文本输出解析 checks 行
      if [ "$TOTAL" -eq 0 ]; then
        CHECKS_LINE=$(grep -E 'checks' "$CLEAN_FILE" | grep -E '✓|✗|\d+%' | tail -1 || true)
        if [ -n "$CHECKS_LINE" ]; then
          echo "[DEBUG] k6 checks 行: $CHECKS_LINE" >&2
          PASSED=$(echo "$CHECKS_LINE" | grep -oP '✓\s*\K\d+' || echo "0")
          FAILED=$(echo "$CHECKS_LINE" | grep -oP '✗\s*\K\d+' || echo "0")
          [ -z "$PASSED" ] && PASSED=0
          [ -z "$FAILED" ] && FAILED=0
          TOTAL=$((PASSED + FAILED))
        fi
      fi
      # fallback: 从工作流汇总行解析
      if [ "$TOTAL" -eq 0 ]; then
        SUMMARY_LINE=$(grep -E '全量统计.*checks' "$CLEAN_FILE" | tail -1 || true)
        if [ -n "$SUMMARY_LINE" ]; then
          echo "[DEBUG] k6 汇总行: $SUMMARY_LINE" >&2
          PASSED=$(echo "$SUMMARY_LINE" | grep -oP '✓\s*\K\d+' || echo "0")
          FAILED=$(echo "$SUMMARY_LINE" | grep -oP '✗\s*\K\d+' || echo "0")
          [ -z "$PASSED" ] && PASSED=0
          [ -z "$FAILED" ] && FAILED=0
          TOTAL=$((PASSED + FAILED))
        fi
      fi
      # k6 耗时
      DURATION=$(grep -oP 'http_reqs\.+:\s+\K\d+' "$CLEAN_FILE" 2>/dev/null | tail -1 || echo "0")
      [ -z "$DURATION" ] && DURATION=0
      echo "[DEBUG] k6 最终结果: total=$TOTAL passed=$PASSED failed=$FAILED" >&2
      ;;
  esac
  rm -f "$CLEAN_FILE"
fi

# ── 安全网：确保所有数值变量都是单行数字（防止管道异常导致多行值）──
sanitize_num() { printf '%s\n' "$1" | grep -Eo '[0-9]+([.][0-9]+)?' | tail -1; }
TOTAL=$(sanitize_num "$TOTAL"); [ -z "$TOTAL" ] && TOTAL=0
PASSED=$(sanitize_num "$PASSED"); [ -z "$PASSED" ] && PASSED=0
FAILED=$(sanitize_num "$FAILED"); [ -z "$FAILED" ] && FAILED=0
SKIPPED=$(sanitize_num "$SKIPPED"); [ -z "$SKIPPED" ] && SKIPPED=0
ERRORS=$(sanitize_num "$ERRORS"); [ -z "$ERRORS" ] && ERRORS=0
DURATION=$(sanitize_num "$DURATION"); [ -z "$DURATION" ] && DURATION=0

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
FAILURES_JSON="[]"
if [ "$FAILED" -gt 0 ]; then
  # 从 JUnit XML 提取失败用例（pytest/selenium/playwright）
  if [ -n "$XML_FILE" ] && [ -f "$XML_FILE" ]; then
    FAILURES_JSON=$(python3 -c "
import xml.etree.ElementTree as ET, json, sys
try:
    tree = ET.parse('$XML_FILE')
    root = tree.getroot()
    failures = []
    for tc in root.iter('testcase'):
        fail = tc.find('failure')
        err = tc.find('error')
        node = fail if fail is not None else err
        if node is not None:
            failures.append({
                'name': tc.get('name',''),
                'classname': tc.get('classname',''),
                'status': 'failed' if fail is not None else 'error',
                'duration_s': float(tc.get('time','0')),
                'error': (node.get('message','') or node.text or '')[:500]
            })
    print(json.dumps(failures, ensure_ascii=False))
except Exception as e:
    print('[]', file=sys.stdout)
" 2>/dev/null || echo "[]")
  fi
  # 从输出文本提取失败信息（Cypress/Puppeteer/k6）
  if [ "$FAILURES_JSON" = "[]" ] && [ -n "$OUTPUT_FILE" ] && [ -f "$OUTPUT_FILE" ]; then
    FAILURE_DETAILS=$(grep -A 3 "FAILED\|FAIL\|Error\|✗\|✘\|AssertionError\|assert" "$OUTPUT_FILE" 2>/dev/null | head -200 || true)
  fi
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
  "failures": $FAILURES_JSON
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
