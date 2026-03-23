import requests
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

@dataclass
class ApiResponse:
    status_code: int
    body: Dict[str, Any]
    headers: Dict[str, str]
    elapsed_ms: float
    
    @property
    def is_success(self) -> bool:
        return self.status_code in [200, 201, 204]
    
    @property
    def error_msg(self) -> Optional[str]:
        if self.body and isinstance(self.body, dict):
            return self.body.get('message') or self.body.get('error')
        return None

class ApiClient:
    """HTTP 请求封装"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        
    def set_auth(self, access_token: str, refresh_token: Optional[str] = None):
        """设置认证令牌"""
        self.access_token = access_token
        self.refresh_token = refresh_token
        
    def _get_headers(self, custom_headers: Optional[Dict] = None) -> Dict[str, str]:
        """生成请求头"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'AIOPS-Test-Client/1.0'
        }
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        if custom_headers:
            headers.update(custom_headers)
        return headers
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> ApiResponse:
        """发送 HTTP 请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # 合并默认参数
        request_kwargs = {
            'timeout': self.timeout,
            'headers': self._get_headers(kwargs.pop('headers', None))
        }
        request_kwargs.update(kwargs)
        
        try:
            start_time = time.time()
            response = self.session.request(method, url, **request_kwargs)
            elapsed_ms = (time.time() - start_time) * 1000
            
            try:
                body = response.json()
            except:
                body = response.text
                
            return ApiResponse(
                status_code=response.status_code,
                body=body,
                headers=dict(response.headers),
                elapsed_ms=elapsed_ms
            )
        except Exception as e:
            raise Exception(f"请求失败 [{method} {url}]: {str(e)}")
    
    def get(self, endpoint: str, **kwargs) -> ApiResponse:
        """GET 请求"""
        return self._request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, json_data: Optional[Dict] = None, **kwargs) -> ApiResponse:
        """POST 请求"""
        if json_data:
            kwargs['json'] = json_data
        return self._request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, json_data: Optional[Dict] = None, **kwargs) -> ApiResponse:
        """PUT 请求"""
        if json_data:
            kwargs['json'] = json_data
        return self._request('PUT', endpoint, **kwargs)
    
    def patch(self, endpoint: str, json_data: Optional[Dict] = None, **kwargs) -> ApiResponse:
        """PATCH 请求"""
        if json_data:
            kwargs['json'] = json_data
        return self._request('PATCH', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> ApiResponse:
        """DELETE 请求"""
        return self._request('DELETE', endpoint, **kwargs)

# 示例用法
if __name__ == '__main__':
    client = ApiClient('http://localhost:5000/api')
    
    # 登陆
    resp = client.post('account/auth/login', json_data={
        'username': 'admin',
        'password': 'Admin@123'
    })
    print(f"登陆状态码: {resp.status_code}, 耗时: {resp.elapsed_ms:.0f}ms")
    
    if resp.is_success and isinstance(resp.body, dict) and 'data' in resp.body:
        token = resp.body['data'].get('accessToken')
        client.set_auth(token)
        print(f"获得 Token: {token[:30]}...")
        
        # 获取菜单
        resp = client.get('permission/menus')
        print(f"菜单状态码: {resp.status_code}")
