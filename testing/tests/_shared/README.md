# 六工具共享测试常量

本目录存放所有六个测试工具（pytest / Cypress / Puppeteer / Selenium / Playwright / k6）的共享测试数据。

## 文件说明

| 文件 | 用途 | 引用方 |
|-----|------|--------|
| `constants.json` | 全局测试常量：用户、租户、设备、场站、菜单、权限码、DB配置 | 全部六工具 |
| `mock-responses.json` | 统一 `ApiResult<T>` Mock 响应模板：认证、设备、场站、充电、工单等 | Cypress（fixture引用）、Puppeteer（page.route 拦截） |

## 各工具引用方式

### Python（pytest / Selenium）
```python
import json, pathlib
SHARED = json.loads((pathlib.Path(__file__).parent.parent / '_shared' / 'constants.json').read_text('utf-8'))
ADMIN = SHARED['admin']
```

### JavaScript（Cypress / Puppeteer / k6）
```javascript
const SHARED = require('../../_shared/constants.json');
// 或 ES Module
import SHARED from '../../_shared/constants.json' assert { type: 'json' };
```

### TypeScript（Playwright）
```typescript
import SHARED from '../../_shared/constants.json';
// tsconfig.json 需要 "resolveJsonModule": true
```

## 规则

1. **所有工具禁止独立硬编码测试用户、租户 ID、设备编码等信息** — 统一从此目录读取
2. **新增测试数据必须同步更新此处** — 保证六工具数据一致
3. **Mock 响应模板必须与后端 `ApiResult<T>` 格式一致** — `{ success, code, message, data, timestamp }`
