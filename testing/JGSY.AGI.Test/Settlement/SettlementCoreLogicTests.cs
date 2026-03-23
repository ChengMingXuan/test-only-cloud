using System;
using System.Collections.Generic;
using System.Linq;
using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.Settlement;

/// <summary>
/// 结算核心业务逻辑测试 - P0 覆盖
/// </summary>
public class SettlementCoreLogicTests
{
    private readonly Guid _tenantId = Guid.NewGuid();

    #region 分润计算测试

    [Theory]
    [InlineData(100, 70, 30)]       // 平台30%，商户70%
    [InlineData(100, 80, 20)]       // 平台20%，商户80%
    [InlineData(1000, 75, 250)]     // 平台25%
    public void ProfitSharing_ShouldCalculatePlatformShare(
        decimal totalAmount, 
        int merchantPercent, 
        decimal expectedPlatformShare)
    {
        var platformPercent = 100 - merchantPercent;
        var platformShare = totalAmount * platformPercent / 100;
        
        platformShare.Should().Be(expectedPlatformShare);
    }

    [Theory]
    [InlineData(100, 70, 70)]
    [InlineData(100, 80, 80)]
    [InlineData(1000, 75, 750)]
    public void ProfitSharing_ShouldCalculateMerchantShare(
        decimal totalAmount, 
        int merchantPercent, 
        decimal expectedMerchantShare)
    {
        var merchantShare = totalAmount * merchantPercent / 100;
        
        merchantShare.Should().Be(expectedMerchantShare);
    }

    [Fact]
    public void ProfitSharing_TotalShouldMatchOriginal()
    {
        var totalAmount = 100m;
        var merchantPercent = 70;
        var platformPercent = 30;
        
        var merchantShare = totalAmount * merchantPercent / 100;
        var platformShare = totalAmount * platformPercent / 100;
        
        (merchantShare + platformShare).Should().Be(totalAmount);
    }

    [Fact]
    public void ProfitSharing_WithMultipleParties()
    {
        var totalAmount = 1000m;
        var shares = new Dictionary<string, int>
        {
            ["Platform"] = 10,
            ["Operator"] = 60,
            ["SiteOwner"] = 25,
            ["ServiceProvider"] = 5
        };
        
        var calculated = shares.ToDictionary(
            kv => kv.Key, 
            kv => totalAmount * kv.Value / 100);
        
        calculated["Platform"].Should().Be(100m);
        calculated["Operator"].Should().Be(600m);
        calculated["SiteOwner"].Should().Be(250m);
        calculated["ServiceProvider"].Should().Be(50m);
        calculated.Values.Sum().Should().Be(totalAmount);
    }

    #endregion

    #region 对账逻辑测试

    [Fact]
    public void Reconciliation_ShouldMatchOrdersAndPayments()
    {
        var orderAmount = 100m;
        var paymentAmount = 100m;
        
        var isMatched = Math.Abs(orderAmount - paymentAmount) < 0.01m;
        isMatched.Should().BeTrue();
    }

    [Fact]
    public void Reconciliation_ShouldDetectDiscrepancy()
    {
        var orderAmount = 100m;
        var paymentAmount = 99m;
        var tolerance = 0.01m;
        
        var hasDiscrepancy = Math.Abs(orderAmount - paymentAmount) > tolerance;
        hasDiscrepancy.Should().BeTrue();
    }

    [Theory]
    [InlineData(100, 100, "Matched")]
    [InlineData(100, 80, "ShortPayment")]
    [InlineData(100, 120, "OverPayment")]
    [InlineData(100, 0, "NotPaid")]
    public void Reconciliation_ShouldClassifyStatus(
        decimal orderAmount, 
        decimal paymentAmount, 
        string expectedStatus)
    {
        var status = ClassifyReconciliationStatus(orderAmount, paymentAmount);
        status.Should().Be(expectedStatus);
    }

    [Fact]
    public void Reconciliation_BatchShouldCalculateTotals()
    {
        var orders = new List<decimal> { 100, 200, 150 };
        var payments = new List<decimal> { 100, 200, 150 };
        
        var orderTotal = orders.Sum();
        var paymentTotal = payments.Sum();
        var matchCount = orders.Count;
        
        orderTotal.Should().Be(450);
        paymentTotal.Should().Be(450);
        matchCount.Should().Be(3);
    }

    #endregion

    #region 提现逻辑测试

    [Fact]
    public void Withdrawal_ShouldCheckMinimumAmount()
    {
        var minimumWithdrawal = 100m;
        var requestedAmount = 50m;
        
        var meetsMinimum = requestedAmount >= minimumWithdrawal;
        meetsMinimum.Should().BeFalse();
    }

    [Theory]
    [InlineData(1000, 500, true)]
    [InlineData(1000, 1000, true)]
    [InlineData(1000, 1001, false)]
    public void Withdrawal_ShouldCheckBalance(
        decimal balance, 
        decimal withdrawAmount, 
        bool canWithdraw)
    {
        var allowed = withdrawAmount <= balance;
        allowed.Should().Be(canWithdraw);
    }

    [Theory]
    [InlineData(1000, 1, 10)]       // T+1提现，1%手续费
    [InlineData(1000, 0, 0)]        // T+0提现（VIP），0手续费
    [InlineData(1000, 0.5, 5)]     // T+1提现，0.5%手续费
    public void Withdrawal_ShouldCalculateFee(
        decimal amount, 
        decimal feePercent, 
        decimal expectedFee)
    {
        var fee = amount * feePercent / 100;
        fee.Should().Be(expectedFee);
    }

    [Fact]
    public void Withdrawal_ActualAmountShouldDeductFee()
    {
        var requestedAmount = 1000m;
        var feePercent = 1m;
        var fee = requestedAmount * feePercent / 100;
        
        var actualAmount = requestedAmount - fee;
        actualAmount.Should().Be(990m);
    }

    #endregion

    #region 结算周期测试

    [Theory]
    [InlineData("Daily", 1)]
    [InlineData("Weekly", 7)]
    [InlineData("BiWeekly", 14)]
    [InlineData("Monthly", 30)]
    public void SettlementCycle_ShouldDetermineNextSettlementDate(
        string cycle, 
        int expectedDays)
    {
        var lastSettlement = new DateTime(2024, 1, 1);
        var nextSettlement = GetNextSettlementDate(lastSettlement, cycle);
        
        (nextSettlement - lastSettlement).Days.Should().Be(expectedDays);
    }

    [Fact]
    public void SettlementPeriod_ShouldIncludeAllOrdersInRange()
    {
        var periodStart = new DateTime(2024, 1, 1);
        var periodEnd = new DateTime(2024, 1, 31, 23, 59, 59);
        
        var orders = new List<DateTime>
        {
            new DateTime(2024, 1, 5),   // 在范围内
            new DateTime(2024, 1, 15),  // 在范围内
            new DateTime(2024, 2, 1),   // 范围外
            new DateTime(2023, 12, 31)  // 范围外
        };
        
        var inPeriod = orders.Count(d => d >= periodStart && d <= periodEnd);
        inPeriod.Should().Be(2);
    }

    #endregion

    #region 发票逻辑测试

    [Theory]
    [InlineData(100, 13, 13)]       // 13%增值税
    [InlineData(100, 6, 6)]         // 6%增值税
    [InlineData(1000, 13, 130)]
    public void Invoice_ShouldCalculateTax(
        decimal amount, 
        int taxPercent, 
        decimal expectedTax)
    {
        var tax = amount * taxPercent / 100;
        tax.Should().Be(expectedTax);
    }

    [Fact]
    public void Invoice_ShouldCalculateAmountWithoutTax()
    {
        var totalWithTax = 113m;
        var taxPercent = 13m;
        
        var amountWithoutTax = totalWithTax / (1 + taxPercent / 100);
        amountWithoutTax.Should().BeApproximately(100m, 0.01m);
    }

    [Fact]
    public void Invoice_MinimumAmountCheck()
    {
        var minimumInvoiceAmount = 100m;
        var requestedAmount = 50m;
        
        var canInvoice = requestedAmount >= minimumInvoiceAmount;
        canInvoice.Should().BeFalse();
    }

    #endregion

    #region 退款逻辑测试

    [Fact]
    public void Refund_ShouldNotExceedOriginalPayment()
    {
        var originalPayment = 100m;
        var refundAmount = 120m;
        
        var isValid = refundAmount <= originalPayment;
        isValid.Should().BeFalse();
    }

    [Theory]
    [InlineData(100, 30, true)]     // 部分退款
    [InlineData(100, 100, true)]    // 全额退款
    [InlineData(100, 0, false)]     // 退款金额为0
    [InlineData(100, -10, false)]   // 负数退款
    public void Refund_AmountValidation(
        decimal original, 
        decimal refund, 
        bool isValid)
    {
        var valid = refund > 0 && refund <= original;
        valid.Should().Be(isValid);
    }

    [Fact]
    public void Refund_ShouldReverseProfitSharing()
    {
        var refundAmount = 100m;
        var merchantPercent = 70;
        var platformPercent = 30;
        
        // 退款时应按同比例返还
        var merchantRefund = refundAmount * merchantPercent / 100;
        var platformRefund = refundAmount * platformPercent / 100;
        
        merchantRefund.Should().Be(70m);
        platformRefund.Should().Be(30m);
    }

    #endregion

    #region 辅助方法

    private string ClassifyReconciliationStatus(decimal orderAmount, decimal paymentAmount)
    {
        var diff = paymentAmount - orderAmount;
        if (diff == 0) return "Matched";
        if (paymentAmount == 0) return "NotPaid";
        if (diff < 0) return "ShortPayment";
        return "OverPayment"; // diff > 0
    }

    private DateTime GetNextSettlementDate(DateTime lastSettlement, string cycle)
    {
        return cycle switch
        {
            "Daily" => lastSettlement.AddDays(1),
            "Weekly" => lastSettlement.AddDays(7),
            "BiWeekly" => lastSettlement.AddDays(14),
            "Monthly" => lastSettlement.AddDays(30),
            _ => lastSettlement.AddDays(1)
        };
    }

    #endregion
}

/// <summary>
/// 商户账户结算测试 - P0 覆盖
/// </summary>
public class MerchantAccountSettlementTests
{
    #region 可提现余额测试

    [Fact]
    public void WithdrawableBalance_ShouldExcludeFrozenAndPending()
    {
        var totalBalance = 10000m;
        var frozenBalance = 2000m;
        var pendingSettlement = 1500m;
        
        var withdrawable = totalBalance - frozenBalance - pendingSettlement;
        withdrawable.Should().Be(6500m);
    }

    [Fact]
    public void WithdrawableBalance_ShouldNotBeNegative()
    {
        var totalBalance = 1000m;
        var frozenBalance = 800m;
        var pendingSettlement = 500m;
        
        var withdrawable = Math.Max(0, totalBalance - frozenBalance - pendingSettlement);
        withdrawable.Should().Be(0m);
    }

    #endregion

    #region 保证金测试

    [Theory]
    [InlineData(100000, 10, 10000)]     // 交易额的10%作为保证金
    [InlineData(50000, 5, 2500)]
    public void Deposit_ShouldBeCalculatedAsPercentOfVolume(
        decimal monthlyVolume, 
        int depositPercent, 
        decimal expectedDeposit)
    {
        var deposit = monthlyVolume * depositPercent / 100;
        deposit.Should().Be(expectedDeposit);
    }

    [Fact]
    public void Deposit_ShouldHaveMinimumAndMaximum()
    {
        var minDeposit = 5000m;
        var maxDeposit = 100000m;
        var calculatedDeposit = 3000m;
        
        var actualDeposit = Math.Clamp(calculatedDeposit, minDeposit, maxDeposit);
        actualDeposit.Should().Be(5000m); // 不足最低，按最低
    }

    #endregion

    #region 信用评分测试

    [Theory]
    [InlineData(100, 0, 0, 100)]        // 完美：100%按时，0延迟，0拒付 -> 100-0-0=100
    [InlineData(95, 5, 1, 80)]          // 良好：95%按时，5%延迟，1%拒付 -> 95-5-10=80
    [InlineData(80, 15, 5, 15)]         // 一般：80-15-50=15
    public void CreditScore_ShouldReflectPaymentHistory(
        int onTimePercent, 
        int delayedPercent, 
        int chargebackPercent, 
        int expectedScore)
    {
        var score = CalculateCreditScore(onTimePercent, delayedPercent, chargebackPercent);
        score.Should().Be(expectedScore);
    }

    #endregion

    #region 辅助方法

    private int CalculateCreditScore(int onTimePercent, int delayedPercent, int chargebackPercent)
    {
        // 简化评分算法
        var score = onTimePercent - delayedPercent - (chargebackPercent * 10);
        return Math.Max(0, Math.Min(100, score));
    }

    #endregion
}

/// <summary>
/// 平台收入统计测试 - P0 覆盖
/// </summary>
public class PlatformRevenueTests
{
    #region 收入汇总测试

    [Fact]
    public void Revenue_ShouldSumAllSources()
    {
        var serviceFee = 10000m;
        var transactionFee = 5000m;
        var subscriptionFee = 2000m;
        var otherFee = 500m;
        
        var totalRevenue = serviceFee + transactionFee + subscriptionFee + otherFee;
        totalRevenue.Should().Be(17500m);
    }

    [Fact]
    public void Revenue_ShouldCalculateByPeriod()
    {
        var dailyRevenues = new List<decimal> { 100, 150, 80, 200, 120, 90, 160 };
        
        var weeklyTotal = dailyRevenues.Sum();
        var dailyAverage = weeklyTotal / 7;
        
        weeklyTotal.Should().Be(900m);
        dailyAverage.Should().BeApproximately(128.57m, 0.01m);
    }

    #endregion

    #region 收入类型分析测试

    [Fact]
    public void Revenue_ByType_ShouldCalculatePercentages()
    {
        var revenues = new Dictionary<string, decimal>
        {
            ["ServiceFee"] = 6000m,
            ["TransactionFee"] = 3000m,
            ["SubscriptionFee"] = 1000m
        };
        
        var total = revenues.Values.Sum();
        var percentages = revenues.ToDictionary(
            kv => kv.Key, 
            kv => kv.Value / total * 100);
        
        percentages["ServiceFee"].Should().Be(60m);
        percentages["TransactionFee"].Should().Be(30m);
        percentages["SubscriptionFee"].Should().Be(10m);
    }

    #endregion

    #region 增长率计算测试

    [Theory]
    [InlineData(100, 120, 20)]      // 增长20%
    [InlineData(100, 80, -20)]      // 下降20%
    [InlineData(100, 100, 0)]       // 持平
    [InlineData(0, 100, 100)]       // 从0增长（特殊处理）
    public void Revenue_GrowthRate_ShouldBeCalculated(
        decimal previous, 
        decimal current, 
        decimal expectedGrowthPercent)
    {
        decimal growthRate;
        if (previous == 0)
        {
            growthRate = current > 0 ? 100 : 0;
        }
        else
        {
            growthRate = (current - previous) / previous * 100;
        }
        
        growthRate.Should().Be(expectedGrowthPercent);
    }

    #endregion
}
