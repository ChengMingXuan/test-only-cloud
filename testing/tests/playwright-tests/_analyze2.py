import re, os, collections

counter = collections.Counter()
unconditional_names = collections.Counter()
unconditional_count = 0
conditional_count = 0

for root, dirs, files in os.walk('tests'):
    for fn in files:
        if not fn.endswith('.spec.ts'):
            continue
        lines = open(os.path.join(root, fn), encoding='utf-8').readlines()
        for i, line in enumerate(lines):
            if 'test.skip()' not in line:
                continue
            stripped = line.strip()
            if stripped == 'test.skip();':
                unconditional_count += 1
                for j in range(i - 1, max(i - 5, -1), -1):
                    m = re.search(r"test\(['\"](.+?)['\"]", lines[j])
                    if m:
                        unconditional_names[m.group(1)] += 1
                        break
            else:
                conditional_count += 1
                texts = re.findall(r'has-text\("([^"]+)"\)', line)
                for t in texts:
                    counter[t] += 1
                if not texts:
                    sels = re.findall(r"page\.locator\('([^']+)'\)", line)
                    for s in sels:
                        counter['SEL:' + s[:80]] += 1
                    sels2 = re.findall(r'page\.locator\("([^"]+)"\)', line)
                    for s in sels2:
                        counter['SEL:' + s[:80]] += 1

print(f"=== 统计 ===")
print(f"无条件 skip: {unconditional_count}")
print(f"条件 skip: {conditional_count}")
print(f"\n=== 条件 skip 查找的按钮文本 ===")
for k, v in counter.most_common(40):
    print(f"  {v:4d}  {k}")
print(f"\n=== 无条件 skip 的测试名 ===")
for k, v in unconditional_names.most_common(20):
    print(f"  {v:4d}  {k}")
