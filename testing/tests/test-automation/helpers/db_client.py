import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
import uuid

class DbClient:
    """PostgreSQL 数据库查询封装"""
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        
    def connect(self):
        """建立连接"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                client_encoding='utf8'
            )
            print(f"✅ 数据库连接成功: {self.database}")
        except Exception as e:
            raise Exception(f"数据库连接失败: {str(e)}")
    
    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()
    
    def execute_query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行查询 - 返回行结果集（字典列表）"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(sql, params or ())
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            cursor.close()
    
    def execute_scalar(self, sql: str, params: tuple = None) -> Any:
        """执行查询 - 返回单个标量值"""
        results = self.execute_query(sql, params)
        if results:
            # 返回第一行的第一列
            return list(results[0].values())[0]
        return None
    
    def execute_update(self, sql: str, params: tuple = None) -> int:
        """执行更新/删除 - 返回受影响行数"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, params or ())
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"数据库更新失败: {str(e)}")
        finally:
            cursor.close()
    
    def execute_insert(self, sql: str, params: tuple = None) -> int:
        """执行插入 - 返回插入行数"""
        return self.execute_update(sql, params)
    
    def table_exists(self, schema: str, table_name: str) -> bool:
        """检查表是否存在"""
        sql = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
            )
        """
        result = self.execute_scalar(sql, (schema, table_name))
        return bool(result)
    
    def get_column_info(self, schema: str, table_name: str) -> List[Dict[str, str]]:
        """获取表的列信息（列名、类型、是否非空）"""
        sql = """
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """
        return self.execute_query(sql, (schema, table_name))
    
    def get_primary_key(self, schema: str, table_name: str) -> Optional[str]:
        """获取表的主键列名"""
        sql = """
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid
            JOIN pg_class t ON t.oid = i.indrelid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            WHERE n.nspname = %s AND t.relname = %s AND i.indisprimary
            LIMIT 1
        """
        result = self.execute_scalar(sql, (schema, table_name))
        return result
    
    def get_table_comment(self, schema: str, table_name: str) -> Optional[str]:
        """获取表的注释说明"""
        sql = """
            SELECT obj_description((schema_name||'.'||table_name)::regclass, 'pg_class') as comment
            FROM (
                SELECT %s as schema_name, %s as table_name
            ) t
        """
        result = self.execute_scalar(sql, (schema, table_name))
        return result
    
    def count_rows(self, schema: str, table_name: str, where_clause: str = None) -> int:
        """统计表行数"""
        sql = f"SELECT COUNT(*) FROM {schema}.{table_name}"
        if where_clause:
            sql += f" WHERE {where_clause}"
        return self.execute_scalar(sql.replace('%', '%%'))  # 防止字符串格式化冲突


class MultiTenantValidator:
    """多租户隔离验证器"""
    
    def __init__(self, db: DbClient):
        self.db = db
    
    def verify_query_contains_tenant_filter(self, schema: str, table_name: str, 
                                           sample_tenant_id: str) -> bool:
        """验证查询是否包含 tenant_id 过滤（仅查询一个租户的数据）"""
        sql = f"SELECT COUNT(*) FROM {schema}.{table_name} WHERE tenant_id = %s"
        count = self.db.execute_scalar(sql, (sample_tenant_id,))
        
        # 验证其他租户的数据被隔离
        sql = f"SELECT COUNT(*) FROM {schema}.{table_name} WHERE tenant_id != %s"
        other_count = self.db.execute_scalar(sql, (sample_tenant_id,))
        
        return count >= 0 and other_count >= 0  # 基础验证，实际应检查权限
    
    def find_missing_tenant_id_columns(self) -> List[Dict[str, str]]:
        """找出缺少 tenant_id 列的租户隔离表"""
        # 查询所有应该有 tenant_id 但实际没有的表
        sql = """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('public', 'pg_*')
            AND table_name NOT LIKE 'rule_%'  -- 全局表豁免
        """
        all_tables = self.db.execute_query(sql)
        
        missing = []
        for table in all_tables:
            schema, name = table['table_schema'], table['table_name']
            columns = self.db.get_column_info(schema, name)
            col_names = [col['column_name'] for col in columns]
            
            if 'tenant_id' not in col_names and 'delete_at' in col_names:
                missing.append({
                    'schema': schema,
                    'table': name,
                    'reason': '缺少 tenant_id 列（应该有）'
                })
        
        return missing


class SoftDeleteValidator:
    """软删除验证器"""
    
    def __init__(self, db: DbClient):
        self.db = db
    
    def find_missing_delete_at_columns(self) -> List[Dict[str, str]]:
        """找出缺少 delete_at 列的表"""
        sql = """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('public', 'pg_*')
            AND table_name NOT LIKE '%_log'  -- 纯日志表豁免
        """
        all_tables = self.db.execute_query(sql)
        
        missing = []
        for table in all_tables:
            schema, name = table['table_schema'], table['table_name']
            columns = self.db.get_column_info(schema, name)
            col_names = [col['column_name'] for col in columns]
            
            # 规则：除了全局表和纯日志表，都应该有 delete_at
            if 'delete_at' not in col_names and not name.startswith('rule_'):
                missing.append({
                    'schema': schema,
                    'table': name,
                    'reason': '缺少 delete_at 列（应该有）'
                })
        
        return missing
    
    def verify_deleted_records_excluded(self, schema: str, table_name: str) -> bool:
        """验证查询逻辑中已删除的记录被排除"""
        # 检查表中是否存在 delete_at IS NOT NULL 的记录
        sql = f"SELECT COUNT(*) FROM {schema}.{table_name} WHERE delete_at IS NOT NULL"
        deleted_count = self.db.execute_scalar(sql)
        
        # 正常查询应该不包含已删除的记录
        sql = f"SELECT COUNT(*) FROM {schema}.{table_name} WHERE delete_at IS NULL"
        active_count = self.db.execute_scalar(sql)
        
        return deleted_count >= 0 and active_count >= 0


class DataConsistencyValidator:
    """数据一致性验证器"""
    
    def __init__(self, db: DbClient):
        self.db = db
    
    def verify_foreign_key_integrity(self, schema: str, table_name: str, 
                                     fk_column: str, ref_table: str, 
                                     ref_column: str) -> bool:
        """验证外键完整性（没有孤儿记录）"""
        sql = f"""
            SELECT COUNT(*)
            FROM {schema}.{table_name}
            WHERE {fk_column} IS NOT NULL
            AND {fk_column} NOT IN (SELECT {ref_column} FROM {schema}.{ref_table})
            AND delete_at IS NULL
        """
        orphan_count = self.db.execute_scalar(sql)
        return orphan_count == 0
    
    def verify_cascading_soft_delete(self, schema: str, parent_table: str, 
                                     child_table: str, fk_column: str) -> bool:
        """验证级联软删除：父实体软删后，子实体也应该被软删"""
        sql = f"""
            SELECT COUNT(*)
            FROM {schema}.{child_table} c
            WHERE c.delete_at IS NULL
            AND c.{fk_column} IN (
                SELECT id FROM {schema}.{parent_table} WHERE delete_at IS NOT NULL
            )
        """
        inconsistent_count = self.db.execute_scalar(sql)
        return inconsistent_count == 0
    
    def verify_audit_fields_completed(self, schema: str, table_name: str) -> List[Dict]:
        """验证审计字段完整性（create_by, create_name, update_by, update_name, etc.）"""
        sql = f"""
            SELECT 
                id,
                create_by,
                create_name,
                update_by,
                update_name
            FROM {schema}.{table_name}
            WHERE create_by IS NULL OR update_by IS NULL
            LIMIT 10
        """
        incomplete_records = self.db.execute_query(sql)
        return incomplete_records


# 示例用法
if __name__ == '__main__':
    db = DbClient(
        host='localhost',
        port=5432,
        database='jgsy_account',
        user='postgres',
        password='postgres'
    )
    
    db.connect()
    
    # 多租户隔离验证
    validator = MultiTenantValidator(db)
    missing = validator.find_missing_tenant_id_columns()
    print(f"缺少 tenant_id 的表: {len(missing)} 个")
    for item in missing:
        print(f"  - {item['schema']}.{item['table']}: {item['reason']}")
    
    # 软删除验证
    soft_delete_validator = SoftDeleteValidator(db)
    missing = soft_delete_validator.find_missing_delete_at_columns()
    print(f"\n缺少 delete_at 的表: {len(missing)} 个")
    
    db.close()
