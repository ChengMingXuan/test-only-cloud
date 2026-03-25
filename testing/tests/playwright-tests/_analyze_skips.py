"""分析 Playwright 测试中所有 skip 的原因和需要的元素"""
import re, os, collections

# 统计条件 skip 中查找的按钮文本
btn_counter = collections.Counter()
# 统计无条件 skip 的测试名
unconditional = []
# 统计条件 skip 的选择器模式
selector_counter = collections.Counter()

for root, dirs, files in os.walk('tests'):
    for fn in files:
        if not fn.endswith('.spec.ts'):
            continue
        path = os.path.join(root, fn)
        lines = open(path, encoding='utf-8').readlines()
        for i, line in enumerate(lines):
            if 'test.skip()' not in line:
                continue
            stripped = line.strip()
            # 无条件 skip
            if stripped == 'test.skip();':
                # 往上找 test 名
                for j in range(i-1, max(i-5, -1), -1):
                    m = re.search(r"test\(['\"](.+?)['\"]", lines[j])
                    if m:
                        unconditional.append(m.group(1))
                        break
            # 条件 skip：提取按钮文本
            for m in re.findall(r'has-text\("([^"]+)"\)', line):
                btn_counter[m] += 1
            # 提取选择器模式（locator 参数）
            for m in re.findall(r"locator\('([^']+)'\)", line):
                selector_counter[m] += 1

print("=== 条件 skip 中查找的按钮文本 (需要添加到 Mock HTML) ===")
for k, v in btn_counter.most_common(30):
    print(f"  {v:4d}x  {k}")
print(f"\n  总计: {sum(btn_counter.values())} 处条件 skip 涉及按钮文本")

print(f"\n=== 无条件 skip 的测试名 ({len(unconditional)} 个) ===")
names = collections.Counter(unconditional)
for k, v in names.most_common(20):
    print(f"  {v:4d}x  {k}")

print(f"\n=== 条件 skip 中的选择器模式 ===")
for k, v in selector_counter.most_common(20):
    print(f"  {v:4d}x  {k}")
