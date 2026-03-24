# selenium 测试错误报告

- **执行时间**: 2026-03-24 06:24:51 UTC
- **Git Commit**: 6f232d004bed373a4783d65def5e616c54dd134a

## 失败详情

```
BrokenPipeError: [Errno 32] Broken pipe
BrokenPipeError: [Errno 32] Broken pipe
BrokenPipeError: [Errno 32] Broken pipe
BrokenPipeError: [Errno 32] Broken pipe
BrokenPipeError: [Errno 32] Broken pipe
BrokenPipeError: [Errno 32] Broken pipe
BrokenPipeError: [Errno 32] Broken pipe
BrokenPipeError: [Errno 32] Broken pipe
E   ConnectionRefusedError: [Errno 111] Connection refused
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=4444): Max retries exceeded with url: /session (Caused by NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused"))
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
E   ConnectionRefusedError: [Errno 111] Connection refused
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=4444): Max retries exceeded with url: /session (Caused by NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused"))
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
E   ConnectionRefusedError: [Errno 111] Connection refused
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=4444): Max retries exceeded with url: /session (Caused by NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused"))
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
E   ConnectionRefusedError: [Errno 111] Connection refused
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=4444): Max retries exceeded with url: /session (Caused by NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused"))
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
E   ConnectionRefusedError: [Errno 111] Connection refused
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=4444): Max retries exceeded with url: /session (Caused by NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused"))
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
E   ConnectionRefusedError: [Errno 111] Connection refused
    raise NewConnectionError(
```
