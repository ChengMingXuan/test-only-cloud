# 🔬 Selenium（浏览器兼容性测试） — 测试报告

> 来源：GitHub Actions CI | 级别：full | 2026-03-24 06:24:50 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 6540 |
| 实际执行 | 8258 |
| ✅ 通过 | 7550 |
| ❌ 失败 | 684 |
| ⏭️ 跳过 | 24 |
| 通过率 | 91.43% |
| 耗时(s) | 1290.890
0 |

## 发布门禁

- **状态**：❌ 有失败 (684)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `6f232d004bed373a4783d65def5e616c54dd134a` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | full |

## 失败详情

```
BrokenPipeError: [Errno 32] Broken pipe
----------------------------------------
......................................... [ 34%]
........................................................................ [ 34%]
--
BrokenPipeError: [Errno 32] Broken pipe
----------------------------------------
.. [ 40%]
........................................................................ [ 41%]
--
BrokenPipeError: [Errno 32] Broken pipe
----------------------------------------
........................................................... [ 46%]
........................................................................ [ 47%]
--
BrokenPipeError: [Errno 32] Broken pipe
----------------------------------------
........................ [ 52%]
........................................................................ [ 53%]
--
BrokenPipeError: [Errno 32] Broken pipe
----------------------------------------
... [ 69%]
........................................................................ [ 70%]
--
BrokenPipeError: [Errno 32] Broken pipe
----------------------------------------
............................... [ 74%]
........................................................................ [ 74%]
--
BrokenPipeError: [Errno 32] Broken pipe
----------------------------------------
----------------------------------------
Exception occurred during processing of request from ('127.0.0.1', 36626)
--
BrokenPipeError: [Errno 32] Broken pipe
----------------------------------------
.ssss..EE..ss.s.s.ss.s...ss.ss.ssss............... [ 96%]
..........sE.s..........EE.EEEEEEEEEEE.E.EEE..EE.EE.EE..EEE.E.EE.E.EEE.E [ 97%]
--
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
--
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
test_compat/test_compat_charging-form_chrome.py:13: in setup
--
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=4444): Max retries exceeded with url: /session (Caused by NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused"))
------------------------------ Captured log setup ------------------------------
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
______ ERROR at setup of Test_charging_form_chrome.test_layout_responsive ______
[gw0] linux -- Python 3.11.15 /opt/hostedtoolcache/Python/3.11.15/x64/bin/python
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
--
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
--
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
test_compat/test_compat_charging-form_chrome.py:13: in setup
--
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=4444): Max retries exceeded with url: /session (Caused by NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused"))
------------------------------ Captured log setup ------------------------------
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
______ ERROR at setup of Test_charging_form_chrome.test_button_clickable _______
[gw0] linux -- Python 3.11.15 /opt/hostedtoolcache/Python/3.11.15/x64/bin/python
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
--
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
--
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
test_compat/test_compat_charging-form_chrome.py:13: in setup
--
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=4444): Max retries exceeded with url: /session (Caused by NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused"))
------------------------------ Captured log setup ------------------------------
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
___________ ERROR at setup of Test_charging_form_edge.test_page_load ___________
[gw0] linux -- Python 3.11.15 /opt/hostedtoolcache/Python/3.11.15/x64/bin/python
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
--
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
--
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
test_compat/test_compat_charging-form_edge.py:13: in setup
--
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=4444): Max retries exceeded with url: /session (Caused by NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused"))
------------------------------ Captured log setup ------------------------------
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
_______ ERROR at setup of Test_charging_form_edge.test_layout_responsive _______
[gw0] linux -- Python 3.11.15 /opt/hostedtoolcache/Python/3.11.15/x64/bin/python
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
--
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
--
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
test_compat/test_compat_charging-form_edge.py:13: in setup
--
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=4444): Max retries exceeded with url: /session (Caused by NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused"))
------------------------------ Captured log setup ------------------------------
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
_______ ERROR at setup of Test_charging_form_edge.test_button_clickable ________
[gw0] linux -- Python 3.11.15 /opt/hostedtoolcache/Python/3.11.15/x64/bin/python
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
--
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
--
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
test_compat/test_compat_charging-form_edge.py:13: in setup
--
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=4444): Max retries exceeded with url: /session (Caused by NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused"))
------------------------------ Captured log setup ------------------------------
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
_________ ERROR at setup of Test_charging_form_firefox.test_page_load __________
[gw0] linux -- Python 3.11.15 /opt/hostedtoolcache/Python/3.11.15/x64/bin/python
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
--
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
--
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
test_compat/test_compat_charging-form_firefox.py:13: in setup
--
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=4444): Max retries exceeded with url: /session (Caused by NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused"))
------------------------------ Captured log setup ------------------------------
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
_____ ERROR at setup of Test_charging_form_firefox.test_layout_responsive ______
[gw0] linux -- Python 3.11.15 /opt/hostedtoolcache/Python/3.11.15/x64/bin/python
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
--
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
--
    raise NewConnectionError(
```
