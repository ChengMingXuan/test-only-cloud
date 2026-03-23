using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Xunit;

namespace JGSY.AGI.Test.Integration;

/// <summary>
/// 租户注册端到端测试
/// 测试目标: 完整的用户注册流程（前端→Tenant→User→Redis→SMS→Email）
/// 测试层级: L3-端对端测试
/// 注意: 需要完整基础设施运行（PostgreSQL, Redis, Consul, SMS 网关等）
/// 跳过原因: WebApplicationFactory 需要完整的 DI 容器（包含 Consul/Redis/SMS），
///          当前环境缺少 IServiceDiscoveryClient 注册，无法启动 Tenant 服务
/// </summary>
public class TenantRegistrationE2ETests
{
    private const string SkipReason = "L3 端到端测试 - 需要完整基础设施运行（Consul + Redis + SMS 网关）";

    [Fact(Skip = SkipReason)]
    public async Task CompleteRegistrationFlow_ShouldSucceed()
    {
        using var factory = new WebApplicationFactory<Program>();
        var client = factory.CreateClient();

        var phone = $"138{DateTime.Now.Ticks % 100000000:00000000}";
        var companyName = $"测试公司_{DateTime.Now.Ticks}";
        var tenantCode = $"TEST{DateTime.Now.Ticks % 1000000}";

        var sendSmsRequest = new { Mobile = phone, Type = "register" };
        var smsResponse = await client.PostAsJsonAsync("/api/sms/send", sendSmsRequest);
        smsResponse.IsSuccessStatusCode.Should().BeTrue("因为发送验证码是必要步骤");
        var smsResult = await smsResponse.Content.ReadFromJsonAsync<ApiResponse>();
        smsResult.Should().NotBeNull();
        smsResult!.Success.Should().BeTrue();

        var registerRequest = new
        {
            CompanyName = companyName, TenantCode = tenantCode, AdminName = "张三",
            AdminPhone = phone, AdminEmail = $"admin_{DateTime.Now.Ticks}@test.com",
            Password = "Test@123456", SmsCode = "123456", Industry = "互联网", Scale = "50-200人"
        };
        var registerResponse = await client.PostAsJsonAsync("/api/tenant-registration/register", registerRequest);
        registerResponse.IsSuccessStatusCode.Should().BeTrue("因为所有输入数据均有效");
        var registerResult = await registerResponse.Content.ReadFromJsonAsync<TenantRegisterResponse>();
        registerResult.Should().NotBeNull();
        registerResult!.Success.Should().BeTrue();
        registerResult.Data.Should().NotBeNull("因为注册成功应返回数据");
        registerResult.Data!.TenantId.Should().NotBeNullOrEmpty("因为租户创建成功");
    }

    [Fact(Skip = SkipReason)]
    public async Task RegistrationWithInvalidSmsCode_ShouldFail()
    {
        using var factory = new WebApplicationFactory<Program>();
        var client = factory.CreateClient();

        var phone = $"138{DateTime.Now.Ticks % 100000000:00000000}";
        var registerRequest = new
        {
            CompanyName = "测试公司", TenantCode = $"TEST{DateTime.Now.Ticks % 1000000}",
            AdminName = "李四", AdminPhone = phone, AdminEmail = $"admin_{DateTime.Now.Ticks}@test.com",
            Password = "Test@123456", SmsCode = "999999", Industry = "互联网"
        };
        var response = await client.PostAsJsonAsync("/api/tenant-registration/register", registerRequest);
        var result = await response.Content.ReadFromJsonAsync<TenantRegisterResponse>();
        result.Should().NotBeNull();
        result!.Success.Should().BeFalse("因为验证码错误");
        result.Message.Should().Contain("验证码");
    }

    [Theory(Skip = SkipReason)]
    [InlineData("", "TEST001", "138000000", "admin@test.com", "Test@123", "企业名称不能为空")]
    [InlineData("测试", "ab", "13800000000", "admin@test.com", "Test@123", "租户编码长度必须在3-50字符之间")]
    [InlineData("测试公司", "TEST001", "12345", "admin@test.com", "Test@123", "请输入有效的11位手机号")]
    [InlineData("测试公司", "TEST001", "13800000000", "invalid", "Test@123", "邮箱格式不正确")]
    [InlineData("测试公司", "TEST001", "13800000000", "admin@test.com", "weakpass", "密码必须包含大小写字母、数字和特殊字符")]
    public async Task RegistrationWithInvalidInput_ShouldReturnValidationError(
        string companyName, string tenantCode, string phone, string email, string password, string expectedError)
    {
        using var factory = new WebApplicationFactory<Program>();
        var client = factory.CreateClient();

        var registerRequest = new
        {
            CompanyName = companyName, TenantCode = tenantCode, AdminName = "测试用户",
            AdminPhone = phone, AdminEmail = email, Password = password, SmsCode = "123456"
        };
        var response = await client.PostAsJsonAsync("/api/tenant-registration/register", registerRequest);
        response.IsSuccessStatusCode.Should().BeFalse("因为输入数据不符合验证规则");
        var content = await response.Content.ReadAsStringAsync();
        content.Should().Contain(expectedError, "因为应返回对应的验证错误提示");
    }

    [Fact(Skip = SkipReason)]
    public async Task RegistrationWithDuplicateTenantCode_ShouldFail()
    {
        using var factory = new WebApplicationFactory<Program>();
        var client = factory.CreateClient();

        var phone1 = $"138{DateTime.Now.Ticks % 100000000:00000000}";
        var tenantCode = $"TEST{DateTime.Now.Ticks % 1000000}";
        var request1 = new
        {
            CompanyName = "测试公司A", TenantCode = tenantCode, AdminName = "用户A",
            AdminPhone = phone1, AdminEmail = $"usera_{DateTime.Now.Ticks}@test.com",
            Password = "Test@123456", SmsCode = "123456"
        };
        await client.PostAsJsonAsync("/api/tenant-registration/register", request1);
        await Task.Delay(500);

        var phone2 = $"139{DateTime.Now.Ticks % 100000000:00000000}";
        var request2 = new
        {
            CompanyName = "测试公司B", TenantCode = tenantCode, AdminName = "用户B",
            AdminPhone = phone2, AdminEmail = $"userb_{DateTime.Now.Ticks}@test.com",
            Password = "Test@123456", SmsCode = "123456"
        };
        var response = await client.PostAsJsonAsync("/api/tenant-registration/register", request2);
        var result = await response.Content.ReadFromJsonAsync<TenantRegisterResponse>();
        result.Should().NotBeNull();
        result!.Success.Should().BeFalse("因为租户编码已存在");
        result.Message.Should().NotBeNullOrEmpty("因为应返回错误消息");
    }

    [Fact(Skip = SkipReason)]
    public async Task RegistrationWithExpiredSmsCode_ShouldFail()
    {
        // 此测试需要修改Redis过期时间或使用Time Provider模拟
        await Task.CompletedTask;
    }
}

/// <summary>
/// API响应模型（匹配 ApiResponse<T> 标准格式）
/// </summary>
public class ApiResponse
{
    public bool Success { get; set; }
    public string? Code { get; set; }
    public string? Message { get; set; }
    public string? TraceId { get; set; }
}

/// <summary>
/// 租户注册响应模型（匹配 ApiResponse<TenantRegisterData>）
/// </summary>
public class TenantRegisterResponse
{
    public bool Success { get; set; }
    public string? Code { get; set; }
    public string? Message { get; set; }
    public TenantRegisterData? Data { get; set; }
}

/// <summary>
/// 租户注册数据
/// </summary>
public class TenantRegisterData
{
    public string? TenantId { get; set; }
    public string? CompanyName { get; set; }
    public string? AdminPhone { get; set; }
}
