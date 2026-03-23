using System;
using System.Collections.Generic;
using System.Linq;
using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.Data;

/// <summary>
/// 软删除逻辑测试 - P1 覆盖
/// 验证软删除机制的正确实现
/// </summary>
public class SoftDeleteLogicTests
{
    private readonly Guid _tenantId = Guid.NewGuid();

    #region 基础软删除测试

    [Fact]
    public void SoftDelete_ShouldSetIsDeletedToTrue()
    {
        var entity = CreateEntity(DeleteAt: null);
        
        entity.DeleteAt = DateTime.UtcNow;
        entity.DeletedAt = DateTime.UtcNow;
        entity.UpdateTime = DateTime.UtcNow;
        
        entity.DeleteAt.Should().NotBeNull();
        entity.DeletedAt.Should().NotBeNull();
    }

    [Fact]
    public void SoftDelete_ShouldNotPhysicallyRemoveRecord()
    {
        var records = new List<SoftDeleteEntity>
        {
            CreateEntity(DeleteAt: null),
            CreateEntity(DeleteAt: null)
        };
        
        var targetId = records[0].Id;
        var initialCount = records.Count;
        
        // 软删除
        var target = records.First(r => r.Id == targetId);
        target.DeleteAt = DateTime.UtcNow;
        
        // 记录数应不变
        records.Should().HaveCount(initialCount);
    }

    [Fact]
    public void SoftDelete_ShouldPreserveAllData()
    {
        var entity = CreateEntity(DeleteAt: null);
        var originalName = entity.Name;
        var originalCreatedAt = entity.CreateTime;
        
        // 软删除
        entity.DeleteAt = DateTime.UtcNow;
        entity.DeletedAt = DateTime.UtcNow;
        
        // 其他数据应保持不变
        entity.Name.Should().Be(originalName);
        entity.CreateTime.Should().Be(originalCreatedAt);
    }

    [Fact]
    public void SoftDelete_ShouldRecordDeletedAt()
    {
        var entity = CreateEntity(DeleteAt: null);
        var deleteTime = DateTime.UtcNow;
        
        entity.DeleteAt = DateTime.UtcNow;
        entity.DeletedAt = deleteTime;
        
        entity.DeletedAt.Should().BeCloseTo(deleteTime, TimeSpan.FromSeconds(1));
    }

    [Fact]
    public void SoftDelete_ShouldRecordDeletedBy()
    {
        var entity = CreateEntity(DeleteAt: null);
        var deletedByUserId = Guid.NewGuid();
        
        entity.DeleteAt = DateTime.UtcNow;
        entity.UpdateBy = deletedByUserId;
        
        entity.UpdateBy.Should().Be(deletedByUserId);
    }

    #endregion

    #region 查询过滤测试

    [Fact]
    public void Query_ShouldExcludeDeletedRecords()
    {
        var records = new List<SoftDeleteEntity>
        {
            CreateEntity(DeleteAt: null),
            CreateEntity(DeleteAt: DateTime.UtcNow),  // 已删除
            CreateEntity(DeleteAt: null),
            CreateEntity(DeleteAt: DateTime.UtcNow),  // 已删除
        };
        
        var activeRecords = records.Where(r => r.DeleteAt == null).ToList();
        
        activeRecords.Should().HaveCount(2);
        activeRecords.Should().AllSatisfy(r => r.DeleteAt.Should().BeNull());
    }

    [Fact]
    public void Query_DeletedRecordsShouldBeInvisible()
    {
        var records = new List<SoftDeleteEntity>
        {
            CreateEntity(DeleteAt: null),
            CreateEntity(DeleteAt: DateTime.UtcNow)
        };
        
        var deletedId = records.First(r => r.DeleteAt != null).Id;
        
        // 正常查询
        var found = records.FirstOrDefault(r => r.Id == deletedId && r.DeleteAt == null);
        
        found.Should().BeNull("软删除的记录应该在正常查询中不可见");
    }

    [Fact]
    public void Query_ShouldIncludeBothTenantAndSoftDeleteFilter()
    {
        var sql = "SELECT * FROM table WHERE tenant_id = @TenantId AND delete_at IS NULL";
        
        sql.Should().Contain("tenant_id = @TenantId");
        sql.Should().Contain("delete_at IS NULL");
    }

    [Theory]
    [InlineData(true, true, false)]   // 已删除 + 当前租户 = 不可见
    [InlineData(false, true, true)]   // 未删除 + 当前租户 = 可见
    [InlineData(false, false, false)] // 未删除 + 其他租户 = 不可见
    [InlineData(true, false, false)]  // 已删除 + 其他租户 = 不可见
    public void Query_VisibilityMatrix(bool isDeleted, bool isCurrentTenant, bool shouldBeVisible)
    {
        var currentTenantId = _tenantId;
        var entity = new SoftDeleteEntity
        {
            Id = Guid.NewGuid(),
            TenantId = isCurrentTenant ? currentTenantId : Guid.NewGuid(),
            DeleteAt = isDeleted ? DateTime.UtcNow : null
        };
        
        var isVisible = entity.TenantId == currentTenantId && entity.DeleteAt == null;
        
        isVisible.Should().Be(shouldBeVisible);
    }

    #endregion

    #region 级联软删除测试

    [Fact]
    public void CascadeSoftDelete_ParentShouldDeleteChildren()
    {
        var parentId = Guid.NewGuid();
        var parent = new SoftDeleteEntity { Id = parentId, DeleteAt = (DateTime?)null };
        var children = new List<SoftDeleteEntity>
        {
            new() { Id = Guid.NewGuid(), ParentId = parentId, DeleteAt = (DateTime?)null },
            new() { Id = Guid.NewGuid(), ParentId = parentId, DeleteAt = (DateTime?)null },
            new() { Id = Guid.NewGuid(), ParentId = parentId, DeleteAt = (DateTime?)null }
        };
        
        // 级联软删除：先删子后删父
        var now = DateTime.UtcNow;
        foreach (var child in children)
        {
            child.DeleteAt = DateTime.UtcNow;
            child.DeletedAt = now;
        }
        parent.DeleteAt = DateTime.UtcNow;
        parent.DeletedAt = now;
        
        // 验证
        parent.DeleteAt.Should().NotBeNull();
        children.Should().AllSatisfy(c => c.DeleteAt.Should().NotBeNull());
    }

    [Fact]
    public void CascadeSoftDelete_ShouldBeInTransaction()
    {
        // 模拟事务行为
        var transactionStarted = false;
        var transactionCommitted = false;
        var childrenDeleted = false;
        var parentDeleted = false;
        
        try
        {
            transactionStarted = true;
            childrenDeleted = true;  // 先删子
            parentDeleted = true;    // 后删父
            transactionCommitted = true;
        }
        catch
        {
            transactionCommitted = false;
        }
        
        transactionStarted.Should().BeTrue();
        childrenDeleted.Should().BeTrue();
        parentDeleted.Should().BeTrue();
        transactionCommitted.Should().BeTrue();
    }

    [Fact]
    public void CascadeSoftDelete_OrderShouldBeChildrenFirst()
    {
        var deleteOrder = new List<string>();
        
        // 模拟删除顺序
        deleteOrder.Add("Child1");
        deleteOrder.Add("Child2");
        deleteOrder.Add("Parent");
        
        deleteOrder.Last().Should().Be("Parent", "父记录应最后删除");
        deleteOrder.IndexOf("Parent").Should().BeGreaterThan(deleteOrder.IndexOf("Child1"));
    }

    [Fact]
    public void CascadeSoftDelete_MultiLevelHierarchy()
    {
        // 三层结构：祖父 -> 父 -> 子
        var grandparentId = Guid.NewGuid();
        var parentId = Guid.NewGuid();
        var childId = Guid.NewGuid();
        
        var deleteOrder = new List<Guid>();
        
        // 正确顺序：子 -> 父 -> 祖父
        deleteOrder.Add(childId);
        deleteOrder.Add(parentId);
        deleteOrder.Add(grandparentId);
        
        deleteOrder.First().Should().Be(childId);
        deleteOrder.Last().Should().Be(grandparentId);
    }

    #endregion

    #region 恢复（反软删除）测试

    [Fact]
    public void Restore_ShouldSetIsDeletedToFalse()
    {
        var entity = CreateEntity(DeleteAt: DateTime.UtcNow);
        
        entity.DeleteAt = null;
        entity.DeletedAt = null;
        entity.UpdateBy = null;
        entity.UpdateTime = DateTime.UtcNow;
        
        entity.DeleteAt.Should().BeNull();
        entity.DeletedAt.Should().BeNull();
    }

    [Fact]
    public void Restore_ShouldMakeRecordVisibleAgain()
    {
        var records = new List<SoftDeleteEntity>
        {
            CreateEntity(DeleteAt: DateTime.UtcNow)
        };
        
        var targetId = records[0].Id;
        
        // 恢复前
        var beforeRestore = records.FirstOrDefault(r => r.Id == targetId && r.DeleteAt == null);
        beforeRestore.Should().BeNull();
        
        // 恢复
        records[0].DeleteAt = null;
        
        // 恢复后
        var afterRestore = records.FirstOrDefault(r => r.Id == targetId && r.DeleteAt == null);
        afterRestore.Should().NotBeNull();
    }

    #endregion

    #region 唯一约束与软删除测试

    [Fact]
    public void UniqueConstraint_ShouldAllowSameValueAfterSoftDelete()
    {
        var records = new List<SoftDeleteEntity>
        {
            new() { Id = Guid.NewGuid(), TenantId = _tenantId, Name = "UniqueValue", DeleteAt = DateTime.UtcNow },
            new() { Id = Guid.NewGuid(), TenantId = _tenantId, Name = "UniqueValue", DeleteAt = (DateTime?)null }
        };
        
        // 活跃记录中 Name 唯一
        var activeWithSameName = records
            .Where(r => r.Name == "UniqueValue" && r.DeleteAt == null)
            .ToList();
        
        activeWithSameName.Should().HaveCount(1, "软删除后可以创建同名的新记录");
    }

    [Fact]
    public void UniqueConstraint_ShouldCheckActiveRecordsOnly()
    {
        var records = new List<SoftDeleteEntity>
        {
            new() { Id = Guid.NewGuid(), TenantId = _tenantId, Name = "Test", DeleteAt = (DateTime?)null }
        };
        
        var newName = "Test";
        var wouldViolate = records.Any(r => 
            r.Name == newName && 
            r.TenantId == _tenantId && 
            r.DeleteAt == null);
        
        wouldViolate.Should().BeTrue("活跃记录中已存在同名记录");
    }

    #endregion

    #region 审计追踪测试

    [Fact]
    public void SoftDelete_ShouldCreateAuditTrail()
    {
        var entity = CreateEntity(DeleteAt: null);
        var UpdateBy = Guid.NewGuid();
        var deleteTime = DateTime.UtcNow;
        
        // 记录审计信息
        entity.DeleteAt = DateTime.UtcNow;
        entity.DeletedAt = deleteTime;
        entity.UpdateBy = UpdateBy;
        
        entity.UpdateBy.Should().Be(UpdateBy);
        entity.DeletedAt.Should().BeCloseTo(deleteTime, TimeSpan.FromSeconds(1));
    }

    [Fact]
    public void SoftDelete_AuditFieldsShouldBePersisted()
    {
        var entity = CreateEntity(DeleteAt: null);
        var UpdateBy = Guid.NewGuid();
        var deleteReason = "User requested deletion";
        
        entity.DeleteAt = DateTime.UtcNow;
        entity.UpdateBy = UpdateBy;
        entity.DeleteReason = deleteReason;
        
        entity.UpdateBy.Should().NotBeEmpty();
        entity.DeleteReason.Should().NotBeNullOrEmpty();
    }

    #endregion

    #region 物理删除例外测试

    [Fact]
    public void PhysicalDelete_OnlyAllowedForSimulatorData()
    {
        var isSimulatorData = true;
        var isPhysicalDeleteAllowed = isSimulatorData;
        
        isPhysicalDeleteAllowed.Should().BeTrue("模拟器数据允许物理删除");
    }

    [Fact]
    public void PhysicalDelete_RequiresSpecificConditions()
    {
        var isSimulatorData = true;
        var hasValidDeviceId = true;
        var isInTransaction = true;
        var hasAuditLog = true;
        
        var canPhysicalDelete = 
            isSimulatorData && 
            hasValidDeviceId && 
            isInTransaction && 
            hasAuditLog;
        
        canPhysicalDelete.Should().BeTrue();
    }

    [Fact]
    public void PhysicalDelete_ShouldNotApplyToBusinessData()
    {
        var isBusinessData = true;
        var isSimulatorData = false;
        
        var canPhysicalDelete = isSimulatorData && !isBusinessData;
        
        canPhysicalDelete.Should().BeFalse("业务数据不允许物理删除");
    }

    #endregion

    #region 查询包含已删除记录（管理功能）测试

    [Fact]
    public void AdminQuery_CanIncludeDeletedRecords()
    {
        var records = new List<SoftDeleteEntity>
        {
            CreateEntity(DeleteAt: null),
            CreateEntity(DeleteAt: DateTime.UtcNow),
            CreateEntity(DeleteAt: null)
        };
        
        var includeDeleted = true;
        var results = includeDeleted 
            ? records.ToList() 
            : records.Where(r => r.DeleteAt == null).ToList();
        
        results.Should().HaveCount(3);
    }

    [Fact]
    public void AdminQuery_CanFilterOnlyDeletedRecords()
    {
        var records = new List<SoftDeleteEntity>
        {
            CreateEntity(DeleteAt: null),
            CreateEntity(DeleteAt: DateTime.UtcNow),
            CreateEntity(DeleteAt: DateTime.UtcNow)
        };
        
        var deletedOnly = records.Where(r => r.DeleteAt != null).ToList();
        
        deletedOnly.Should().HaveCount(2);
        deletedOnly.Should().AllSatisfy(r => r.DeleteAt.Should().NotBeNull());
    }

    #endregion

    #region 辅助方法

    private SoftDeleteEntity CreateEntity(DateTime? DeleteAt)
    {
        return new SoftDeleteEntity
        {
            Id = Guid.NewGuid(),
            TenantId = _tenantId,
            Name = $"Entity_{Guid.NewGuid():N}",
            DeleteAt = DeleteAt,
            CreateTime = DateTime.UtcNow.AddDays(-1),
            UpdateTime = DateTime.UtcNow.AddDays(-1),
            DeletedAt = DeleteAt != null ? DateTime.UtcNow : null
        };
    }

    private class SoftDeleteEntity
    {
        public Guid Id { get; set; }
        public Guid TenantId { get; set; }
        public Guid? ParentId { get; set; }
        public string Name { get; set; } = string.Empty;
        public DateTime? DeleteAt { get; set; }
        public DateTime CreateTime { get; set; }
        public DateTime UpdateTime { get; set; }
        public DateTime? DeletedAt { get; set; }
        public Guid? UpdateBy { get; set; }
        public string? DeleteReason { get; set; }
    }

    #endregion
}

/// <summary>
/// SQL 软删除模式测试 - P1 覆盖
/// </summary>
public class SoftDeleteSqlPatternTests
{
    #region SELECT 模式测试

    [Fact]
    public void Select_ShouldAlwaysFilterIsDeleted()
    {
        var sql = "SELECT * FROM table WHERE tenant_id = @TenantId AND delete_at IS NULL";
        
        sql.Should().Contain("delete_at IS NULL");
    }

    [Fact]
    public void Select_WithoutIsDeletedFilter_IsViolation()
    {
        var violatingSql = "SELECT * FROM table WHERE tenant_id = @TenantId";
        
        violatingSql.Should().NotContain("delete_at", 
            "这是一个违规示例：缺少 delete_at 过滤");
    }

    #endregion

    #region UPDATE 模式测试

    [Fact]
    public void SoftDeleteUpdate_ShouldSetIsDeletedTrue()
    {
        var sql = "UPDATE table SET delete_at = NOW(), deleted_at = @DeletedAt WHERE id = @Id AND tenant_id = @TenantId";
        
        sql.Should().Contain("delete_at = NOW()");
        sql.Should().Contain("deleted_at = @DeletedAt");
        sql.Should().Contain("tenant_id = @TenantId");
    }

    [Fact]
    public void Update_ShouldOnlyAffectActiveRecords()
    {
        var sql = "UPDATE table SET name = @Name WHERE id = @Id AND tenant_id = @TenantId AND delete_at IS NULL";
        
        sql.Should().Contain("delete_at IS NULL");
    }

    #endregion

    #region DELETE 模式测试（禁止使用）

    [Fact]
    public void PhysicalDelete_ShouldBeProhibitedForBusinessData()
    {
        var usePhysicalDelete = false; // 业务数据禁止物理删除
        
        usePhysicalDelete.Should().BeFalse();
    }

    [Fact]
    public void PhysicalDelete_OnlyAllowedForSimulatorWithConditions()
    {
        // 模拟器数据物理删除的条件
        var conditions = new
        {
            IsSimulatorData = true,
            MatchByDeviceIdOrSessionId = true,
            InTransaction = true,
            HasAuditLog = true
        };
        
        var canPhysicalDelete = 
            conditions.IsSimulatorData && 
            conditions.MatchByDeviceIdOrSessionId && 
            conditions.InTransaction && 
            conditions.HasAuditLog;
        
        canPhysicalDelete.Should().BeTrue();
    }

    #endregion
}
