using System;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.Integration;

/// <summary>
/// 能源业务流程集成测试
/// 测试层级: L2-集成测试（业务流程）
/// 测试场景: VPP 调度 + 电力交易 + 结算 + 账户余额
/// 依赖服务: EnergyCore(8022), EnergyServices(8026), Settlement(8014), Account(8008)
/// </summary>
/// <remarks>
/// 测试关键业务流程:
/// 1. VPP 资源创建 → 调度指令下发 → 设备响应 → 事件发布
/// 2. 电力交易订单 → 成交结算 → 账户余额更新
/// 3. 充电订单 → 计费 → 结算 → 账户扣款
/// </remarks>
public class EnergyBusinessFlowTests
{
    private const string GatewayBaseUrl = "http://localhost:5000";
    private const string SkipReason = "需要完整基础设施运行（PostgreSQL + Consul + Redis + RabbitMQ）";

    /// <summary>
    /// 场景1: VPP 虚拟电厂调度完整流程
    /// 创建 VPP 资源 → 注册设备 → 下发调度指令 → 验证响应
    /// </summary>
    [Fact(Skip = SkipReason)]
    public async Task VPP_Dispatch_CompleteFlow_ShouldSucceed()
    {
        using var client = new HttpClient { BaseAddress = new Uri(GatewayBaseUrl) };

        // 1. 管理员登录
        var loginResponse = await client.PostAsJsonAsync("/api/identity/auth/login", new
        {
            Username = "admin",
            Password = "Admin@123",
            TenantCode = "PLATFORM"
        });
        var loginResult = await loginResponse.Content.ReadFromJsonAsync<ApiResult<LoginData>>();
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", loginResult!.Data!.AccessToken);

        // ==================== Step 1: 创建 VPP 虚拟电厂 ====================
        var createVppRequest = new
        {
            VppName = $"测试VPP_{DateTime.Now:yyyyMMddHHmmss}",
            VppCode = $"VPP_{DateTime.Now.Ticks}",
            TotalCapacity = 1000.0, // kW
            AvailableCapacity = 800.0,
            VppType = "Industrial", // 工业型
            Location = "北京市朝阳区",
            Description = "集成测试用 VPP"
        };

        var createVppResponse = await client.PostAsJsonAsync("/api/energycore/vpp/create", createVppRequest);
        createVppResponse.StatusCode.Should().Be(HttpStatusCode.OK, "因为 VPP 创建数据有效");

        var vppResult = await createVppResponse.Content.ReadFromJsonAsync<ApiResult<VppCreateData>>();
        vppResult.Should().NotBeNull();
        vppResult!.Success.Should().BeTrue();
        vppResult.Data!.VppId.Should().NotBeEmpty();

        var vppId = vppResult.Data.VppId;

        // ==================== Step 2: 向 VPP 注册可调度设备 ====================
        var registerDeviceRequest = new
        {
            VppId = vppId,
            DeviceId = Guid.NewGuid().ToString(),
            DeviceType = "EnergyStorage", // 储能设备
            RatedCapacity = 200.0, // kW
            MaxChargeRate = 100.0,
            MaxDischargeRate = 100.0,
            DeviceName = "测试储能柜1号"
        };

        var registerDeviceResponse = await client.PostAsJsonAsync("/api/energycore/vpp/register-device", registerDeviceRequest);
        registerDeviceResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var deviceResult = await registerDeviceResponse.Content.ReadFromJsonAsync<ApiResult<DeviceRegisterData>>();
        deviceResult!.Success.Should().BeTrue();

        // ==================== Step 3: 下发调度指令（放电 100kW） ====================
        var dispatchRequest = new
        {
            VppId = vppId,
            DispatchType = "Discharge", // 放电
            TargetPower = 100.0, // kW
            StartTime = DateTime.Now.AddMinutes(5),
            EndTime = DateTime.Now.AddHours(1),
            Priority = "High",
            Reason = "电网调峰需求"
        };

        var dispatchResponse = await client.PostAsJsonAsync("/api/energycore/vpp/dispatch", dispatchRequest);
        dispatchResponse.StatusCode.Should().Be(HttpStatusCode.OK, "因为调度指令数据有效");

        var dispatchResult = await dispatchResponse.Content.ReadFromJsonAsync<ApiResult<DispatchCommandData>>();
        dispatchResult!.Success.Should().BeTrue();
        dispatchResult.Data!.CommandId.Should().NotBeEmpty();
        dispatchResult.Data.Status.Should().Be("Pending"); // 等待执行

        var commandId = dispatchResult.Data.CommandId;

        // ==================== Step 4: 等待并查询调度指令状态 ====================
        await Task.Delay(2000); // 等待 2 秒模拟设备响应

        var statusResponse = await client.GetAsync($"/api/energycore/vpp/dispatch/{commandId}/status");
        var statusResult = await statusResponse.Content.ReadFromJsonAsync<ApiResult<DispatchStatusData>>();

        statusResult!.Success.Should().BeTrue();
        statusResult.Data!.Status.Should().BeOneOf("Executing", "Completed", "Pending", "因为调度指令已下发");

        // ==================== Step 5: 查询 VPP 实时状态 ====================
        var vppStatusResponse = await client.GetAsync($"/api/energycore/vpp/{vppId}/status");
        var vppStatusResult = await vppStatusResponse.Content.ReadFromJsonAsync<ApiResult<VppStatusData>>();

        vppStatusResult!.Success.Should().BeTrue();
        vppStatusResult.Data!.VppId.Should().Be(vppId);
        vppStatusResult.Data.DeviceCount.Should().BeGreaterOrEqualTo(1, "因为注册了至少 1 台设备");
    }

    /// <summary>
    /// 场景2: 电力交易订单完整流程
    /// 创建买入订单 → 匹配成交 → 生成结算单 → 账户余额更新
    /// </summary>
    [Fact(Skip = SkipReason)]
    public async Task ElecTrade_Order_Settlement_AccountUpdate_ShouldSucceed()
    {
        using var client = new HttpClient { BaseAddress = new Uri(GatewayBaseUrl) };

        // 1. 登录
        var loginResponse = await client.PostAsJsonAsync("/api/identity/auth/login", new
        {
            Username = "trader",
            Password = "Trader@123",
            TenantCode = "TRADER_001"
        });
        var loginResult = await loginResponse.Content.ReadFromJsonAsync<ApiResult<LoginData>>();
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", loginResult!.Data!.AccessToken);

        // ==================== Step 1: 查询账户余额（交易前） ====================
        var accountBeforeResponse = await client.GetAsync("/api/account/account/my-account");
        var accountBefore = await accountBeforeResponse.Content.ReadFromJsonAsync<ApiResult<AccountData>>();
        accountBefore!.Success.Should().BeTrue();
        var balanceBefore = accountBefore.Data!.Balance;

        // ==================== Step 2: 创建买入订单（购买 1000kWh 电力） ====================
        var createOrderRequest = new
        {
            OrderType = "Buy", // 买入
            Quantity = 1000.0, // kWh
            Price = 0.85, // 元/kWh
            TradeDate = DateTime.Now.AddDays(1).Date, // 明日交易
            OrderPriority = "Market", // 市价单
            ValidUntil = DateTime.Now.AddHours(24)
        };

        var createOrderResponse = await client.PostAsJsonAsync("/api/energyservices/trade/order/create", createOrderRequest);
        createOrderResponse.StatusCode.Should().Be(HttpStatusCode.OK, "因为订单数据有效");

        var orderResult = await createOrderResponse.Content.ReadFromJsonAsync<ApiResult<OrderCreateData>>();
        orderResult!.Success.Should().BeTrue();
        orderResult.Data!.OrderId.Should().NotBeEmpty();

        var orderId = orderResult.Data.OrderId;

        // ==================== Step 3: 等待订单匹配（模拟市场撮合） ====================
        await Task.Delay(3000); // 等待 3 秒模拟撮合过程

        var orderStatusResponse = await client.GetAsync($"/api/energyservices/trade/order/{orderId}");
        var orderStatus = await orderStatusResponse.Content.ReadFromJsonAsync<ApiResult<OrderData>>();

        orderStatus!.Success.Should().BeTrue();
        // 订单状态可能是: Pending（等待）、PartiallyFilled（部分成交）、Filled（完全成交）
        orderStatus.Data!.Status.Should().BeOneOf("Pending", "PartiallyFilled", "Filled");

        // 如果订单已成交，检查交易金额
        if (orderStatus.Data.Status == "Filled")
        {
            orderStatus.Data.FilledQuantity.Should().Be(1000.0);
            orderStatus.Data.TotalAmount.Should().BeGreaterThan(0, "因为应该计算了交易金额");

            // ==================== Step 4: 查询结算单 ====================
            var settlementResponse = await client.GetAsync($"/api/settlement/settlement/by-trade-order/{orderId}");
            var settlement = await settlementResponse.Content.ReadFromJsonAsync<ApiResult<SettlementData>>();

            settlement!.Success.Should().BeTrue();
            settlement.Data!.OrderId.Should().Be(orderId);
            settlement.Data.SettlementAmount.Should().Be(orderStatus.Data.TotalAmount);
            settlement.Data.Status.Should().BeOneOf("Pending", "Completed");

            // ==================== Step 5: 验证账户余额（交易后） ====================
            var accountAfterResponse = await client.GetAsync("/api/account/account/my-account");
            var accountAfter = await accountAfterResponse.Content.ReadFromJsonAsync<ApiResult<AccountData>>();

            accountAfter!.Success.Should().BeTrue();
            var balanceAfter = accountAfter.Data!.Balance;

            // 余额应该减少（买入电力需要支付）
            balanceAfter.Should().BeLessThan(balanceBefore, "因为购买电力需要扣款");
        }
    }

    /// <summary>
    /// 场景3: 充电订单 → 计费 → 结算 → 账户扣款流程
    /// </summary>
    [Fact(Skip = SkipReason)]
    public async Task Charging_Order_Billing_Settlement_AccountDeduction_ShouldSucceed()
    {
        using var client = new HttpClient { BaseAddress = new Uri(GatewayBaseUrl) };

        // 1. 普通用户登录
        var loginResponse = await client.PostAsJsonAsync("/api/identity/auth/login", new
        {
            Username = "user01",
            Password = "User@123",
            TenantCode = "USER_TENANT"
        });
        var loginResult = await loginResponse.Content.ReadFromJsonAsync<ApiResult<LoginData>>();
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", loginResult!.Data!.AccessToken);

        // ==================== Step 1: 查询用户账户余额（充电前） ====================
        var accountBeforeResponse = await client.GetAsync("/api/account/account/my-account");
        var accountBefore = await accountBeforeResponse.Content.ReadFromJsonAsync<ApiResult<AccountData>>();
        var balanceBefore = accountBefore!.Data!.Balance;

        // ==================== Step 2: 扫码启动充电（模拟） ====================
        var startChargingRequest = new
        {
            StationId = "STATION_001",
            PileId = "PILE_001",
            ConnectorId = "CONNECTOR_01",
            VehiclePlateNumber = "京A12345",
            MaxChargingAmount = 50.0 // 最多充 50 元
        };

        var startChargingResponse = await client.PostAsJsonAsync("/api/charging/charging-session/start", startChargingRequest);
        startChargingResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var sessionResult = await startChargingResponse.Content.ReadFromJsonAsync<ApiResult<ChargingSessionData>>();
        sessionResult!.Success.Should().BeTrue();
        sessionResult.Data!.SessionId.Should().NotBeEmpty();
        sessionResult.Data.Status.Should().Be("Charging");

        var sessionId = sessionResult.Data.SessionId;

        // ==================== Step 3: 模拟充电过程（等待 5 秒） ====================
        await Task.Delay(5000);

        // ==================== Step 4: 停止充电 ====================
        var stopChargingResponse = await client.PostAsync($"/api/charging/charging-session/{sessionId}/stop", null);
        stopChargingResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var stopResult = await stopChargingResponse.Content.ReadFromJsonAsync<ApiResult<ChargingStopData>>();
        stopResult!.Success.Should().BeTrue();
        stopResult.Data!.TotalEnergy.Should().BeGreaterThan(0, "因为充电了一段时间");
        stopResult.Data.TotalAmount.Should().BeGreaterThan(0, "因为应该计算了费用");

        var totalAmount = stopResult.Data.TotalAmount;

        // ==================== Step 5: 查询充电账单 ====================
        var billResponse = await client.GetAsync($"/api/charging/charging-bill/by-session/{sessionId}");
        var bill = await billResponse.Content.ReadFromJsonAsync<ApiResult<ChargingBillData>>();

        bill!.Success.Should().BeTrue();
        bill.Data!.TotalAmount.Should().Be(totalAmount);
        bill.Data.Status.Should().BeOneOf("Pending", "Paid");

        // ==================== Step 6: 验证账户余额（充电后） ====================
        var accountAfterResponse = await client.GetAsync("/api/account/account/my-account");
        var accountAfter = await accountAfterResponse.Content.ReadFromJsonAsync<ApiResult<AccountData>>();

        var balanceAfter = accountAfter!.Data!.Balance;

        // 余额应该减少（充电需要扣款）
        (balanceBefore - balanceAfter).Should().BeApproximately(totalAmount, 0.01, "因为账户应该扣除充电费用");
    }

    #region Response DTOs

    private record ApiResult<T>(bool Success, int Code, string Message, T? Data);
    private record LoginData(string AccessToken, string RefreshToken);
    private record VppCreateData(string VppId, string VppCode);
    private record DeviceRegisterData(string DeviceId, string VppId);
    private record DispatchCommandData(string CommandId, string Status);
    private record DispatchStatusData(string CommandId, string Status, double? ActualPower);
    private record VppStatusData(string VppId, int DeviceCount, double TotalCapacity, double AvailableCapacity);
    private record OrderCreateData(string OrderId, string OrderNo);
    private record OrderData(string OrderId, string Status, double Quantity, double FilledQuantity, double TotalAmount);
    private record SettlementData(string SettlementId, string OrderId, double SettlementAmount, string Status);
    private record AccountData(string AccountId, double Balance, string Currency);
    private record ChargingSessionData(string SessionId, string Status, DateTime StartTime);
    private record ChargingStopData(string SessionId, double TotalEnergy, double TotalAmount, DateTime EndTime);
    private record ChargingBillData(string BillId, string SessionId, double TotalAmount, string Status);

    #endregion
}
