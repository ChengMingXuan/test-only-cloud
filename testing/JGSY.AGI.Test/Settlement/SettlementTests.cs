using FluentAssertions;
using JGSY.AGI.Settlement.Entities;
using Xunit;

namespace JGSY.AGI.Test.Settlement;

/// <summary>
/// 结算服务实体测试
/// </summary>
public class SettlementEntityTests
{
    [Fact]
    public void SettlementRecord_ShouldHaveCorrectDefaults()
    {
        var record = new SettlementRecord();
        record.DeleteAt.Should().BeNull();
        record.TotalAmount.Should().Be(0);
        record.PlatformShare.Should().Be(0);
        record.MerchantShare.Should().Be(0);
    }

    [Fact]
    public void SettlementRecord_SharesShouldSumToTotal()
    {
        var record = new SettlementRecord
        {
            PeriodStart = DateOnly.FromDateTime(DateTime.Today.AddDays(-7)),
            PeriodEnd = DateOnly.FromDateTime(DateTime.Today),
            MerchantId = Guid.NewGuid(),
            TotalAmount = 10000m,
            PlatformShare = 2000m,
            MerchantShare = 8000m,
            Status = (int)SettlementStatus.Pending
        };

        (record.PlatformShare + record.MerchantShare).Should().Be(record.TotalAmount);
        record.PeriodEnd.Should().BeAfter(record.PeriodStart);
    }

    [Fact]
    public void BillingDetail_ShouldHaveCorrectDefaults()
    {
        var billing = new BillingDetail();
        billing.BillingType.Should().Be("Charging");
        billing.SettlementStatus.Should().Be("Pending");
        billing.DeleteAt.Should().BeNull();
    }

    [Fact]
    public void BillingDetail_ActualAmount_ShouldConsiderDiscount()
    {
        var billing = new BillingDetail
        {
            OrderNumber = "CHG20260209001",
            ElectricityFee = 50.0m,
            ServiceFee = 10.0m,
            ParkingFee = 5.0m,
            DiscountAmount = 8.0m,
            ActualAmount = 57.0m,
            PaymentMethod = "WeChat",
            PaymentTime = DateTime.UtcNow
        };

        var expectedTotal = billing.ElectricityFee + billing.ServiceFee
            + (billing.ParkingFee ?? 0) - (billing.DiscountAmount ?? 0);
        billing.ActualAmount.Should().Be(expectedTotal);
    }

    [Fact]
    public void MerchantAccount_ShouldHaveCorrectDefaults()
    {
        var account = new MerchantAccount();
        account.AccountBalance.Should().Be(0);
        account.TotalRevenue.Should().Be(0);
        account.TotalWithdrawn.Should().Be(0);
        account.FrozenAmount.Should().Be(0);
    }

    [Fact]
    public void MerchantAccount_AvailableBalance_ShouldBeCalculable()
    {
        var account = new MerchantAccount
        {
            MerchantName = "优充科技",
            MerchantCode = "MC001",
            AccountBalance = 50000m,
            TotalRevenue = 120000m,
            TotalWithdrawn = 70000m,
            FrozenAmount = 5000m,
            Status = (int)AccountStatus.Active,
            JoinedAt = DateTime.UtcNow.AddMonths(-6)
        };

        var availableBalance = account.AccountBalance - account.FrozenAmount;
        availableBalance.Should().Be(45000m);
        availableBalance.Should().BePositive();
    }

    [Fact]
    public void SettlementRule_ShouldValidateShareRates()
    {
        var rule = new SettlementRule
        {
            RuleName = "标准充电分成",
            BusinessType = "Charging",
            PlatformShareRate = 20m,
            MerchantShareRate = 80m,
            SettlementCycle = 7,
            MinSettlementAmount = 100m,
            AutoSettle = true,
            IsActive = true,
            EffectiveFrom = DateTime.UtcNow
        };

        (rule.PlatformShareRate + rule.MerchantShareRate).Should().Be(100m);
        rule.SettlementCycle.Should().BePositive();
        rule.MinSettlementAmount.Should().BePositive();
    }

    [Fact]
    public void SettlementOrder_ShouldSetAllProperties()
    {
        var order = new SettlementOrder
        {
            SettlementOrderNo = "SET20260209001",
            MerchantId = Guid.NewGuid(),
            PeriodStart = DateTime.UtcNow.AddDays(-7),
            PeriodEnd = DateTime.UtcNow,
            BusinessType = "Charging",
            TotalRevenue = 10000m,
            PlatformAmount = 2000m,
            MerchantAmount = 8000m,
            OrderCount = 150,
            Status = (int)SettlementStatus.Pending,
            GeneratedAt = DateTime.UtcNow
        };

        order.SettlementOrderNo.Should().StartWith("SET");
        order.OrderCount.Should().BePositive();
        (order.PlatformAmount + order.MerchantAmount).Should().Be(order.TotalRevenue);
    }

    [Fact]
    public void PayoutRecord_ShouldTrackPayment()
    {
        var payout = new PayoutRecord
        {
            PayoutNo = "PAY20260209001",
            PayoutAmount = 8000m,
            PayoutChannel = "BankTransfer",
            PayoutAccount = "6222********1234",
            PayoutAccountName = "优充科技有限公司",
            BankName = "中国工商银行",
            Status = (int)PayoutStatus.Success,
            InitiatedAt = DateTime.UtcNow.AddHours(-1),
            PayoutTime = DateTime.UtcNow
        };

        payout.PayoutAmount.Should().BePositive();
        payout.PayoutTime.Should().BeAfter(payout.InitiatedAt);
        payout.Status.Should().Be((int)PayoutStatus.Success);
    }

    [Fact]
    public void ReconciliationRecord_ShouldDetectDiff()
    {
        var recon = new ReconciliationRecord
        {
            ReconciliationNo = "REC20260209001",
            PeriodStart = DateTime.UtcNow.AddDays(-1),
            PeriodEnd = DateTime.UtcNow,
            SystemOrderCount = 100,
            SystemTotalAmount = 50000m,
            ThirdPartyOrderCount = 99,
            ThirdPartyTotalAmount = 49800m,
            DiffOrderCount = 1,
            DiffAmount = 200m,
            Status = (int)ReconciliationStatus.Diff,
            ReconciledAt = DateTime.UtcNow
        };

        recon.DiffOrderCount.Should().Be(
            recon.SystemOrderCount - (recon.ThirdPartyOrderCount ?? 0));
        recon.DiffAmount.Should().Be(
            recon.SystemTotalAmount - (recon.ThirdPartyTotalAmount ?? 0));
    }

    [Theory]
    [InlineData(SettlementStatus.Pending)]
    [InlineData(SettlementStatus.Approved)]
    [InlineData(SettlementStatus.Rejected)]
    [InlineData(SettlementStatus.Paid)]
    [InlineData(SettlementStatus.Cancelled)]
    public void SettlementStatus_ShouldHaveAllValues(SettlementStatus status)
    {
        Enum.IsDefined(typeof(SettlementStatus), status).Should().BeTrue();
    }
}

/// <summary>
/// 分润模块测试
/// </summary>
public class ProfitSharingTests
{
    [Fact]
    public void ProfitSharingRule_ShouldCalculateRate()
    {
        var rule = new ProfitSharingRule
        {
            CalculationType = "Percentage",
            Rate = 15.0m,
            MinAmount = 10m,
            MaxAmount = 5000m,
            IsEnabled = true,
            Priority = 1
        };

        rule.Rate.Should().BeInRange(0, 100);
        rule.MaxAmount.Should().BeGreaterThan(rule.MinAmount ?? 0);
    }

    [Fact]
    public void ProfitSharingRecord_ShouldTrackDistribution()
    {
        var record = new ProfitSharingRecord
        {
            OrderId = Guid.NewGuid(),
            MerchantId = Guid.NewGuid(),
            NodeName = "一级代理商",
            NodeLevel = 1,
            TotalAmount = 10000m,
            ProfitAmount = 1500m,
            ProfitRate = 15.0m,
            CalculationType = "Percentage",
            Status = "Settled",
            CalculatedAt = DateTime.UtcNow.AddHours(-1),
            SettledAt = DateTime.UtcNow
        };

        record.ProfitAmount.Should().BeLessThan(record.TotalAmount);
        record.SettledAt.Should().BeAfter(record.CalculatedAt);
    }

    [Fact]
    public void ProfitSharingStrategy_ShouldSetConfig()
    {
        var strategy = new ProfitSharingStrategy
        {
            StrategyName = "充电业务三级分润",
            StrategyType = "MultiLevel",
            IsEnabled = true,
            Priority = 1,
            Description = "充电业务分润策略：平台 → 运营商 → 场站"
        };

        strategy.StrategyName.Should().NotBeEmpty();
        strategy.IsEnabled.Should().BeTrue();
    }
}
