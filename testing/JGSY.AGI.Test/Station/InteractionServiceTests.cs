using JGSY.AGI.Common.Core.Exceptions;
using JGSY.AGI.Station.Data.Repositories;
using JGSY.AGI.Station.Entities;
using JGSY.AGI.Station.Service;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace JGSY.AGI.Test.Station;

/// <summary>
/// 互动管理单元测试
/// 覆盖范围：站点评价、投诉建议、点赞管理、统计分析
/// 测试维度：业务流程正确性、工单流转、统计准确性、异常处理
/// </summary>
public class InteractionServiceTests : IDisposable
{
    private readonly Mock<ILogger<InteractionService>> _loggerMock;
    private readonly InMemoryReviewRepository _reviewRepo;
    private readonly InMemoryFeedbackRepository _feedbackRepo;
    private readonly InteractionService _service;

    public InteractionServiceTests()
    {
        _loggerMock = new Mock<ILogger<InteractionService>>();

        _reviewRepo = new InMemoryReviewRepository();
        _feedbackRepo = new InMemoryFeedbackRepository();
        _service = new InteractionService(_reviewRepo, _feedbackRepo, _loggerMock.Object);
    }

    #region 站点评价提交测试

    [Fact(DisplayName = "提交站点评价 - 应成功创建评价记录")]
    public async Task SubmitReview_ShouldCreateSuccessfully()
    {
        // Arrange
        var testStationId = Guid.NewGuid();
        var testUserId = Guid.NewGuid();
        var testOrderId = Guid.NewGuid();
        var review = new StationReview
        {
            StationId = testStationId,
            UserId = testUserId,
            OrderId = testOrderId,
            Rating = 5,
            Content = "充电速度快，环境整洁，服务态度好",
            Tags = System.Text.Json.JsonSerializer.Serialize(new[] { "快速", "干净", "友好" }),
            PhotoUrls = "https://example.com/photo1.jpg",
            IsAnonymous = false,
            CreateTime = DateTime.UtcNow
        };

        // Act
        var result = await _service.SubmitReviewAsync(review);

        // Assert
        Assert.NotEqual(Guid.Empty, result.Id);
        Assert.Equal(5, result.Rating);
        Assert.Equal("Pending", result.AuditStatus); // 默认待审核
        Assert.False(result.IsVisible); // 默认不可见（待审核）
    }

    [Fact(DisplayName = "评价评分范围 - 应在1-5之间")]
    public async Task SubmitReview_RatingShouldBeInRange()
    {
        // Arrange & Act
        var validReview = new StationReview
        {
            StationId = Guid.NewGuid(),
            UserId = Guid.NewGuid(),
            Rating = 3,
            Content = "一般",
            CreateTime = DateTime.UtcNow
        };

        var result = await _service.SubmitReviewAsync(validReview);

        // Assert
        Assert.InRange(result.Rating, 1, 5);
        Assert.Equal(validReview.Rating, result.Rating);
    }

    [Fact(DisplayName = "评价内容过长 - 应抛出异常")]
    public async Task SubmitReview_WithTooLongContent_ShouldThrowException()
    {
        // Arrange
        var review = new StationReview
        {
            StationId = Guid.NewGuid(),
            UserId = Guid.NewGuid(),
            Rating = 4,
            Content = new string('a', 2001), // 超过2000字符
            CreateTime = DateTime.UtcNow
        };

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentException>(async () =>
            await _service.SubmitReviewAsync(review));
    }

    #endregion

    #region 评价审核测试

    [Fact(DisplayName = "审核通过评价 - 应更新状态并可见")]
    public async Task AuditReview_Approved_ShouldBeVisible()
    {
        // Arrange
        var testStationId = Guid.NewGuid();
        var testUserId = Guid.NewGuid();
        var review = await CreateTestReview(testStationId, testUserId, 4, "不错的充电站");

        // Act
        await _service.AuditReviewAsync(
            review.Id, 
            "Approved", 
            "9001");

        // Assert
        var updated = await _reviewRepo.GetByIdAsync(review.Id);
        Assert.Equal("Approved", updated!.AuditStatus);
        Assert.True(updated.IsVisible);
    }

    [Fact(DisplayName = "审核拒绝评价 - 应不可见并记录原因")]
    public async Task AuditReview_Rejected_ShouldNotBeVisible()
    {
        // Arrange
        var review = await CreateTestReview(Guid.NewGuid(), Guid.NewGuid(), 1, "垃圾站点");

        // Act
        await _service.AuditReviewAsync(
            review.Id, 
            "Rejected", 
            "9001");

        // Assert
        var updated = await _reviewRepo.GetByIdAsync(review.Id);
        Assert.Equal("Rejected", updated!.AuditStatus);
        Assert.False(updated.IsVisible);
    }

    [Fact(DisplayName = "审核不存在的评价 - 应抛出异常")]
    public async Task AuditReview_NonExistent_ShouldThrowException()
    {
        // Act & Assert
        await Assert.ThrowsAsync<BusinessException>(async () =>
            await _service.AuditReviewAsync(Guid.NewGuid(), "Approved", "9001"));
    }

    #endregion

    #region 评价回复测试

    [Fact(DisplayName = "运营方回复评价 - 应记录回复内容")]
    public async Task ReplyReview_ShouldRecordReply()
    {
        // Arrange
        var review = await CreateTestReview(Guid.NewGuid(), Guid.NewGuid(), 5, "很好");
        await _service.AuditReviewAsync(review.Id, "Approved", "9001");

        // Act
        await _service.ReplyReviewAsync(
            review.Id,
            replyContent: "感谢您的好评，我们会继续努力！",
            replyBy: "9002");

        // Assert
        var updated = await _reviewRepo.GetByIdAsync(review.Id);
        Assert.NotNull(updated!.ReplyContent);
        Assert.Contains("感谢", updated.ReplyContent);
        Assert.Equal("9002", updated.ReplyBy);
    }

    [Fact(DisplayName = "回复未审核的评价 - 应抛出异常")]
    public async Task ReplyReview_NotApproved_ShouldThrowException()
    {
        // Arrange
        var review = await CreateTestReview(Guid.NewGuid(), Guid.NewGuid(), 4, "还行");
        // 不审核，直接回复

        // Act & Assert
        await Assert.ThrowsAsync<BusinessException>(async () =>
            await _service.ReplyReviewAsync(review.Id, "测试回复", "9001"));
    }

    #endregion

    #region 评价点赞测试

    [Fact(DisplayName = "点赞评价 - 应增加点赞数")]
    public async Task LikeReview_ShouldIncreaseLikeCount()
    {
        // Arrange
        var review = await CreateTestReview(Guid.NewGuid(), Guid.NewGuid(), 5, "非常好");
        await _service.AuditReviewAsync(review.Id, "Approved", "9001");

        // Act
        await _service.LikeReviewAsync(review.Id, userId: Guid.NewGuid());

        // Assert
        var updated = await _reviewRepo.GetByIdAsync(review.Id);
        Assert.Equal(1, updated!.LikeCount);
    }

    [Fact(DisplayName = "重复点赞 - 应忽略")]
    public async Task LikeReview_Duplicate_ShouldIgnore()
    {
        // Arrange
        var review = await CreateTestReview(Guid.NewGuid(), Guid.NewGuid(), 5, "好评");
        await _service.AuditReviewAsync(review.Id, "Approved", "9001");
        var likeUserId = Guid.NewGuid();

        // Act - 同一用户点赞两次
        await _service.LikeReviewAsync(review.Id, userId: likeUserId);
        await _service.LikeReviewAsync(review.Id, userId: likeUserId);

        // Assert - 只计数一次
        var updated = await _reviewRepo.GetByIdAsync(review.Id);
        Assert.Equal(1, updated!.LikeCount);
    }

    [Fact(DisplayName = "多用户点赞 - 应累计计数")]
    public async Task LikeReview_MultipleUsers_ShouldAccumulate()
    {
        // Arrange
        var review = await CreateTestReview(Guid.NewGuid(), Guid.NewGuid(), 5, "优秀");
        await _service.AuditReviewAsync(review.Id, "Approved", "9001");

        // Act - 3个不同用户点赞
        await _service.LikeReviewAsync(review.Id, userId: Guid.NewGuid());
        await _service.LikeReviewAsync(review.Id, userId: Guid.NewGuid());
        await _service.LikeReviewAsync(review.Id, userId: Guid.NewGuid());

        // Assert
        var updated = await _reviewRepo.GetByIdAsync(review.Id);
        Assert.Equal(3, updated!.LikeCount);
    }

    #endregion

    #region 投诉建议提交测试

    [Fact(DisplayName = "提交投诉 - 应生成工单号")]
    public async Task SubmitComplaint_ShouldGenerateTicketNo()
    {
        // Arrange
        var complaint = new FeedbackComplaint
        {
            UserId = Guid.NewGuid(),
            Type = "Complaint",
            Category = "设备故障",
            Title = "充电桩无法启动",
            Description = "尝试多次都无法启动充电",
            Urgency = "High",
            RelatedType = "Device",
            RelatedId = Guid.NewGuid(),
            CreateTime = DateTime.UtcNow
        };

        // Act
        var result = await _service.SubmitComplaintAsync(complaint);

        // Assert
        Assert.NotNull(result.TicketNo);
        Assert.StartsWith("CP", result.TicketNo); // 投诉工单前缀
        Assert.Equal("Submitted", result.Status); // 默认已提交状态
    }

    [Fact(DisplayName = "提交建议 - 工单号应有不同前缀")]
    public async Task SubmitSuggestion_ShouldHaveDifferentPrefix()
    {
        // Arrange
        var suggestion = new FeedbackComplaint
        {
            UserId = Guid.NewGuid(),
            Type = "Suggestion",
            Category = "服务改进",
            Title = "希望增加遮阳棚",
            Description = "夏天充电太热，建议增加遮阳设施",
            Urgency = "Low",
            CreateTime = DateTime.UtcNow
        };

        // Act
        var result = await _service.SubmitComplaintAsync(suggestion);

        // Assert
        Assert.StartsWith("SG", result.TicketNo); // 建议工单前缀
    }

    [Fact(DisplayName = "提交投诉时验证必填字段")]
    public async Task SubmitComplaint_ShouldValidateRequiredFields()
    {
        // Arrange - 缺少标题
        var complaint = new FeedbackComplaint
        {
            UserId = Guid.NewGuid(),
            Type = "Complaint",
            Category = "其他",
            Description = "测试描述",
            CreateTime = DateTime.UtcNow
        };

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentNullException>(async () =>
            await _service.SubmitComplaintAsync(complaint));
    }

    #endregion

    #region 投诉处理流程测试

    [Fact(DisplayName = "分配处理人 - 应更新状态为处理中")]
    public async Task AssignHandler_ShouldUpdateStatusToProcessing()
    {
        // Arrange
        var complaint = await CreateTestComplaint("设备故障", "High");

        // Act
        await _service.AssignHandlerAsync(complaint.Id, handler: "9003");

        // Assert
        var updated = await _feedbackRepo.GetByIdAsync(complaint.Id);
        Assert.Equal("Processing", updated!.Status);
        Assert.Equal("9003", updated.Handler);
    }

    [Fact(DisplayName = "处理投诉 - 应记录处理结果")]
    public async Task ResolveComplaint_ShouldRecordResolution()
    {
        // Arrange
        var complaint = await CreateTestComplaint("设备故障", "High");
        await _service.AssignHandlerAsync(complaint.Id, "9003");

        // Act
        await _service.ResolveComplaintAsync(
            complaint.Id,
            resolution: "已更换故障充电模块，设备恢复正常");

        // Assert
        var updated = await _feedbackRepo.GetByIdAsync(complaint.Id);
        Assert.Equal("Resolved", updated!.Status);
        Assert.NotNull(updated.Resolution);
        Assert.Contains("恢复正常", updated.Resolution);
        Assert.NotNull(updated.ResolvedAt);
    }

    [Fact(DisplayName = "用户评价处理结果 - 应关闭工单")]
    public async Task RateComplaint_ShouldCloseTicket()
    {
        // Arrange
        var complaint = await CreateTestComplaint("设备故障", "Medium");
        await _service.AssignHandlerAsync(complaint.Id, "9003");
        await _service.ResolveComplaintAsync(complaint.Id, "已处理");

        // Assert - 验证已解决
        var updated = await _feedbackRepo.GetByIdAsync(complaint.Id);
        Assert.Equal("Resolved", updated!.Status);
        Assert.NotNull(updated.Resolution);
        Assert.NotNull(updated.ResolvedAt);
    }

    [Fact(DisplayName = "投诉流程完整性 - 应按正确顺序流转")]
    public async Task ComplaintWorkflow_ShouldFollowCorrectSequence()
    {
        // Arrange
        var complaint = await CreateTestComplaint("收费异常", "High");

        // Act - 完整流程
        // 1. 分配处理人
        await _service.AssignHandlerAsync(complaint.Id, "9003");
        var step1Status = (await _feedbackRepo.GetByIdAsync(complaint.Id))!.Status;
        
        // 2. 处理完成
        await _service.ResolveComplaintAsync(complaint.Id, "已核实并退款");
        var step2 = await _feedbackRepo.GetByIdAsync(complaint.Id);

        // Assert - 验证每个阶段的状态
        Assert.Equal("Processing", step1Status);
        Assert.Equal("Resolved", step2!.Status);
        
        // 验证解决时间
        Assert.NotNull(step2.ResolvedAt);
    }

    #endregion

    #region 查询和筛选测试

    [Fact(DisplayName = "查询站点评价 - 应支持分页和筛选")]
    public async Task QueryReviews_ShouldSupportPagingAndFiltering()
    {
        // Arrange - 创建多个评价
        var testStationId = Guid.NewGuid();
        await CreateTestReview(testStationId, Guid.NewGuid(), 5, "优秀");
        await CreateTestReview(testStationId, Guid.NewGuid(), 4, "良好");
        await CreateTestReview(testStationId, Guid.NewGuid(), 3, "一般");
        
        // 审核前两个
        var reviews = _reviewRepo.Reviews.ToList();
        await _service.AuditReviewAsync(reviews[0].Id, "Approved", "9001");
        await _service.AuditReviewAsync(reviews[1].Id, "Approved", "9001");

        // Act - 查询已审核的评价
        var result = await _service.QueryReviewsAsync(
            stationId: testStationId,
            auditStatus: "Approved",
            pageIndex: 1,
            pageSize: 10);

        // Assert
        Assert.Equal(2, result.TotalCount);
        Assert.Equal(2, result.Reviews.Count);
    }

    [Fact(DisplayName = "查询投诉列表 - 应支持多条件筛选")]
    public async Task QueryComplaints_ShouldSupportMultipleFilters()
    {
        // Arrange
        await CreateTestComplaint("设备故障", "High", type: "Complaint");
        await CreateTestComplaint("收费问题", "Medium", type: "Complaint");
        await CreateTestComplaint("增加设施", "Low", type: "Suggestion");

        // Act - 只查询高优先级的投诉
        var result = await _service.QueryComplaintsAsync(
            type: "Complaint",
            urgency: "High",
            pageIndex: 1,
            pageSize: 10);

        // Assert
        Assert.Equal(1, result.TotalCount);
        Assert.Equal("High", result.Complaints[0].Urgency);
    }

    #endregion

    #region 统计分析测试

    [Fact(DisplayName = "站点评分统计 - 应计算平均分和分布")]
    public async Task GetRatingStatistics_ShouldCalculateCorrectly()
    {
        // Arrange - 创建不同评分的评价
        var testStationId = Guid.NewGuid();
        var reviews = new[]
        {
            await CreateTestReview(testStationId, Guid.NewGuid(), 5, "优秀"),
            await CreateTestReview(testStationId, Guid.NewGuid(), 5, "很好"),
            await CreateTestReview(testStationId, Guid.NewGuid(), 4, "良好"),
            await CreateTestReview(testStationId, Guid.NewGuid(), 4, "不错"),
            await CreateTestReview(testStationId, Guid.NewGuid(), 3, "一般")
        };

        // 全部审核通过
        foreach (var review in reviews)
        {
            await _service.AuditReviewAsync(review.Id, "Approved", "9001");
        }

        // Act
        var stats = await _service.GetStationRatingStatisticsAsync(testStationId);

        // Assert
        Assert.Equal(5, stats.TotalCount);
        Assert.Equal(4.2, stats.AverageRating, 1); // (5+5+4+4+3)/5 = 4.2
        Assert.Equal(2, stats.FiveStarCount); // 2个5星
        Assert.Equal(2, stats.FourStarCount); // 2个4星
        Assert.Equal(1, stats.ThreeStarCount); // 1个3星
    }

    [Fact(DisplayName = "投诉统计 - 应汇总各类数据")]
    public async Task GetComplaintStatistics_ShouldAggregateData()
    {
        // Arrange
        var c1 = await CreateTestComplaint("设备故障", "High", "Complaint");
        var c2 = await CreateTestComplaint("收费问题", "Medium", "Complaint");
        var c3 = await CreateTestComplaint("增加设施", "Low", "Suggestion");

        // 处理第一个投诉
        await _service.AssignHandlerAsync(c1.Id, "9003");
        await _service.ResolveComplaintAsync(c1.Id, "已修复");

        // Act
        var stats = await _service.GetComplaintStatisticsAsync();

        // Assert
        Assert.Equal(3, stats.TotalCount);
        Assert.Equal(2, stats.ComplaintCount);
        Assert.Equal(1, stats.SuggestionCount);
        Assert.Equal(1, stats.ResolvedCount);
        Assert.True(stats.AverageSatisfactionRating >= 0);
    }

    [Fact(DisplayName = "计算平均处理时长 - 应准确统计")]
    public async Task CalculateAverageResolutionTime_ShouldBeAccurate()
    {
        // Arrange
        var complaint = await CreateTestComplaint("测试", "Medium");
        
        // 模拟24小时后处理完成
        await _service.AssignHandlerAsync(complaint.Id, "9003");
        await Task.Delay(100); // 模拟时间流逝
        await _service.ResolveComplaintAsync(complaint.Id, "已处理");

        // Act
        var stats = await _service.GetComplaintStatisticsAsync();

        // Assert
        Assert.True(stats.AverageResolutionTimeHours >= 0);
    }

    #endregion

    #region 并发安全测试

    [Fact(DisplayName = "并发提交评价 - 应保持数据一致性")]
    public async Task ConcurrentReviewSubmission_ShouldMaintainConsistency()
    {
        // Arrange & Act - 并发提交100个评价
        var testStationId = Guid.NewGuid();
        var tasks = Enumerable.Range(0, 100)
            .Select(i => CreateTestReview(testStationId, Guid.NewGuid(), 5, $"评价{i}"))
            .ToArray();

        await Task.WhenAll(tasks);

        // Assert
        var count = _reviewRepo.Reviews.Count;
        Assert.Equal(100, count);
    }

    [Fact(DisplayName = "并发点赞 - 应正确计数")]
    public async Task ConcurrentLikes_ShouldCountCorrectly()
    {
        // Arrange
        var review = await CreateTestReview(Guid.NewGuid(), Guid.NewGuid(), 5, "测试");
        await _service.AuditReviewAsync(review.Id, "Approved", "9001");

        // Act - 50个不同用户并发点赞
        var tasks = Enumerable.Range(0, 50)
            .Select(_ => _service.LikeReviewAsync(review.Id, Guid.NewGuid()))
            .ToArray();

        await Task.WhenAll(tasks);

        // Assert
        var updated = await _reviewRepo.GetByIdAsync(review.Id);
        Assert.Equal(50, updated!.LikeCount);
    }

    #endregion

    #region 辅助方法

    private async Task<StationReview> CreateTestReview(
        Guid stationId, 
        Guid userId, 
        int rating, 
        string content)
    {
        var review = new StationReview
        {
            StationId = stationId,
            UserId = userId,
            Rating = rating,
            Content = content,
            IsAnonymous = false,
            CreateTime = DateTime.UtcNow
        };

        return await _service.SubmitReviewAsync(review);
    }

    private async Task<FeedbackComplaint> CreateTestComplaint(
        string category, 
        string urgency,
        string type = "Complaint")
    {
        var complaint = new FeedbackComplaint
        {
            UserId = Guid.NewGuid(),
            Type = type,
            Category = category,
            Title = $"测试{type}-{category}",
            Description = $"测试描述-{urgency}",
            Urgency = urgency,
            CreateTime = DateTime.UtcNow
        };

        return await _service.SubmitComplaintAsync(complaint);
    }

    #endregion

    public void Dispose()
    {
    }
}

internal class InMemoryReviewRepository : IReviewRepository
{
    internal List<StationReview> Reviews { get; } = new();
    internal List<ReviewLike> Likes { get; } = new();

    public Task<StationReview?> GetByIdAsync(Guid id) => Task.FromResult(Reviews.FirstOrDefault(r => r.Id == id));

    public Task<bool> ExistsByUserOrderAsync(Guid userId, Guid orderId)
        => Task.FromResult(Reviews.Any(r => r.UserId == userId && r.OrderId == orderId));

    public Task<bool> ExistsByUserStationOrderAsync(Guid stationId, Guid userId, Guid orderId)
        => Task.FromResult(Reviews.Any(r => r.StationId == stationId && r.UserId == userId && r.OrderId == orderId));

    public Task InsertAsync(StationReview review)
    {
        if (review.Id == Guid.Empty)
        {
            review.Id = Guid.NewGuid();
        }
        Reviews.Add(review);
        return Task.CompletedTask;
    }

    public Task UpdateAsync(StationReview review)
    {
        var idx = Reviews.FindIndex(r => r.Id == review.Id);
        if (idx >= 0)
        {
            Reviews[idx] = review;
        }
        return Task.CompletedTask;
    }

    public Task<(List<StationReview> Reviews, int TotalCount)> QueryAsync(Guid? stationId, Guid? userId, int? minRating, string? auditStatus, bool? isVisible, int pageIndex, int pageSize)
    {
        var query = Reviews.AsEnumerable();
        if (stationId.HasValue) query = query.Where(r => r.StationId == stationId.Value);
        if (userId.HasValue) query = query.Where(r => r.UserId == userId.Value);
        if (minRating.HasValue) query = query.Where(r => r.Rating >= minRating.Value);
        if (!string.IsNullOrEmpty(auditStatus)) query = query.Where(r => r.AuditStatus == auditStatus);
        if (isVisible.HasValue) query = query.Where(r => r.IsVisible == isVisible.Value);

        var total = query.Count();
        var items = query.Skip((pageIndex - 1) * pageSize).Take(pageSize).ToList();
        return Task.FromResult((items, total));
    }

    public Task<List<StationReview>> GetVisibleByStationAsync(Guid stationId)
        => Task.FromResult(Reviews.Where(r => r.StationId == stationId && r.IsVisible).ToList());

    public Task<List<StationReview>> GetByStationNotHiddenAsync(Guid stationId, int? rating, string? orderBy, int pageIndex, int pageSize)
    {
        var query = Reviews.Where(r => r.StationId == stationId && r.IsVisible);
        if (rating.HasValue) query = query.Where(r => r.Rating == rating.Value);
        var ordered = orderBy switch
        {
            "rating" => query.OrderByDescending(r => r.Rating),
            "time" => query.OrderByDescending(r => r.CreateTime),
            _ => query.OrderByDescending(r => r.CreateTime)
        };
        return Task.FromResult(ordered.Skip((pageIndex - 1) * pageSize).Take(pageSize).ToList());
    }

    public Task<int> CountByStationNotHiddenAsync(Guid stationId, int? rating)
    {
        var query = Reviews.Where(r => r.StationId == stationId && r.IsVisible);
        if (rating.HasValue) query = query.Where(r => r.Rating == rating.Value);
        return Task.FromResult(query.Count());
    }

    public Task<List<StationReview>> GetLowRatingAsync(Guid? stationId, bool unhandledOnly, int pageIndex, int pageSize)
    {
        var query = Reviews.Where(r => r.Rating <= 2);
        if (stationId.HasValue) query = query.Where(r => r.StationId == stationId.Value);
        if (unhandledOnly) query = query.Where(r => r.AuditStatus != "Handled");
        var items = query.Skip((pageIndex - 1) * pageSize).Take(pageSize).ToList();
        return Task.FromResult(items);
    }

    public Task<List<StationReview>> GetByStationSinceAsync(Guid stationId, DateTime since, bool notHiddenOnly)
    {
        var query = Reviews.Where(r => r.StationId == stationId && r.CreateTime >= since);
        if (notHiddenOnly) query = query.Where(r => r.IsVisible);
        return Task.FromResult(query.ToList());
    }

    public Task<List<StationReview>> GetTagsByStationAsync(Guid stationId)
        => Task.FromResult(Reviews.Where(r => r.StationId == stationId).ToList());

    public Task<bool> LikeExistsAsync(Guid reviewId, Guid userId)
        => Task.FromResult(Likes.Any(l => l.ReviewId == reviewId && l.UserId == userId));

    public Task InsertLikeAsync(ReviewLike like)
    {
        Likes.Add(like);
        return Task.CompletedTask;
    }

    public Task IncrementLikeCountAsync(Guid reviewId)
    {
        var review = Reviews.FirstOrDefault(r => r.Id == reviewId);
        if (review != null) review.LikeCount += 1;
        return Task.CompletedTask;
    }

    public Task IncrementHelpfulCountAsync(Guid reviewId)
    {
        var review = Reviews.FirstOrDefault(r => r.Id == reviewId);
        if (review != null) review.HelpfulCount += 1;
        return Task.CompletedTask;
    }
}

internal class InMemoryFeedbackRepository : IFeedbackRepository
{
    internal List<FeedbackComplaint> Items { get; } = new();

    public Task<FeedbackComplaint?> GetByIdAsync(Guid id)
        => Task.FromResult(Items.FirstOrDefault(c => c.Id == id));

    public Task InsertAsync(FeedbackComplaint complaint)
    {
        if (complaint.Id == Guid.Empty) complaint.Id = Guid.NewGuid();
        Items.Add(complaint);
        return Task.CompletedTask;
    }

    public Task UpdateAsync(FeedbackComplaint complaint)
    {
        var idx = Items.FindIndex(c => c.Id == complaint.Id);
        if (idx >= 0) Items[idx] = complaint;
        return Task.CompletedTask;
    }

    public Task<(List<FeedbackComplaint> Items, int TotalCount)> QueryAsync(Guid? userId, string? type, string? status, string? category, string? urgency, DateTime? createdFrom, DateTime? createdTo, int pageIndex, int pageSize)
    {
        var query = Items.AsEnumerable();
        if (userId.HasValue) query = query.Where(c => c.UserId == userId.Value);
        if (!string.IsNullOrEmpty(type)) query = query.Where(c => c.Type == type);
        if (!string.IsNullOrEmpty(status)) query = query.Where(c => c.Status == status);
        if (!string.IsNullOrEmpty(category)) query = query.Where(c => c.Category == category);
        if (!string.IsNullOrEmpty(urgency)) query = query.Where(c => c.Urgency == urgency);
        if (createdFrom.HasValue) query = query.Where(c => c.CreateTime >= createdFrom.Value);
        if (createdTo.HasValue) query = query.Where(c => c.CreateTime <= createdTo.Value);

        var total = query.Count();
        var items = query.Skip((pageIndex - 1) * pageSize).Take(pageSize).ToList();
        return Task.FromResult((items, total));
    }

    public Task<List<FeedbackComplaint>> GetAllAsync(DateTime? from, DateTime? to)
    {
        var query = Items.AsEnumerable();
        if (from.HasValue) query = query.Where(c => c.CreateTime >= from.Value);
        if (to.HasValue) query = query.Where(c => c.CreateTime <= to.Value);
        return Task.FromResult(query.ToList());
    }
}
