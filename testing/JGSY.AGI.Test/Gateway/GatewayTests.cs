using FluentAssertions;
using global::JGSY.AGI.Gateway.Consul;
using global::JGSY.AGI.Gateway.ServiceDiscovery;
using Xunit;

namespace JGSY.AGI.Test.Gateway;

/// <summary>
/// 网关服务发现配置测试
/// </summary>
public class GatewayServiceDiscoveryTests
{
    [Fact]
    public void YarpServiceDiscoveryOptions_ShouldDefaultToConsul()
    {
        var options = new YarpServiceDiscoveryOptions
        {
            Mode = "consul"
        };

        options.GetMode().Should().Be(ServiceDiscoveryMode.Consul);
    }

    [Fact]
    public void YarpServiceDiscoveryOptions_ShouldSupportK8s()
    {
        var options = new YarpServiceDiscoveryOptions
        {
            Mode = "kubernetes",
            RefreshIntervalSeconds = 30
        };

        options.GetMode().Should().Be(ServiceDiscoveryMode.Kubernetes);
        options.RefreshIntervalSeconds.Should().Be(30);
    }

    [Theory]
    [InlineData(ServiceDiscoveryMode.Consul)]
    [InlineData(ServiceDiscoveryMode.Kubernetes)]
    public void ServiceDiscoveryMode_ShouldHaveDefinedValues(ServiceDiscoveryMode mode)
    {
        Enum.IsDefined(typeof(ServiceDiscoveryMode), mode).Should().BeTrue();
    }
}

/// <summary>
/// Consul 配置测试
/// </summary>
public class ConsulOptionsTests
{
    [Fact]
    public void ConsulOptions_ShouldBuildAddress()
    {
        var options = new global::JGSY.AGI.Gateway.ServiceDiscovery.ConsulOptions
        {
            Host = "jgsy-consul",
            Port = 8500,
            PassingOnly = true
        };

        var address = options.GetAddress();
        address.Should().NotBeNull();
        address.Host.Should().Be("jgsy-consul");
        address.Port.Should().Be(8500);
    }

    [Fact]
    public void ConsulOptions_ServiceConfig_ShouldSetAllFields()
    {
        var options = new global::JGSY.AGI.Gateway.Consul.ConsulOptions
        {
            Host = "jgsy-consul",
            Port = 8500,
            ServiceName = "jgsy-gateway",
            ServiceId = "jgsy-gateway-01",
            ServicePort = 5000,
            HealthCheckPath = "/health",
            HealthCheckIntervalSeconds = 10,
            HealthCheckTimeoutSeconds = 5,
            DeregisterCriticalServiceAfterSeconds = 90,
            Tags = new[] { "gateway", "yarp" }
        };

        options.ServiceName.Should().Be("jgsy-gateway");
        options.HealthCheckPath.Should().Be("/health");
        options.Tags.Should().Contain("gateway");
        options.DeregisterCriticalServiceAfterSeconds.Should().BePositive();
    }
}

/// <summary>
/// Kubernetes 配置测试
/// </summary>
public class KubernetesOptionsTests
{
    [Fact]
    public void KubernetesOptions_ShouldGenerateServiceAddress()
    {
        var options = new KubernetesOptions
        {
            Namespace = "jgsy-prod",
            ServiceSuffix = ".svc.cluster.local",
            InCluster = true,
            DefaultPort = 8080
        };

        var address = options.GetServiceAddress("jgsy-station");
        address.Should().Contain("jgsy-station");
        address.Should().Contain("jgsy-prod");
    }

    [Fact]
    public void KubernetesOptions_OutOfCluster_ShouldUseKubeConfig()
    {
        var options = new KubernetesOptions
        {
            Namespace = "default",
            InCluster = false,
            KubeConfigPath = "~/.kube/config"
        };

        options.InCluster.Should().BeFalse();
        options.KubeConfigPath.Should().NotBeEmpty();
    }
}

/// <summary>
/// 服务映射配置测试
/// </summary>
public class ServiceMappingTests
{
    [Fact]
    public void ServiceMapping_ShouldDefineConsulAndK8sNames()
    {
        var mapping = new ServiceMapping
        {
            ClusterId = "station-cluster",
            ConsulServiceName = "jgsy-station",
            K8sServiceName = "jgsy-station",
            HealthCheckPath = "/health"
        };

        mapping.ClusterId.Should().NotBeEmpty();
        mapping.HealthCheckPath.Should().StartWith("/");
    }

    [Theory]
    [InlineData("jgsy-gateway", "/health")]
    [InlineData("jgsy-tenant", "/health")]
    [InlineData("jgsy-identity", "/health")]
    [InlineData("jgsy-station", "/health")]
    public void ServiceMapping_AllServices_ShouldHaveHealthCheck(string service, string healthPath)
    {
        var mapping = new ServiceMapping
        {
            ConsulServiceName = service,
            HealthCheckPath = healthPath
        };

        mapping.HealthCheckPath.Should().Be("/health");
    }
}
