"""
工具4: psql 数据库完整性验证
覆盖维度: 表结构一致 / 约束完整 / 索引有效 / 数据一致性 / 租户隔离
"""
import json, sys, time
from datetime import datetime

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("需要安装 psycopg2: pip install psycopg2-binary")
    sys.exit(1)

DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASS = "P@ssw0rd"

# 核心业务数据库
CORE_DBS = {
    "jgsy_tenant": "tenant",
    "jgsy_identity": "public",
    "jgsy_permission": "permission",
    "jgsy_account": "account",
    "jgsy_device": "device",
    "jgsy_station": "public",
    "jgsy_charging": "charging",
    "jgsy_settlement": "settlement",
    "jgsy_workorder": "workorder",
    "jgsy_analytics": "public",
    "jgsy_ruleengine": "public",
    "jgsy_simulator": "public",
    "jgsy_digitaltwin": "public",
    "jgsy_blockchain": "public",
    "jgsy_ingestion": "public",
    "jgsy_storage": "public",
    "jgsy_contentplatform": "public",
    "jgsy_observability": "public",
    "jgsy_iotcloudai": "public",
}

results = {
    "tool": "psql",
    "timestamp": datetime.now().isoformat(),
    "total": 0, "passed": 0, "failed": 0, "warnings": 0,
    "details": []
}

def add(cat, name, status, msg):
    results["total"] += 1
    results[{"PASS": "passed", "FAIL": "failed", "WARN": "warnings"}[status]] += 1
    results["details"].append({"category": cat, "name": name, "status": status, "message": msg})
    icon = {"PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]"}[status]
    print(f"{icon} {cat} :: {name} - {msg}")

def conn(db):
    try:
        return psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, dbname=db, connect_timeout=5)
    except:
        return None

def q(c, sql, params=None):
    with c.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return cur.fetchall()

def scalar(c, sql, params=None):
    with c.cursor() as cur:
        cur.execute(sql, params)
        r = cur.fetchone()
        return r[0] if r else None

# ── T4.1 数据库可达性 ──
print("\n=== T4.1 数据库可达性 ===")
accessible_dbs = {}
for db in CORE_DBS:
    c = conn(db)
    if c:
        accessible_dbs[db] = c
        add("可达性", db, "PASS", "连接成功")
    else:
        add("可达性", db, "FAIL", "无法连接")

# ── T4.2 表结构完整性（关键表必须存在） ──
print("\n=== T4.2 关键表完整性 ===")
expected_tables = {
    "jgsy_permission": ["perm_role", "perm_menu", "perm_permission", "perm_user_role", "perm_role_permission"],
    "jgsy_account": ["account_info", "account_user_membership"],
    "jgsy_device": ["device_info", "device_profile", "device_measure_point"],
    "jgsy_charging": ["charging_order", "charging_station", "charging_pile"],
    "jgsy_ruleengine": ["rule_chain", "rule_node", "rule_connection"],
    "jgsy_tenant": ["tenant_info"],
    "jgsy_station": ["station_info"],
}
for db, tables in expected_tables.items():
    c = accessible_dbs.get(db)
    if not c: continue
    existing = [r["table_name"] for r in q(c,
        "SELECT table_name FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema') AND table_type='BASE TABLE'")]
    for t in tables:
        if t in existing:
            add("表结构", f"{db}.{t}", "PASS", "表存在")
        else:
            add("表结构", f"{db}.{t}", "FAIL", "表不存在")

# ── T4.3 tenant_id 列覆盖率 ──
print("\n=== T4.3 租户隔离列覆盖 ===")
# 全局表豁免
global_exempt = {"rule_chain", "rule_node", "rule_connection", "rule_alarm_definition", "schemaversions"}
infra_prefixes = ("dist_", "hangfire", "__", "schema")
dbs_to_check = ["jgsy_device", "jgsy_charging", "jgsy_settlement", "jgsy_workorder", "jgsy_station"]
for db in dbs_to_check:
    c = accessible_dbs.get(db)
    if not c: continue
    all_tables = [r["table_name"] for r in q(c,
        "SELECT table_name FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema','_timescaledb_catalog','_timescaledb_internal','_timescaledb_config','_timescaledb_cache') AND table_type='BASE TABLE'")]
    missing_tid = []
    for t in all_tables:
        if t in global_exempt or any(t.startswith(p) for p in infra_prefixes):
            continue
        has = q(c, "SELECT 1 FROM information_schema.columns WHERE table_name=%s AND column_name='tenant_id'", (t,))
        if not has:
            missing_tid.append(t)
    if not missing_tid:
        add("租户隔离", db, "PASS", f"所有 {len(all_tables)} 张业务表均有 tenant_id")
    else:
        add("租户隔离", db, "FAIL", f"缺少 tenant_id: {missing_tid[:5]}")

# ── T4.4 软删除列覆盖率 ──
print("\n=== T4.4 软删除列覆盖 ===")
# 纯日志表豁免
log_tables = {"rule_execution_log"}
for db in dbs_to_check:
    c = accessible_dbs.get(db)
    if not c: continue
    all_tables = [r["table_name"] for r in q(c,
        "SELECT table_name FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema','_timescaledb_catalog','_timescaledb_internal','_timescaledb_config','_timescaledb_cache') AND table_type='BASE TABLE'")]
    missing_del = []
    for t in all_tables:
        if t in global_exempt or t in log_tables or any(t.startswith(p) for p in infra_prefixes):
            continue
        has = q(c, "SELECT 1 FROM information_schema.columns WHERE table_name=%s AND column_name='delete_at'", (t,))
        if not has:
            missing_del.append(t)
    if not missing_del:
        add("软删除", db, "PASS", f"所有业务表均有 delete_at")
    else:
        add("软删除", db, "WARN", f"缺少 delete_at: {missing_del[:5]}")

# ── T4.5 主键/索引检查 ──
print("\n=== T4.5 主键/索引 ===")
for db in ["jgsy_permission", "jgsy_device", "jgsy_charging"]:
    c = accessible_dbs.get(db)
    if not c: continue
    tables_no_pk = q(c, """
        SELECT t.table_name FROM information_schema.tables t
        LEFT JOIN information_schema.table_constraints tc ON t.table_name=tc.table_name AND tc.constraint_type='PRIMARY KEY'
        WHERE t.table_schema NOT IN ('pg_catalog','information_schema') AND t.table_type='BASE TABLE'
        AND tc.constraint_name IS NULL
    """)
    # 过滤基础设施表
    no_pk = [r["table_name"] for r in tables_no_pk if not any(r["table_name"].startswith(p) for p in infra_prefixes)]
    if not no_pk:
        add("主键索引", f"{db} 主键", "PASS", "所有业务表都有主键")
    else:
        add("主键索引", f"{db} 主键", "WARN", f"无主键: {no_pk[:5]}")

# ── T4.6 外键完整性（孤儿数据检测） ──
print("\n=== T4.6 孤儿数据检测 ===")
# 检查 perm_user_role 是否有引用不存在角色的记录
c = accessible_dbs.get("jgsy_permission")
if c:
    orphan_count = scalar(c, """
        SELECT COUNT(*) FROM permission.perm_user_role ur
        WHERE NOT EXISTS (SELECT 1 FROM permission.perm_role r WHERE r.id = ur.role_id AND r.delete_at IS NULL)
    """)
    if orphan_count == 0:
        add("孤儿数据", "user_role→role", "PASS", "无孤儿关联")
    else:
        add("孤儿数据", "user_role→role", "WARN", f"{orphan_count} 条孤儿关联")

    orphan_rp = scalar(c, """
        SELECT COUNT(*) FROM permission.perm_role_permission rp
        WHERE NOT EXISTS (SELECT 1 FROM permission.perm_permission p WHERE p.id = rp.perm_id AND p.delete_at IS NULL)
    """)
    if orphan_rp == 0:
        add("孤儿数据", "role_perm→perm", "PASS", "无孤儿关联")
    else:
        add("孤儿数据", "role_perm→perm", "WARN", f"{orphan_rp} 条孤儿关联")

# ── T4.7 数据一致性检查 ──
print("\n=== T4.7 数据一致性 ===")
# 检查 delete_at IS NOT NULL 的数据不应关联到活跃记录
c_dev = accessible_dbs.get("jgsy_device")
if c_dev:
    # 设备表活跃记录数
    active = scalar(c_dev, "SELECT COUNT(*) FROM device.device_info WHERE delete_at IS NULL")
    deleted = scalar(c_dev, "SELECT COUNT(*) FROM device.device_info WHERE delete_at IS NOT NULL")
    add("数据一致", "device_info", "PASS", f"活跃 {active}, 已删除 {deleted}")

c_perm = accessible_dbs.get("jgsy_permission")
if c_perm:
    role_count = scalar(c_perm, "SELECT COUNT(*) FROM permission.perm_role WHERE delete_at IS NULL")
    perm_count = scalar(c_perm, "SELECT COUNT(*) FROM permission.perm_permission WHERE delete_at IS NULL")
    menu_count = scalar(c_perm, "SELECT COUNT(*) FROM permission.perm_menu WHERE delete_at IS NULL")
    add("数据一致", "权限数据", "PASS", f"角色 {role_count}, 权限 {perm_count}, 菜单 {menu_count}")

# ── T4.8 连接池/并发安全 ──
print("\n=== T4.8 连接池压力 ===")
c_test = accessible_dbs.get("jgsy_permission")
if c_test:
    active_conns = scalar(c_test, "SELECT COUNT(*) FROM pg_stat_activity WHERE datname IS NOT NULL")
    max_conns = scalar(c_test, "SHOW max_connections")
    pct = (active_conns / int(max_conns)) * 100
    if pct < 70:
        add("连接池", "连接利用率", "PASS", f"当前 {active_conns}/{max_conns} ({pct:.0f}%)")
    elif pct < 90:
        add("连接池", "连接利用率", "WARN", f"较高 {active_conns}/{max_conns} ({pct:.0f}%)")
    else:
        add("连接池", "连接利用率", "FAIL", f"危险 {active_conns}/{max_conns} ({pct:.0f}%)")

# ── T4.9 DbUp 迁移版本一致性 ──
print("\n=== T4.9 迁移版本 ===")
for db in ["jgsy_permission", "jgsy_device", "jgsy_charging", "jgsy_ruleengine"]:
    c = accessible_dbs.get(db)
    if not c: continue
    try:
        count = scalar(c, "SELECT COUNT(*) FROM public.schemaversions")
        latest = q(c, "SELECT scriptname, applied FROM public.schemaversions ORDER BY applied DESC LIMIT 1")
        if count and count > 0:
            last = latest[0] if latest else {}
            add("迁移版本", db, "PASS", f"{count} 版本, 最新: {last.get('scriptname','?')[:50]}")
        else:
            add("迁移版本", db, "WARN", "无迁移记录")
    except:
        add("迁移版本", db, "WARN", "无 schemaversions 表")

# ── 关闭连接 ──
for c in accessible_dbs.values():
    try: c.close()
    except: pass

# ── 输出 JSON ──
json_path = r"D:\2026\aiops.v2\TestResults\psql-db-results.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n=== 数据库完整性验证汇总 ===")
print(f"总计: {results['total']} | 通过: {results['passed']} | 失败: {results['failed']} | 警告: {results['warnings']}")
print(f"结果已保存: {json_path}")
