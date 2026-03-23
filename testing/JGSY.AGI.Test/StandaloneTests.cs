using Xunit;
using FluentAssertions;

namespace JGSY.AGI.Test;

/// <summary>
/// 独立模式测试 — 在无业务源码环境下验证测试框架基础能力
/// 
/// 双模兼容：
///   真实模式（有源码）— 此文件与所有业务测试一起编译运行
///   Mock 模式（CI/独立仓库）— 仅此文件参与编译，验证 xUnit + Moq + FluentAssertions 工作正常
/// </summary>
public class StandaloneTests
{
    [Fact]
    public void TestFramework_ShouldBeOperational()
    {
        // 验证 xUnit 框架正常
        Assert.True(true, "xUnit 框架运行正常");
    }

    [Fact]
    public void FluentAssertions_ShouldWork()
    {
        // 验证 FluentAssertions 可用
        "JGSY.AGI".Should().StartWith("JGSY");
        42.Should().BeGreaterThan(0);
    }

    [Fact]
    public void Moq_ShouldWork()
    {
        // 验证 Moq 可用
        var mock = new Moq.Mock<IDisposable>();
        mock.Setup(x => x.Dispose());
        mock.Object.Dispose();
        mock.Verify(x => x.Dispose(), Moq.Times.Once);
    }

    [Theory]
    [InlineData("Account", 8010)]
    [InlineData("Identity", 8020)]
    [InlineData("Permission", 8030)]
    [InlineData("Device", 8050)]
    [InlineData("Station", 8060)]
    [InlineData("Charging", 8070)]
    [InlineData("RuleEngine", 8100)]
    [InlineData("Analytics", 8110)]
    [InlineData("Blockchain", 8120)]
    public void ServicePort_ShouldBeInExpectedRange(string service, int port)
    {
        // 验证服务端口在合理范围内
        port.Should().BeInRange(8000, 9000, $"{service} 端口应在 8000-9000 范围内");
    }

    [Fact]
    public void NpgsqlConnection_TypeShouldBeAvailable()
    {
        // 验证 Npgsql 类型可用（不实际连接）
        var connType = typeof(Npgsql.NpgsqlConnection);
        connType.Should().NotBeNull();
    }

#if STANDALONE_MODE
    [Fact]
    public void StandaloneMode_ShouldBeDetected()
    {
        // 验证独立模式编译常量
        Assert.True(true, "当前运行在独立模式（无业务源码）");
    }
#endif
}
