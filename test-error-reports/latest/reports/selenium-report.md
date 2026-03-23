# 🔬 Selenium（浏览器兼容性测试） — 测试报告

> 来源：GitHub Actions CI | 级别：smoke | 2026-03-23 17:13:00 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 6540 |
| 实际执行 | 6 |
| ✅ 通过 | 0 |
| ❌ 失败 | 6 |
| ⏭️ 跳过 | 0 |
| 通过率 | 0.0% |
| 耗时(s) | 5.804 |

## 发布门禁

- **状态**：❌ 有失败 (6)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `6b9d56d03ad2a776e764a452a8898629462f371d` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | smoke |

## 失败详情

```
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py:188: in exec_module
    source_stat, co = _rewrite_test(fn, self.config)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py:357: in _rewrite_test
    tree = ast.parse(source, filename=strfn)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/ast.py:50: in parse
--
E   SyntaxError: invalid syntax
________ ERROR collecting test_compat/test_compat_charging-form_edge.py ________
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/python.py:507: in importtestmodule
    mod = import_path(
--
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py:188: in exec_module
    source_stat, co = _rewrite_test(fn, self.config)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py:357: in _rewrite_test
    tree = ast.parse(source, filename=strfn)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/ast.py:50: in parse
--
E   SyntaxError: invalid syntax
______ ERROR collecting test_compat/test_compat_charging-form_firefox.py _______
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/python.py:507: in importtestmodule
    mod = import_path(
--
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py:188: in exec_module
    source_stat, co = _rewrite_test(fn, self.config)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py:357: in _rewrite_test
    tree = ast.parse(source, filename=strfn)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/ast.py:50: in parse
--
E   SyntaxError: invalid syntax
________ ERROR collecting test_compat/test_compat_device-list_chrome.py ________
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/python.py:507: in importtestmodule
    mod = import_path(
--
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py:188: in exec_module
    source_stat, co = _rewrite_test(fn, self.config)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py:357: in _rewrite_test
    tree = ast.parse(source, filename=strfn)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/ast.py:50: in parse
--
E   SyntaxError: invalid syntax
_________ ERROR collecting test_compat/test_compat_device-list_edge.py _________
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/python.py:507: in importtestmodule
    mod = import_path(
--
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py:188: in exec_module
    source_stat, co = _rewrite_test(fn, self.config)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py:357: in _rewrite_test
    tree = ast.parse(source, filename=strfn)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/ast.py:50: in parse
--
E   SyntaxError: invalid syntax
_______ ERROR collecting test_compat/test_compat_device-list_firefox.py ________
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/python.py:507: in importtestmodule
    mod = import_path(
--
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py:188: in exec_module
    source_stat, co = _rewrite_test(fn, self.config)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py:357: in _rewrite_test
    tree = ast.parse(source, filename=strfn)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/ast.py:50: in parse
--
E   SyntaxError: invalid syntax
=============================== warnings summary ===============================
tests/generated/supplement/test_085_blockchain_cert_compat.py:40
  /home/runner/work/test-only-cloud/test-only-cloud/testing/tests/selenium-tests/tests/generated/supplement/test_085_blockchain_cert_compat.py:40: PytestUnknownMarkWarning: Unknown pytest.mark.chrome - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
```
