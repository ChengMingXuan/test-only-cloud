"""
Selenium 测试 - 跨浏览器兼容性
AIOPS 平台登录页面兼容性测试

测试矩阵:
- Chrome 120+ / 110-119 / 90-109
- Firefox Latest / ESR
- Edge Latest
- Safari 16+ / 15
- Mobile Chrome / Safari
"""

import os
import pytest
import requests as _requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def _check_frontend():
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:8000")
    try:
        _requests.get(base_url, timeout=5)
        return True
    except Exception:
        return False


_frontend_available = _check_frontend()
pytestmark = pytest.mark.skipif(not _frontend_available, reason="前端服务不可用")


class TestLoginPageCompatibility:
    """登录页面跨浏览器兼容性测试"""
    
    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    @pytest.mark.compatibility
    def test_login_page_rendering(self, driver, test_config, browser):
        """
        [P0] 登录页面在主流浏览器中正确渲染
        """
        driver.get(f"{test_config['base_url']}/login")
        
        # 断言：页面标题正确
        assert "AIOPS" in driver.title, f"{browser}: 页面标题不正确"
        
        # 断言：关键元素可见
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        assert username_input.is_displayed(), f"{browser}: 用户名输入框不可见"
        
        password_input = driver.find_element(By.ID, "password")
        assert password_input.is_displayed(), f"{browser}: 密码输入框不可见"
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        assert login_button.is_displayed(), f"{browser}: 登录按钮不可见"
        assert login_button.is_enabled(), f"{browser}: 登录按钮未启用"
    
    
    @pytest.mark.browser("chrome")
    def test_login_chrome_specific(self, chrome_driver, test_config):
        """[P1] Chrome浏览器专项测试"""
        chrome_driver.get(f"{test_config['base_url']}/login")
        
        # 测试Chrome特定功能（如自动填充）
        username_input = chrome_driver.find_element(By.ID, "username")
        autocomplete = username_input.get_attribute("autocomplete")
        assert autocomplete in ["username", "email", "on"], "Chrome自动填充属性不正确"
    
    
    @pytest.mark.browser("firefox")
    def test_login_firefox_specific(self, firefox_driver, test_config):
        """[P1] Firefox浏览器专项测试"""
        firefox_driver.get(f"{test_config['base_url']}/login")
        
        # 测试Firefox特定行为
        login_button = firefox_driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        assert login_button.tag_name == "button", "Firefox按钮标签不正确"
    
    
    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.cross_browser
    def test_login_form_submission(self, driver, test_config, browser):
        """
        [P0] 登录表单在所有浏览器中可正常提交
        """
        driver.get(f"{test_config['base_url']}/login")
        
        # 填写表单
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        
        username_input.send_keys("admin@jgsy.com")
        password_input.send_keys("P@ssw0rd")
        
        # 提交表单
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # 断言：跳转到Dashboard（或显示错误）
        try:
            WebDriverWait(driver, 15).until(
                EC.url_contains("/dashboard")
            )
            assert "/dashboard" in driver.current_url, f"{browser}: 登录成功后未跳转到Dashboard"
        except TimeoutException:
            # 如果未跳转，检查是否有错误提示
            error_message = driver.find_elements(By.CSS_SELECTOR, ".error-message, .alert-danger")
            if error_message:
                print(f"{browser}: 登录失败，错误信息: {error_message[0].text}")
            else:
                raise AssertionError(f"{browser}: 登录后既未跳转也未显示错误")
    
    
    @pytest.mark.parametrize("browser", ["chrome", "firefox"])
    @pytest.mark.compatibility
    def test_css_flexbox_compatibility(self, driver, test_config, browser):
        """
        [P1] CSS Flexbox布局兼容性（登录表单居中）
        """
        driver.get(f"{test_config['base_url']}/login")
        
        login_form = driver.find_element(By.CLASS_NAME, "login-form")
        display_property = login_form.value_of_css_property("display")
        
        # 断言：使用flex布局
        assert display_property == "flex" or "flex" in display_property, \
            f"{browser}: 登录表单未使用Flexbox布局"
    
    
    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.compatibility
    def test_form_validation_messages(self, driver, test_config, browser):
        """
        [P1] 表单验证提示在所有浏览器中正确显示
        """
        driver.get(f"{test_config['base_url']}/login")
        
        # 不填写直接提交
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # 断言：显示验证错误（HTML5验证或自定义验证）
        try:
            # 尝试HTML5验证
            username_input = driver.find_element(By.ID, "username")
            validation_message = username_input.get_attribute("validationMessage")
            assert validation_message, f"{browser}: 未显示HTML5验证提示"
        except:
            # 尝试自定义验证提示
            error_messages = driver.find_elements(By.CSS_SELECTOR, ".field-error, .invalid-feedback")
            assert len(error_messages) > 0, f"{browser}: 未显示表单验证提示"


class TestLoginPageResponsive:
    """登录页面响应式布局测试"""
    
    @pytest.mark.parametrize("viewport", [
        (1920, 1080),  # 桌面
        (1366, 768),   # 笔记本
        (768, 1024),   # 平板竖屏
        (375, 667),    # 手机
    ])
    @pytest.mark.compatibility
    def test_login_responsive_layout(self, chrome_driver, test_config, viewport):
        """
        [P1] 登录页面响应式布局（不同视口尺寸）
        """
        width, height = viewport
        chrome_driver.set_window_size(width, height)
        chrome_driver.get(f"{test_config['base_url']}/login")
        
        # 断言：关键元素可见
        username_input = chrome_driver.find_element(By.ID, "username")
        password_input = chrome_driver.find_element(By.ID, "password")
        login_button = chrome_driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        assert username_input.is_displayed(), f"{width}x{height}: 用户名输入框不可见"
        assert password_input.is_displayed(), f"{width}x{height}: 密码输入框不可见"
        assert login_button.is_displayed(), f"{width}x{height}: 登录按钮不可见"
        
        # 断言：输入框宽度合理（不超出视口）
        username_width = username_input.size['width']
        assert username_width <= width - 40, f"{width}x{height}: 输入框宽度超出视口"
    
    
    @pytest.mark.mobile
    def test_login_mobile_chrome(self, mobile_chrome_driver, test_config):
        """[P1] 移动Chrome浏览器登录页面"""
        mobile_chrome_driver.get(f"{test_config['base_url']}/login")
        
        # 断言：移动视口下元素垂直排列
        login_form = mobile_chrome_driver.find_element(By.CLASS_NAME, "login-form")
        flex_direction = login_form.value_of_css_property("flex-direction")
        assert flex_direction == "column", "移动端表单未垂直排列"


class TestCSSCompatibility:
    """CSS兼容性测试"""
    
    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.compatibility
    def test_css_grid_support(self, driver, test_config, browser):
        """
        [P2] CSS Grid布局兼容性（Dashboard卡片布局）
        """
        # 先登录
        driver.get(f"{test_config['base_url']}/login")
        driver.find_element(By.ID, "username").send_keys("admin@jgsy.com")
        driver.find_element(By.ID, "password").send_keys("P@ssw0rd")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # 等待Dashboard加载
        try:
            WebDriverWait(driver, 15).until(EC.url_contains("/dashboard"))
        except TimeoutException:
            pytest.skip(f"{browser}: 无法登录到Dashboard")
        
        # 检查Grid布局
        dashboard_grid = driver.find_element(By.CLASS_NAME, "dashboard-grid")
        display_property = dashboard_grid.value_of_css_property("display")
        assert "grid" in display_property, f"{browser}: Dashboard未使用Grid布局"
    
    
    @pytest.mark.parametrize("browser", ["chrome", "firefox"])
    @pytest.mark.compatibility
    def test_css_variables_support(self, driver, test_config, browser):
        """
        [P2] CSS变量（自定义属性）兼容性
        """
        driver.get(f"{test_config['base_url']}/login")
        
        # 获取CSS变量值
        primary_color = driver.execute_script(
            "return getComputedStyle(document.documentElement).getPropertyValue('--primary-color');"
        )
        
        assert primary_color.strip(), f"{browser}: CSS变量未生效"


class TestJavaScriptCompatibility:
    """JavaScript兼容性测试"""
    
    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.compatibility
    def test_es6_features(self, driver, test_config, browser):
        """
        [P2] ES6语法兼容性（箭头函数、Promise、async/await）
        """
        driver.get(f"{test_config['base_url']}/login")
        
        # 测试Promise支持
        promise_supported = driver.execute_script(
            "return typeof Promise !== 'undefined';"
        )
        assert promise_supported, f"{browser}: 不支持Promise"
        
        # 测试async/await支持（间接检测）
        async_supported = driver.execute_script(
            "return typeof (async () => {})().then === 'function';"
        )
        assert async_supported, f"{browser}: 不支持async/await"
    
    
    @pytest.mark.parametrize("browser", ["chrome", "firefox"])
    @pytest.mark.compatibility
    def test_local_storage_support(self, driver, test_config, browser):
        """
        [P1] LocalStorage兼容性
        """
        driver.get(f"{test_config['base_url']}/login")
        
        # 测试LocalStorage读写
        driver.execute_script("localStorage.setItem('test_key', 'test_value');")
        value = driver.execute_script("return localStorage.getItem('test_key');")
        
        assert value == "test_value", f"{browser}: LocalStorage读写失败"
        
        # 清理
        driver.execute_script("localStorage.removeItem('test_key');")


class TestOlderBrowsers:
    """老旧浏览器兼容性测试（需要Selenium Grid）"""
    
    @pytest.mark.skip(reason="需要配置Selenium Grid和老旧浏览器环境")
    @pytest.mark.compatibility
    def test_ie11_compatibility(self, test_config):
        """[P2] IE11兼容性测试（如果需要支持）"""
        # 需要特殊的IE11驱动和配置
        pass
    
    
    @pytest.mark.skip(reason="需要配置Selenium Grid和Edge Legacy")
    @pytest.mark.compatibility
    def test_edge_legacy_compatibility(self, test_config):
        """[P2] Edge Legacy兼容性测试"""
        # 需要Edge Legacy驱动
        pass
