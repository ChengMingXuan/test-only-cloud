# 🔬 Selenium（浏览器兼容性测试） — 测试报告

> 来源：GitHub Actions CI | 级别：smoke | 2026-03-23 22:29:31 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 6540 |
| 实际执行 | 8258 |
| ✅ 通过 | 7570 |
| ❌ 失败 | 663 |
| ⏭️ 跳过 | 25 |
| 通过率 | 91.67% |
| 耗时(s) | 4193.230
0 |

## 发布门禁

- **状态**：❌ 有失败 (663)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `75eee389b707d0c3c5489029b23ccbe8d9587442` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | smoke |

## 失败详情

```
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
______ ERROR at setup of Test_charging_form_chrome.test_layout_responsive ______
test_compat/test_compat_charging-form_chrome.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
______ ERROR at setup of Test_charging_form_chrome.test_button_clickable _______
test_compat/test_compat_charging-form_chrome.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
___________ ERROR at setup of Test_charging_form_edge.test_page_load ___________
test_compat/test_compat_charging-form_edge.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_______ ERROR at setup of Test_charging_form_edge.test_layout_responsive _______
test_compat/test_compat_charging-form_edge.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_______ ERROR at setup of Test_charging_form_edge.test_button_clickable ________
test_compat/test_compat_charging-form_edge.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_________ ERROR at setup of Test_charging_form_firefox.test_page_load __________
test_compat/test_compat_charging-form_firefox.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_____ ERROR at setup of Test_charging_form_firefox.test_layout_responsive ______
test_compat/test_compat_charging-form_firefox.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
______ ERROR at setup of Test_charging_form_firefox.test_button_clickable ______
test_compat/test_compat_charging-form_firefox.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
____________ ERROR at setup of Test_dashboard_chrome.test_page_load ____________
test_compat/test_compat_dashboard_chrome.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
________ ERROR at setup of Test_dashboard_chrome.test_layout_responsive ________
test_compat/test_compat_dashboard_chrome.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
________ ERROR at setup of Test_dashboard_chrome.test_button_clickable _________
test_compat/test_compat_dashboard_chrome.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_____________ ERROR at setup of Test_dashboard_edge.test_page_load _____________
test_compat/test_compat_dashboard_edge.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_________ ERROR at setup of Test_dashboard_edge.test_layout_responsive _________
test_compat/test_compat_dashboard_edge.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_________ ERROR at setup of Test_dashboard_edge.test_button_clickable __________
test_compat/test_compat_dashboard_edge.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
___________ ERROR at setup of Test_dashboard_firefox.test_page_load ____________
test_compat/test_compat_dashboard_firefox.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_______ ERROR at setup of Test_dashboard_firefox.test_layout_responsive ________
test_compat/test_compat_dashboard_firefox.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
________ ERROR at setup of Test_dashboard_firefox.test_button_clickable ________
test_compat/test_compat_dashboard_firefox.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
___________ ERROR at setup of Test_device_list_chrome.test_page_load ___________
test_compat/test_compat_device-list_chrome.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_______ ERROR at setup of Test_device_list_chrome.test_layout_responsive _______
test_compat/test_compat_device-list_chrome.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_______ ERROR at setup of Test_device_list_chrome.test_button_clickable ________
test_compat/test_compat_device-list_chrome.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
____________ ERROR at setup of Test_device_list_edge.test_page_load ____________
test_compat/test_compat_device-list_edge.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
________ ERROR at setup of Test_device_list_edge.test_layout_responsive ________
test_compat/test_compat_device-list_edge.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
________ ERROR at setup of Test_device_list_edge.test_button_clickable _________
test_compat/test_compat_device-list_edge.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
__________ ERROR at setup of Test_device_list_firefox.test_page_load ___________
test_compat/test_compat_device-list_firefox.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
______ ERROR at setup of Test_device_list_firefox.test_layout_responsive _______
test_compat/test_compat_device-list_firefox.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_______ ERROR at setup of Test_device_list_firefox.test_button_clickable _______
test_compat/test_compat_device-list_firefox.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
______________ ERROR at setup of Test_login_chrome.test_page_load ______________
test_compat/test_compat_login_chrome.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
__________ ERROR at setup of Test_login_chrome.test_layout_responsive __________
test_compat/test_compat_login_chrome.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
__________ ERROR at setup of Test_login_chrome.test_button_clickable ___________
test_compat/test_compat_login_chrome.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_______________ ERROR at setup of Test_login_edge.test_page_load _______________
test_compat/test_compat_login_edge.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
___________ ERROR at setup of Test_login_edge.test_layout_responsive ___________
test_compat/test_compat_login_edge.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
___________ ERROR at setup of Test_login_edge.test_button_clickable ____________
test_compat/test_compat_login_edge.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_____________ ERROR at setup of Test_login_firefox.test_page_load ______________
test_compat/test_compat_login_firefox.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_________ ERROR at setup of Test_login_firefox.test_layout_responsive __________
test_compat/test_compat_login_firefox.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
__________ ERROR at setup of Test_login_firefox.test_button_clickable __________
test_compat/test_compat_login_firefox.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
___________ ERROR at setup of Test_settlement_chrome.test_page_load ____________
test_compat/test_compat_settlement_chrome.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_______ ERROR at setup of Test_settlement_chrome.test_layout_responsive ________
test_compat/test_compat_settlement_chrome.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
________ ERROR at setup of Test_settlement_chrome.test_button_clickable ________
test_compat/test_compat_settlement_chrome.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
____________ ERROR at setup of Test_settlement_edge.test_page_load _____________
test_compat/test_compat_settlement_edge.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
________ ERROR at setup of Test_settlement_edge.test_layout_responsive _________
test_compat/test_compat_settlement_edge.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_________ ERROR at setup of Test_settlement_edge.test_button_clickable _________
test_compat/test_compat_settlement_edge.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
___________ ERROR at setup of Test_settlement_firefox.test_page_load ___________
test_compat/test_compat_settlement_firefox.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_______ ERROR at setup of Test_settlement_firefox.test_layout_responsive _______
test_compat/test_compat_settlement_firefox.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_______ ERROR at setup of Test_settlement_firefox.test_button_clickable ________
test_compat/test_compat_settlement_firefox.py:13: in setup
    self.driver = webdriver.Remote(
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
_ ERROR at setup of TestPageRenderingCompatibility.test_page_render_all_browsers[chrome-/login] _
test_comprehensive_browser_compat.py:68: in browser
    driver = config['driver_class'](
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'executable_path'
_ ERROR at setup of TestPageRenderingCompatibility.test_page_render_all_browsers[chrome-/dashboard] _
test_comprehensive_browser_compat.py:68: in browser
    driver = config['driver_class'](
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'executable_path'
_ ERROR at setup of TestPageRenderingCompatibility.test_page_render_all_browsers[chrome-/device/list] _
test_comprehensive_browser_compat.py:68: in browser
    driver = config['driver_class'](
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'executable_path'
_ ERROR at setup of TestPageRenderingCompatibility.test_page_render_all_browsers[chrome-/device/create] _
test_comprehensive_browser_compat.py:68: in browser
    driver = config['driver_class'](
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'executable_path'
_ ERROR at setup of TestPageRenderingCompatibility.test_page_render_all_browsers[chrome-/station/list] _
test_comprehensive_browser_compat.py:68: in browser
    driver = config['driver_class'](
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'executable_path'
_ ERROR at setup of TestPageRenderingCompatibility.test_page_render_all_browsers[chrome-/charging/records] _
test_comprehensive_browser_compat.py:68: in browser
    driver = config['driver_class'](
```
