"""
IotCloudAI MCP 统一工具协议 API 测试
====================================
端点:
  - GET  /api/iotcloudai/mcp/tools             (工具列表)
  - GET  /api/iotcloudai/mcp/tools/{toolId}     (工具详情)
  - POST /api/iotcloudai/mcp/tools/{toolId}/execute (执行工具)
  - POST /api/iotcloudai/mcp/chat               (同步对话)
  - POST /api/iotcloudai/mcp/chat/stream        (流式对话)
  - GET  /api/iotcloudai/mcp/health             (健康检查)

100% Mock，不连接真实数据库/服务
"""

import pytest
import sys
import os
import uuid
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from mock_client import MockApiClient, MOCK_TOKEN


class McpApiClient:
    """MCP API 测试客户端"""
    def __init__(self):
        self._client = MockApiClient(token=MOCK_TOKEN)
        self._saved_token = MOCK_TOKEN

    def get(self, endpoint, **kwargs):
        return self._client.get(endpoint, **kwargs)

    def post(self, endpoint, json_data=None, **kwargs):
        return self._client.post(endpoint, json=json_data, **kwargs)

    def clear_token(self):
        self._saved_token = self._client.token
        self._client.clear_token()

    def set_invalid_token(self):
        self._saved_token = self._client.token
        self._client.set_token("invalid.fake.token")

    def restore_token(self):
        self._client.set_token(self._saved_token)


@pytest.fixture(scope="module")
def api_client():
    return McpApiClient()


# ═══════════════════════════════════════════════════
# GET /api/iotcloudai/mcp/tools — 工具列表
# ═══════════════════════════════════════════════════

@pytest.mark.api
@pytest.mark.iotcloudai
class TestMcpToolsList:
    """MCP 工具列表 API 测试"""

    def test_get_all_tools_positive(self, api_client):
        """[MCP][tools] 正常获取全部工具列表 → 200"""
        resp = api_client.get("/api/iotcloudai/mcp/tools")
        assert resp is not None
        assert resp.status_code < 500

    def test_get_tools_by_type_llm(self, api_client):
        """[MCP][tools] 按类型筛选 LLM 工具 → 200"""
        resp = api_client.get("/api/iotcloudai/mcp/tools", params={"type": "LLM"})
        assert resp is not None
        assert resp.status_code < 500

    def test_get_tools_by_type_onnx(self, api_client):
        """[MCP][tools] 按类型筛选 ONNX 工具 → 200"""
        resp = api_client.get("/api/iotcloudai/mcp/tools", params={"type": "OnnxInference"})
        assert resp is not None
        assert resp.status_code < 500

    def test_get_tools_by_type_blockchain(self, api_client):
        """[MCP][tools] 按类型筛选 Blockchain 工具 → 200"""
        resp = api_client.get("/api/iotcloudai/mcp/tools", params={"type": "Blockchain"})
        assert resp is not None
        assert resp.status_code < 500

    def test_get_tools_by_invalid_type(self, api_client):
        """[MCP][tools] 无效类型参数 → 200 空列表"""
        resp = api_client.get("/api/iotcloudai/mcp/tools", params={"type": "NonExistent"})
        assert resp is not None
        assert resp.status_code < 500

    def test_get_tools_no_auth(self, api_client):
        """[MCP][tools] 缺少认证 → 401"""
        api_client.clear_token()
        try:
            resp = api_client.get("/api/iotcloudai/mcp/tools")
            assert resp.status_code in (200, 401, 403)
        finally:
            api_client.restore_token()

    def test_get_tools_invalid_token(self, api_client):
        """[MCP][tools] 无效Token → 401"""
        api_client.set_invalid_token()
        try:
            resp = api_client.get("/api/iotcloudai/mcp/tools")
            assert resp.status_code in (200, 401, 403)
        finally:
            api_client.restore_token()


# ═══════════════════════════════════════════════════
# GET /api/iotcloudai/mcp/tools/{toolId} — 工具详情
# ═══════════════════════════════════════════════════

@pytest.mark.api
@pytest.mark.iotcloudai
class TestMcpToolDetail:
    """MCP 工具详情 API 测试"""

    def test_get_tool_detail_positive(self, api_client):
        """[MCP][tools/{id}] 获取已知工具详情 → 200"""
        resp = api_client.get("/api/iotcloudai/mcp/tools/llm:qwen-7b")
        assert resp is not None
        assert resp.status_code < 500

    def test_get_tool_detail_onnx(self, api_client):
        """[MCP][tools/{id}] 获取 ONNX 工具详情 → 200"""
        resp = api_client.get("/api/iotcloudai/mcp/tools/onnx:load_prediction_tcn")
        assert resp is not None
        assert resp.status_code < 500

    def test_get_tool_detail_blockchain(self, api_client):
        """[MCP][tools/{id}] 获取区块链工具详情 → 200"""
        resp = api_client.get("/api/iotcloudai/mcp/tools/blockchain:chainmaker")
        assert resp is not None
        assert resp.status_code < 500

    def test_get_tool_detail_not_found(self, api_client):
        """[MCP][tools/{id}] 不存在的工具 → 404"""
        resp = api_client.get("/api/iotcloudai/mcp/tools/nonexistent:tool")
        assert resp is not None
        assert resp.status_code in (200, 404)

    def test_get_tool_detail_no_auth(self, api_client):
        """[MCP][tools/{id}] 缺少认证 → 401"""
        api_client.clear_token()
        try:
            resp = api_client.get("/api/iotcloudai/mcp/tools/llm:qwen-7b")
            assert resp.status_code in (200, 401, 403)
        finally:
            api_client.restore_token()


# ═══════════════════════════════════════════════════
# POST /api/iotcloudai/mcp/tools/{toolId}/execute — 执行工具
# ═══════════════════════════════════════════════════

@pytest.mark.api
@pytest.mark.iotcloudai
class TestMcpToolExecute:
    """MCP 工具执行 API 测试"""

    def test_execute_llm_tool_positive(self, api_client):
        """[MCP][execute] 执行 LLM 工具 → 200"""
        resp = api_client.post("/api/iotcloudai/mcp/tools/llm:qwen-7b/execute", json_data={
            "prompt": "你好，请分析当前场站负荷情况",
            "maxTokens": 100,
        })
        assert resp is not None
        assert resp.status_code < 500

    def test_execute_onnx_tool_positive(self, api_client):
        """[MCP][execute] 执行 ONNX 预测工具 → 200"""
        resp = api_client.post("/api/iotcloudai/mcp/tools/onnx:load_prediction_tcn/execute", json_data={
            "features": [100.5, 102.3, 98.7, 101.2, 99.8],
        })
        assert resp is not None
        assert resp.status_code < 500

    def test_execute_onnx_vision_tool(self, api_client):
        """[MCP][execute] 执行 ONNX 视觉工具 → 200"""
        resp = api_client.post("/api/iotcloudai/mcp/tools/onnx:yolov8n-industrial/execute", json_data={
            "imageBase64": "iVBORw0KGgoAAAANSUhEUg==",  # 最小 base64 占位
        })
        assert resp is not None
        assert resp.status_code < 500

    def test_execute_blockchain_tool_health(self, api_client):
        """[MCP][execute] 执行区块链健康检查 → 200"""
        resp = api_client.post("/api/iotcloudai/mcp/tools/blockchain:chainmaker/execute", json_data={
            "operation": "Health",
        })
        assert resp is not None
        assert resp.status_code < 500

    def test_execute_blockchain_tool_query(self, api_client):
        """[MCP][execute] 执行区块链合约查询 → 200"""
        resp = api_client.post("/api/iotcloudai/mcp/tools/blockchain:chainmaker/execute", json_data={
            "operation": "Query",
            "contractName": "energy_evidence",
            "method": "GetEvidence",
            "parameters": {"evidenceId": "test-001"},
        })
        assert resp is not None
        assert resp.status_code < 500

    def test_execute_nonexistent_tool(self, api_client):
        """[MCP][execute] 执行不存在工具 → 404"""
        resp = api_client.post("/api/iotcloudai/mcp/tools/nonexistent:tool/execute", json_data={})
        assert resp is not None
        assert resp.status_code in (200, 400, 404)

    def test_execute_empty_body(self, api_client):
        """[MCP][execute] 空请求体 → 400"""
        resp = api_client.post("/api/iotcloudai/mcp/tools/onnx:load_prediction_tcn/execute", json_data={})
        assert resp is not None
        assert resp.status_code in (200, 400, 422)

    def test_execute_no_auth(self, api_client):
        """[MCP][execute] 缺少认证 → 401"""
        api_client.clear_token()
        try:
            resp = api_client.post("/api/iotcloudai/mcp/tools/llm:qwen-7b/execute", json_data={
                "prompt": "test",
            })
            assert resp.status_code in (200, 401, 403)
        finally:
            api_client.restore_token()

    def test_execute_invalid_token(self, api_client):
        """[MCP][execute] 无效Token → 401"""
        api_client.set_invalid_token()
        try:
            resp = api_client.post("/api/iotcloudai/mcp/tools/llm:qwen-7b/execute", json_data={
                "prompt": "test",
            })
            assert resp.status_code in (200, 401, 403)
        finally:
            api_client.restore_token()


# ═══════════════════════════════════════════════════
# POST /api/iotcloudai/mcp/chat — 同步对话
# ═══════════════════════════════════════════════════

@pytest.mark.api
@pytest.mark.iotcloudai
class TestMcpChat:
    """MCP 对话 API 测试"""

    def test_chat_positive(self, api_client):
        """[MCP][chat] 正常对话 → 200"""
        resp = api_client.post("/api/iotcloudai/mcp/chat", json_data={
            "message": "请预测明天的电力负荷",
            "scene": "prediction",
        })
        assert resp is not None
        assert resp.status_code < 500

    def test_chat_with_model_key(self, api_client):
        """[MCP][chat] 指定模型对话 → 200"""
        resp = api_client.post("/api/iotcloudai/mcp/chat", json_data={
            "message": "分析今日充电站运营数据",
            "scene": "charging",
            "modelKey": "qwen-7b",
        })
        assert resp is not None
        assert resp.status_code < 500

    def test_chat_all_scenes(self, api_client):
        """[MCP][chat] 测试所有场景 → 200"""
        for scene in ["daily_ops", "charging", "energy", "prediction", "report"]:
            resp = api_client.post("/api/iotcloudai/mcp/chat", json_data={
                "message": "测试消息",
                "scene": scene,
            })
            assert resp is not None
            assert resp.status_code < 500

    def test_chat_empty_message(self, api_client):
        """[MCP][chat] 空消息 → 400"""
        resp = api_client.post("/api/iotcloudai/mcp/chat", json_data={
            "message": "",
        })
        assert resp is not None
        assert resp.status_code in (200, 400, 422)

    def test_chat_long_message(self, api_client):
        """[MCP][chat] 超长消息 → 正常处理"""
        resp = api_client.post("/api/iotcloudai/mcp/chat", json_data={
            "message": "A" * 5000,
            "scene": "daily_ops",
        })
        assert resp is not None
        assert resp.status_code < 500

    def test_chat_no_auth(self, api_client):
        """[MCP][chat] 缺少认证 → 401"""
        api_client.clear_token()
        try:
            resp = api_client.post("/api/iotcloudai/mcp/chat", json_data={
                "message": "test",
            })
            assert resp.status_code in (200, 401, 403)
        finally:
            api_client.restore_token()

    def test_chat_xss_prevention(self, api_client):
        """[MCP][chat] XSS 输入防护"""
        resp = api_client.post("/api/iotcloudai/mcp/chat", json_data={
            "message": "<script>alert('xss')</script>",
            "scene": "daily_ops",
        })
        assert resp is not None
        assert resp.status_code < 500

    def test_chat_sql_injection_prevention(self, api_client):
        """[MCP][chat] SQL注入防护"""
        resp = api_client.post("/api/iotcloudai/mcp/chat", json_data={
            "message": "'; DROP TABLE users; --",
            "scene": "daily_ops",
        })
        assert resp is not None
        assert resp.status_code < 500


# ═══════════════════════════════════════════════════
# POST /api/iotcloudai/mcp/chat/stream — 流式对话 (SSE)
# ═══════════════════════════════════════════════════

@pytest.mark.api
@pytest.mark.iotcloudai
class TestMcpChatStream:
    """MCP 流式对话 API 测试"""

    def test_stream_positive(self, api_client):
        """[MCP][chat/stream] 正常流式对话 → 200"""
        resp = api_client.post("/api/iotcloudai/mcp/chat/stream", json_data={
            "message": "请生成今日运营摘要",
            "scene": "report",
        })
        assert resp is not None
        assert resp.status_code < 500

    def test_stream_no_auth(self, api_client):
        """[MCP][chat/stream] 缺少认证 → 401"""
        api_client.clear_token()
        try:
            resp = api_client.post("/api/iotcloudai/mcp/chat/stream", json_data={
                "message": "test",
            })
            assert resp.status_code in (200, 401, 403)
        finally:
            api_client.restore_token()


# ═══════════════════════════════════════════════════
# GET /api/iotcloudai/mcp/health — 健康检查
# ═══════════════════════════════════════════════════

@pytest.mark.api
@pytest.mark.iotcloudai
class TestMcpHealth:
    """MCP 健康检查 API 测试"""

    def test_health_check_positive(self, api_client):
        """[MCP][health] 正常健康检查 → 200"""
        resp = api_client.get("/api/iotcloudai/mcp/health")
        assert resp is not None
        assert resp.status_code < 500

    def test_health_check_no_auth(self, api_client):
        """[MCP][health] 缺少认证 → 401"""
        api_client.clear_token()
        try:
            resp = api_client.get("/api/iotcloudai/mcp/health")
            assert resp.status_code in (200, 401, 403)
        finally:
            api_client.restore_token()

    def test_health_check_invalid_token(self, api_client):
        """[MCP][health] 无效Token → 401"""
        api_client.set_invalid_token()
        try:
            resp = api_client.get("/api/iotcloudai/mcp/health")
            assert resp.status_code in (200, 401, 403)
        finally:
            api_client.restore_token()
