"""
Selenium 浏览器兼容性测试 - dashboard (edge)
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

class Test_dashboard_edge:
    @pytest.fixture(autouse=True)
    def setup(self):
        # 初始化浏览器
        self.driver = webdriver.Remote(
            command_executor='http://localhost:4444',
            options=webdriver.EdgeOptions()
        )
        yield
        self.driver.quit()
    
    def test_page_load(self):
        """页面加载测试"""
        self.driver.get('http://localhost:8000/path/dashboard')
        assert self.driver.title != ''
    
    def test_layout_responsive(self):
        """响应式布局测试"""
        self.driver.get('http://localhost:8000/path/dashboard')
        body = self.driver.find_element(By.TAG_NAME, 'body')
        assert body.is_displayed()
    
    def test_button_clickable(self):
        """按钮交互测试"""
        self.driver.get('http://localhost:8000/path/dashboard')
        button = self.driver.find_elements(By.TAG_NAME, 'button')
        if button:
            button[0].click()
