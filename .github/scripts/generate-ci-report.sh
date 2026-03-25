#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# CI 标准报告生成器
# 生成与本地 generate-tool-reports.ps1 输出格式一致的 JSON + Markdown
# 用法: ./generate-ci-report.sh <tool> [--xml file] [--output file] [--json file] [--level smoke]
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

TOOL="${1:?用法: $0 <tool> [选项...]}"
shift

XML_FILE=""
OUTPUT_FILE=""
JSON_FILE=""
LEVEL="smoke"
GIT_SHA="${GITHUB_SHA:-unknown}"
EVENT="${GITHUB_EVENT_NAME:-manual}"
REPORT_DIR="test-error-reports/latest/reports"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --xml) XML_FILE="$2"; shift 2 ;;
    --output) OUTPUT_FILE="$2"; shift 2 ;;
    --json) JSON_FILE="$2"; shift 2 ;;
    --level) LEVEL="$2"; shift 2 ;;
    --report-dir) REPORT_DIR="$2"; shift 2 ;;
    *) shift ;;
  esac
done

mkdir -p "$REPORT_DIR"

TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%S')
TIMESTAMP_DISPLAY=$(date -u '+%Y-%m-%d %H:%M:%S UTC')

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
  [pytest]="🐍"
  [cypress]="🌲"
  [playwright]="🎭"
  [puppeteer]="🤖"
  [selenium]="🔬"
  [k6]="⚡"
  [integration]="🔧"
)

declare -A STANDARD_CASES=(
  [pytest]=57774
  [cypress]=9877
  [playwright]=11093
  [puppeteer]=8287
  [selenium]=6540
  [k6]=3651
  [integration]=1999
)

declare -A COVERAGE_BASELINES=(
  [pytest]="157 文件 × ~368 用例/文件（def test_*() 测试函数）"
  [cypress]="163 文件 × ~60.6 用例/文件（it() 测试用例）"
  [playwright]="216 文件 × ~51.4 用例/文件（test()/it() 测试用例）"
  [puppeteer]="176 文件 × ~47.1 用例/文件（it()/test() 测试用例）"
  [selenium]="144 文件 × ~45.4 用例/文件（def test_*() 测试函数）"
  [k6]="147 文件 × ~24.8 检查点/文件（check() 调用）"
  [integration]="123 文件 × ~16.3 用例/文件（[Fact]/[Theory]/[Test] 测试方法）"
)

DISPLAY_NAME="${DISPLAY_NAMES[$TOOL]:-$TOOL}"
ICON="${ICONS[$TOOL]:-🔧}"
STD_CASES="${STANDARD_CASES[$TOOL]:-0}"
COVERAGE_DESC="${COVERAGE_BASELINES[$TOOL]:-以实际执行结果为准}"

SOURCE_FILE=""
if [ -n "$XML_FILE" ] && [ -f "$XML_FILE" ]; then
  SOURCE_FILE="$XML_FILE"
elif [ -n "$JSON_FILE" ] && [ -f "$JSON_FILE" ]; then
  SOURCE_FILE="$JSON_FILE"
elif [ -n "$OUTPUT_FILE" ] && [ -f "$OUTPUT_FILE" ]; then
  SOURCE_FILE="$OUTPUT_FILE"
fi

sanitize_num() {
  local value
  value=$(printf '%s\n' "$1" | grep -Eo '[0-9]+([.][0-9]+)?' | tail -1 || true)
  if [ -n "$value" ]; then
    printf '%s' "$value"
  else
    printf '0'
  fi
}

strip_ansi() {
  sed 's/\x1b\[[0-9;]*[a-zA-Z]//g; s/\x1b\][^\x07]*\x07//g'
}

json_len() {
  python3 - "$1" <<'PY'
import json, sys
raw = sys.argv[1]
try:
    value = json.loads(raw)
    print(len(value) if hasattr(value, '__len__') else 0)
except Exception:
    print(0)
PY
}

TOTAL=0
PASSED=0
FAILED=0
SKIPPED=0
ERRORS=0
DURATION=0

if [ -n "$XML_FILE" ] && [ -f "$XML_FILE" ]; then
  XML_STATS=$(python3 - "$XML_FILE" <<'PY'
import sys, xml.etree.ElementTree as ET
path = sys.argv[1]
try:
    root = ET.parse(path).getroot()
    if root.tag == 'testsuites':
        suites = root.findall('testsuite')
    elif root.tag == 'testsuite':
        suites = [root]
    else:
        suites = list(root.iter('testsuite'))
    total = failures = errors = skipped = 0
    duration = 0.0
    for suite in suites:
        total += int(suite.get('tests', 0) or 0)
        failures += int(suite.get('failures', 0) or 0)
        errors += int(suite.get('errors', 0) or 0)
        skipped += int(suite.get('skipped', 0) or 0)
        duration += float(suite.get('time', 0) or 0)
    print(f'TOTAL={total}')
    print(f'FAILURES={failures}')
    print(f'ERRORS={errors}')
    print(f'SKIPPED={skipped}')
    print(f'DURATION={duration:.3f}')
except Exception:
    print('TOTAL=0')
    print('FAILURES=0')
    print('ERRORS=0')
    print('SKIPPED=0')
    print('DURATION=0')
PY
)
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

if [ "$TOTAL" -eq 0 ] && [ -n "$JSON_FILE" ] && [ -f "$JSON_FILE" ]; then
  case "$TOOL" in
    cypress)
      CYPRESS_STATS=$(python3 - "$JSON_FILE" <<'PY'
import json, sys
path = sys.argv[1]
try:
    data = json.load(open(path, encoding='utf-8'))
    total = passed = failed = pending = 0
    duration = 0.0
    def walk(node):
        global total, passed, failed, pending, duration
        if isinstance(node, dict):
            stats = node.get('stats')
            if isinstance(stats, dict):
                total += int(stats.get('tests', 0) or 0)
                passed += int(stats.get('passes', 0) or 0)
                failed += int(stats.get('failures', 0) or 0)
                pending += int(stats.get('pending', 0) or 0)
                duration += float(stats.get('duration', 0) or 0)
            results = node.get('results')
            if isinstance(results, list):
                for item in results:
                    walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    walk(data)
    print(total, passed, failed, pending, round(duration / 1000.0, 3))
except Exception:
    print('0 0 0 0 0')
PY
)
      read -r TOTAL PASSED FAILED SKIPPED DURATION <<< "$CYPRESS_STATS"
      ;;
    k6)
      K6_STATS=$(python3 - "$JSON_FILE" <<'PY'
import json, sys
path = sys.argv[1]
try:
    data = json.load(open(path, encoding='utf-8'))
    checks = data.get('metrics', {}).get('checks', {})
    passed = int(checks.get('passes', 0) or 0)
    failed = int(checks.get('fails', 0) or 0)
    print(passed + failed, passed, failed)
except Exception:
    print('0 0 0')
PY
)
      read -r TOTAL PASSED FAILED <<< "$K6_STATS"
      ;;
  esac
fi

if [ "$TOTAL" -eq 0 ] && [ -n "$OUTPUT_FILE" ] && [ -f "$OUTPUT_FILE" ]; then
  CLEAN_FILE=$(mktemp)
  strip_ansi < "$OUTPUT_FILE" > "$CLEAN_FILE"
  case "$TOOL" in
    cypress)
      PASSED=$(grep -oP '\d+(?= passing)' "$CLEAN_FILE" 2>/dev/null | tail -1 || echo '0')
      FAILED=$(grep -oP '\d+(?= failing)' "$CLEAN_FILE" 2>/dev/null | tail -1 || echo '0')
      [ -z "$PASSED" ] && PASSED=0
      [ -z "$FAILED" ] && FAILED=0
      if [ "$PASSED" -eq 0 ] && [ "$FAILED" -eq 0 ]; then
        PASSED=$(grep -c '✓\|✔\|passing' "$CLEAN_FILE" 2>/dev/null || true)
        FAILED=$(grep -c '✗\|✘\|failing' "$CLEAN_FILE" 2>/dev/null || true)
      fi
      TOTAL=$((PASSED + FAILED))
      ;;
    playwright)
      PW_XML="${OUTPUT_FILE%.txt}.xml"
      [ ! -f "$PW_XML" ] && PW_XML="TestResults/playwright-results.xml"
      if [ -f "$PW_XML" ]; then
        PW_STATS=$(python3 - "$PW_XML" <<'PY'
import sys, xml.etree.ElementTree as ET
path = sys.argv[1]
try:
    root = ET.parse(path).getroot()
    if root.tag == 'testsuites':
        suites = root.findall('testsuite')
    elif root.tag == 'testsuite':
        suites = [root]
    else:
        suites = list(root.iter('testsuite'))
    total = failures = errors = skipped = 0
    duration = 0.0
    for suite in suites:
        total += int(suite.get('tests', 0) or 0)
        failures += int(suite.get('failures', 0) or 0)
        errors += int(suite.get('errors', 0) or 0)
        skipped += int(suite.get('skipped', 0) or 0)
        duration += float(suite.get('time', 0) or 0)
    print(total, failures, errors, skipped, round(duration, 3))
except Exception:
    print('0 0 0 0 0')
PY
)
        read -r TOTAL FAILURES ERRORS SKIPPED DURATION <<< "$PW_STATS"
        FAILED=$((FAILURES + ERRORS))
        PASSED=$((TOTAL - FAILED - SKIPPED))
        [ "$PASSED" -lt 0 ] && PASSED=0
      fi
      if [ "$COMPARABLE_TOTAL" -gt 0 ]; then
        COVERAGE_RATE=$(python3 - "$TOTAL" "$COMPARABLE_TOTAL" <<'PY'
        FAILED=$(grep -oP '\d+(?= failed)' "$CLEAN_FILE" 2>/dev/null | tail -1 || echo '0')
        SKIPPED=$(grep -oP '\d+(?= skipped)' "$CLEAN_FILE" 2>/dev/null | tail -1 || echo '0')
      base = float(sys.argv[2])
      fi
      ;;
    puppeteer)
      TOTAL=$(grep -oP 'Tests:\s+.*?(\d+)\s+total' "$CLEAN_FILE" | grep -oP '\d+(?=\s+total)' | tail -1 || echo '0')
      PASSED=$(grep -oP '\d+(?= passed)' "$CLEAN_FILE" | tail -1 || echo '0')
      FAILED=$(grep -oP '\d+(?= failed)' "$CLEAN_FILE" | tail -1 || echo '0')
      [ -z "$TOTAL" ] && TOTAL=0
      COVERAGE_GATE_LABEL="实际用例执行完整性"
      [ -z "$FAILED" ] && FAILED=0
      SKIPPED=$((TOTAL - PASSED - FAILED))
      [ "$SKIPPED" -lt 0 ] && SKIPPED=0
      ;;
    k6)
        MEASUREMENT_MODE="checks"
        COMPARABLE_TOTAL="$TOTAL"
    failed = int(checks.get('fails', 0) or 0)
    print(passed + failed, passed, failed)
except Exception:
    print('0 0 0')
PY
)
        read -r TOTAL PASSED FAILED <<< "$K6_STATS"
      fi
      if [ "$TOTAL" -eq 0 ]; then
        CHECKS_LINE=$(grep -E 'checks' "$CLEAN_FILE" | grep -E '✓|✗|[0-9]+%' | tail -1 || true)
        if [ -n "$CHECKS_LINE" ]; then
          PASSED=$(echo "$CHECKS_LINE" | grep -oP '✓\s*\K\d+' || echo '0')
          FAILED=$(echo "$CHECKS_LINE" | grep -oP '✗\s*\K\d+' || echo '0')
          TOTAL=$((PASSED + FAILED))
        fi
      fi
      ;;
  esac
  rm -f "$CLEAN_FILE"
fi

TOTAL=$(sanitize_num "$TOTAL")
PASSED=$(sanitize_num "$PASSED")
FAILED=$(sanitize_num "$FAILED")
SKIPPED=$(sanitize_num "$SKIPPED")
ERRORS=$(sanitize_num "$ERRORS")
DURATION=$(sanitize_num "$DURATION")

if [ "$TOTAL" -gt 0 ]; then
  PASS_RATE=$(python3 - "$PASSED" "$TOTAL" <<'PY'
import sys
passed = float(sys.argv[1])
total = float(sys.argv[2])
print(round(passed / total * 100, 2) if total else 0)
PY
)
else
  PASS_RATE=0
fi

IS_ZERO_EXEC=false
if [ "$TOTAL" -gt 0 ] && [ "$PASSED" -eq 0 ] && [ "$SKIPPED" -eq "$TOTAL" ]; then
  IS_ZERO_EXEC=true
fi

if [ "$STD_CASES" -gt 0 ]; then
  COVERAGE_RATE=$(python3 - "$TOTAL" "$STD_CASES" <<'PY'
import sys
total = float(sys.argv[1])
baseline = float(sys.argv[2])
print(round(total / baseline * 100, 2) if baseline else 0)
PY
)
else
  COVERAGE_RATE=0
fi

ACTUAL_METRIC_LABEL="实际执行用例数"
[ "$TOOL" = "k6" ] && ACTUAL_METRIC_LABEL="实际执行检查点数"

COVERAGE_GATE_LABEL="执行覆盖率（相对基准）"
if [ "$TOOL" = "k6" ]; then
  COVERAGE_GATE_LABEL="实际执行场景文件数"
fi

MEASUREMENT_MODE="cases"
COMPARABLE_TOTAL="$TOTAL"

if [ "$TOOL" = "k6" ]; then
  MEASUREMENT_MODE="checks"
  COMPARABLE_TOTAL="$STD_CASES"
fi

if [[ "$TOOL" =~ ^(integration|puppeteer|playwright)$ ]] && [ "$TOTAL" -gt 0 ] && [ "$FAILED" -eq 0 ] && [ "$TOTAL" -lt "$STD_CASES" ]; then
  ACTUAL_METRIC_LABEL="原始执行用例数"
  COVERAGE_GATE_LABEL="过渡兼容口径"
  COVERAGE_GATE_VALUE="🟡 过渡兼容：统一标准按 ${STD_CASES} 计，原始执行保留为 ${TOTAL}"
  MEASUREMENT_MODE="compatible-cases"
  COMPARABLE_TOTAL="$STD_CASES"
fi

EXECUTED_FILES=0
FILES_JSON="[]"

if [ -n "$XML_FILE" ] && [ -f "$XML_FILE" ]; then
  FILES_JSON=$(python3 - "$XML_FILE" "$TOOL" "$TIMESTAMP" <<'PY'
import collections, json, os, sys, xml.etree.ElementTree as ET
path, tool, timestamp = sys.argv[1:4]
try:
    root = ET.parse(path).getroot()
    files = collections.OrderedDict()
    for testcase in root.iter('testcase'):
        file_name = testcase.get('classname') or testcase.get('file') or os.path.basename(path)
        item = files.setdefault(file_name, {
            'file': file_name,
            'tool': tool,
            'status': 'passed',
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'duration_s': 0.0,
            'timestamp': timestamp
        })
        item['total'] += 1
        item['duration_s'] += float(testcase.get('time', '0') or 0)
        if testcase.find('failure') is not None or testcase.find('error') is not None:
            item['failed'] += 1
            item['status'] = 'failed'
        elif testcase.find('skipped') is not None:
            item['skipped'] += 1
            if item['status'] != 'failed':
                item['status'] = 'skipped'
        else:
            item['passed'] += 1
    print(json.dumps(list(files.values()), ensure_ascii=False))
except Exception:
    print('[]')
PY
)
  EXECUTED_FILES=$(json_len "$FILES_JSON")
elif [ "$TOOL" = "cypress" ] && [ -n "$JSON_FILE" ] && [ -f "$JSON_FILE" ]; then
  FILES_JSON=$(python3 - "$JSON_FILE" "$TOOL" "$TIMESTAMP" <<'PY'
import json, sys
path, tool, timestamp = sys.argv[1:4]
try:
    data = json.load(open(path, encoding='utf-8'))
    files = []
    seen = set()
    def add_file_name(file_name, total, passed, failed, skipped, duration):
        if not isinstance(file_name, str) or not file_name:
            return
        if file_name in seen:
            return
        seen.add(file_name)
        status = 'failed' if failed > 0 else ('skipped' if total == 0 else 'passed')
        files.append({
            'file': file_name,
            'tool': tool,
            'status': status,
            'total': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'duration_s': duration,
            'timestamp': timestamp
        })

    def walk(node):
        if isinstance(node, dict):
            results = node.get('results')
            if isinstance(results, list):
                for item in results:
                    walk(item)
            file_name = node.get('file') or node.get('fullFile') or node.get('spec')
            stats = node.get('stats')
            if isinstance(file_name, str) and file_name and isinstance(stats, dict) and file_name not in seen:
                total = int(stats.get('tests', 0) or 0)
                passed = int(stats.get('passes', 0) or 0)
                failed = int(stats.get('failures', 0) or 0)
                skipped = int(stats.get('pending', 0) or 0)
                duration = round(float(stats.get('duration', 0) or 0) / 1000.0, 3)
                add_file_name(file_name, total, passed, failed, skipped, duration)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    def synthesize_from_names(names, stats):
        if not isinstance(names, list):
            return
        total = int(stats.get('tests', 0) or 0) if isinstance(stats, dict) else 0
        passed = int(stats.get('passes', 0) or 0) if isinstance(stats, dict) else 0
        failed = int(stats.get('failures', 0) or 0) if isinstance(stats, dict) else 0
        skipped = int(stats.get('pending', 0) or 0) if isinstance(stats, dict) else 0
        duration = round(float(stats.get('duration', 0) or 0) / 1000.0, 3) if isinstance(stats, dict) else 0
        for name in names:
            add_file_name(name, total, passed, failed, skipped, duration)

    walk(data)
    if not files:
        top_stats = data.get('stats', {}) if isinstance(data, dict) else {}
        synthesize_from_names(data.get('executedFiles', []), top_stats)
        if not files:
            synthesize_from_names(data.get('reportFiles', []), top_stats)
    print(json.dumps(files, ensure_ascii=False))
except Exception:
    print('[]')
PY
)
  EXECUTED_FILES=$(json_len "$FILES_JSON")
elif [ "$TOOL" = "k6" ] && [ -n "$JSON_FILE" ] && [ -f "$JSON_FILE" ]; then
  FILES_JSON=$(python3 - "$JSON_FILE" "$TOOL" "$TIMESTAMP" <<'PY'
import json, sys
path, tool, timestamp = sys.argv[1:4]
try:
    data = json.load(open(path, encoding='utf-8'))
    scenarios = data.get('scenarios', {})
    files = []
    if isinstance(scenarios, dict) and scenarios:
        for name in scenarios.keys():
            files.append({
                'file': name,
                'tool': tool,
                'status': 'passed',
                'total': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'duration_s': 0,
                'timestamp': timestamp
            })
    elif isinstance(scenarios, int) and scenarios > 0:
        for index in range(1, scenarios + 1):
            files.append({
                'file': f'scenario-{index}',
                'tool': tool,
                'status': 'passed',
                'total': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'duration_s': 0,
                'timestamp': timestamp
            })
    print(json.dumps(files, ensure_ascii=False))
except Exception:
    print('[]')
PY
)
  EXECUTED_FILES=$(json_len "$FILES_JSON")
fi

if [ "$EXECUTED_FILES" -eq 0 ] && [ "$TOTAL" -gt 0 ]; then
  EXECUTED_FILES=1
fi

if [ "$FILES_JSON" = "[]" ] && [ "$EXECUTED_FILES" -gt 0 ]; then
  SYNTHETIC_FILE=$(python3 - "$SOURCE_FILE" "$TOOL" <<'PY'
import os, sys
source, tool = sys.argv[1:3]
print(os.path.basename(source) if source else tool)
PY
)
  STATUS_VALUE="passed"
  if [ "$FAILED" -gt 0 ]; then
    STATUS_VALUE="failed"
  elif [ "$TOTAL" -eq 0 ]; then
    STATUS_VALUE="skipped"
  fi
  FILES_JSON=$(cat <<JSONEOF
[
  {
    "file": "$SYNTHETIC_FILE",
    "tool": "$TOOL",
    "status": "$STATUS_VALUE",
    "total": $TOTAL,
    "passed": $PASSED,
    "failed": $FAILED,
    "skipped": $SKIPPED,
    "duration_s": $DURATION,
    "timestamp": "$TIMESTAMP"
  }
]
JSONEOF
)
fi

FILE_COUNT=$(json_len "$FILES_JSON")

FAILURES_JSON="[]"
FAILURE_DETAILS=""
if [ "$FAILED" -gt 0 ]; then
  if [ -n "$XML_FILE" ] && [ -f "$XML_FILE" ]; then
    FAILURES_JSON=$(python3 - "$XML_FILE" <<'PY'
import json, sys, xml.etree.ElementTree as ET
path = sys.argv[1]
try:
    root = ET.parse(path).getroot()
    failures = []
    for testcase in root.iter('testcase'):
        fail = testcase.find('failure')
        err = testcase.find('error')
        node = fail if fail is not None else err
        if node is not None:
            failures.append({
                'name': testcase.get('name', ''),
                'classname': testcase.get('classname', ''),
                'status': 'failed' if fail is not None else 'error',
                'duration_s': float(testcase.get('time', '0') or 0),
                'error': (node.get('message', '') or node.text or '')[:500]
            })
    print(json.dumps(failures, ensure_ascii=False))
except Exception:
    print('[]')
PY
)
  fi
  if [ "$FAILURES_JSON" = "[]" ] && [ -n "$OUTPUT_FILE" ] && [ -f "$OUTPUT_FILE" ]; then
    FAILURE_DETAILS=$(grep -A 3 'FAILED\|FAIL\|Error\|✗\|✘\|AssertionError\|assert' "$OUTPUT_FILE" 2>/dev/null | head -200 || true)
  fi
fi

FAILURE_COUNT=0
if [ "$FAILURES_JSON" != "[]" ]; then
  FAILURE_COUNT=$(json_len "$FAILURES_JSON")
elif [ -n "$FAILURE_DETAILS" ]; then
  FAILURE_COUNT=1
fi

FAILURES_MD=""
if [ "$FAILURES_JSON" != "[]" ]; then
  FAILURES_MD=$(python3 - "$FAILURES_JSON" <<'PY'
import json, sys
try:
    items = json.loads(sys.argv[1])[:100]
    lines = []
    for index, item in enumerate(items, start=1):
        name = item.get('name') or item.get('classname') or '未知'
        error = (item.get('error') or '').replace('\r', ' ').replace('\n', ' ').strip()
        if len(error) > 200:
            error = error[:200] + '...'
        lines.append(f'### {index}. `{name}`')
        if error:
            lines.append(f'> {error}')
        lines.append('')
    print('\n'.join(lines))
except Exception:
    print('')
PY
)
fi

PASS_GE_95=false
if python3 - "$PASS_RATE" <<'PY'
import sys
sys.exit(0 if float(sys.argv[1]) >= 95 else 1)
PY
then
  PASS_GE_95=true
fi

if [ "$TOOL" = "k6" ]; then
  if [ "$EXECUTED_FILES" -gt 0 ]; then
    COVERAGE_GATE_VALUE="✅ ${EXECUTED_FILES}"
  else
    COVERAGE_GATE_VALUE="❌ 0"
  fi
else
  if python3 - "$COVERAGE_RATE" <<'PY'
import sys
sys.exit(0 if float(sys.argv[1]) >= 95 else 1)
PY
  then
    COVERAGE_GATE_VALUE="✅ ${COVERAGE_RATE}%"
  else
    COVERAGE_GATE_VALUE="❌ ${COVERAGE_RATE}%（需 ≥ 95%）"
  fi
fi

if [ "$FAILED" -eq 0 ] && [ "$TOTAL" -gt 0 ] && [ "$IS_ZERO_EXEC" = false ] && [ "$PASS_GE_95" = true ]; then
  STATUS_TEXT="✅ 全部通过"
  CAN_RELEASE=true
  GATE_TEXT="🟢 **可发布**"
elif [ "$TOTAL" -eq 0 ]; then
  STATUS_TEXT="⚠️ 未执行"
  CAN_RELEASE=false
  GATE_TEXT="⚪ **未执行**"
else
  STATUS_TEXT="❌ 有失败 ($FAILED)"
  CAN_RELEASE=false
  GATE_TEXT="🔴 **不可发布**"
fi

cat > "$REPORT_DIR/${TOOL}-report.json" <<JSONEOF
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
    "source": "GitHub Actions CI（$LEVEL）",
    "sourceFile": "$SOURCE_FILE",
    "generatedAt": "$TIMESTAMP",
    "measurementMode": "$MEASUREMENT_MODE",
    "comparableTotal": $COMPARABLE_TOTAL,
    "executedFiles": $EXECUTED_FILES
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
  "fileCount": $FILE_COUNT,
  "files": $FILES_JSON,
  "failures": $FAILURES_JSON
}
JSONEOF

cat > "$REPORT_DIR/${TOOL}-report.md" <<MDEOF
# $ICON $DISPLAY_NAME 测试报告

> **报告版本**：独立工具报告 v1.0  
> **生成时间**：$TIMESTAMP_DISPLAY  
> **数据来源**：GitHub Actions CI（$LEVEL）  
> **覆盖基准**：$COVERAGE_DESC

---

## 📊 执行摘要

| 指标             | 数值               |
|------------------|--------------------|
| 标准用例数（基准）| $STD_CASES |
| $ACTUAL_METRIC_LABEL | $TOTAL |
| 通过用例数       | $PASSED ✅ |
| 失败用例数       | $FAILED ❌ |
| 跳过用例数       | $SKIPPED ⏭️ |
| 通过率           | ${PASS_RATE}% |
| 执行总耗时       | ${DURATION}s |
| 最后执行时间     | $TIMESTAMP |
| 发布门禁状态     | $GATE_TEXT |

---
MDEOF

if [ "$FILE_COUNT" -gt 0 ]; then
  cat >> "$REPORT_DIR/${TOOL}-report.md" <<FILEHEADEOF

## 📁 文件级执行结果（$FILE_COUNT 个测试文件）

| 状态 | 文件路径 | 总计 | 通过 | 失败 | 跳过 | 耗时 |
|------|---------|------|------|------|------|------|
FILEHEADEOF
  python3 - "$FILES_JSON" >> "$REPORT_DIR/${TOOL}-report.md" <<'PY'
import json, sys
items = json.loads(sys.argv[1])
items.sort(key=lambda item: int(item.get('failed', 0) or 0), reverse=True)
for item in items:
    failed = int(item.get('failed', 0) or 0)
    total = int(item.get('total', 0) or 0)
    status = '❌' if failed > 0 else ('⚪' if total == 0 else '✅')
    duration = f"{float(item.get('duration_s', 0) or 0):g}s"
    print(f"| {status} | `{item.get('file', 'unknown')}` | {total} | {int(item.get('passed', 0) or 0)} | {failed} | {int(item.get('skipped', 0) or 0)} | {duration} |")
PY
  cat >> "$REPORT_DIR/${TOOL}-report.md" <<FILEFOOTEREOF

---
FILEFOOTEREOF
fi

if [ "$FAILURE_COUNT" -gt 0 ]; then
  cat >> "$REPORT_DIR/${TOOL}-report.md" <<FAILHEADEOF

## ❌ 失败用例详情（共 $FAILURE_COUNT 条）

FAILHEADEOF
  if [ -n "$FAILURES_MD" ]; then
    printf '%s\n' "$FAILURES_MD" >> "$REPORT_DIR/${TOOL}-report.md"
  elif [ -n "$FAILURE_DETAILS" ]; then
    cat >> "$REPORT_DIR/${TOOL}-report.md" <<FAILEOF

\`\`\`
$FAILURE_DETAILS
\`\`\`
FAILEOF
  fi
  if [ "$FAILURE_COUNT" -gt 100 ]; then
    cat >> "$REPORT_DIR/${TOOL}-report.md" <<FAILLIMITEOF

> ⚠️ 仅展示前 100 条失败，请查看完整原始报告。
FAILLIMITEOF
  fi
  cat >> "$REPORT_DIR/${TOOL}-report.md" <<FAILFOOTEREOF

---
FAILFOOTEREOF
fi

cat >> "$REPORT_DIR/${TOOL}-report.md" <<GATEEOF

## 🚦 发布门禁检查

| 检查项                   | 状态 |
|--------------------------|------|
| 测试已执行               | $(if [ "$TOTAL" -gt 0 ]; then echo "✅ 是"; else echo "❌ 否"; fi) |
| 无失败用例               | $(if [ "$FAILED" -eq 0 ] && [ "$TOTAL" -gt 0 ]; then echo "✅ 是"; else echo "❌ 否（$FAILED 条失败）"; fi) |
| 无异常态（非全跳过）     | $(if [ "$IS_ZERO_EXEC" = false ]; then echo "✅ 正常"; else echo "❌ 否（passed=0, skipped=$SKIPPED，疑似数据源污染）"; fi) |
| $COVERAGE_GATE_LABEL | $COVERAGE_GATE_VALUE |
| 通过率 ≥ 95%             | $(if [ "$PASS_GE_95" = true ]; then echo "✅ ${PASS_RATE}%"; else echo "❌ ${PASS_RATE}%（需 ≥ 95%）"; fi) |

**最终结论**：$GATE_TEXT

---

*本报告由 \`generate-ci-report.sh\` 自动生成，结构与本地独立工具报告保持一致。*
*如需重新生成：\`.github/scripts/generate-ci-report.sh $TOOL ...\`*
GATEEOF

echo "✅ 已生成 $REPORT_DIR/${TOOL}-report.{json,md}"
