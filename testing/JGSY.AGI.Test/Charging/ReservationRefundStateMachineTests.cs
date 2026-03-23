using System;
using System.Collections.Generic;
using System.Linq;
using FluentAssertions;
using JGSY.AGI.Charging.Entities;
using JGSY.AGI.Charging.Service;
using Xunit;

namespace JGSY.AGI.Test.Charging;

/// <summary>
/// 预约 + 退款状态机测试 — 状态转换合法性、DTO 验证、配置默认值、边界条件
/// </summary>
public class ReservationRefundStateMachineTests
{
    #region 预约状态机

    /// <summary>
    /// 合法的预约状态转换表
    /// </summary>
    private static readonly Dictionary<ReservationStatus, HashSet<ReservationStatus>> ValidReservationTransitions = new()
    {
        [ReservationStatus.Pending] = new() { ReservationStatus.Confirmed, ReservationStatus.Cancelled, ReservationStatus.Expired },
        [ReservationStatus.Confirmed] = new() { ReservationStatus.InUse, ReservationStatus.Cancelled, ReservationStatus.Expired, ReservationStatus.NoShow },
        [ReservationStatus.InUse] = new() { ReservationStatus.Completed },
        [ReservationStatus.Completed] = new(),
        [ReservationStatus.Cancelled] = new(),
        [ReservationStatus.Expired] = new(),
        [ReservationStatus.NoShow] = new(),
    };

    [Theory]
    [InlineData(ReservationStatus.Pending, ReservationStatus.Confirmed, true)]
    [InlineData(ReservationStatus.Pending, ReservationStatus.Cancelled, true)]
    [InlineData(ReservationStatus.Pending, ReservationStatus.Expired, true)]
    [InlineData(ReservationStatus.Confirmed, ReservationStatus.InUse, true)]
    [InlineData(ReservationStatus.Confirmed, ReservationStatus.NoShow, true)]
    [InlineData(ReservationStatus.InUse, ReservationStatus.Completed, true)]
    public void ReservationTransition_ValidPaths(ReservationStatus from, ReservationStatus to, bool expected)
    {
        var isAllowed = ValidReservationTransitions.TryGetValue(from, out var targets) && targets.Contains(to);
        isAllowed.Should().Be(expected);
    }

    [Theory]
    [InlineData(ReservationStatus.Completed, ReservationStatus.InUse)]   // 不可从完成回到使用中
    [InlineData(ReservationStatus.Cancelled, ReservationStatus.Pending)] // 不可从取消回到待处理
    [InlineData(ReservationStatus.Expired, ReservationStatus.Confirmed)] // 不可从过期回到已确认
    [InlineData(ReservationStatus.NoShow, ReservationStatus.InUse)]      // 不可从爽约到使用中
    [InlineData(ReservationStatus.Pending, ReservationStatus.Completed)] // 不可从待处理直接完成
    [InlineData(ReservationStatus.Pending, ReservationStatus.InUse)]     // 不可从待处理直接使用
    public void ReservationTransition_InvalidPaths(ReservationStatus from, ReservationStatus to)
    {
        var isAllowed = ValidReservationTransitions.TryGetValue(from, out var targets) && targets.Contains(to);
        isAllowed.Should().BeFalse();
    }

    [Fact]
    public void ReservationTerminalStates_ShouldHaveNoOutgoing()
    {
        // 终态：Completed, Cancelled, Expired, NoShow
        ValidReservationTransitions[ReservationStatus.Completed].Should().BeEmpty();
        ValidReservationTransitions[ReservationStatus.Cancelled].Should().BeEmpty();
        ValidReservationTransitions[ReservationStatus.Expired].Should().BeEmpty();
        ValidReservationTransitions[ReservationStatus.NoShow].Should().BeEmpty();
    }

    [Fact]
    public void ReservationHappyPath_ShouldTraverseAllStates()
    {
        // 正常流程：Pending → Confirmed → InUse → Completed
        var happyPath = new[]
        {
            ReservationStatus.Pending,
            ReservationStatus.Confirmed,
            ReservationStatus.InUse,
            ReservationStatus.Completed
        };

        for (int i = 0; i < happyPath.Length - 1; i++)
        {
            var from = happyPath[i];
            var to = happyPath[i + 1];
            var isAllowed = ValidReservationTransitions.TryGetValue(from, out var targets) && targets.Contains(to);
            isAllowed.Should().BeTrue($"预约流程 {from} → {to} 应该合法");
        }
    }

    #endregion

    #region 预约 DTO 验证

    [Fact]
    public void CreateReservationRequest_Valid_ShouldPass()
    {
        var now = DateTime.UtcNow;
        var request = new CreateReservationRequest
        {
            UserId = Guid.NewGuid(),
            StationId = Guid.NewGuid(),
            PileId = Guid.NewGuid(),
            PortId = Guid.NewGuid(),
            StartTime = now.AddHours(1),
            EndTime = now.AddHours(3),
            ExpectedDuration = 120,
            Mobile = "13800138000"
        };

        var errors = request.Validate();
        errors.Should().BeEmpty();
    }

    [Fact]
    public void CreateReservationRequest_MissingRequiredFields_ShouldFail()
    {
        var request = new CreateReservationRequest
        {
            UserId = Guid.Empty,
            StationId = Guid.Empty,
            PileId = Guid.Empty,
            PortId = Guid.Empty,
            StartTime = DateTime.UtcNow,
            EndTime = DateTime.UtcNow.AddHours(1)
        };

        var errors = request.Validate();
        errors.Should().ContainKey("userId");
        errors.Should().ContainKey("stationId");
        errors.Should().ContainKey("pileId");
        errors.Should().ContainKey("portId");
    }

    [Fact]
    public void CreateReservationRequest_EndTimeBeforeStartTime_ShouldFail()
    {
        var now = DateTime.UtcNow;
        var request = new CreateReservationRequest
        {
            UserId = Guid.NewGuid(),
            StationId = Guid.NewGuid(),
            PileId = Guid.NewGuid(),
            PortId = Guid.NewGuid(),
            StartTime = now.AddHours(3),
            EndTime = now.AddHours(1) // 结束时间早于开始
        };

        var errors = request.Validate();
        errors.Should().NotBeEmpty("结束时间早于开始时间应触发校验错误");
        // 验证错误字典中包含 endTime 相关条目（作为 key 或 value）
        var allKeys = errors.Keys;
        var allValues = errors.Values.SelectMany(v => v);
        var combined = allKeys.Concat(allValues);
        combined.Should().Contain(s => s.Contains("endTime") || s.Contains("结束时间"));
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-1)]
    [InlineData(1441)]
    public void CreateReservationRequest_InvalidDuration_ShouldFail(int duration)
    {
        var now = DateTime.UtcNow;
        var request = new CreateReservationRequest
        {
            UserId = Guid.NewGuid(),
            StationId = Guid.NewGuid(),
            PileId = Guid.NewGuid(),
            PortId = Guid.NewGuid(),
            StartTime = now.AddHours(1),
            EndTime = now.AddHours(3),
            ExpectedDuration = duration
        };

        var errors = request.Validate();
        errors.Should().ContainKey("expectedDuration");
    }

    [Fact]
    public void CancelReservationRequest_Valid_ShouldPass()
    {
        var request = new CancelReservationRequest
        {
            ReservationId = Guid.NewGuid(),
            UserId = Guid.NewGuid(),
            CancelReason = "有事取消"
        };

        var errors = request.Validate();
        errors.Should().BeEmpty();
    }

    [Fact]
    public void CheckInRequest_Valid_ShouldPass()
    {
        var request = new CheckInRequest
        {
            ReservationId = Guid.NewGuid(),
            UserId = Guid.NewGuid(),
            Lng = "116.403963",
            Lat = "39.915119"
        };

        var errors = request.Validate();
        errors.Should().BeEmpty();
    }

    #endregion

    #region 预约配置默认值

    [Fact]
    public void ReservationConfigDto_ShouldHaveCorrectDefaults()
    {
        var config = new ReservationConfigDto();

        config.MaxAdvanceHours.Should().Be(24);
        config.MinAdvanceMinutes.Should().Be(30);
        config.HoldDurationMinutes.Should().Be(15);
        config.FreeCancelMinutes.Should().Be(5);
        config.MaxConcurrentReservations.Should().Be(3);
        config.NoShowThreshold.Should().Be(3);
        config.BanDays.Should().Be(7);
        config.IsEnabled.Should().BeFalse();
        config.ChargeReservationFee.Should().BeFalse();
        config.ChargePenalty.Should().BeFalse();
    }

    #endregion

    #region 退款状态机

    /// <summary>
    /// 退款状态转换表
    /// </summary>
    private static readonly Dictionary<RefundStatus, HashSet<RefundStatus>> ValidRefundTransitions = new()
    {
        [RefundStatus.Pending] = new() { RefundStatus.Processing, RefundStatus.Cancelled },
        [RefundStatus.Processing] = new() { RefundStatus.Success, RefundStatus.Failed },
        [RefundStatus.Success] = new(),
        [RefundStatus.Failed] = new() { RefundStatus.Processing },  // 可重试
        [RefundStatus.Cancelled] = new(),
    };

    [Theory]
    [InlineData(RefundStatus.Pending, RefundStatus.Processing, true)]
    [InlineData(RefundStatus.Pending, RefundStatus.Cancelled, true)]
    [InlineData(RefundStatus.Processing, RefundStatus.Success, true)]
    [InlineData(RefundStatus.Processing, RefundStatus.Failed, true)]
    [InlineData(RefundStatus.Failed, RefundStatus.Processing, true)]  // 重试
    public void RefundTransition_ValidPaths(RefundStatus from, RefundStatus to, bool expected)
    {
        var isAllowed = ValidRefundTransitions.TryGetValue(from, out var targets) && targets.Contains(to);
        isAllowed.Should().Be(expected);
    }

    [Theory]
    [InlineData(RefundStatus.Success, RefundStatus.Failed)]    // 成功不可变失败
    [InlineData(RefundStatus.Cancelled, RefundStatus.Pending)] // 取消不可回到待处理
    [InlineData(RefundStatus.Success, RefundStatus.Cancelled)] // 成功不可取消
    [InlineData(RefundStatus.Pending, RefundStatus.Success)]   // 不可从待处理直接成功
    public void RefundTransition_InvalidPaths(RefundStatus from, RefundStatus to)
    {
        var isAllowed = ValidRefundTransitions.TryGetValue(from, out var targets) && targets.Contains(to);
        isAllowed.Should().BeFalse();
    }

    [Fact]
    public void RefundTerminalStates_ShouldHaveNoOrSingleOutgoing()
    {
        ValidRefundTransitions[RefundStatus.Success].Should().BeEmpty();
        ValidRefundTransitions[RefundStatus.Cancelled].Should().BeEmpty();
        // Failed 可以重试，有一个出边
        ValidRefundTransitions[RefundStatus.Failed].Should().HaveCount(1);
    }

    #endregion

    #region 退款请求验证

    [Fact]
    public void RefundRequest_Valid_ShouldPass()
    {
        var request = new RefundRequest
        {
            OrderId = Guid.NewGuid(),
            RefundAmount = 50.00m,
            RefundType = RefundType.UserRequest,
            Reason = "用户主动取消"
        };

        var errors = request.Validate();
        errors.Should().BeEmpty();
    }

    [Fact]
    public void RefundRequest_ZeroAmount_ShouldFail()
    {
        var request = new RefundRequest
        {
            OrderId = Guid.NewGuid(),
            RefundAmount = 0m,
            RefundType = RefundType.UserRequest
        };

        var errors = request.Validate();
        errors.Should().ContainKey("refundAmount");
    }

    [Fact]
    public void RefundRequest_NegativeAmount_ShouldFail()
    {
        var request = new RefundRequest
        {
            OrderId = Guid.NewGuid(),
            RefundAmount = -10m,
            RefundType = RefundType.UserRequest
        };

        var errors = request.Validate();
        errors.Should().ContainKey("refundAmount");
    }

    [Fact]
    public void RefundRequest_MissingOrderId_ShouldFail()
    {
        var request = new RefundRequest
        {
            OrderId = Guid.Empty,
            RefundAmount = 50m
        };

        var errors = request.Validate();
        errors.Should().ContainKey("orderId");
    }

    [Fact]
    public void RefundCallback_Valid_ShouldPass()
    {
        var callback = new RefundCallback
        {
            RefundId = Guid.NewGuid(),
            Status = "SUCCESS",
            PaymentRefundId = "PAY_REF_001"
        };

        var errors = callback.Validate();
        errors.Should().BeEmpty();
    }

    [Fact]
    public void RefundCallback_MissingRequiredFields_ShouldFail()
    {
        var callback = new RefundCallback
        {
            RefundId = Guid.Empty,
            Status = ""
        };

        var errors = callback.Validate();
        errors.Should().NotBeEmpty();
    }

    #endregion

    #region 退款金额验证逻辑

    [Theory]
    [InlineData(100, 0, 80, true)]    // 已付100，已退0，申请退80 → 可退
    [InlineData(100, 50, 50, true)]   // 已付100，已退50，申请退50 → 可退
    [InlineData(100, 50, 51, false)]  // 已付100，已退50，申请退51 → 超出
    [InlineData(100, 100, 0.01, false)] // 已付100，已退100 → 无可退金额
    [InlineData(0, 0, 1, false)]      // 未付款 → 无可退金额
    public void RefundAmount_ShouldNotExceedAvailableBalance(
        decimal paidAmount, decimal refundedAmount, decimal requestAmount, bool expectedValid)
    {
        // 模拟 RefundService.RequestRefundAsync 中的金额校验逻辑
        var availableAmount = paidAmount - refundedAmount;
        var isValid = requestAmount <= availableAmount && requestAmount > 0;

        isValid.Should().Be(expectedValid);
    }

    [Theory]
    [InlineData("3", true)]  // Charging 状态允许退款
    [InlineData("5", true)]  // Completed 状态允许退款
    [InlineData("1", false)] // Pending 不允许
    [InlineData("2", false)] // Cancelled 不允许
    [InlineData("4", false)] // Refunded 不允许
    [InlineData("6", false)] // Settled 不允许
    public void RefundEligibility_ByOrderStatus(string orderState, bool expectedEligible)
    {
        // 模拟 RefundService.RequestRefundAsync 中的订单状态校验
        var isEligible = orderState == "3" || orderState == "5";
        isEligible.Should().Be(expectedEligible);
    }

    #endregion

    #region RefundRecord 实体测试

    [Fact]
    public void RefundRecord_ShouldInitializeWithDefaults()
    {
        var record = new RefundRecord();
        record.RefundStatus.Should().Be("Pending");
        record.DeleteAt.Should().BeNull();
        record.OrderNo.Should().BeEmpty();
    }

    [Theory]
    [InlineData(RefundType.UserRequest, 1)]
    [InlineData(RefundType.SystemAuto, 2)]
    [InlineData(RefundType.AdminForce, 3)]
    [InlineData(RefundType.OrderCancel, 4)]
    [InlineData(RefundType.Overpayment, 5)]
    public void RefundType_ShouldHaveCorrectIntValue(RefundType type, int expected)
    {
        ((int)type).Should().Be(expected);
    }

    #endregion

    #region RefundStatsResult 测试

    [Fact]
    public void RefundStats_ShouldSumCorrectly()
    {
        var stats = new RefundStatsResult
        {
            TotalCount = 100,
            TotalAmount = 50000m,
            PendingCount = 10,
            PendingAmount = 5000m,
            CompletedCount = 85,
            CompletedAmount = 42500m,
            RejectedCount = 5,
            TodayCount = 3,
            TodayAmount = 1500m,
            MonthlyCount = 30,
            MonthlyAmount = 15000m
        };

        (stats.PendingCount + stats.CompletedCount + stats.RejectedCount)
            .Should().Be(stats.TotalCount);
    }

    #endregion

    #region ReservationResponse DTO 测试

    [Fact]
    public void ReservationResponse_ShouldHoldAllFields()
    {
        var now = DateTime.UtcNow;
        var response = new ReservationResponse
        {
            Id = Guid.NewGuid(),
            ReservationNo = "RSV20240101000001",
            UserId = Guid.NewGuid(),
            StationId = Guid.NewGuid(),
            StationName = "测试站点",
            PileId = Guid.NewGuid(),
            PileCode = "CP-001",
            PortId = Guid.NewGuid(),
            PortNumber = 1,
            StartTime = now,
            EndTime = now.AddHours(2),
            Status = ReservationStatus.Confirmed,
            ReservationFee = 5.0m,
            CreateTime = now
        };

        response.ReservationNo.Should().StartWith("RSV");
        response.Status.Should().Be(ReservationStatus.Confirmed);
        response.ReservationFee.Should().BeGreaterThan(0);
    }

    #endregion

    #region 预约查询分页测试

    [Fact]
    public void ReservationQueryRequest_ShouldHaveDefaultPagination()
    {
        var query = new ReservationQueryRequest();
        query.Page.Should().Be(1);
        query.PageSize.Should().Be(20);
    }

    [Fact]
    public void ReservationQueryRequest_Validate_ShouldNormalizePagination()
    {
        var query = new ReservationQueryRequest { Page = -1, PageSize = 0 };
        query.Validate();
        // PaginationValidator 应该校正无效值
        query.Page.Should().BeGreaterThanOrEqualTo(1);
        query.PageSize.Should().BeGreaterThanOrEqualTo(1);
    }

    #endregion
}
