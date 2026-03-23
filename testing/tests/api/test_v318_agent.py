"""
AI Agent API 测试
=================
覆盖 AgentController 全部 5 个端点
"""
import pytest
import uuid
from tests.conftest import ApiClient

BASE = "/api/iotcloudai/agent"


@pytest.fixture
def agent_config():
    return {
        "agentName": f"Agent_{uuid.uuid4().hex[:6]}",
        "agentType": "diagnostic",
        "modelId": str(uuid.uuid4()),
        "parameters": {"maxTokens": 2048, "temperature": 0.7},
    }


@pytest.fixture
def agent_task():
    return {
        "agentId": str(uuid.uuid4()),
        "taskType": "anomaly_detection",
        "deviceIds": [str(uuid.uuid4()), str(uuid.uuid4())],
        "context": {"timeRange": "1h"},
    }


class TestAgentConfig:
    """Agent 配置管理"""

    def test_create_agent(self, api: ApiClient, agent_config):
        resp = api.post(f"{BASE}/config", json=agent_config)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True

    def test_list_agents(self, api: ApiClient):
        resp = api.get(f"{BASE}/config", params={"page": 1, "pageSize": 10})
        assert resp.status_code == 200

    def test_get_agent(self, api: ApiClient):
        agent_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/config/{agent_id}")
        assert resp.status_code in (200, 404)

    def test_update_agent(self, api: ApiClient, agent_config):
        agent_id = str(uuid.uuid4())
        resp = api.put(f"{BASE}/config/{agent_id}", json=agent_config)
        assert resp.status_code in (200, 404)

    def test_delete_agent(self, api: ApiClient):
        agent_id = str(uuid.uuid4())
        resp = api.delete(f"{BASE}/config/{agent_id}")
        assert resp.status_code in (200, 404)

    def test_create_agent_unauthorized(self, anon_api: ApiClient, agent_config):
        resp = anon_api.post(f"{BASE}/config", json=agent_config)
        assert resp.status_code == 401


class TestAgentExecution:
    """Agent 任务执行"""

    def test_execute_task(self, api: ApiClient, agent_task):
        resp = api.post(f"{BASE}/execute", json=agent_task)
        assert resp.status_code == 200

    def test_execute_missing_agent(self, api: ApiClient):
        resp = api.post(f"{BASE}/execute", json={"taskType": "anomaly_detection"})
        assert resp.status_code in (400, 422)

    def test_execute_unauthorized(self, anon_api: ApiClient, agent_task):
        resp = anon_api.post(f"{BASE}/execute", json=agent_task)
        assert resp.status_code == 401


class TestAgentHistory:
    """Agent 执行历史"""

    def test_get_history(self, api: ApiClient):
        agent_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/{agent_id}/history", params={"page": 1, "pageSize": 10})
        assert resp.status_code in (200, 404)

    def test_get_task_result(self, api: ApiClient):
        task_id = str(uuid.uuid4())
        resp = api.get(f"{BASE}/tasks/{task_id}")
        assert resp.status_code in (200, 404)

    def test_history_unauthorized(self, anon_api: ApiClient):
        agent_id = str(uuid.uuid4())
        resp = anon_api.get(f"{BASE}/{agent_id}/history")
        assert resp.status_code == 401
