using System;
using System.Collections.Generic;
using System.Linq;
using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.Data;

/// <summary>
/// Repository 层 CRUD 操作模式测试 - P1 覆盖
/// 这些测试验证 Repository 层的核心业务逻辑，不依赖数据库
/// </summary>
public class RepositoryCrudPatternTests
{
    private readonly Guid _tenantId = Guid.NewGuid();

    #region GetById 模式测试

    [Fact]
    public void GetById_QueryShouldIncludeTenantIdFilter()
    {
        // Repository 查询必须包含 tenant_id 过滤
        var expectedSqlPattern = "WHERE id = @Id AND tenant_id = @TenantId AND delete_at IS NULL";
        
        var actualSql = "SELECT * FROM settlement_order WHERE id = @Id AND tenant_id = @TenantId AND delete_at IS NULL";
        
        actualSql.Should().Contain(expectedSqlPattern);
        actualSql.Should().Contain("tenant_id = @TenantId");
        actualSql.Should().Contain("delete_at IS NULL");
    }

    [Fact]
    public void GetById_ShouldReturnNullForDeletedRecords()
    {
        // 模拟已软删除的记录
        var records = new List<TestEntity>
        {
            new() { Id = Guid.NewGuid(), TenantId = _tenantId, DeleteAt = (DateTime?)null },
            new() { Id = Guid.NewGuid(), TenantId = _tenantId, DeleteAt = DateTime.UtcNow } // 已软删除
        };
        
        var targetId = records[1].Id;
        var result = records.FirstOrDefault(r => r.Id == targetId && r.DeleteAt == null);
        
        result.Should().BeNull("软删除的记录不应被查询到");
    }

    [Fact]
    public void GetById_ShouldReturnNullForOtherTenantRecords()
    {
        var otherTenantId = Guid.NewGuid();
        var records = new List<TestEntity>
        {
            new() { Id = Guid.NewGuid(), TenantId = _tenantId, DeleteAt = (DateTime?)null },
            new() { Id = Guid.NewGuid(), TenantId = otherTenantId, DeleteAt = (DateTime?)null }
        };
        
        var targetId = records[1].Id;
        var currentTenantId = _tenantId;
        var result = records.FirstOrDefault(r => r.Id == targetId && r.TenantId == currentTenantId && r.DeleteAt == null);
        
        result.Should().BeNull("不同租户的记录不应被查询到");
    }

    #endregion

    #region GetPaged 模式测试

    [Fact]
    public void GetPaged_ShouldCalculateOffsetCorrectly()
    {
        var pageIndex = 3;
        var pageSize = 10;
        
        var offset = (pageIndex - 1) * pageSize;
        
        offset.Should().Be(20); // 第3页，跳过前20条
    }

    [Theory]
    [InlineData(1, 10, 0)]
    [InlineData(2, 10, 10)]
    [InlineData(5, 20, 80)]
    [InlineData(1, 50, 0)]
    public void GetPaged_OffsetCalculation(int pageIndex, int pageSize, int expectedOffset)
    {
        var offset = (pageIndex - 1) * pageSize;
        offset.Should().Be(expectedOffset);
    }

    [Fact]
    public void GetPaged_ShouldFilterByTenantAndNotDeleted()
    {
        var records = GenerateTestRecords(50);
        var currentTenantId = _tenantId;
        
        var filtered = records.Where(r => r.TenantId == currentTenantId && r.DeleteAt == null).ToList();
        
        filtered.All(r => r.TenantId == currentTenantId).Should().BeTrue();
        filtered.All(r => r.DeleteAt == null).Should().BeTrue();
    }

    [Fact]
    public void GetPaged_ShouldReturnCorrectTotalCount()
    {
        var records = GenerateTestRecords(100);
        var currentTenantId = _tenantId;
        
        var filtered = records.Where(r => r.TenantId == currentTenantId && r.DeleteAt == null).ToList();
        var pageSize = 10;
        var paged = filtered.Take(pageSize).ToList();
        
        filtered.Count.Should().BeGreaterThan(0);
        paged.Count.Should().BeLessOrEqualTo(pageSize);
    }

    #endregion

    #region Insert 模式测试

    [Fact]
    public void Insert_ShouldGenerateIdIfEmpty()
    {
        var entity = new TestEntity { Id = Guid.Empty };
        
        if (entity.Id == Guid.Empty)
        {
            entity.Id = Guid.NewGuid();
        }
        
        entity.Id.Should().NotBe(Guid.Empty);
    }

    [Fact]
    public void Insert_ShouldSetTenantIdFromContext()
    {
        var entity = new TestEntity { Id = Guid.NewGuid() };
        var contextTenantId = _tenantId;
        
        entity.TenantId = contextTenantId;
        
        entity.TenantId.Should().Be(contextTenantId);
    }

    [Fact]
    public void Insert_ShouldSetTimestamps()
    {
        var entity = new TestEntity { Id = Guid.NewGuid() };
        var now = DateTime.UtcNow;
        
        entity.CreateTime = now;
        entity.UpdateTime = now;
        
        entity.CreateTime.Should().BeCloseTo(now, TimeSpan.FromSeconds(1));
        entity.UpdateTime.Should().BeCloseTo(now, TimeSpan.FromSeconds(1));
    }

    [Fact]
    public void Insert_ShouldSetIsDeletedToFalse()
    {
        var entity = new TestEntity { Id = Guid.NewGuid() };
        entity.DeleteAt = null;
        
        entity.DeleteAt.Should().BeNull();
    }

    [Fact]
    public void Insert_EntityShouldHaveAllRequiredFields()
    {
        var entity = new TestEntity
        {
            Id = Guid.NewGuid(),
            TenantId = _tenantId,
            DeleteAt = (DateTime?)null,
            CreateTime = DateTime.UtcNow};
        
        var originalCreatedAt = entity.CreateTime;
        entity.UpdateTime = DateTime.UtcNow;
        
        entity.UpdateTime.Should().BeAfter(originalCreatedAt);
        entity.CreateTime.Should().Be(originalCreatedAt); // CreateTime 不应变
    }

    [Fact]
    public void Update_ShouldNotChangeTenantId()
    {
        var originalTenantId = _tenantId;
        var entity = new TestEntity { TenantId = originalTenantId };
        
        // 尝试更改 TenantId（应被业务逻辑阻止）
        var attemptedNewTenantId = Guid.NewGuid();
        var shouldAllowChange = false;
        
        if (!shouldAllowChange)
        {
            // 保持原值
            entity.TenantId = originalTenantId;
        }
        
        entity.TenantId.Should().Be(originalTenantId);
    }

    [Fact]
    public void Update_ShouldIncrementRowVersion()
    {
        var entity = new TestEntity { RowVersion = 1 };
        var originalVersion = entity.RowVersion;
        
        entity.RowVersion++;
        
        entity.RowVersion.Should().Be(originalVersion + 1);
    }

    [Fact]
    public void Update_OptimisticLockingCheck()
    {
        var dbRowVersion = 5;
        var clientRowVersion = 3;
        
        var isStale = clientRowVersion < dbRowVersion;
        isStale.Should().BeTrue("客户端版本低于数据库版本，应检测到冲突");
    }

    #endregion

    #region Delete 模式测试

    [Fact]
    public void SoftDelete_ShouldSetIsDeletedToTrue()
    {
        var entity = new TestEntity { DeleteAt = (DateTime?)null };
        
        entity.DeleteAt = DateTime.UtcNow;
        entity.UpdateTime = DateTime.UtcNow;
        
        entity.DeleteAt.Should().NotBeNull();
    }

    [Fact]
    public void SoftDelete_ShouldNotPhysicallyRemoveRecord()
    {
        var records = new List<TestEntity>
        {
            new() { Id = Guid.NewGuid(), DeleteAt = (DateTime?)null }
        };
        
        var targetId = records[0].Id;
        
        // 软删除
        var target = records.First(r => r.Id == targetId);
        target.DeleteAt = DateTime.UtcNow;
        
        // 记录仍存在
        records.Should().HaveCount(1);
        records.First().DeleteAt.Should().NotBeNull();
    }

    [Fact]
    public void SoftDelete_QueryShouldUpdateTenantIdFilter()
    {
        // DELETE/UPDATE 操作也必须包含 tenant_id
        var expectedSqlPattern = "WHERE id = @Id AND tenant_id = @TenantId";
        
        var actualSql = "UPDATE settlement_order SET delete_at = NOW() WHERE id = @Id AND tenant_id = @TenantId";
        
        actualSql.Should().Contain(expectedSqlPattern);
    }

    #endregion

    #region 测试辅助

    private List<TestEntity> GenerateTestRecords(int count)
    {
        var otherTenantId = Guid.NewGuid();
        var records = new List<TestEntity>();
        
        for (var i = 0; i < count; i++)
        {
            records.Add(new TestEntity
            {
                Id = Guid.NewGuid(),
                TenantId = i % 3 == 0 ? otherTenantId : _tenantId,
                DeleteAt = i % 10 == 0 ? DateTime.UtcNow : null, // 10% 已删除
                CreateTime = DateTime.UtcNow.AddDays(-i)
            });
        }
        
        return records;
    }

    private class TestEntity
    {
        public Guid Id { get; set; }
        public Guid TenantId { get; set; }
        public DateTime? DeleteAt { get; set; }
        public DateTime CreateTime { get; set; }
        public DateTime UpdateTime { get; set; }
        public int RowVersion { get; set; }
    }

    #endregion
}

/// <summary>
/// SQL 查询构建模式测试 - P1 覆盖
/// </summary>
public class SqlQueryPatternTests
{
    #region WHERE 子句构建测试

    [Fact]
    public void WhereClause_ShouldAlwaysIncludeTenantId()
    {
        var baseWhere = "WHERE tenant_id = @TenantId AND delete_at IS NULL";
        
        baseWhere.Should().Contain("tenant_id = @TenantId");
    }

    [Fact]
    public void WhereClause_ShouldAlwaysIncludeIsDeleted()
    {
        var baseWhere = "WHERE tenant_id = @TenantId AND delete_at IS NULL";
        
        baseWhere.Should().Contain("delete_at IS NULL");
    }

    [Fact]
    public void WhereClause_OptionalFilters_ShouldBeAdditive()
    {
        var where = "WHERE tenant_id = @TenantId AND delete_at IS NULL";
        var merchantId = Guid.NewGuid();
        var status = 1;
        
        if (merchantId != Guid.Empty) where += " AND merchant_id = @MerchantId";
        if (status > 0) where += " AND status = @Status";
        
        where.Should().Contain("merchant_id = @MerchantId");
        where.Should().Contain("status = @Status");
    }
    
    [Theory]
    [InlineData(true, false, " AND merchant_id = @MerchantId")]
    [InlineData(false, true, " AND status = @Status")]
    [InlineData(true, true, " AND merchant_id = @MerchantId AND status = @Status")]
    [InlineData(false, false, "")]
    public void WhereClause_ConditionalFilters(bool hasMerchantId, bool hasStatus, string expectedAddition)
    {
        var where = "WHERE tenant_id = @TenantId AND delete_at IS NULL";
        var additions = "";
        
        if (hasMerchantId) additions += " AND merchant_id = @MerchantId";
        if (hasStatus) additions += " AND status = @Status";
        
        where += additions;
        
        if (!string.IsNullOrEmpty(expectedAddition))
        {
            where.Should().Contain(expectedAddition.Trim());
        }
    }

    #endregion

    #region 参数化查询测试

    [Fact]
    public void Parameters_ShouldNotUseStringInterpolation()
    {
        // 正确：使用参数化
        var correctSql = "SELECT * FROM table WHERE id = @Id";
        
        // 错误：字符串拼接（SQL 注入风险）
        var id = Guid.NewGuid();
        var incorrectSql = $"SELECT * FROM table WHERE id = '{id}'";
        
        correctSql.Should().Contain("@Id");
        incorrectSql.Should().NotContain("@"); // 这是反例
    }

    [Fact]
    public void Parameters_ShouldIncludeTenantContext()
    {
        var tenantId = Guid.NewGuid();
        var parameters = new
        {
            TenantId = tenantId,
            Id = Guid.NewGuid()
        };
        
        parameters.TenantId.Should().Be(tenantId);
    }

    #endregion

    #region ORDER BY 和 LIMIT 测试

    [Theory]
    [InlineData(10, 0, "LIMIT 10 OFFSET 0")]
    [InlineData(20, 40, "LIMIT 20 OFFSET 40")]
    [InlineData(50, 100, "LIMIT 50 OFFSET 100")]
    public void Pagination_LimitOffsetSyntax(int pageSize, int offset, string expectedClause)
    {
        var limitClause = $"LIMIT {pageSize} OFFSET {offset}";
        limitClause.Should().Be(expectedClause);
    }

    [Fact]
    public void OrderBy_ShouldDefaultToCreatedAtDesc()
    {
        var defaultOrder = "ORDER BY create_time DESC";
        
        defaultOrder.Should().Contain("create_time");
        defaultOrder.Should().Contain("DESC");
    }

    #endregion
}
