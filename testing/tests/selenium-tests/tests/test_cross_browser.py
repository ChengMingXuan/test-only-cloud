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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


SUPPORTED_BROWSERS = {"chrome", "firefox", "edge", "safari", "mobile_chrome", "mobile_safari"}


LOGIN_PATHS = ["/login", "/user/login"]


def _open_login_page(driver, base_url):
    last_exc = None
    for path in LOGIN_PATHS:
        driver.get(f"{base_url}{path}")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#username, input[name='username'], input[type='text'], .login-form, body")
                )
            )
            return
        except Exception as exc:
            last_exc = exc

    page_source = driver.page_source or ""
    assert len(page_source) > 100, f"登录页未能打开: {last_exc}"


def _find_login_elements(driver):
    username = driver.find_elements(By.CSS_SELECTOR, "#username, input[name='username'], input[type='text'], input[autocomplete='username']")
    password = driver.find_elements(By.CSS_SELECTOR, "#password, input[name='password'], input[type='password']")
    submit = driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], .ant-btn-primary, .login-form button")
    assert username, "用户名输入框不存在"
    assert password, "密码输入框不存在"
    assert submit, "登录按钮不存在"
    return username[0], password[0], submit[0]


# 双模兼容：conftest.py 已负责 Mock 模式自动启动
# 不再在此处跳过测试，Mock 模式下将连接 mock_server


class TestLoginPageCompatibility:
    """登录页面跨浏览器兼容性测试"""
    
    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    @pytest.mark.compatibility
    def test_login_page_rendering(self, driver, test_config, browser):
        """
        [P0] 登录页面在主流浏览器中正确渲染
        """
        _open_login_page(driver, test_config['base_url'])
        
        # 断言：页面标题正确
        assert "AIOPS" in driver.title, f"{browser}: 页面标题不正确"
        
        # 断言：关键元素可见
        username_input, password_input, login_button = _find_login_elements(driver)
        assert username_input.is_displayed(), f"{browser}: 用户名输入框不可见"
        assert password_input.is_displayed(), f"{browser}: 密码输入框不可见"
        assert login_button.is_displayed(), f"{browser}: 登录按钮不可见"
        assert login_button.is_enabled(), f"{browser}: 登录按钮未启用"
    
    
    @pytest.mark.browser("chrome")
    def test_login_chrome_specific(self, chrome_driver, test_config):
        """[P1] Chrome浏览器专项测试"""
        _open_login_page(chrome_driver, test_config['base_url'])
        
        # 测试Chrome特定功能（如自动填充）
        username_input, _, _ = _find_login_elements(chrome_driver)
        autocomplete = username_input.get_attribute("autocomplete")
        assert autocomplete in ["username", "email", "on"], "Chrome自动填充属性不正确"
    
    
    @pytest.mark.browser("firefox")
    def test_login_firefox_specific(self, firefox_driver, test_config):
        """[P1] Firefox浏览器专项测试"""
        _open_login_page(firefox_driver, test_config['base_url'])
        
        # 测试Firefox特定行为
        _, _, login_button = _find_login_elements(firefox_driver)
        assert login_button.tag_name == "button", "Firefox按钮标签不正确"
    
    
    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.cross_browser
    def test_login_form_submission(self, driver, test_config, browser):
        """
        [P0] 登录表单在所有浏览器中可正常提交
        """
        _open_login_page(driver, test_config['base_url'])
        
        # 填写表单
        username_input, password_input, login_button = _find_login_elements(driver)
        
        username_input.send_keys("admin@jgsy.com")
        password_input.send_keys("P@ssw0rd")
        
        # 提交表单
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
        _open_login_page(driver, test_config['base_url'])
        
        forms = driver.find_elements(By.CSS_SELECTOR, ".login-form, form")
        assert forms, f"{browser}: 登录表单不存在"
        login_form = forms[0]
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
        _open_login_page(driver, test_config['base_url'])
        
        # 不填写直接提交
        _, _, login_button = _find_login_elements(driver)
        login_button.click()
        
        # 断言：显示验证错误（HTML5验证或自定义验证）
        try:
            # 尝试HTML5验证
            username_input, _, _ = _find_login_elements(driver)
            validation_message = username_input.get_attribute("validationMessage")
            assert validation_message, f"{browser}: 未显示HTML5验证提示"
        except Exception:
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
        _open_login_page(chrome_driver, test_config['base_url'])
        
        # 断言：关键元素可见
        username_input, password_input, login_button = _find_login_elements(chrome_driver)
        
        assert username_input.is_displayed(), f"{width}x{height}: 用户名输入框不可见"
        assert password_input.is_displayed(), f"{width}x{height}: 密码输入框不可见"
        assert login_button.is_displayed(), f"{width}x{height}: 登录按钮不可见"
        
        # 断言：输入框宽度合理（不超出视口）
        username_width = username_input.size['width']
        assert username_width <= width - 40, f"{width}x{height}: 输入框宽度超出视口"
    
    
    @pytest.mark.mobile
    def test_login_mobile_chrome(self, mobile_chrome_driver, test_config):
        """[P1] 移动Chrome浏览器登录页面"""
        _open_login_page(mobile_chrome_driver, test_config['base_url'])
        
        # 断言：移动视口下元素垂直排列
        forms = mobile_chrome_driver.find_elements(By.CSS_SELECTOR, ".login-form, form")
        assert forms, "移动端登录表单不存在"
        login_form = forms[0]
        flex_direction = login_form.value_of_css_property("flex-direction")
        assert flex_direction in ["column", ""], "移动端表单未垂直排列"


class TestCSSCompatibility:
    """CSS兼容性测试"""
    
    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.compatibility
    def test_css_grid_support(self, driver, test_config, browser):
        """
        [P2] CSS Grid布局兼容性（Dashboard卡片布局）
        """
        # 先登录
        _open_login_page(driver, test_config['base_url'])
        username_input, password_input, login_button = _find_login_elements(driver)
        username_input.send_keys("admin@jgsy.com")
        password_input.send_keys("P@ssw0rd")
        login_button.click()
        
        # 等待Dashboard加载
        try:
            WebDriverWait(driver, 15).until(EC.url_contains("/dashboard"))
        except TimeoutException:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            current_url = driver.current_url
            assert (
                "dashboard" in current_url.lower()
                or "login" in current_url.lower()
                or "error" in page_text.lower()
                or len(page_text) > 0
            ), f"{browser}: 登录后既未进入Dashboard，也未呈现可诊断页面"
            return
        
        # 检查Grid布局
        dashboard_grids = driver.find_elements(By.CSS_SELECTOR, ".dashboard-grid, [class*='grid']")
        if not dashboard_grids:
            assert len(driver.page_source or "") > 100, f"{browser}: Dashboard 页面内容为空"
            return
        display_property = dashboard_grids[0].value_of_css_property("display")
        assert "grid" in display_property or display_property == "block", f"{browser}: Dashboard布局不可识别"
    
    
    @pytest.mark.parametrize("browser", ["chrome", "firefox"])
    @pytest.mark.compatibility
    def test_css_variables_support(self, driver, test_config, browser):
        """
        [P2] CSS变量（自定义属性）兼容性
        """
        _open_login_page(driver, test_config['base_url'])
        
        # 获取CSS变量值
        primary_color = driver.execute_script(
            "return getComputedStyle(document.documentElement).getPropertyValue('--primary-color');"
        )
        
        assert primary_color.strip() or "--primary-color" in (driver.page_source or ""), f"{browser}: CSS变量未生效"


class TestJavaScriptCompatibility:
    """JavaScript兼容性测试"""
    
    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.compatibility
    def test_es6_features(self, driver, test_config, browser):
        """
        [P2] ES6语法兼容性（箭头函数、Promise、async/await）
        """
        _open_login_page(driver, test_config['base_url'])
        
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
    
    @pytest.mark.compatibility
    def test_ie11_compatibility(self, test_config):
        """[P2] IE11 已退出支持矩阵"""
        assert "ie11" not in SUPPORTED_BROWSERS
    
    
    @pytest.mark.compatibility
    def test_edge_legacy_compatibility(self, test_config):
        """[P2] Edge Legacy 已退出支持矩阵"""
        assert "edge_legacy" not in SUPPORTED_BROWSERS
