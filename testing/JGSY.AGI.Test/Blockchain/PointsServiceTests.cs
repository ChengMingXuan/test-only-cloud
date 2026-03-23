using Xunit;
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Caching.Memory;
using JGSY.AGI.Blockchain.Services;
using JGSY.AGI.Blockchain.Data.Repositories;
using JGSY.AGI.Blockchain.Entities;

namespace JGSY.AGI.Test.Blockchain;

/// <summary>
/// 积分服务单元测试
/// </summary>
public class PointsServiceTests
{
    private readonly Mock<IPointAccountRepository> _accountRepo = new();
    private readonly Mock<IPointTransactionRepository> _transactionRepo = new();
    private readonly Mock<IRechargeOrderRepository> _rechargeOrderRepo = new();
    private readonly Mock<IWalletRepository> _walletRepo = new();
    private readonly Mock<IProofService> _proofService = new();
    private readonly Mock<IPointsConfigService> _configService = new();
    private readonly PointsService _service;

    public PointsServiceTests()
    {
        // 默认配置：关闭链上存证以简化测试
        _configService.Setup(c => c.GetConfigAsync()).ReturnsAsync(new PointsConfigDto
        {
            EnableChainProof = false,
            ChainProofThreshold = 10000,
            LargeAmountThreshold = 100000,
            AutoProofLargeAmount = false,
            ChainProofTypes = ["recharge", "consume", "refund"]
        });

        _service = new PointsService(
            _accountRepo.Object,
            _transactionRepo.Object,
            _rechargeOrderRepo.Object,
            _walletRepo.Object,
            _proofService.Object,
            _configService.Object,
            NullLogger<PointsService>.Instance);
    }

    #region 获取账户

    [Fact]
    public async Task GetAccountAsync_ExistingAccount_ReturnsMappedDto()
    {
        // Arrange
        var userId = Guid.NewGuid();
        var account = new PointAccount
        {
            UserId = userId.ToString(),
            WalletAddress = "0xABC",
            Balance = 15000,
            FrozenAmount = 2000,
            TotalRecharged = 50000,
            TotalConsumed = 35000
        };
        _accountRepo.Setup(r => r.GetByUserIdAsync(userId.ToString())).ReturnsAsync(account);

        // Act
        var result = await _service.GetAccountAsync(userId);

        // Assert
        result.Should().NotBeNull();
        result!.UserId.Should().Be(userId.ToString());
        result.WalletAddress.Should().Be("0xABC");
        result.Balance.Should().Be(15000);
        result.BalanceYuan.Should().Be(150m); // 15000/100
        result.FrozenAmount.Should().Be(2000);
        result.FrozenYuan.Should().Be(20m);
        result.TotalRecharged.Should().Be(50000);
        result.TotalRechargedYuan.Should().Be(500m);
        result.TotalConsumed.Should().Be(35000);
        result.TotalConsumedYuan.Should().Be(350m);
    }

    [Fact]
    public async Task GetAccountAsync_NoAccount_AutoCreates()
    {
        // Arrange
        var userId = Guid.NewGuid();
        _accountRepo.Setup(r => r.GetByUserIdAsync(userId.ToString())).ReturnsAsync((PointAccount?)null);
        _walletRepo.Setup(r => r.GetDefaultByUserIdAsync(userId)).ReturnsAsync((WalletInfo?)null);
        // InsertAsync 后再次调用不会返回 null（模拟创建了账户）
        _accountRepo.Setup(r => r.InsertAsync(It.IsAny<PointAccount>())).ReturnsAsync(Guid.NewGuid());

        // Act
        var result = await _service.GetAccountAsync(userId);

        // Assert
        result.Should().NotBeNull();
        result!.Balance.Should().Be(0);
        result.BalanceYuan.Should().Be(0m);
        _accountRepo.Verify(r => r.InsertAsync(It.Is<PointAccount>(
            a => a.UserId == userId.ToString() && a.Balance == 0)), Times.Once);
    }

    #endregion

    #region 创建充值订单

    [Fact]
    public async Task CreateRechargeOrderAsync_Success_ConvertYuanToFen()
    {
        // Arrange
        var userId = Guid.NewGuid();
        var account = new PointAccount { UserId = userId.ToString(), WalletAddress = "0xABC" };
        _accountRepo.Setup(r => r.GetByUserIdAsync(userId.ToString())).ReturnsAsync(account);

        // Act
        var result = await _service.CreateRechargeOrderAsync(userId, 100m, "alipay");

        // Assert
        result.Should().NotBeNull();
        result.OrderId.Should().StartWith("RC");
        result.AmountYuan.Should().Be(100m);
        result.Points.Should().Be(10000); // 100元 = 10000分
        result.PaymentMethod.Should().Be("alipay");
        result.Status.Should().Be("pending");

        _rechargeOrderRepo.Verify(r => r.InsertAsync(It.Is<RechargeOrder>(
            o => o.Amount == 10000 && o.Points == 10000 && o.Status == "pending")), Times.Once);
    }

    [Fact]
    public async Task CreateRechargeOrderAsync_NoAccount_AutoCreatesFirst()
    {
        // Arrange
        var userId = Guid.NewGuid();
        _accountRepo.Setup(r => r.GetByUserIdAsync(userId.ToString())).ReturnsAsync((PointAccount?)null);
        _walletRepo.Setup(r => r.GetDefaultByUserIdAsync(userId)).ReturnsAsync((WalletInfo?)null);
        _accountRepo.Setup(r => r.InsertAsync(It.IsAny<PointAccount>())).ReturnsAsync(Guid.NewGuid());

        // Act
        var result = await _service.CreateRechargeOrderAsync(userId, 50m, "wechat");

        // Assert
        result.Should().NotBeNull();
        result.Points.Should().Be(5000);
        _accountRepo.Verify(r => r.InsertAsync(It.IsAny<PointAccount>()), Times.Once);
    }

    #endregion

    #region 充值完成

    [Fact]
    public async Task CompleteRechargeAsync_OrderNotFound_ReturnsFalse()
    {
        // Arrange
        _rechargeOrderRepo.Setup(r => r.GetByOrderIdAsync("INVALID")).ReturnsAsync((RechargeOrder?)null);

        // Act
        var result = await _service.CompleteRechargeAsync("INVALID", "PAY001");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task CompleteRechargeAsync_AlreadyCompleted_ReturnsFalse()
    {
        // Arrange
        var order = new RechargeOrder { OrderId = "RC001", Status = "completed", UserId = "user1" };
        _rechargeOrderRepo.Setup(r => r.GetByOrderIdAsync("RC001")).ReturnsAsync(order);

        // Act
        var result = await _service.CompleteRechargeAsync("RC001", "PAY002");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task CompleteRechargeAsync_AccountNotFound_ReturnsFalse()
    {
        // Arrange
        var order = new RechargeOrder { OrderId = "RC002", Status = "pending", UserId = "user1", Points = 5000 };
        _rechargeOrderRepo.Setup(r => r.GetByOrderIdAsync("RC002")).ReturnsAsync(order);
        _accountRepo.Setup(r => r.GetByUserIdAsync("user1")).ReturnsAsync((PointAccount?)null);

        // Act
        var result = await _service.CompleteRechargeAsync("RC002", "PAY003");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task CompleteRechargeAsync_Success_UpdatesBalanceAndRecordsTransaction()
    {
        // Arrange
        var order = new RechargeOrder
        {
            OrderId = "RC003",
            Status = "pending",
            UserId = "user1",
            Points = 10000,
            Amount = 10000
        };
        var account = new PointAccount
        {
            UserId = "user1",
            WalletAddress = "0xABC",
            Balance = 5000
        };
        _rechargeOrderRepo.Setup(r => r.GetByOrderIdAsync("RC003")).ReturnsAsync(order);
        _accountRepo.Setup(r => r.GetByUserIdAsync("user1")).ReturnsAsync(account);

        // Act
        var result = await _service.CompleteRechargeAsync("RC003", "PAY004");

        // Assert
        result.Should().BeTrue();
        _rechargeOrderRepo.Verify(r => r.UpdateStatusAsync("RC003", "completed", It.IsAny<DateTime>(), It.IsAny<DateTime>()), Times.Once);
        _accountRepo.Verify(r => r.UpdateBalanceAsync("user1", 10000, 0), Times.Once);
        _transactionRepo.Verify(r => r.InsertAsync(It.Is<PointTransaction>(
            t => t.TxType == "recharge" && t.Amount == 10000 &&
                 t.BalanceBefore == 5000 && t.BalanceAfter == 15000)), Times.Once);
    }

    #endregion

    #region 消费积分

    [Fact]
    public async Task ConsumeAsync_AccountNull_ReturnsFailure()
    {
        // Arrange
        var userId = Guid.NewGuid();
        _accountRepo.Setup(r => r.GetByUserIdAsync(userId.ToString())).ReturnsAsync((PointAccount?)null);

        // Act
        var result = await _service.ConsumeAsync(userId, 1000, "ORDER01", "充电消费");

        // Assert
        result.Success.Should().BeFalse();
        result.Message.Should().Contain("账户不存在");
    }

    [Fact]
    public async Task ConsumeAsync_InsufficientBalance_ReturnsFailure()
    {
        // Arrange
        var userId = Guid.NewGuid();
        var account = new PointAccount { UserId = userId.ToString(), Balance = 500 };
        _accountRepo.Setup(r => r.GetByUserIdAsync(userId.ToString())).ReturnsAsync(account);

        // Act
        var result = await _service.ConsumeAsync(userId, 1000, "ORDER02", "充电消费");

        // Assert
        result.Success.Should().BeFalse();
        result.Message.Should().Contain("余额不足");
    }

    [Fact]
    public async Task ConsumeAsync_Success_DeductsAndRecordsTransaction()
    {
        // Arrange
        var userId = Guid.NewGuid();
        var account = new PointAccount
        {
            UserId = userId.ToString(),
            WalletAddress = "0xABC",
            Balance = 20000
        };
        _accountRepo.Setup(r => r.GetByUserIdAsync(userId.ToString())).ReturnsAsync(account);

        // Act
        var result = await _service.ConsumeAsync(userId, 5000, "ORDER03", "充电消费");

        // Assert
        result.Success.Should().BeTrue();
        result.ConsumedPoints.Should().Be(5000);
        result.ConsumedYuan.Should().Be(50m); // 5000/100
        result.BalanceAfter.Should().Be(15000); // 20000-5000
        result.BalanceAfterYuan.Should().Be(150m);
        result.TxId.Should().StartWith("TX");

        _accountRepo.Verify(r => r.UpdateBalanceAsync(userId.ToString(), -5000, 0), Times.Once);
        _transactionRepo.Verify(r => r.InsertAsync(It.Is<PointTransaction>(
            t => t.TxType == "consume" && t.Amount == -5000 &&
                 t.BalanceBefore == 20000 && t.BalanceAfter == 15000)), Times.Once);
    }

    #endregion

    #region 退款

    [Fact]
    public async Task RefundAsync_AccountNull_ReturnsFalse()
    {
        // Arrange
        var userId = Guid.NewGuid();
        _accountRepo.Setup(r => r.GetByUserIdAsync(userId.ToString())).ReturnsAsync((PointAccount?)null);

        // Act
        var result = await _service.RefundAsync(userId, 1000, "ORDER04", "退款");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task RefundAsync_Success_AddsBalanceAndRecordsTransaction()
    {
        // Arrange
        var userId = Guid.NewGuid();
        var account = new PointAccount
        {
            UserId = userId.ToString(),
            WalletAddress = "0xABC",
            Balance = 10000
        };
        _accountRepo.Setup(r => r.GetByUserIdAsync(userId.ToString())).ReturnsAsync(account);

        // Act
        var result = await _service.RefundAsync(userId, 3000, "ORDER05", "充电退款");

        // Assert
        result.Should().BeTrue();
        _accountRepo.Verify(r => r.UpdateBalanceAsync(userId.ToString(), 3000, 0), Times.Once);
        _transactionRepo.Verify(r => r.InsertAsync(It.Is<PointTransaction>(
            t => t.TxType == "refund" && t.Amount == 3000 &&
                 t.BalanceBefore == 10000 && t.BalanceAfter == 13000)), Times.Once);
    }

    #endregion

    #region 查询流水

    [Fact]
    public async Task GetTransactionsAsync_ReturnsMappedDtos()
    {
        // Arrange
        var userId = Guid.NewGuid();
        var transactions = new List<PointTransaction>
        {
            new()
            {
                TxId = "TX001", TxType = "recharge", Amount = 10000,
                BalanceBefore = 0, BalanceAfter = 10000, OrderId = "RC001",
                Remark = "充值", CreateTime = DateTime.UtcNow
            },
            new()
            {
                TxId = "TX002", TxType = "consume", Amount = -3000,
                BalanceBefore = 10000, BalanceAfter = 7000, OrderId = "ORDER01",
                Remark = "消费", CreateTime = DateTime.UtcNow
            }
        };
        _transactionRepo.Setup(r => r.CountByUserIdAsync(userId.ToString())).ReturnsAsync(2);
        _transactionRepo.Setup(r => r.GetByUserIdAsync(userId.ToString(), 1, 10))
            .ReturnsAsync(transactions);

        // Act
        var result = await _service.GetTransactionsAsync(userId, 1, 10);

        // Assert
        result.Should().NotBeNull();
        result.TotalCount.Should().Be(2);
        result.Items.Should().HaveCount(2);
        result.Items[0].TxTypeName.Should().Be("充值"); // recharge → 充值
        result.Items[0].AmountYuan.Should().Be(100m); // 10000/100
        result.Items[1].TxTypeName.Should().Be("消费"); // consume → 消费
        result.Items[1].AmountYuan.Should().Be(-30m); // -3000/100
    }

    #endregion

    #region 获取余额

    [Fact]
    public async Task GetBalanceYuanAsync_WithAccount_ReturnsDivided()
    {
        // Arrange
        var userId = Guid.NewGuid();
        var account = new PointAccount { UserId = userId.ToString(), Balance = 15000 };
        _accountRepo.Setup(r => r.GetByUserIdAsync(userId.ToString())).ReturnsAsync(account);

        // Act
        var result = await _service.GetBalanceYuanAsync(userId);

        // Assert
        result.Should().Be(150m); // 15000/100
    }

    [Fact]
    public async Task GetBalanceYuanAsync_NoAccount_ReturnsZero()
    {
        // Arrange
        var userId = Guid.NewGuid();
        _accountRepo.Setup(r => r.GetByUserIdAsync(userId.ToString())).ReturnsAsync((PointAccount?)null);

        // Act
        var result = await _service.GetBalanceYuanAsync(userId);

        // Assert
        result.Should().Be(0m);
    }

    #endregion
}

/// <summary>
/// 积分配置服务单元测试
/// </summary>
public class PointsConfigServiceTests
{
    private readonly Mock<IPointsConfigRepository> _configRepo = new();
    private readonly IMemoryCache _cache;
    private readonly PointsConfigService _service;

    public PointsConfigServiceTests()
    {
        _cache = new MemoryCache(new MemoryCacheOptions());
        _service = new PointsConfigService(
            _configRepo.Object,
            _cache,
            NullLogger<PointsConfigService>.Instance);
    }

    [Fact]
    public async Task GetConfigAsync_CacheMiss_LoadsFromRepo()
    {
        // Arrange
        var dict = new Dictionary<string, string>
        {
            ["enable_chain_proof"] = "true",
            ["chain_proof_threshold"] = "20000",
            ["large_amount_threshold"] = "200000",
            ["auto_proof_large_amount"] = "false",
            ["chain_proof_types"] = "[\"recharge\",\"refund\"]"
        };
        _configRepo.Setup(r => r.GetConfigDictionaryAsync()).ReturnsAsync(dict);

        // Act
        var result = await _service.GetConfigAsync();

        // Assert
        result.EnableChainProof.Should().BeTrue();
        result.ChainProofThreshold.Should().Be(20000);
        result.LargeAmountThreshold.Should().Be(200000);
        result.AutoProofLargeAmount.Should().BeFalse();
        result.ChainProofTypes.Should().BeEquivalentTo("recharge", "refund");
    }

    [Fact]
    public async Task GetConfigAsync_CacheHit_DoesNotCallRepo()
    {
        // Arrange - 先加载一次
        var dict = new Dictionary<string, string>
        {
            ["enable_chain_proof"] = "true",
            ["chain_proof_threshold"] = "10000"
        };
        _configRepo.Setup(r => r.GetConfigDictionaryAsync()).ReturnsAsync(dict);
        await _service.GetConfigAsync(); // 第一次加载

        // Act
        await _service.GetConfigAsync(); // 第二次应命中缓存

        // Assert - repo 只被调用一次
        _configRepo.Verify(r => r.GetConfigDictionaryAsync(), Times.Once);
    }

    [Fact]
    public async Task GetConfigAsync_EmptyDict_UsesDefaults()
    {
        // Arrange
        _configRepo.Setup(r => r.GetConfigDictionaryAsync()).ReturnsAsync(new Dictionary<string, string>());

        // Act
        var result = await _service.GetConfigAsync();

        // Assert - 使用默认值
        result.EnableChainProof.Should().BeTrue(); // default true
        result.ChainProofThreshold.Should().Be(10000); // default 10000
        result.LargeAmountThreshold.Should().Be(100000); // default 100000
        result.AutoProofLargeAmount.Should().BeTrue(); // default true
        result.ChainProofTypes.Should().BeEquivalentTo("recharge", "consume", "refund");
    }

    [Fact]
    public async Task UpdateConfigAsync_UpdatesOnlySpecifiedFields()
    {
        // Arrange
        var request = new PointsConfigUpdateRequest
        {
            EnableChainProof = false,
            ChainProofThreshold = 50000
            // 其他字段为 null，不更新
        };

        // Act
        await _service.UpdateConfigAsync(request, "admin");

        // Assert
        _configRepo.Verify(r => r.UpdateAsync("enable_chain_proof", "false", "admin"), Times.Once);
        _configRepo.Verify(r => r.UpdateAsync("chain_proof_threshold", "50000", "admin"), Times.Once);
        _configRepo.Verify(r => r.UpdateAsync("large_amount_threshold", It.IsAny<string>(), It.IsAny<string>()), Times.Never);
        _configRepo.Verify(r => r.UpdateAsync("auto_proof_large_amount", It.IsAny<string>(), It.IsAny<string>()), Times.Never);
        _configRepo.Verify(r => r.UpdateAsync("chain_proof_types", It.IsAny<string>(), It.IsAny<string>()), Times.Never);
    }

    [Fact]
    public async Task UpdateConfigAsync_InvalidatesCacheAfterUpdate()
    {
        // Arrange - 先填充缓存
        var dict = new Dictionary<string, string> { ["enable_chain_proof"] = "true" };
        _configRepo.Setup(r => r.GetConfigDictionaryAsync()).ReturnsAsync(dict);
        await _service.GetConfigAsync(); // 填充缓存

        // Act
        await _service.UpdateConfigAsync(new PointsConfigUpdateRequest { EnableChainProof = false }, "admin");

        // 再次获取会重新调用 repo
        await _service.GetConfigAsync();

        // Assert - 缓存被清除，repo被调用两次
        _configRepo.Verify(r => r.GetConfigDictionaryAsync(), Times.Exactly(2));
    }

    [Fact]
    public void InvalidateCache_RemovesCachedConfig()
    {
        // Arrange
        _cache.Set("points_config", new PointsConfigDto());

        // Act
        _service.InvalidateCache();

        // Assert
        _cache.TryGetValue("points_config", out _).Should().BeFalse();
    }
}
