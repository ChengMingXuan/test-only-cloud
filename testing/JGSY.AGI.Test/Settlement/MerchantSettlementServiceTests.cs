using Xunit;
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using JGSY.AGI.Settlement.Service;
using JGSY.AGI.Settlement.Data.Repositories;
using JGSY.AGI.Settlement.Entities;
using JGSY.AGI.Common.Core.Exceptions;

namespace JGSY.AGI.Test.Settlement;

/// <summary>
/// 商户结算服务单元测试
/// </summary>
public class MerchantSettlementServiceTests
{
    private readonly Mock<IMerchantAccountRepository> _merchantRepo = new();
    private readonly Mock<ISettlementRuleRepository> _ruleRepo = new();
    private readonly Mock<ISettlementOrderRepository> _orderRepo = new();
    private readonly Mock<IPayoutRecordRepository> _payoutRepo = new();
    private readonly Mock<IReconciliationRepository> _reconRepo = new();
    private readonly MerchantSettlementService _service;

    public MerchantSettlementServiceTests()
    {
        _service = new MerchantSettlementService(
            _merchantRepo.Object,
            _ruleRepo.Object,
            _orderRepo.Object,
            _payoutRepo.Object,
            _reconRepo.Object,
            NullLogger<MerchantSettlementService>.Instance);
    }

    #region 创建商户账户

    [Fact]
    public async Task CreateMerchantAccountAsync_CodeExists_ThrowsBusinessException()
    {
        // Arrange
        _merchantRepo.Setup(r => r.ExistsByCodeAsync("MC001")).ReturnsAsync(true);

        // Act & Assert
        var act = () => _service.CreateMerchantAccountAsync("测试商户", "MC001", MerchantType.Platform);
        await act.Should().ThrowAsync<BusinessException>().WithMessage("*MC001*已存在*");
    }

    [Fact]
    public async Task CreateMerchantAccountAsync_Success_ReturnsAccount()
    {
        // Arrange
        _merchantRepo.Setup(r => r.ExistsByCodeAsync("MC002")).ReturnsAsync(false);

        // Act
        var result = await _service.CreateMerchantAccountAsync(
            "测试商户", "MC002", MerchantType.Agent, "张三", "13800000000", "工商银行", "6222000000000001");

        // Assert
        result.Should().NotBeNull();
        result.MerchantName.Should().Be("测试商户");
        result.MerchantCode.Should().Be("MC002");
        result.MerchantType.Should().Be((int)MerchantType.Agent);
        result.ContactPerson.Should().Be("张三");
        result.ContactPhone.Should().Be("13800000000");
        result.BankName.Should().Be("工商银行");
        result.BankAccount.Should().Be("6222000000000001");
        result.AccountBalance.Should().Be(0);
        result.Status.Should().Be((int)AccountStatus.Active);
        result.Id.Should().NotBeEmpty();

        _merchantRepo.Verify(r => r.InsertAsync(It.IsAny<MerchantAccount>()), Times.Once);
    }

    #endregion

    #region 获取商户账户

    [Fact]
    public async Task GetMerchantAccountAsync_DelegatesToRepo()
    {
        // Arrange
        var id = Guid.NewGuid();
        var account = new MerchantAccount { Id = id, MerchantName = "商户A" };
        _merchantRepo.Setup(r => r.GetByIdAsync(id)).ReturnsAsync(account);

        // Act
        var result = await _service.GetMerchantAccountAsync(id);

        // Assert
        result.Should().NotBeNull();
        result!.MerchantName.Should().Be("商户A");
    }

    [Fact]
    public async Task GetMerchantAccountByCodeAsync_DelegatesToRepo()
    {
        // Arrange
        var account = new MerchantAccount { MerchantCode = "MC001", MerchantName = "商户B" };
        _merchantRepo.Setup(r => r.GetByCodeAsync("MC001")).ReturnsAsync(account);

        // Act
        var result = await _service.GetMerchantAccountByCodeAsync("MC001");

        // Assert
        result.Should().NotBeNull();
        result!.MerchantCode.Should().Be("MC001");
    }

    #endregion

    #region 更新银行信息

    [Fact]
    public async Task UpdateMerchantBankInfoAsync_NotFound_ThrowsBusinessException()
    {
        // Arrange
        var id = Guid.NewGuid();
        _merchantRepo.Setup(r => r.GetByIdAsync(id)).ReturnsAsync((MerchantAccount?)null);

        // Act & Assert
        var act = () => _service.UpdateMerchantBankInfoAsync(id, "工商银行", "622200001");
        await act.Should().ThrowAsync<BusinessException>().WithMessage("*商户不存在*");
    }

    [Fact]
    public async Task UpdateMerchantBankInfoAsync_Success_UpdatesBank()
    {
        // Arrange
        var id = Guid.NewGuid();
        _merchantRepo.Setup(r => r.GetByIdAsync(id)).ReturnsAsync(new MerchantAccount { Id = id });

        // Act
        await _service.UpdateMerchantBankInfoAsync(id, "工商银行", "622200001", "支行信息");

        // Assert
        _merchantRepo.Verify(r => r.UpdateBankInfoAsync(id, "工商银行", "622200001", "支行信息"), Times.Once);
    }

    #endregion

    #region 设置商户状态

    [Fact]
    public async Task SetMerchantAccountStatusAsync_NotFound_ThrowsBusinessException()
    {
        // Arrange
        var id = Guid.NewGuid();
        _merchantRepo.Setup(r => r.GetByIdAsync(id)).ReturnsAsync((MerchantAccount?)null);

        // Act & Assert
        var act = () => _service.SetMerchantAccountStatusAsync(id, AccountStatus.Frozen);
        await act.Should().ThrowAsync<BusinessException>().WithMessage("*商户不存在*");
    }

    [Fact]
    public async Task SetMerchantAccountStatusAsync_Success_UpdatesStatus()
    {
        // Arrange
        var id = Guid.NewGuid();
        var merchant = new MerchantAccount { Id = id, Status = (int)AccountStatus.Active };
        _merchantRepo.Setup(r => r.GetByIdAsync(id)).ReturnsAsync(merchant);

        // Act
        await _service.SetMerchantAccountStatusAsync(id, AccountStatus.Frozen);

        // Assert
        merchant.Status.Should().Be((int)AccountStatus.Frozen);
        _merchantRepo.Verify(r => r.UpdateAsync(merchant), Times.Once);
    }

    #endregion

    #region 创建结算规则

    [Fact]
    public async Task CreateSettlementRuleAsync_RatesNotEqual100_ThrowsBusinessException()
    {
        // Arrange & Act & Assert
        var act = () => _service.CreateSettlementRuleAsync(
            Guid.NewGuid(), "规则A", "Charging", 60, 30, 30);
        await act.Should().ThrowAsync<BusinessException>().WithMessage("*总和必须为100*");
    }

    [Fact]
    public async Task CreateSettlementRuleAsync_Success_ReturnsRule()
    {
        // Arrange
        var merchantId = Guid.NewGuid();

        // Act
        var result = await _service.CreateSettlementRuleAsync(
            merchantId, "充电结算", "Charging", 30, 70, 7, 100m);

        // Assert
        result.Should().NotBeNull();
        result.MerchantId.Should().Be(merchantId);
        result.RuleName.Should().Be("充电结算");
        result.PlatformShareRate.Should().Be(30);
        result.MerchantShareRate.Should().Be(70);
        result.SettlementCycle.Should().Be(7);
        result.MinSettlementAmount.Should().Be(100m);
        result.IsActive.Should().BeTrue();

        _ruleRepo.Verify(r => r.InsertAsync(It.IsAny<SettlementRule>()), Times.Once);
    }

    #endregion

    #region 获取结算规则

    [Fact]
    public async Task GetActiveSettlementRuleAsync_DelegatesToRepo()
    {
        // Arrange
        var merchantId = Guid.NewGuid();
        var rule = new SettlementRule { MerchantId = merchantId, BusinessType = "Charging" };
        _ruleRepo.Setup(r => r.GetActiveByMerchantAsync(merchantId, "Charging")).ReturnsAsync(rule);

        // Act
        var result = await _service.GetActiveSettlementRuleAsync(merchantId, "Charging");

        // Assert
        result.Should().NotBeNull();
        result!.BusinessType.Should().Be("Charging");
    }

    #endregion

    #region 生成结算单

    [Fact]
    public async Task GenerateSettlementOrderAsync_RuleNotFound_ThrowsBusinessException()
    {
        // Arrange
        var ruleId = Guid.NewGuid();
        _ruleRepo.Setup(r => r.GetByIdAsync(ruleId)).ReturnsAsync((SettlementRule?)null);

        // Act & Assert
        var act = () => _service.GenerateSettlementOrderAsync(
            Guid.NewGuid(), ruleId, DateTime.UtcNow.AddDays(-7), DateTime.UtcNow, "Charging", 10000m, 50);
        await act.Should().ThrowAsync<BusinessException>().WithMessage("*结算规则不存在*");
    }

    [Fact]
    public async Task GenerateSettlementOrderAsync_BelowMinAmount_ThrowsBusinessException()
    {
        // Arrange
        var ruleId = Guid.NewGuid();
        var rule = new SettlementRule
        {
            Id = ruleId,
            PlatformShareRate = 30,
            MerchantShareRate = 70,
            MinSettlementAmount = 5000m
        };
        _ruleRepo.Setup(r => r.GetByIdAsync(ruleId)).ReturnsAsync(rule);

        // Act & Assert - merchantAmount=1000*70/100=700 < 5000
        var act = () => _service.GenerateSettlementOrderAsync(
            Guid.NewGuid(), ruleId, DateTime.UtcNow.AddDays(-7), DateTime.UtcNow, "Charging", 1000m, 10);
        await act.Should().ThrowAsync<BusinessException>().WithMessage("*最小金额*");
    }

    [Fact]
    public async Task GenerateSettlementOrderAsync_Success_CalculatesAmountsCorrectly()
    {
        // Arrange
        var merchantId = Guid.NewGuid();
        var ruleId = Guid.NewGuid();
        var rule = new SettlementRule
        {
            Id = ruleId,
            PlatformShareRate = 20,
            MerchantShareRate = 80,
            MinSettlementAmount = 0
        };
        _ruleRepo.Setup(r => r.GetByIdAsync(ruleId)).ReturnsAsync(rule);

        // Act
        var result = await _service.GenerateSettlementOrderAsync(
            merchantId, ruleId, DateTime.UtcNow.AddDays(-7), DateTime.UtcNow, "Charging", 10000m, 50);

        // Assert - platformAmount=10000*20/100=2000, merchantAmount=10000*80/100=8000
        result.Should().NotBeNull();
        result.PlatformAmount.Should().Be(2000m);
        result.MerchantAmount.Should().Be(8000m);
        result.TotalRevenue.Should().Be(10000m);
        result.OrderCount.Should().Be(50);
        result.Status.Should().Be((int)SettlementStatus.Pending);
        result.SettlementOrderNo.Should().StartWith("ST");

        _orderRepo.Verify(r => r.InsertAsync(It.IsAny<SettlementOrder>()), Times.Once);
    }

    #endregion

    #region 审核结算单

    [Fact]
    public async Task ApproveSettlementOrderAsync_OrderNotFound_ThrowsBusinessException()
    {
        // Arrange
        var id = Guid.NewGuid();
        _orderRepo.Setup(r => r.GetByIdAsync(id)).ReturnsAsync((SettlementOrder?)null);

        // Act & Assert
        var act = () => _service.ApproveSettlementOrderAsync(id, Guid.NewGuid(), true);
        await act.Should().ThrowAsync<BusinessException>().WithMessage("*结算单不存在*");
    }

    [Fact]
    public async Task ApproveSettlementOrderAsync_NotPending_ThrowsBusinessException()
    {
        // Arrange
        var id = Guid.NewGuid();
        var order = new SettlementOrder { Id = id, Status = (int)SettlementStatus.Approved };
        _orderRepo.Setup(r => r.GetByIdAsync(id)).ReturnsAsync(order);

        // Act & Assert
        var act = () => _service.ApproveSettlementOrderAsync(id, Guid.NewGuid(), true);
        await act.Should().ThrowAsync<BusinessException>().WithMessage("*无法审核*");
    }

    [Fact]
    public async Task ApproveSettlementOrderAsync_Approved_UpdatesStatusToApproved()
    {
        // Arrange
        var id = Guid.NewGuid();
        var approver = Guid.NewGuid();
        var order = new SettlementOrder { Id = id, Status = (int)SettlementStatus.Pending, SettlementOrderNo = "ST001" };
        _orderRepo.Setup(r => r.GetByIdAsync(id)).ReturnsAsync(order);

        // Act
        await _service.ApproveSettlementOrderAsync(id, approver, true, "审核通过");

        // Assert
        order.Status.Should().Be((int)SettlementStatus.Approved);
        order.ApprovedBy.Should().Be(approver);
        order.ApprovalComment.Should().Be("审核通过");
        _orderRepo.Verify(r => r.UpdateStatusAsync(id, SettlementStatus.Approved, It.IsAny<Guid?>(), It.IsAny<string?>()), Times.Once);
    }

    [Fact]
    public async Task ApproveSettlementOrderAsync_Rejected_UpdatesStatusToRejected()
    {
        // Arrange
        var id = Guid.NewGuid();
        var order = new SettlementOrder { Id = id, Status = (int)SettlementStatus.Pending, SettlementOrderNo = "ST002" };
        _orderRepo.Setup(r => r.GetByIdAsync(id)).ReturnsAsync(order);

        // Act
        await _service.ApproveSettlementOrderAsync(id, Guid.NewGuid(), false, "驳回");

        // Assert
        order.Status.Should().Be((int)SettlementStatus.Rejected);
        _orderRepo.Verify(r => r.UpdateStatusAsync(id, SettlementStatus.Rejected, It.IsAny<Guid?>(), It.IsAny<string?>()), Times.Once);
    }

    #endregion

    #region 打款管理

    [Fact]
    public async Task CreatePayoutRecordAsync_OrderNotFound_ThrowsBusinessException()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        _orderRepo.Setup(r => r.GetByIdAsync(orderId)).ReturnsAsync((SettlementOrder?)null);

        // Act & Assert
        var act = () => _service.CreatePayoutRecordAsync(orderId, "银行转账", "622200001", "张三");
        await act.Should().ThrowAsync<BusinessException>().WithMessage("*结算单不存在*");
    }

    [Fact]
    public async Task CreatePayoutRecordAsync_OrderNotApproved_ThrowsBusinessException()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        var order = new SettlementOrder { Id = orderId, Status = (int)SettlementStatus.Pending };
        _orderRepo.Setup(r => r.GetByIdAsync(orderId)).ReturnsAsync(order);

        // Act & Assert
        var act = () => _service.CreatePayoutRecordAsync(orderId, "银行转账", "622200001", "张三");
        await act.Should().ThrowAsync<BusinessException>().WithMessage("*未审核通过*");
    }

    [Fact]
    public async Task CreatePayoutRecordAsync_Success_CreatesPayout()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        var merchantId = Guid.NewGuid();
        var order = new SettlementOrder
        {
            Id = orderId,
            MerchantId = merchantId,
            MerchantAmount = 8000m,
            Status = (int)SettlementStatus.Approved
        };
        _orderRepo.Setup(r => r.GetByIdAsync(orderId)).ReturnsAsync(order);

        // Act
        var result = await _service.CreatePayoutRecordAsync(orderId, "银行转账", "622200001", "张三", "工商银行");

        // Assert
        result.Should().NotBeNull();
        result.PayoutNo.Should().StartWith("PO");
        result.SettlementOrderId.Should().Be(orderId);
        result.MerchantId.Should().Be(merchantId);
        result.PayoutAmount.Should().Be(8000m);
        result.PayoutChannel.Should().Be("银行转账");
        result.Status.Should().Be((int)PayoutStatus.Pending);

        _payoutRepo.Verify(r => r.InsertAsync(It.IsAny<PayoutRecord>()), Times.Once);
    }

    #endregion

    #region 更新打款状态

    [Fact]
    public async Task UpdatePayoutStatusAsync_PayoutNotFound_ThrowsBusinessException()
    {
        // Arrange
        var id = Guid.NewGuid();
        _payoutRepo.Setup(r => r.GetByIdAsync(id)).ReturnsAsync((PayoutRecord?)null);

        // Act & Assert
        var act = () => _service.UpdatePayoutStatusAsync(id, PayoutStatus.Success);
        await act.Should().ThrowAsync<BusinessException>().WithMessage("*打款记录不存在*");
    }

    [Fact]
    public async Task UpdatePayoutStatusAsync_Success_UpdatesOrderAndBalance()
    {
        // Arrange
        var payoutId = Guid.NewGuid();
        var orderId = Guid.NewGuid();
        var merchantId = Guid.NewGuid();
        var payout = new PayoutRecord
        {
            Id = payoutId,
            PayoutNo = "PO001",
            SettlementOrderId = orderId,
            MerchantId = merchantId,
            PayoutAmount = 8000m
        };
        _payoutRepo.Setup(r => r.GetByIdAsync(payoutId)).ReturnsAsync(payout);

        // Act
        await _service.UpdatePayoutStatusAsync(payoutId, PayoutStatus.Success, "TX123", "http://voucher.url");

        // Assert - Success 触发更新结算单和商户余额
        _orderRepo.Verify(r => r.UpdatePaidAsync(orderId, payoutId), Times.Once);
        _merchantRepo.Verify(r => r.UpdateBalanceAsync(merchantId, 8000m, 8000m), Times.Once);
        _payoutRepo.Verify(r => r.UpdateStatusAsync(payoutId, PayoutStatus.Success, "TX123", (string?)null, (string?)null), Times.Once);
    }

    [Fact]
    public async Task UpdatePayoutStatusAsync_Failed_DoesNotUpdateOrderOrBalance()
    {
        // Arrange
        var payoutId = Guid.NewGuid();
        var payout = new PayoutRecord
        {
            Id = payoutId,
            PayoutNo = "PO002",
            SettlementOrderId = Guid.NewGuid(),
            MerchantId = Guid.NewGuid(),
            PayoutAmount = 5000m
        };
        _payoutRepo.Setup(r => r.GetByIdAsync(payoutId)).ReturnsAsync(payout);

        // Act
        await _service.UpdatePayoutStatusAsync(payoutId, PayoutStatus.Failed, failureReason: "余额不足");

        // Assert - 非 Success 不触发更新
        _orderRepo.Verify(r => r.UpdatePaidAsync(It.IsAny<Guid>(), It.IsAny<Guid>()), Times.Never);
        _merchantRepo.Verify(r => r.UpdateBalanceAsync(It.IsAny<Guid>(), It.IsAny<decimal>(), It.IsAny<decimal>()), Times.Never);
    }

    #endregion

    #region 对账管理

    [Fact]
    public async Task CreateReconciliationRecordAsync_PerfectMatch_ReturnsSuccess()
    {
        // Arrange & Act
        var result = await _service.CreateReconciliationRecordAsync(
            Guid.NewGuid(),
            DateTime.UtcNow.AddDays(-7), DateTime.UtcNow,
            "Charging",
            100, 50000m,
            100, 50000m);

        // Assert
        result.Should().NotBeNull();
        result.DiffOrderCount.Should().Be(0);
        result.DiffAmount.Should().Be(0);
        result.Status.Should().Be((int)ReconciliationStatus.Success);
        result.ReconciliationNo.Should().StartWith("RC");

        _reconRepo.Verify(r => r.InsertAsync(It.IsAny<ReconciliationRecord>()), Times.Once);
    }

    [Fact]
    public async Task CreateReconciliationRecordAsync_HasDiff_ReturnsDiffStatus()
    {
        // Arrange & Act
        var result = await _service.CreateReconciliationRecordAsync(
            Guid.NewGuid(),
            DateTime.UtcNow.AddDays(-7), DateTime.UtcNow,
            "Charging",
            100, 50000m,
            98, 49500m);

        // Assert
        result.DiffOrderCount.Should().Be(2);
        result.DiffAmount.Should().Be(500m);
        result.Status.Should().Be((int)ReconciliationStatus.Diff);
    }

    [Fact]
    public async Task CreateReconciliationRecordAsync_NoThirdParty_MatchesByDefault()
    {
        // Arrange & Act - 不传第三方数据时使用系统数据做差异比较
        var result = await _service.CreateReconciliationRecordAsync(
            Guid.NewGuid(),
            DateTime.UtcNow.AddDays(-7), DateTime.UtcNow,
            "Charging",
            100, 50000m);

        // Assert - null 默认取 systemOrderCount/systemTotalAmount → diff=0
        result.DiffOrderCount.Should().Be(0);
        result.DiffAmount.Should().Be(0);
        result.Status.Should().Be((int)ReconciliationStatus.Success);
    }

    #endregion

    #region 统计

    [Fact]
    public async Task GetMerchantSettlementStatsAsync_DelegatesToRepo()
    {
        // Arrange
        var merchantId = Guid.NewGuid();
        _orderRepo.Setup(r => r.GetMerchantStatsAsync(merchantId, null, null))
            .ReturnsAsync((100, 500000m, 20, 60));

        // Act
        var (totalOrders, totalAmount, pendingCount, paidCount) =
            await _service.GetMerchantSettlementStatsAsync(merchantId);

        // Assert
        totalOrders.Should().Be(100);
        totalAmount.Should().Be(500000m);
        pendingCount.Should().Be(20);
        paidCount.Should().Be(60);
    }

    #endregion
}
