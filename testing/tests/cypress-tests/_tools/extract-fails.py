#!/usr/bin/env python3
"""从并行日志提取所有失败选择器"""
import os, re

logdir = 'parallel-results'
fails = {}
for f in sorted(os.listdir(logdir)):
    if not f.endswith('.log'):
        continue
    with open(os.path.join(logdir, f), 'r', encoding='utf-8', errors='replace') as fh:
        txt = fh.read()
    
    sels = set()
    # 提取 "Expected to find element: `xxx`"
    for m in re.finditer(r'Expected to find element: `([^`]+)`', txt):
        sels.add(m.group(1))
    
    # 提取 AssertionError 中的选择器
    for m in re.finditer(r"Timed out retrying.*?cy\.get\('([^']+)'\)", txt, re.DOTALL):
        sels.add(m.group(1))
    
    # first() 失败
    if 'cy.first()' in txt:
        sels.add('__FIRST_ISSUE__')
    
    # 检查是否有失败
    has_fail = bool(re.search(r'\d+ failing', txt))
    
    if has_fail and sels:
        fails[f.replace('.log', '')] = sorted(sels)
    elif has_fail:
        fails[f.replace('.log', '')] = ['__UNKNOWN__']

for spec, sels in sorted(fails.items()):
    print(f'{spec}:')
    for s in sels:
        print(f'  - {s}')

print(f'\n=== 总计 {len(fails)} 个文件有失败 ===')
