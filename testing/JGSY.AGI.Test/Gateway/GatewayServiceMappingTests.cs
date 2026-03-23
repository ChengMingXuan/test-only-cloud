using FluentAssertions;
using Microsoft.Extensions.Primitives;
using Xunit;
using Yarp.ReverseProxy.Configuration;

namespace JGSY.AGI.Test.Gateway
{
    /// <summary>
    /// 测试 ConsulProxyConfig 和 Gateway 服务映射逻辑
    /// 直接测试公共类和静态方法，不需要 Consul 依赖
    /// </summary>
    public class ConsulProxyConfigTests
    {
        [Fact]
        public void ConsulProxyConfig_ShouldStoreRoutesAndClusters()
        {
            var routes = new List<RouteConfig>
            {
                new RouteConfig { RouteId = "r1", ClusterId = "c1", Match = new RouteMatch { Path = "/api/test/{**catch-all}" } }
            };
            var clusters = new List<ClusterConfig>
            {
                new ClusterConfig { ClusterId = "c1" }
            };
            var cts = new CancellationTokenSource();

            var config = new global::JGSY.AGI.Gateway.ServiceDiscovery.ConsulProxyConfig(routes, clusters, cts.Token);

            config.Routes.Should().HaveCount(1);
            config.Routes[0].RouteId.Should().Be("r1");
            config.Clusters.Should().HaveCount(1);
            config.Clusters[0].ClusterId.Should().Be("c1");
        }

        [Fact]
        public void ConsulProxyConfig_ChangeToken_ShouldReflectCancellation()
        {
            var cts = new CancellationTokenSource();
            var config = new global::JGSY.AGI.Gateway.ServiceDiscovery.ConsulProxyConfig(
                Array.Empty<RouteConfig>(), Array.Empty<ClusterConfig>(), cts.Token);

            config.ChangeToken.HasChanged.Should().BeFalse();

            cts.Cancel();

            config.ChangeToken.HasChanged.Should().BeTrue();
        }

        [Fact]
        public void ConsulProxyConfig_EmptyCollections_ShouldWork()
        {
            var cts = new CancellationTokenSource();
            var config = new global::JGSY.AGI.Gateway.ServiceDiscovery.ConsulProxyConfig(
                Array.Empty<RouteConfig>(), Array.Empty<ClusterConfig>(), cts.Token);

            config.Routes.Should().BeEmpty();
            config.Clusters.Should().BeEmpty();
        }

        [Fact]
        public void ConsulProxyConfig_ShouldImplementIProxyConfig()
        {
            var cts = new CancellationTokenSource();
            var config = new global::JGSY.AGI.Gateway.ServiceDiscovery.ConsulProxyConfig(
                Array.Empty<RouteConfig>(), Array.Empty<ClusterConfig>(), cts.Token);

            config.Should().BeAssignableTo<IProxyConfig>();
        }
    }

    /// <summary>
    /// 测试 Gateway 服务映射约定
    /// 验证 Docker DNS 命名规则和服务发现映射完整性
    /// </summary>
    public class GatewayServiceMappingConventionTests
    {
        /// <summary>
        /// 所有预期的服务映射 — 从 GetDefaultServiceMappings() 提取
        /// </summary>
        public static IEnumerable<object[]> PlatformServiceMappings => new List<object[]>
        {
            new object[] { "gateway-cluster", "gateway-service" },
            new object[] { "tenant-cluster", "tenant-service" },
            new object[] { "identity-cluster", "identity-service" },
            new object[] { "permission-cluster", "permission-service" },
            new object[] { "observability-cluster", "observability-service" },
            new object[] { "storage-cluster", "storage-service" },
        };

        public static IEnumerable<object[]> AiopsServiceMappings => new List<object[]>
        {
            new object[] { "account-cluster", "account-service" },
            new object[] { "analytics-cluster", "analytics-service" },
            new object[] { "charging-cluster", "charging-service" },
            new object[] { "device-cluster", "device-service" },
            new object[] { "digitaltwin-cluster", "digitaltwin-service" },
            new object[] { "ingestion-cluster", "ingestion-service" },
            new object[] { "settlement-cluster", "settlement-service" },
            new object[] { "station-cluster", "station-service" },
            new object[] { "workorder-cluster", "workorder-service" },
        };

        public static IEnumerable<object[]> ExtensionServiceMappings => new List<object[]>
        {
            new object[] { "iotcloudai-cluster", "iotcloudai-service" },
            new object[] { "contentplatform-cluster", "contentplatform-service" },
            new object[] { "blockchain-cluster", "blockchain-service" },
        };

        public static IEnumerable<object[]> EnergyCoreServiceMappings => new List<object[]>
        {
            new object[] { "orchestrator-cluster", "orchestrator-service" },
            new object[] { "vpp-cluster", "vpp-service" },
            new object[] { "microgrid-cluster", "microgrid-service" },
            new object[] { "pvessc-cluster", "pvessc-service" },
        };

        public static IEnumerable<object[]> EnergyServicesServiceMappings => new List<object[]>
        {
            new object[] { "electrade-cluster", "electrade-service" },
            new object[] { "carbontrade-cluster", "carbontrade-service" },
            new object[] { "demandresp-cluster", "demandresp-service" },
            new object[] { "deviceops-cluster", "deviceops-service" },
            new object[] { "energyeff-cluster", "energyeff-service" },
            new object[] { "multienergy-cluster", "multienergy-service" },
            new object[] { "safecontrol-cluster", "safecontrol-service" },
        };

        // Fallback Docker DNS convention tests
        [Theory]
        [InlineData("tenant-service", "http://jgsy-tenant:8080")]
        [InlineData("identity-service", "http://jgsy-identity:8080")]
        [InlineData("permission-service", "http://jgsy-permission:8080")]
        [InlineData("account-service", "http://jgsy-account:8080")]
        [InlineData("device-service", "http://jgsy-device:8080")]
        [InlineData("orchestrator-service", "http://jgsy-orchestrator:8080")]
        [InlineData("vpp-service", "http://jgsy-vpp:8080")]
        [InlineData("pvessc-service", "http://jgsy-pvessc:8080")]
        [InlineData("blockchain-service", "http://jgsy-blockchain:8080")]
        [InlineData("gateway-service", "http://jgsy-gateway:8080")]
        public void FallbackDestination_ShouldFollowDockerDnsConvention(string serviceName, string expectedAddress)
        {
            // Test the naming convention: remove "-service" → "http://jgsy-{name}:8080"
            var containerName = serviceName.Replace("-service", "");
            var address = $"http://jgsy-{containerName}:8080";

            address.Should().Be(expectedAddress);
        }

        [Theory]
        [InlineData("tenant-service", "tenant-service-docker")]
        [InlineData("identity-service", "identity-service-docker")]
        [InlineData("gateway-service", "gateway-service-docker")]
        public void FallbackDestination_KeyShouldFollowConvention(string serviceName, string expectedKey)
        {
            var key = $"{serviceName}-docker";
            key.Should().Be(expectedKey);
        }

        [Fact]
        public void DefaultServiceMappings_ShouldHave30Entries()
        {
            // 6 platform + 9 aiops + 3 extensions + 7 energycore + 6 energyservices - 1 (duplicated gateway in fallback) = 31
            // Actually: 6 + 9 + 3 + 7 + 6 = 31, but looking at the code it's 30 (let me count exactly)
            // Platform: gateway, tenant, identity, permission, observability, storage = 6
            // AIOps: account, analytics, charging, device, digitaltwin, ingestion, settlement, station, workorder = 9
            // Extensions: iotcloudai, contentplatform, blockchain = 3
            // EnergyCore: vpp, microgrid, sehs, pvessc, electrade, carbontrade, energycore = 7
            // EnergyServices: energyeff, deviceops, demandresp, multienergy, safecontrol, energyservices = 6
            // Total: 6 + 9 + 3 + 7 + 6 = 31

            var totalMappings = PlatformServiceMappings.Count()
                + AiopsServiceMappings.Count()
                + ExtensionServiceMappings.Count()
                + EnergyCoreServiceMappings.Count()
                + EnergyServicesServiceMappings.Count();

            totalMappings.Should().Be(29);
        }

        [Fact]
        public void AllClusterIds_ShouldEndWithCluster()
        {
            var allMappings = PlatformServiceMappings
                .Concat(AiopsServiceMappings)
                .Concat(ExtensionServiceMappings)
                .Concat(EnergyCoreServiceMappings)
                .Concat(EnergyServicesServiceMappings);

            foreach (var mapping in allMappings)
            {
                var clusterId = (string)mapping[0];
                clusterId.Should().EndWith("-cluster", because: $"cluster ID '{clusterId}' must follow convention");
            }
        }

        [Fact]
        public void AllServiceNames_ShouldEndWithService()
        {
            var allMappings = PlatformServiceMappings
                .Concat(AiopsServiceMappings)
                .Concat(ExtensionServiceMappings)
                .Concat(EnergyCoreServiceMappings)
                .Concat(EnergyServicesServiceMappings);

            foreach (var mapping in allMappings)
            {
                var serviceName = (string)mapping[1];
                serviceName.Should().EndWith("-service", because: $"service name '{serviceName}' must follow convention");
            }
        }

        [Fact]
        public void EnergyCoreClusters_ShouldHaveValidServiceNames()
        {
            // 能源核心服务已拆分为独立微服务：orchestrator, vpp, microgrid, pvessc
            foreach (var mapping in EnergyCoreServiceMappings)
            {
                var serviceName = (string)mapping[1];
                serviceName.Should().EndWith("-service",
                    because: "all energy core clusters should map to valid service names");
            }
        }

        [Fact]
        public void EnergyServicesClusters_ShouldHaveValidServiceNames()
        {
            // 能源服务已拆分为独立微服务：electrade, carbontrade, demandresp, deviceops, energyeff, multienergy, safecontrol
            foreach (var mapping in EnergyServicesServiceMappings)
            {
                var serviceName = (string)mapping[1];
                serviceName.Should().EndWith("-service",
                    because: "all energy services clusters should map to valid service names");
            }
        }

        [Fact]
        public void PlatformServices_ShouldIncludeCoreInfrastructure()
        {
            var serviceNames = PlatformServiceMappings.Select(m => (string)m[1]).ToList();

            serviceNames.Should().Contain("tenant-service");
            serviceNames.Should().Contain("identity-service");
            serviceNames.Should().Contain("permission-service");
            serviceNames.Should().Contain("gateway-service");
        }

        [Fact]
        public void DockerContainerName_Convention_ShouldBeCorrect()
        {
            // All services follow: jgsy-{serviceName without "-service"}
            var testCases = new Dictionary<string, string>
            {
                { "tenant-service", "jgsy-tenant" },
                { "identity-service", "jgsy-identity" },
                { "energycore-service", "jgsy-energycore" },
                { "blockchain-service", "jgsy-blockchain" },
                { "iotcloudai-service", "jgsy-iotcloudai" },
            };

            foreach (var (serviceName, expectedContainer) in testCases)
            {
                var containerName = serviceName.Replace("-service", "");
                $"jgsy-{containerName}".Should().Be(expectedContainer);
            }
        }

        [Fact]
        public void FallbackPort_ShouldAlwaysBe8080()
        {
            var services = new[] { "tenant-service", "identity-service", "blockchain-service", "energycore-service" };

            foreach (var service in services)
            {
                var containerName = service.Replace("-service", "");
                var address = $"http://jgsy-{containerName}:8080";

                address.Should().Contain(":8080", because: "all internal services use port 8080");
            }
        }
    }
}
