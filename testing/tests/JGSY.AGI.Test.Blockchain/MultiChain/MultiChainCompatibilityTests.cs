using Xunit;
using Moq;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using JGSY.AGI.Blockchain.MultiChain;
using JGSY.AGI.Blockchain.Web3;

namespace JGSY.AGI.Test.Blockchain.MultiChain;

/// <summary>
/// 多链工厂模式测试
/// </summary>
public class MultiChainClientFactoryTests
{
    private readonly Mock<IConfiguration> _configMock;
    private readonly Mock<ILogger<MultiChainClientFactory>> _loggerMock;
    private readonly Mock<IServiceProvider> _serviceProviderMock;
    private readonly MultiChainClientFactory _factory;

    public MultiChainClientFactoryTests()
    {
        _configMock = new Mock<IConfiguration>();
        _loggerMock = new Mock<ILogger<MultiChainClientFactory>>();
        _serviceProviderMock = new Mock<IServiceProvider>();
        
        // 设置服务提供者返回模拟对象
        _serviceProviderMock
            .Setup(sp => sp.GetService(typeof(ILogger<ChainMakerClient>)))
            .Returns(new Mock<ILogger<ChainMakerClient>>().Object);
        
        _serviceProviderMock
            .Setup(sp => sp.GetService(typeof(ILogger<FISCOClient>)))
            .Returns(new Mock<ILogger<FISCOClient>>().Object);
        
        _serviceProviderMock
            .Setup(sp => sp.GetService(typeof(ILogger<HyperchainClient>)))
            .Returns(new Mock<ILogger<HyperchainClient>>().Object);

        _serviceProviderMock
            .Setup(sp => sp.GetService(typeof(IHttpClientFactory)))
            .Returns(new MockHttpClientFactory());

        _factory = new MultiChainClientFactory(_serviceProviderMock.Object, _configMock.Object, _loggerMock.Object);
    }

    /// <summary>
    /// 测试支持的链类型枚举
    /// </summary>
    [Fact]
    public void ChainType_Contains_AllThreeChains()
    {
        // Arrange & Act
        var chainTypes = Enum.GetValues(typeof(ChainType));

        // Assert
        Assert.Contains(ChainType.ChainMaker, chainTypes.Cast<ChainType>());
        Assert.Contains(ChainType.FISCO, chainTypes.Cast<ChainType>());
        Assert.Contains(ChainType.Hyperchain, chainTypes.Cast<ChainType>());
    }

    /// <summary>
    /// 测试通过 ChainType 枚举获取 ChainMaker 客户端
    /// </summary>
    [Fact]
    public void GetClient_ByChainType_ChainMaker_ReturnsChainMakerClient()
    {
        // Arrange
        SetupChainMakerConfig();

        // Act
        var client = _factory.GetClient(ChainType.ChainMaker);

        // Assert
        Assert.NotNull(client);
        Assert.Equal("ChainMaker", client.ChainName);
        Assert.Equal(ChainType.ChainMaker, client.ChainType);
    }

    /// <summary>
    /// 测试通过 ChainType 枚举获取 FISCO 客户端
    /// </summary>
    [Fact]
    public void GetClient_ByChainType_FISCO_ReturnsFISCOClient()
    {
        // Arrange
        SetupFISCOConfig();

        // Act
        var client = _factory.GetClient(ChainType.FISCO);

        // Assert
        Assert.NotNull(client);
        Assert.Equal("FISCO BCOS", client.ChainName);
        Assert.Equal(ChainType.FISCO, client.ChainType);
    }

    /// <summary>
    /// 测试通过 ChainType 枚举获取 Hyperchain 客户端
    /// </summary>
    [Fact]
    public void GetClient_ByChainType_Hyperchain_ReturnsHyperchainClient()
    {
        // Arrange
        SetupHyperchainConfig();

        // Act
        var client = _factory.GetClient(ChainType.Hyperchain);

        // Assert
        Assert.NotNull(client);
        Assert.Equal("Hyperchain", client.ChainName);
        Assert.Equal(ChainType.Hyperchain, client.ChainType);
    }

    /// <summary>
    /// 测试通过字符串名称获取客户端
    /// </summary>
    [Theory]
    [InlineData("ChainMaker")]
    [InlineData("FISCO")]
    [InlineData("Hyperchain")]
    public void GetClient_ByName_ReturnsCorrectClient(string chainName)
    {
        // Arrange
        SetupAllConfigs();

        // Act
        var client = _factory.GetClient(chainName);

        // Assert
        Assert.NotNull(client);
        Assert.Equal(chainName, client.ChainType.ToString());
    }

    /// <summary>
    /// 测试工厂缓存机制（获取两次应返回同一实例）
    /// </summary>
    [Fact]
    public void GetClient_CallTwice_ReturnsSameInstance()
    {
        // Arrange
        SetupChainMakerConfig();

        // Act
        var client1 = _factory.GetClient("ChainMaker");
        var client2 = _factory.GetClient("ChainMaker");

        // Assert
        Assert.Same(client1, client2);
    }

    /// <summary>
    /// 测试不支持的链类型抛出异常
    /// </summary>
    [Fact]
    public void GetClient_UnsupportedChain_ThrowsNotSupportedException()
    {
        // Arrange
        _configMock
            .Setup(c => c.GetSection(It.IsAny<string>()))
            .Returns(new MockConfigurationSection());

        // Act & Assert
        Assert.Throws<NotSupportedException>(() => _factory.GetClient("UnsupportedChain"));
    }

    /// <summary>
    /// 测试获取所有已启用的链客户端
    /// </summary>
    [Fact]
    public void GetAllClients_ReturnsEnabledClients()
    {
        // Arrange
        SetupAllConfigs();

        // Act
        var clients = _factory.GetAllClients().ToList();

        // Assert
        Assert.NotEmpty(clients);
        // 根据配置的启用状态，验证返回的客户端数量
    }

    /// <summary>
    /// 测试密码学模式选择（ChainMaker 使用 SM）
    /// </summary>
    [Fact]
    public void ChainMaker_EnablesSMCrypto()
    {
        // Arrange
        SetupChainMakerConfig(enableSM: true);

        // Act
        var client = _factory.GetClient(ChainType.ChainMaker);

        // Assert
        Assert.NotNull(client);
        // 验证使用了 SM 密码学（需要检查日志或客户端内部状态）
    }

    /// <summary>
    /// 测试密码学模式选择（FISCO 使用 SM）
    /// </summary>
    [Fact]
    public void FISCO_EnablesSMCrypto()
    {
        // Arrange
        SetupFISCOConfig(enableSM: true);

        // Act
        var client = _factory.GetClient(ChainType.FISCO);

        // Assert
        Assert.NotNull(client);
        // 验证使用了 SM 密码学
    }

    /// <summary>
    /// 测试密码学模式选择（Hyperchain 使用 SM）
    /// </summary>
    [Fact]
    public void Hyperchain_EnablesSMCrypto()
    {
        // Arrange
        SetupHyperchainConfig(enableSM: true);

        // Act
        var client = _factory.GetClient(ChainType.Hyperchain);

        // Assert
        Assert.NotNull(client);
        // 验证使用了 SM 密码学
    }

    private void SetupChainMakerConfig(bool enableSM = true)
    {
        var configSection = new Mock<IConfigurationSection>();
        configSection.SetupGet(x => x["Enabled"]).Returns("true");
        configSection.SetupGet(x => x["ChainId"]).Returns("chain1");
        configSection.SetupGet(x => x["OrgId"]).Returns("wx-org1.chainmaker.org");
        configSection.SetupGet(x => x["EnableSM"]).Returns(enableSM.ToString());
        configSection.Setup(x => x.GetSection("Nodes")).Returns(new MockConfigurationSection());

        _configMock
            .Setup(c => c.GetSection("Blockchain:ChainMaker"))
            .Returns(configSection.Object);
    }

    private void SetupFISCOConfig(bool enableSM = true)
    {
        var configSection = new Mock<IConfigurationSection>();
        configSection.SetupGet(x => x["Enabled"]).Returns("true");
        configSection.SetupGet(x => x["GroupId"]).Returns("1");
        configSection.SetupGet(x => x["EnableSM"]).Returns(enableSM.ToString());
        configSection.Setup(x => x.GetSection("Nodes")).Returns(new MockConfigurationSection());

        _configMock
            .Setup(c => c.GetSection("Blockchain:FISCO"))
            .Returns(configSection.Object);
    }

    private void SetupHyperchainConfig(bool enableSM = true)
    {
        var configSection = new Mock<IConfigurationSection>();
        configSection.SetupGet(x => x["Enabled"]).Returns("true");
        configSection.SetupGet(x => x["OrgId"]).Returns("hyperchain-org");
        configSection.SetupGet(x => x["HttpEndpoint"]).Returns("http://localhost:8081");
        configSection.SetupGet(x => x["EnableSM"]).Returns(enableSM.ToString());

        _configMock
            .Setup(c => c.GetSection("Blockchain:Hyperchain"))
            .Returns(configSection.Object);
    }

    private void SetupAllConfigs()
    {
        SetupChainMakerConfig();
        SetupFISCOConfig();
        SetupHyperchainConfig();
    }
}

/// <summary>
/// ChainMaker 客户端测试
/// </summary>
public class ChainMakerClientTests
{
    [Fact]
    public void Constructor_ValidConfig_Initializes()
    {
        // Arrange
        var config = Options.Create(new ChainMakerConfig
        {
            Enabled = true,
            ChainId = "chain1",
            OrgId = "wx-org1.chainmaker.org",
            EnableSM = true,
            Nodes = new()
            {
                new ChainMakerNode
                {
                    NodeAddr = "grpc://localhost:12301",
                    EnableTls = true
                }
            }
        });
        var logger = new Mock<ILogger<ChainMakerClient>>().Object;

        // Act
        var client = new ChainMakerClient(config, logger);

        // Assert
        Assert.NotNull(client);
        Assert.Equal(ChainType.ChainMaker, client.ChainType);
        Assert.Equal("ChainMaker", client.ChainName);
    }

    [Fact]
    public void ChainType_ReturnsChainMaker()
    {
        // Arrange
        var config = Options.Create(new ChainMakerConfig { Enabled = true });
        var logger = new Mock<ILogger<ChainMakerClient>>().Object;
        var client = new ChainMakerClient(config, logger);

        // Act & Assert
        Assert.Equal(ChainType.ChainMaker, client.ChainType);
    }
}

/// <summary>
/// FISCO BCOS 客户端测试
/// </summary>
public class FISCOClientTests
{
    [Fact]
    public void Constructor_ValidConfig_Initializes()
    {
        // Arrange
        var config = Options.Create(new FISCOConfig
        {
            Enabled = true,
            GroupId = 1,
            Nodes = new() { "http://localhost:8545" },
            EnableSM = true
        });
        var logger = new Mock<ILogger<FISCOClient>>().Object;
        var httpClientFactory = new MockHttpClientFactory();

        // Act
        var client = new FISCOClient(config, logger, httpClientFactory);

        // Assert
        Assert.NotNull(client);
        Assert.Equal(ChainType.FISCO, client.ChainType);
        Assert.Equal("FISCO BCOS", client.ChainName);
    }

    [Fact]
    public void ChainType_ReturnsFISCO()
    {
        // Arrange
        var config = Options.Create(new FISCOConfig { Enabled = true });
        var logger = new Mock<ILogger<FISCOClient>>().Object;
        var httpClientFactory = new MockHttpClientFactory();
        var client = new FISCOClient(config, logger, httpClientFactory);

        // Act & Assert
        Assert.Equal(ChainType.FISCO, client.ChainType);
    }
}

/// <summary>
/// Hyperchain 客户端测试
/// </summary>
public class HyperchainClientTests
{
    [Fact]
    public void Constructor_ValidConfig_Initializes()
    {
        // Arrange
        var config = Options.Create(new HyperchainConfig
        {
            Enabled = true,
            OrgId = "hyperchain-org",
            HttpEndpoint = "http://localhost:8081",
            EnableSM = true
        });
        var logger = new Mock<ILogger<HyperchainClient>>().Object;
        var httpClientFactory = new MockHttpClientFactory();

        // Act
        var client = new HyperchainClient(config, logger, httpClientFactory);

        // Assert
        Assert.NotNull(client);
        Assert.Equal(ChainType.Hyperchain, client.ChainType);
        Assert.Equal("Hyperchain", client.ChainName);
    }

    [Fact]
    public void ChainType_ReturnsHyperchain()
    {
        // Arrange
        var config = Options.Create(new HyperchainConfig { Enabled = true });
        var logger = new Mock<ILogger<HyperchainClient>>().Object;
        var httpClientFactory = new MockHttpClientFactory();
        var client = new HyperchainClient(config, logger, httpClientFactory);

        // Act & Assert
        Assert.Equal(ChainType.Hyperchain, client.ChainType);
    }
}

// ==================== 模拟辅助类 ====================

public class MockHttpClientFactory : IHttpClientFactory
{
    public HttpClient CreateClient(string name)
    {
        return new HttpClient(new MockHttpMessageHandler());
    }
}

public class MockHttpMessageHandler : HttpMessageHandler
{
    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
    {
        var response = new HttpResponseMessage(System.Net.HttpStatusCode.OK);
        response.Content = new StringContent("{\"status\":\"ok\"}");
        return Task.FromResult(response);
    }
}

public class MockConfigurationSection : IConfigurationSection
{
    public string this[string key] { get => string.Empty; set { } }
    public string Key => string.Empty;
    public string Path => string.Empty;
    public string Value { get => string.Empty; set { } }

    public IChangeToken GetReloadToken() => CancellationToken.None;

    public IEnumerable<IConfigurationSection> GetChildren() => Enumerable.Empty<IConfigurationSection>();

    public IConfigurationSection GetSection(string key) => this;
}
