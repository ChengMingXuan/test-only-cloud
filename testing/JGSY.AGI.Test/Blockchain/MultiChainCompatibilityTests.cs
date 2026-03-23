using System.Text;
using FluentAssertions;
using JGSY.AGI.Blockchain.MultiChain;
using JGSY.AGI.Blockchain.Web3;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;

namespace JGSY.AGI.Test.Blockchain;

public class CryptoCompatibilityTests
{
    [Fact]
    public void StandardCryptoService_签名验签与地址派生应一致()
    {
        var service = new StandardCryptoService();
        var keyPair = service.GenerateKeyPair();
        var message = Encoding.UTF8.GetBytes("cross-chain-standard-message");

        var signature = service.Sign(keyPair.PrivateKey, message);
        var verified = service.Verify(keyPair.PublicKey, message, signature);
        var address = service.DeriveAddress(keyPair.PublicKey);

        verified.Should().BeTrue();
        signature.Should().HaveCount(65);
        service.Hash(message).Should().HaveCount(32);
        address.Should().StartWith("0x");
        address.Should().HaveLength(42);
    }

    [Fact]
    public void StandardCryptoService_加解密应可逆()
    {
        var service = new StandardCryptoService();
        var key = Enumerable.Range(1, 32).Select(i => (byte)i).ToArray();
        var plaintext = Encoding.UTF8.GetBytes("abi-compatible-standard-payload");

        var ciphertext = service.Encrypt(key, plaintext);
        var decrypted = service.Decrypt(key, ciphertext);

        decrypted.Should().Equal(plaintext);
    }

    [Fact]
    public void SMCryptoService_签名验签与地址派生应一致()
    {
        var service = new SMCryptoService();
        var keyPair = service.GenerateKeyPair();
        var message = Encoding.UTF8.GetBytes("cross-chain-sm-message");

        var signature = service.Sign(keyPair.PrivateKey, message);
        var verified = service.Verify(keyPair.PublicKey, message, signature);
        var address = service.DeriveAddress(keyPair.PublicKey);

        verified.Should().BeTrue();
        signature.Should().HaveCount(64);
        service.Hash(message).Should().HaveCount(32);
        address.Should().StartWith("sm");
        address.Should().HaveLength(42);
    }

    [Fact]
    public void SMCryptoService_加解密应可逆()
    {
        var service = new SMCryptoService();
        var key = Enumerable.Range(1, 16).Select(i => (byte)i).ToArray();
        var plaintext = Encoding.UTF8.GetBytes("abi-compatible-sm-payload");

        var ciphertext = service.Encrypt(key, plaintext);
        var decrypted = service.Decrypt(key, ciphertext);

        decrypted.Should().Equal(plaintext);
    }
}

public class MultiChainFactoryCompatibilityTests
{
    [Fact]
    public void MultiChainClientFactory_应返回三链可用性与客户端映射()
    {
        using var provider = CreateServiceProvider();
        var configuration = CreateConfiguration();
        var factory = new MultiChainClientFactory(
            provider,
            configuration,
            NullLogger<MultiChainClientFactory>.Instance);

        var availability = factory.GetAllChainAvailability();
        var chainMaker = factory.GetClientByType(ChainType.ChainMaker);
        var fisco = factory.GetClientByType(ChainType.FISCO);
        var hyperchain = factory.GetClientByType(ChainType.Hyperchain);

        availability.Should().HaveCount(3);
        availability.Should().Contain(item => item.ChainType == ChainType.ChainMaker && item.Enabled && item.IsDefault);
        availability.Should().Contain(item => item.ChainType == ChainType.FISCO && item.Enabled && !item.IsDefault);
        availability.Should().Contain(item => item.ChainType == ChainType.Hyperchain && item.Enabled && !item.IsDefault);

        chainMaker.ChainType.Should().Be(ChainType.ChainMaker);
        fisco.ChainType.Should().Be(ChainType.FISCO);
        hyperchain.ChainType.Should().Be(ChainType.Hyperchain);
        ChainTypeExtensions.ParseChainType(chainMaker.ChainName).Should().Be(ChainType.ChainMaker);
        ChainTypeExtensions.ParseChainType(fisco.ChainName).Should().Be(ChainType.FISCO);
        ChainTypeExtensions.ParseChainType(hyperchain.ChainName).Should().Be(ChainType.Hyperchain);
    }

    [Fact]
    public void MultiChainClientFactory_应按启用状态返回客户端集合()
    {
        using var provider = CreateServiceProvider();
        var configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["Blockchain:ChainMaker:Enabled"] = "true",
                ["Blockchain:ChainMaker:Nodes:0:NodeAddr"] = "http://127.0.0.1:12301",
                ["Blockchain:FISCO:Enabled"] = "false",
                ["Blockchain:FISCO:Nodes:0:Endpoint"] = "http://127.0.0.1:8545",
                ["Blockchain:Hyperchain:Enabled"] = "false",
                ["Blockchain:Hyperchain:HttpEndpoint"] = "http://127.0.0.1:8081"
            })
            .Build();
        var factory = new MultiChainClientFactory(
            provider,
            configuration,
            NullLogger<MultiChainClientFactory>.Instance);

        var clients = factory.GetAllClients().ToList();

        clients.Should().ContainSingle();
        clients[0].ChainType.Should().Be(ChainType.ChainMaker);
        factory.IsChainEnabled("ChainMaker").Should().BeTrue();
        factory.IsChainEnabled("FISCO").Should().BeFalse();
        factory.IsChainEnabled("Hyperchain").Should().BeFalse();
    }

    private static ServiceProvider CreateServiceProvider()
    {
        var services = new ServiceCollection();
        services.AddLogging();
        services.AddHttpClient();
        return services.BuildServiceProvider();
    }

    private static IConfiguration CreateConfiguration()
    {
        return new ConfigurationBuilder()
            .AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["Blockchain:ChainMaker:Enabled"] = "true",
                ["Blockchain:ChainMaker:Nodes:0:NodeAddr"] = "http://127.0.0.1:12301",
                ["Blockchain:ChainMaker:Nodes:0:Name"] = "cm-primary",
                ["Blockchain:FISCO:Enabled"] = "true",
                ["Blockchain:FISCO:Nodes:0:Endpoint"] = "http://127.0.0.1:8545",
                ["Blockchain:FISCO:Nodes:0:Name"] = "fisco-primary",
                ["Blockchain:Hyperchain:Enabled"] = "true",
                ["Blockchain:Hyperchain:HttpEndpoint"] = "http://127.0.0.1:8081",
                ["Blockchain:Hyperchain:Nodes:0:Endpoint"] = "http://127.0.0.1:8081",
                ["Blockchain:Hyperchain:Nodes:0:Name"] = "hyper-primary"
            })
            .Build();
    }
}

public class AbiCompatibilityTests
{
    [Fact]
    public void DeployRequest_应允许三链共享ABI元数据()
    {
        var request = new DeployRequest
        {
            ContractName = "EnergySettlement",
            Version = "2.1.0",
            Bytecode = Encoding.UTF8.GetBytes("60606040"),
            Abi = "[{\"type\":\"function\",\"name\":\"recordEvidence\",\"inputs\":[{\"name\":\"hash\",\"type\":\"string\"}]}]",
            RuntimeType = "EVM"
        };

        request.Validate().Should().BeEmpty();
        request.Abi.Should().Contain("recordEvidence");
    }

    [Fact]
    public void InvokeAndQueryRequest_应对合约地址与方法名执行统一校验()
    {
        var invoke = new InvokeRequest
        {
            ContractName = "EvidenceContract",
            ContractAddress = "0x1234567890abcdef1234567890abcdef12345678",
            Method = "recordEvidence",
            Parameters = new Dictionary<string, string>
            {
                ["hash"] = "abc123",
                ["category"] = "telemetry"
            }
        };
        var query = new QueryRequest
        {
            ContractName = "EvidenceContract",
            ContractAddress = "0x1234567890abcdef1234567890abcdef12345678",
            Method = "getEvidence",
            Parameters = new Dictionary<string, string>
            {
                ["hash"] = "abc123"
            }
        };

        invoke.Validate().Should().BeEmpty();
        query.Validate().Should().BeEmpty();
    }

    [Fact]
    public void FiscoAbiEncoder_应生成确定性且按32字节对齐的编码结果()
    {
        var method = typeof(FISCOClient).GetMethod("EncodeMethodCall", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static);
        method.Should().NotBeNull();

        var parameters = new Dictionary<string, string>
        {
            ["hash"] = "abc123",
            ["category"] = "telemetry"
        };

        var encoded1 = method!.Invoke(null, new object[] { "recordEvidence", parameters }) as string;
        var encoded2 = method.Invoke(null, new object[] { "recordEvidence", parameters }) as string;

        encoded1.Should().NotBeNullOrEmpty();
        encoded1.Should().Be(encoded2);
        encoded1!.Length.Should().BeGreaterThan(8 + 64 * parameters.Count);
        ((encoded1.Length - 8) % 64).Should().Be(0);
    }
}