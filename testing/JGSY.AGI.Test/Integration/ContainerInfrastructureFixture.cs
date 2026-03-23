using System;
using System.Threading.Tasks;
using DotNet.Testcontainers.Builders;
using Testcontainers.PostgreSql;
using Testcontainers.Redis;
using Xunit;

namespace JGSY.AGI.Test.Integration;

/// <summary>
/// Testcontainers 基础设施 Fixture（PostgreSQL + Redis）
/// 可用于集成测试共享资源，避免每个测试都启动容器
/// </summary>
public class ContainerInfrastructureFixture : IAsyncLifetime
{
    public PostgreSqlContainer PostgresContainer { get; private set; } = null!;
    public RedisContainer RedisContainer { get; private set; } = null!;

    public string PostgresConnectionString => PostgresContainer.GetConnectionString();
    public string RedisConnectionString => $"{RedisContainer.Hostname}:{RedisContainer.GetMappedPublicPort(6379)}";

    public async Task InitializeAsync()
    {
        PostgresContainer = new PostgreSqlBuilder()
            .WithImage("postgres:15-alpine")
            .WithDatabase("test_db")
            .WithUsername("test")
            .WithPassword("test")
            .WithWaitStrategy(Wait.ForUnixContainer().UntilPortIsAvailable(5432))
            .Build();

        RedisContainer = new RedisBuilder()
            .WithImage("redis:7-alpine")
            .WithWaitStrategy(Wait.ForUnixContainer().UntilPortIsAvailable(6379))
            .Build();

        await Task.WhenAll(
            PostgresContainer.StartAsync(),
            RedisContainer.StartAsync()
        );
    }

    public async Task DisposeAsync()
    {
        await Task.WhenAll(
            PostgresContainer.DisposeAsync().AsTask(),
            RedisContainer.DisposeAsync().AsTask()
        );
    }
}

/// <summary>
/// 集成测试集合定义（共享 Testcontainers 实例）
/// </summary>
[CollectionDefinition("ContainerCollection")]
public class ContainerCollection : ICollectionFixture<ContainerInfrastructureFixture>
{
}
