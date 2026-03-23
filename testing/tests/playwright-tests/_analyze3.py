import re, os, collections

counter = collections.Counter()
for root, dirs, files in os.walk('tests'):
    for fn in files:
        if not fn.endswith('.spec.ts'):
            continue
        lines = open(os.path.join(root, fn), encoding='utf-8').readlines()
        for i, line in enumerate(lines):
            s = line.strip()
            if 'test.skip()' not in s or s == 'test.skip();':
                continue
            m = re.search(r'await (\w+)\.count\(\)', s)
            if not m:
                continue
            varname = m.group(1)
            for j in range(i - 1, max(i - 5, -1), -1):
                defline = lines[j]
                if varname in defline and 'locator' in defline:
                    texts = re.findall(r'has-text\("([^"]+)"\)', defline)
                    for t in texts:
                        counter[t] += 1
                    if not texts:
                        sels = re.findall(r"locator\(['\"]([^'\"]+)['\"]\)", defline)
                        for s2 in sels:
                            counter['CSS:' + s2[:60]] += 1
                    break

for k, v in counter.most_common(40):
    print(f'{v:4d}  {k}')
print(f'Total: {sum(counter.values())}')
