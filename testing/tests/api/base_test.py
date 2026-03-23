"""
接口自动化测试 — 基础测试类
============================
所有服务的接口测试类继承此基类
"""
import logging
import pytest
from tests.conftest import ApiClient, DbClient, ApiResultValidator

logger = logging.getLogger(__name__)


class BaseApiTest:
    """接口自动化测试基类"""

    # 子类必须设置
    SERVICE_NAME: str = ""
    API_PREFIX: str = ""

    @pytest.fixture(autouse=True)
    def _setup_validator(self, validator):
        self.v = validator

    def assert_success(self, response, expected_code=200):
        return ApiResultValidator.assert_success(response, expected_code)

    def assert_paged(self, response, min_total=0):
        return ApiResultValidator.assert_paged(response, min_total)

    def assert_error(self, response, expected_http_status=None, expected_code=None):
        return ApiResultValidator.assert_error(response, expected_http_status, expected_code)

    def assert_db_record_exists(self, db: DbClient, table: str, record_id: str, tenant_id: str = None):
        """验证数据库记录存在"""
        sql = f"SELECT * FROM {table} WHERE id = %s AND delete_at IS NULL"
        params = [record_id]
        if tenant_id:
            sql += " AND tenant_id = %s"
            params.append(tenant_id)
        record = db.query_one(sql, params)
        assert record is not None, f"记录不存在: {table}.id={record_id}"
        return record

    def assert_db_record_deleted(self, db: DbClient, table: str, record_id: str):
        """验证数据库记录已软删除"""
        record = db.query_one(
            f"SELECT delete_at FROM {table} WHERE id = %s", (record_id,)
        )
        assert record is not None, f"记录不存在: {table}.id={record_id}"
        assert record["delete_at"] is not None, f"记录未软删除: {table}.id={record_id}"

    def assert_db_field_updated(self, db: DbClient, table: str, record_id: str,
                                 field: str, expected_value):
        """验证数据库字段已更新"""
        record = db.query_one(
            f"SELECT {field}, update_time FROM {table} WHERE id = %s", (record_id,)
        )
        assert record is not None, f"记录不存在: {table}.id={record_id}"
        assert record[field] == expected_value, \
            f"{field}: 期望={expected_value}, 实际={record[field]}"
        return record

    def assert_db_count(self, db: DbClient, table: str, where: str = "", params=None,
                        expected_count: int = None, min_count: int = None):
        """验证数据库记录数"""
        sql = f"SELECT count(*) FROM {table}"
        if where:
            sql += f" WHERE {where}"
        count = db.query_scalar(sql, params)
        if expected_count is not None:
            assert count == expected_count, f"{table} count: 期望={expected_count}, 实际={count}"
        if min_count is not None:
            assert count >= min_count, f"{table} count: 最少={min_count}, 实际={count}"
        return count

    def assert_tenant_isolation(self, db: DbClient, table: str,
                                 record_id: str, tenant_id: str):
        """验证多租户隔离 — 记录的 tenant_id 必须匹配"""
        record = db.query_one(
            f"SELECT tenant_id FROM {table} WHERE id = %s", (record_id,)
        )
        assert record is not None, f"记录不存在: {table}.id={record_id}"
        assert str(record["tenant_id"]) == str(tenant_id), \
            f"租户不匹配: 期望={tenant_id}, 实际={record['tenant_id']}"

    def assert_query_matches_db(self, api_items: list, db_rows: list,
                                 id_field: str = "id"):
        """验证接口查询结果与数据库一致"""
        api_ids = {str(item[id_field]) for item in api_items}
        db_ids = {str(row[id_field]) for row in db_rows}
        assert api_ids == db_ids, \
            f"结果不一致:\n  API多出: {api_ids - db_ids}\n  DB多出: {db_ids - api_ids}"
