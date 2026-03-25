import json
with open('parallel-results/results.json','r',encoding='utf-8') as f:
    data = json.load(f)
for s in data['specs'][:10]:
    print(f"{s['spec']}: status={s['status']}, pass={s['passing']}, fail={s['failing']}, rc={s['returncode']}, t={s['elapsed']}s")
    if 'error' in s:
        print(f"  error: {s['error'][:200]}")
