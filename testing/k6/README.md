# K6 Performance Testing Framework

## 概述
JGSY AGI Platform的性能测试框架，使用K6进行负载测试、压力测试和性能基准测试。

## 性能目标
- **吞吐量**: 10,000 RPS
- **并发用户**: 1,000 VUs
- **响应时间**:
  - P50 < 100ms
  - P90 < 150ms
  - P95 < 200ms ⭐
  - P99 < 500ms ⭐
- **错误率**: < 1%
- **可用性**: 99.9%

## 测试场景

### 1. Smoke Test (冒烟测试)
**目的**: 快速验证系统基本功能是否正常

**配置**:
- VUs: 10
- 持续时间: 3分钟
- 阈值: P95<500ms, P99<1000ms

**运行**:
```bash
k6 run scenarios/smoke-test.js
```

### 2. Load Test (负载测试)
**目的**: 验证系统在正常负载下的性能表现

**配置**:
- VUs: 100 → 200
- 持续时间: 16分钟
- 目标: 500-1000 RPS
- 阈值: P95<200ms, P99<500ms

**运行**:
```bash
k6 run scenarios/load-test.js
```

### 3. Stress Test (压力测试)
**目的**: 找到系统的性能极限和瓶颈

**配置**:
- VUs: 200 → 500 → 1000
- 持续时间: 23分钟
- 目标: 10000+ RPS
- 阈值: P95<500ms, P99<1000ms

**运行**:
```bash
k6 run scenarios/stress-test.js
```

### 4. Spike Test (峰值测试)
**目的**: 验证系统对突发流量的处理能力

**配置**:
- VUs: 100 → 2000 (30秒内激增)
- 持续时间: 5分钟
- 阈值: P95<1000ms, P99<2000ms

**运行**:
```bash
k6 run scenarios/spike-test.js
```

### 5. Soak Test (浸泡测试)
**目的**: 长时间运行检测内存泄漏和性能退化

**配置**:
- VUs: 200
- 持续时间: 70分钟
- 阈值: P95<300ms, P99<600ms

**运行**:
```bash
k6 run scenarios/soak-test.js
```

### 6. Comprehensive Test (综合测试) 🆕
**目的**: 覆盖所有微服务的综合性能测试

**配置**:
- 多场景: smoke, load, stress, spike
- 覆盖服务: Gateway, Auth, Charging, Device, Permission, Analytics, WorkOrder, Blockchain
- 自动生成 HTML 报告

**运行**:
```bash
k6 run scenarios/comprehensive-test.js
```

### 7. Digital Twin Test (数字孪生测试) 🆕
**目的**: 针对 IoT 数据采集和数字孪生的专项测试

**配置**:
- WebSocket 实时数据流: 500 并发连接
- 遥测数据上报: 10000 TPS
- 数字孪生同步: 100 VUs
- ML 预测 API: 20 VUs

**运行**:
```bash
k6 run scenarios/digital-twin-test.js
```

### 8. Blockchain Test (区块链测试) 🆕
**目的**: 针对区块链服务的专项测试

**配置**:
- 钱包操作: 50 VUs
- 绿证操作: 80 VUs
- 交易查询: 30 VUs
- 碳积分: 40 VUs
- 交易市场: 20 VUs

**运行**:
```bash
k6 run scenarios/blockchain-test.js
```

## 安装K6

### Windows (Chocolatey)
```powershell
choco install k6
```

### Windows (手动安装)
```powershell
# 下载
Invoke-WebRequest -Uri "https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-windows-amd64.zip" -OutFile "k6.zip"

# 解压
Expand-Archive -Path "k6.zip" -DestinationPath "C:\k6"

# 添加到PATH
$env:Path += ";C:\k6"
```

### Linux
```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

### macOS
```bash
brew install k6
```

## 配置

### 环境变量
在运行测试前设置以下环境变量：

```bash
# 测试目标URL
export BASE_URL=http://localhost:8000

# 或Windows PowerShell
$env:BASE_URL="http://localhost:8000"
```

### 测试数据
编辑 `config.js` 中的测试数据：
- 测试用户账号
- 测试租户信息
- 测试设备ID

## 运行测试

### 基本运行
```bash
# 冒烟测试
k6 run scenarios/smoke-test.js

# 负载测试
k6 run scenarios/load-test.js

# 压力测试
k6 run scenarios/stress-test.js
```

### 指定环境变量
```bash
k6 run --env BASE_URL=http://localhost:8000 scenarios/load-test.js
```

### 输出结果到文件
```bash
# JSON格式
k6 run --out json=results/load-test.json scenarios/load-test.js

# CSV格式
k6 run --out csv=results/load-test.csv scenarios/load-test.js

# InfluxDB (实时监控)
k6 run --out influxdb=http://localhost:8086/k6 scenarios/load-test.js
```

### 集成Prometheus
```bash
# 启动K6 Prometheus Remote Write
k6 run --out experimental-prometheus-rw=http://localhost:9090/api/v1/write scenarios/load-test.js
```

### 集成Grafana Cloud
```bash
k6 run --out cloud scenarios/load-test.js
```

## CI/CD集成

### GitHub Actions
在 `.github/workflows/performance-test.yml` 中添加：

```yaml
name: Performance Test

on:
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2点
  workflow_dispatch:

jobs:
  performance-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install K6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6
      
      - name: Run Load Test
        env:
          BASE_URL: ${{ secrets.PROD_API_URL }}
        run: |
          k6 run --out json=results.json k6/scenarios/load-test.js
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: k6-results
          path: results.json
```

## 结果分析

### 关键指标

**http_req_duration**: HTTP请求响应时间
- `p(50)`: 中位数 (目标 < 100ms)
- `p(90)`: 90分位 (目标 < 150ms)
- `p(95)`: 95分位 (目标 < 200ms) ⭐
- `p(99)`: 99分位 (目标 < 500ms) ⭐

**http_req_failed**: HTTP请求失败率
- 目标: < 1%

**http_reqs**: 每秒请求数 (RPS)
- 目标: > 10,000 RPS

**checks**: 断言通过率
- 目标: > 99%

**vus**: 虚拟用户数
- 最大: 1,000 VUs

**iteration_duration**: 迭代持续时间
- `p(95)`: < 1s

### 示例输出
```
     ✓ health check status is 200
     ✓ login successful
     ✓ get profile status is 200

     checks.........................: 99.89% ✓ 29967      ✗ 33
     data_received..................: 156 MB 5.2 MB/s
     data_sent......................: 12 MB  400 kB/s
     http_req_blocked...............: avg=1.2ms    min=0s     med=1ms    max=50ms   p(90)=2ms    p(95)=3ms
     http_req_connecting............: avg=800µs    min=0s     med=600µs  max=30ms   p(90)=1.5ms  p(95)=2ms
     http_req_duration..............: avg=125ms    min=10ms   med=98ms   max=2s     p(90)=180ms  p(95)=195ms  ✓
     http_req_failed................: 0.11%  ✓ 33         ✗ 29967
     http_req_receiving.............: avg=2ms      min=0s     med=1.5ms  max=100ms  p(90)=4ms    p(95)=6ms
     http_req_sending...............: avg=500µs    min=0s     med=400µs  max=20ms   p(90)=1ms    p(95)=1.5ms
     http_req_tls_handshaking.......: avg=0s       min=0s     med=0s     max=0s     p(90)=0s     p(95)=0s
     http_req_waiting...............: avg=122ms    min=9ms    med=96ms   max=1.99s  p(90)=178ms  p(95)=192ms
     http_reqs......................: 30000  1000/s
     iteration_duration.............: avg=950ms    min=800ms  med=920ms  max=3s     p(90)=1.1s   p(95)=1.2s
     iterations.....................: 5000   166.67/s
     vus............................: 100    min=10       max=200
     vus_max........................: 200    min=200      max=200
```

### 性能问题诊断

**P95 > 200ms**:
- 检查数据库查询是否优化
- 检查是否存在N+1查询问题
- 增加Redis缓存
- 检查网络延迟

**错误率 > 1%**:
- 检查应用日志
- 检查数据库连接池
- 检查超时配置
- 检查资源限制（CPU/内存）

**RPS < 10000**:
- 增加HPA副本数
- 优化数据库索引
- 增加缓存命中率
- 使用CDN加速静态资源

## 性能优化建议

### 1. 数据库优化
```sql
-- 添加索引
CREATE INDEX idx_charging_records_device_id ON charging_records(device_id);
CREATE INDEX idx_charging_records_start_time ON charging_records(start_time);

-- 查询优化（避免全表扫描）
SELECT * FROM charging_records 
WHERE device_id = @deviceId 
  AND start_time >= @startDate 
ORDER BY start_time DESC 
LIMIT 20;
```

### 2. 缓存策略
```csharp
// 热点数据缓存（Redis）
var cacheKey = $"device:{deviceId}:realtime";
var cachedData = await _cache.GetAsync<DeviceData>(cacheKey);
if (cachedData != null) return cachedData;

var data = await _dbContext.Devices.FindAsync(deviceId);
await _cache.SetAsync(cacheKey, data, TimeSpan.FromSeconds(10));
return data;
```

### 3. 连接池配置
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=postgresql;Database=jgsy_agi;Pooling=true;MinPoolSize=10;MaxPoolSize=100;ConnectionLifeTime=0;"
  }
}
```

### 4. 异步处理
```csharp
// 使用后台队列处理非关键任务
await _backgroundQueue.QueueBackgroundWorkItemAsync(async token =>
{
    await ProcessDeviceDataAsync(deviceData);
});
```

## 持续监控

### Grafana Dashboard
导入K6 Grafana Dashboard：
- Dashboard ID: 2587 (K6 Load Testing Results)
- URL: https://grafana.com/grafana/dashboards/2587

### 告警规则
设置Prometheus告警：
```yaml
groups:
  - name: performance
    rules:
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.2
        for: 5m
        annotations:
          summary: "P95 response time > 200ms"
      
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m
        annotations:
          summary: "Error rate > 1%"
```

## 最佳实践

1. **定期运行**: 每日/每周运行性能测试
2. **基线对比**: 保存历史结果，对比性能变化
3. **渐进式压测**: 从小负载逐步增加，避免系统崩溃
4. **真实场景**: 模拟真实用户行为，不同角色和操作
5. **清理测试数据**: 测试后清理产生的测试数据
6. **监控资源**: 测试期间监控CPU、内存、网络、磁盘

## 故障排查

### 连接超时
```bash
# 增加超时时间
k6 run --http-debug scenarios/load-test.js
```

### 内存不足
```bash
# 减少VU数量或增加ramp-up时间
# 修改config.js中的stages配置
```

### TLS握手失败
```bash
# 禁用TLS验证（仅测试环境）
k6 run --insecure-skip-tls-verify scenarios/load-test.js
```

## 参考资料
- [K6官方文档](https://k6.io/docs/)
- [K6性能测试指南](https://k6.io/docs/testing-guides/)
- [Grafana K6 Cloud](https://k6.io/docs/cloud/)
