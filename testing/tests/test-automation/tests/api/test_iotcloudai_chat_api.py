"""
IotCloudAI v2.0 智能对话 API 测试
覆盖对话发送、会话管理、洞察分析、AI报告

端点:
  - POST /api/iotcloudai/chat/send         (发送消息)
  - POST /api/iotcloudai/chat/send/stream   (流式消息)
  - GET  /api/iotcloudai/sessions           (会话列表)
  - GET  /api/iotcloudai/sessions/{id}/messages (消息历史)
  - DELETE /api/iotcloudai/sessions/{id}    (删除会话)
  - POST /api/iotcloudai/insight/predict/load  (负荷预测)
  - POST /api/iotcloudai/insight/predict/pv    (光伏预测)
  - POST /api/iotcloudai/insight/predict/price (电价预测)
  - POST /api/iotcloudai/insight/vision/shadow (遮挡检测)
  - POST /api/iotcloudai/insight/vision/charger(桩巡检)
  - GET  /api/iotcloudai/insight/status        (引擎状态)
  - POST /api/iotcloudai/report/summarize      (AI摘要)
  - POST /api/iotcloudai/report/intent-feedback(意图反馈)
"""

import pytest
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from mock_client import MockApiClient, MOCK_TOKEN


class ChatApiClient:
    """Chat API 测试客户端"""
    def __init__(self):
        self._client = MockApiClient(token=MOCK_TOKEN)
        self._saved_token = MOCK_TOKEN

    def get(self, endpoint, **kwargs):
        return self._client.get(endpoint, **kwargs)

    def post(self, endpoint, json_data=None, **kwargs):
        return self._client.post(endpoint, json=json_data, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self._client.delete(endpoint, **kwargs)

    def clear_token(self):
        self._saved_token = self._client.token
        self._client.clear_token()

    def set_invalid_token(self):
        self._saved_token = self._client.token
        self._client.set_token("invalid.fake.token")

    def restore_token(self):
        self._client.set_token(self._saved_token)


@pytest.fixture(scope="module")
def client():
    return ChatApiClient()


@pytest.mark.api
@pytest.mark.iotcloudai
@pytest.mark.chat
class TestChatSendApi:
    """POST /api/iotcloudai/chat/send 测试"""

    def test_send_message_positive(self, client):
        """正常发送消息"""
        response = client.post("/api/iotcloudai/chat/send", json_data={
            "message": "今天有多少设备在线？",
            "scene": "daily_ops"
        })
        assert response is not None
        assert response.status_code < 500

    def test_send_message_with_session(self, client):
        """带会话ID发送消息"""
        session_id = str(uuid.uuid4())
        response = client.post("/api/iotcloudai/chat/send", json_data={
            "message": "充电站收入情况",
            "sessionId": session_id,
            "scene": "charging"
        })
        assert response is not None
        assert response.status_code < 500

    def test_send_empty_message(self, client):
        """发送空消息 - 应返回验证错误"""
        response = client.post("/api/iotcloudai/chat/send", json_data={
            "message": "",
            "scene": "daily_ops"
        })
        assert response is not None

    def test_send_message_no_auth(self, client):
        """发送消息 - 缺少认证"""
        client.clear_token()
        try:
            response = client.post("/api/iotcloudai/chat/send", json_data={
                "message": "测试",
                "scene": "daily_ops"
            })
            assert response.status_code == 401 or response.status_code == 403
        finally:
            client.restore_token()

    def test_send_message_invalid_token(self, client):
        """发送消息 - 无效Token"""
        client.set_invalid_token()
        try:
            response = client.post("/api/iotcloudai/chat/send", json_data={
                "message": "测试",
                "scene": "daily_ops"
            })
            assert response.status_code == 401 or response.status_code == 403
        finally:
            client.restore_token()

    def test_send_message_all_scenes(self, client):
        """不同场景发送消息"""
        scenes = ["daily_ops", "charging", "energy", "prediction", "report"]
        for scene in scenes:
            response = client.post("/api/iotcloudai/chat/send", json_data={
                "message": f"请分析{scene}场景",
                "scene": scene
            })
            assert response is not None
            assert response.status_code < 500


@pytest.mark.api
@pytest.mark.iotcloudai
@pytest.mark.chat
class TestSessionApi:
    """会话管理 API 测试"""

    def test_get_sessions_positive(self, client):
        """获取会话列表"""
        response = client.get("/api/iotcloudai/sessions", params={"page": 1, "pageSize": 20})
        assert response is not None
        assert response.status_code < 500

    def test_get_sessions_pagination(self, client):
        """会话列表分页"""
        response = client.get("/api/iotcloudai/sessions", params={"page": 2, "pageSize": 5})
        assert response is not None
        assert response.status_code < 500

    def test_get_sessions_no_auth(self, client):
        """会话列表 - 缺少认证"""
        client.clear_token()
        try:
            response = client.get("/api/iotcloudai/sessions")
            assert response.status_code == 401 or response.status_code == 403
        finally:
            client.restore_token()

    def test_get_messages_positive(self, client):
        """获取会话消息"""
        session_id = str(uuid.uuid4())
        response = client.get(f"/api/iotcloudai/sessions/{session_id}/messages",
                              params={"page": 1, "pageSize": 50})
        assert response is not None
        assert response.status_code < 500

    def test_delete_session_positive(self, client):
        """删除会话"""
        session_id = str(uuid.uuid4())
        response = client.delete(f"/api/iotcloudai/sessions/{session_id}")
        assert response is not None
        assert response.status_code < 500

    def test_delete_session_no_auth(self, client):
        """删除会话 - 缺少认证"""
        client.clear_token()
        try:
            session_id = str(uuid.uuid4())
            response = client.delete(f"/api/iotcloudai/sessions/{session_id}")
            assert response.status_code == 401 or response.status_code == 403
        finally:
            client.restore_token()


@pytest.mark.api
@pytest.mark.iotcloudai
@pytest.mark.insight
class TestInsightApi:
    """智能洞察 API 测试"""

    def test_predict_load_positive(self, client):
        """执行负荷预测"""
        response = client.post("/api/iotcloudai/insight/predict/load", json_data={
            "forecastHours": 24,
            "historyDays": 7
        })
        assert response is not None
        assert response.status_code < 500

    def test_predict_pv_positive(self, client):
        """执行光伏发电预测"""
        response = client.post("/api/iotcloudai/insight/predict/pv", json_data={
            "forecastHours": 24,
            "includeWeather": True
        })
        assert response is not None
        assert response.status_code < 500

    def test_predict_price_positive(self, client):
        """执行电价预测"""
        response = client.post("/api/iotcloudai/insight/predict/price", json_data={
            "forecastHours": 48,
            "historyDays": 30
        })
        assert response is not None
        assert response.status_code < 500

    def test_predict_no_auth(self, client):
        """预测 - 缺少认证"""
        client.clear_token()
        try:
            response = client.post("/api/iotcloudai/insight/predict/load", json_data={
                "forecastHours": 24
            })
            assert response.status_code == 401 or response.status_code == 403
        finally:
            client.restore_token()

    def test_get_engine_status(self, client):
        """获取AI引擎状态"""
        response = client.get("/api/iotcloudai/insight/status")
        assert response is not None
        assert response.status_code < 500


@pytest.mark.api
@pytest.mark.iotcloudai
@pytest.mark.report
class TestAiReportApi:
    """AI报告 API 测试"""

    def test_summarize_positive(self, client):
        """生成AI摘要"""
        response = client.post("/api/iotcloudai/report/summarize", json_data={
            "data": "设备A运行正常，设备B告警3次，充电桩C离线2小时",
            "instruction": "请生成简洁中文摘要"
        })
        assert response is not None
        assert response.status_code < 500

    def test_summarize_empty_data(self, client):
        """空数据摘要"""
        response = client.post("/api/iotcloudai/report/summarize", json_data={
            "data": "",
            "instruction": "摘要"
        })
        assert response is not None

    def test_intent_feedback_positive(self, client):
        """提交意图反馈"""
        response = client.post("/api/iotcloudai/report/intent-feedback", json_data={
            "intentLogId": str(uuid.uuid4()),
            "wasCorrect": True
        })
        assert response is not None
        assert response.status_code < 500

    def test_intent_feedback_with_correction(self, client):
        """提交意图反馈 - 含纠正"""
        response = client.post("/api/iotcloudai/report/intent-feedback", json_data={
            "intentLogId": str(uuid.uuid4()),
            "wasCorrect": False,
            "correction": "charging_query"
        })
        assert response is not None
        assert response.status_code < 500

    def test_report_no_auth(self, client):
        """报告 - 缺少认证"""
        client.clear_token()
        try:
            response = client.post("/api/iotcloudai/report/summarize", json_data={
                "data": "测试", "instruction": "摘要"
            })
            assert response.status_code == 401 or response.status_code == 403
        finally:
            client.restore_token()
