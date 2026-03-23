# Selenium 跨浏览器兼容性测试套件

> **AIOPS 平台浏览器兼容性验证**  
> 基于 Selenium WebDriver 的多浏览器矩阵测试

---

## 📋 目录

- [快速开始](#快速开始)
- [浏览器矩阵](#浏览器矩阵)
- [Selenium Grid](#selenium-grid)
- [执行测试](#执行测试)
- [最佳实践](#最佳实践)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd tests/selenium-tests
pip install -r requirements.txt
```

### 2. 本地执行（自动下载驱动）

```bash
# 运行所有测试（Chrome）
pytest tests/ -v

# 指定浏览器
pytest tests/ --browser=firefox -v
pytest tests/ --browser=edge -v

# Headless模式
pytest tests/ --headless -v
```

### 3. 使用 Selenium Grid

```bash
# 启动Selenium Grid
docker-compose -f selenium-grid-config.yml up -d

# 使用Grid执行测试
pytest tests/ --use-grid -v

# 查看Grid控制台
# 浏览器访问: http://localhost:4444
```

---

## 🌐 浏览器矩阵

### 支持的浏览器

| 浏览器 | 版本 | 操作系统 | 优先级 |
|--------|------|----------|--------|
| **Chrome** | 120+, 110-119, 90-109 | Win/Mac/Linux | P0 |
| **Firefox** | Latest, ESR | Win/Mac/Linux | P0 |
| **Edge** | Latest | Windows | P1 |
| **Safari** | 16+, 15 | macOS | P1 |
| **Mobile Chrome** | Latest | Android模拟 | P2 |
| **Mobile Safari** | Latest | iOS模拟 | P2 |
| **IE11** | 11 | Windows 7/10 | P3（如需支持） |

### 测试覆盖率目标

- ✅ Chrome: 100% 核心功能
- ✅ Firefox: 100% 核心功能
- ✅ Edge: 90% 核心功能
- ✅ Safari: 80% 核心功能（macOS限制）
- ✅ Mobile: 60% 关键流程

---

## 🏗️ Selenium Grid

### 架构图

```
┌─────────────────────────────────────────────┐
│          Selenium Hub (4444)                │
│         ┌─────────┬─────────┬─────────┐    │
│         │  测试1   │  测试2   │  测试3   │    │
│         └─────────┴─────────┴─────────┘    │
└────────────────┬────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼───┐    ┌───▼───┐    ┌───▼───┐
│Chrome │    │Firefox│    │ Edge  │
│Node x2│    │Node x2│    │Node x1│
└───────┘    └───────┘    └───────┘
```

### 启动 Grid

```bash
# 启动完整Grid（Hub + 5个节点）
docker-compose -f selenium-grid-config.yml up -d

# 查看状态
docker-compose -f selenium-grid-config.yml ps

# 查看日志
docker-compose -f selenium-grid-config.yml logs -f

# 停止Grid
docker-compose -f selenium-grid-config.yml down
```

### Grid 配置说明

```yaml
# selenium-grid-config.yml
services:
  selenium-hub:
    image: selenium/hub:4.16.1
    ports:
      - "4444:4444"
  
  chrome-node:
    image: selenium/node-chrome:4.16.1
    environment:
      - SE_NODE_MAX_SESSIONS=5
    deploy:
      replicas: 2  # 2个Chrome节点
  
  firefox-node:
    image: selenium/node-firefox:4.16.1
    deploy:
      replicas: 2  # 2个Firefox节点
```

### Grid Web Console

访问 `http://localhost:4444` 查看：
- ✅ 可用节点数量
- ✅ 正在运行的会话
- ✅ 队列中的测试
- ✅ 节点健康状态

---

## ▶️ 执行测试

### 基础命令

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定文件
pytest tests/test_cross_browser.py -v

# 运行特定测试类
pytest tests/test_cross_browser.py::TestLoginPageCompatibility -v

# 运行特定测试方法
pytest tests/test_cross_browser.py::TestLoginPageCompatibility::test_login_page_rendering -v
```

### 使用标记筛选

```bash
# 仅兼容性测试
pytest tests/ -m compatibility -v

# 仅跨浏览器测试
pytest tests/ -m cross_browser -v

# 仅移动端测试
pytest tests/ -m mobile -v
```

### 浏览器选择

```bash
# Chrome（默认）
pytest tests/ --browser=chrome -v

# Firefox
pytest tests/ --browser=firefox -v

# Edge
pytest tests/ --browser=edge -v

# Safari（仅macOS）
pytest tests/ --browser=safari -v
```

### 并行执行

```bash
# 使用pytest-xdist并行执行（4个worker）
pytest tests/ -n 4 -v

# 使用Selenium Grid并行（自动并行）
pytest tests/ --use-grid -n auto -v
```

### 参数化测试

测试代码中使用 `@pytest.mark.parametrize` 自动运行多浏览器：

```python
@pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
def test_login(driver, browser):
    # 自动运行3次（chrome, firefox, edge）
    pass
```

执行：

```bash
pytest tests/test_cross_browser.py::TestLoginPageCompatibility::test_login_form_submission -v
# 自动运行3次，覆盖3个浏览器
```

---

## 📊 测试报告

### HTML报告

```bash
# 生成HTML报告
pytest tests/ --html=../test-reports/selenium-report/report.html -v

# 查看报告
start ../test-reports/selenium-report/report.html  # Windows
open ../test-reports/selenium-report/report.html   # macOS
```

### Allure报告（推荐）

```bash
# 生成Allure原始数据
pytest tests/ --alluredir=../test-reports/selenium-report/allure-results -v

# 生成并打开Allure报告
allure generate ../test-reports/selenium-report/allure-results -o ../test-reports/selenium-report/allure-report --clean
allure open ../test-reports/selenium-report/allure-report
```

### 截图

测试失败时自动截图，保存到：
- `../test-reports/selenium-report/screenshots/`

### 示例报告输出

```
======================= test session starts =======================
platform win32 -- Python 3.11.0, pytest-7.4.0
collected 24 items

tests/test_cross_browser.py::test_login_chrome .......... [PASSED]
tests/test_cross_browser.py::test_login_firefox ......... [PASSED]
tests/test_cross_browser.py::test_login_edge ............ [PASSED]
tests/test_cross_browser.py::test_css_flexbox_chrome .... [PASSED]
tests/test_cross_browser.py::test_css_flexbox_firefox ... [PASSED]

====================== 24 passed in 180.50s ======================

浏览器兼容性测试通过率: 100%
- Chrome: 8/8 通过
- Firefox: 8/8 通过
- Edge: 8/8 通过
```

---

## 🎯 测试用例

### 已实现测试（30+ 用例）

#### 1. 跨浏览器兼容性

- ✅ 登录页面在主流浏览器中正确渲染
- ✅ Chrome浏览器专项测试
- ✅ Firefox浏览器专项测试
- ✅ 登录表单在所有浏览器中可正常提交
- ✅ CSS Flexbox布局兼容性
- ✅ 表单验证提示在所有浏览器中正确显示

#### 2. 响应式布局

- ✅ 登录页面响应式布局（多种视口尺寸）
- ✅ 移动Chrome浏览器登录页面

#### 3. CSS兼容性

- ✅ CSS Grid布局兼容性
- ✅ CSS变量（自定义属性）兼容性

#### 4. JavaScript兼容性

- ✅ ES6语法兼容性（Promise、async/await）
- ✅ LocalStorage兼容性

### 待实现测试（40+ 用例）

- 充电订单页面跨浏览器兼容性
- 充电站管理页面响应式布局
- 数据看板图表在不同浏览器中渲染
- WebSocket实时通信兼容性
- Service Worker离线缓存兼容性
- IndexedDB数据持久化兼容性

---

## 🔧 最佳实践

### 1. 使用显式等待

**Bad ❌**:
```python
import time
driver.get("https://example.com")
time.sleep(5)  # 固定等待
```

**Good ✅**:
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver.get("https://example.com")
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "element-id"))
)
```

### 2. 处理CORS跨域

```python
# Chrome允许跨域（仅测试环境）
options = ChromeOptions()
options.add_argument("--disable-web-security")
options.add_argument("--disable-site-isolation-trials")
```

### 3. 处理SSL证书错误

```python
# Chrome忽略SSL错误
options = ChromeOptions()
options.add_argument("--ignore-certificate-errors")
```

### 4. 检测元素可见性

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 等待元素可见
element = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "button-id"))
)
```

### 5. 处理弹窗

```python
# Alert弹窗
alert = driver.switch_to.alert
print(alert.text)
alert.accept()  # 或 alert.dismiss()
```

### 6. 截图调试

```python
# 测试失败时自动截图（已在conftest.py中实现）
driver.save_screenshot("debug_screenshot.png")
```

---

## 🐛 常见问题

### Q1: WebDriverManager下载驱动失败？

**A**: 手动下载驱动并指定路径：

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

service = Service(executable_path=r"C:\drivers\chromedriver.exe")
driver = webdriver.Chrome(service=service)
```

### Q2: Selenium Grid无法连接？

**A**: 检查Grid是否启动：

```bash
# 检查容器状态
docker ps | grep selenium

# 检查4444端口
curl http://localhost:4444/status
```

### Q3: Safari驱动无法使用？

**A**: macOS需要手动启用Safari驱动：

```bash
# 启用Safari远程自动化
safaridriver --enable
```

### Q4: 测试速度太慢？

**A**: 使用并行执行和Grid：

```bash
# 本地并行
pytest tests/ -n 4 -v

# Grid并行
pytest tests/ --use-grid -n auto -v
```

### Q5: 如何测试IE11？

**A**: 需要Windows机器和IE Driver：

```python
from selenium import webdriver
driver = webdriver.Ie()
```

---

## 📚 相关文档

- [Selenium 官方文档](https://www.selenium.dev/documentation/)
- [Selenium Grid 文档](https://www.selenium.dev/documentation/grid/)
- [WebDriver Manager](https://github.com/SergeyPirogov/webdriver_manager)
- [00-五工具互补测试架构方案.md](../00-五工具互补测试架构方案.md)

---

## 🔗 快捷命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动Grid
docker-compose -f selenium-grid-config.yml up -d

# 运行全部测试（Grid）
pytest tests/ --use-grid -n auto -v

# 生成HTML报告
pytest tests/ --html=../test-reports/selenium-report/report.html

# 仅Chrome兼容性测试
pytest tests/ -m compatibility --browser=chrome -v

# 停止Grid
docker-compose -f selenium-grid-config.yml down
```

---

**最后更新**: 2026-03-05  
**维护者**: JGSY.AGI 测试团队
