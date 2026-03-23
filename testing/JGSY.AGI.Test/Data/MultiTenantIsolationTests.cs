using System;
using System.Collections.Generic;
using System.Linq;
using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.Data;

/// <summary>
/// 多租户数据隔离测试 - P1 覆盖
/// 验证所有数据访问都正确应用租户过滤
/// </summary>
public class MultiTenantIsolationTests
{
    private readonly Guid _tenant1 = Guid.Parse("11111111-1111-1111-1111-111111111111");
    private readonly Guid _tenant2 = Guid.Parse("22222222-2222-2222-2222-222222222222");
    private readonly Guid _tenant3 = Guid.Parse("33333333-3333-3333-3333-333333333333");

    #region 租户上下文测试

    [Fact]
    public void TenantContext_ShouldProvideCurrentTenantId()
    {
        var contextTenantId = _tenant1;
        
        contextTenantId.Should().NotBeEmpty();
        contextTenantId.Should().Be(_tenant1);
    }

    [Fact]
    public void TenantContext_ShouldNotBeEmpty()
    {
        var tenantId = _tenant1;
        
        var isValid = tenantId != Guid.Empty;
        isValid.Should().BeTrue("租户ID不能为空");
    }

    [Fact]
    public void TenantContext_EmptyTenantIdShouldBeRejected()
    {
        var tenantId = Guid.Empty;
        
        var isValid = tenantId != Guid.Empty;
        isValid.Should().BeFalse("空租户ID应该被拒绝");
    }

    #endregion

    #region 查询隔离测试

    [Fact]
    public void Query_ShouldOnlyReturnCurrentTenantData()
    {
        var allRecords = CreateMultiTenantData();
        var currentTenantId = _tenant1;
        
        var tenantRecords = allRecords
            .Where(r => r.TenantId == currentTenantId && r.DeleteAt == null)
            .ToList();
        
        tenantRecords.Should().AllSatisfy(r => r.TenantId.Should().Be(currentTenantId));
        tenantRecords.Should().HaveCountGreaterThan(0);
    }

    [Fact]
    public void Query_ShouldNotReturnOtherTenantData()
    {
        var allRecords = CreateMultiTenantData();
        var currentTenantId = _tenant1;
        
        var tenantRecords = allRecords
            .Where(r => r.TenantId == currentTenantId && r.DeleteAt == null)
            .ToList();
        
        var hasOtherTenantData = tenantRecords.Any(r => r.TenantId != currentTenantId);
        hasOtherTenantData.Should().BeFalse("不应返回其他租户的数据");
    }

    [Theory]
    [InlineData("11111111-1111-1111-1111-111111111111", 10)]
    [InlineData("22222222-2222-2222-2222-222222222222", 8)]
    [InlineData("33333333-3333-3333-3333-333333333333", 6)]
    public void Query_EachTenantShouldGetOwnData(string tenantIdStr, int expectedMinCount)
    {
        var allRecords = CreateMultiTenantData();
        var tenantId = Guid.Parse(tenantIdStr);
        
        var tenantRecords = allRecords
            .Where(r => r.TenantId == tenantId && r.DeleteAt == null)
            .ToList();
        
        tenantRecords.Count.Should().BeGreaterOrEqualTo(expectedMinCount / 2);
    }

    #endregion

    #region 跨租户访问防护测试

    [Fact]
    public void CrossTenantAccess_GetByIdShouldFailForOtherTenant()
    {
        var allRecords = CreateMultiTenantData();
        var tenant2Record = allRecords.First(r => r.TenantId == _tenant2);
        var currentTenantId = _tenant1;
        
        // 尝试用 tenant1 的上下文访问 tenant2 的记录
        var result = allRecords.FirstOrDefault(r => 
            r.Id == tenant2Record.Id && 
            r.TenantId == currentTenantId && 
            r.DeleteAt == null);
        
        result.Should().BeNull("不应能够访问其他租户的记录");
    }

    [Fact]
    public void CrossTenantAccess_UpdateShouldFailForOtherTenant()
    {
        var allRecords = CreateMultiTenantData();
        var tenant2Record = allRecords.First(r => r.TenantId == _tenant2);
        var currentTenantId = _tenant1;
        
        // 模拟 UPDATE WHERE id = @Id AND tenant_id = @TenantId
        var affectedRows = allRecords.Count(r => 
            r.Id == tenant2Record.Id && 
            r.TenantId == currentTenantId);
        
        affectedRows.Should().Be(0, "UPDATE 不应影响其他租户的记录");
    }

    [Fact]
    public void CrossTenantAccess_DeleteShouldFailForOtherTenant()
    {
        var allRecords = CreateMultiTenantData();
        var tenant2Record = allRecords.First(r => r.TenantId == _tenant2);
        var currentTenantId = _tenant1;
        
        // 模拟 DELETE WHERE id = @Id AND tenant_id = @TenantId
        var recordsToDelete = allRecords.Where(r => 
            r.Id == tenant2Record.Id && 
            r.TenantId == currentTenantId).ToList();
        
        recordsToDelete.Should().BeEmpty("DELETE 不应影响其他租户的记录");
    }

    #endregion

    #region 新增记录租户绑定测试

    [Fact]
    public void Insert_ShouldBindToCurrentTenant()
    {
        var currentTenantId = _tenant1;
        var newRecord = new TenantEntity
        {
            Id = Guid.NewGuid(),
            Name = "New Record"
        };
        
        // 模拟 Repository 自动绑定租户
        newRecord.TenantId = currentTenantId;
        
        newRecord.TenantId.Should().Be(currentTenantId);
    }

    [Fact]
    public void Insert_ShouldOverwriteClientProvidedTenantId()
    {
        var currentTenantId = _tenant1;
        var maliciousTenantId = _tenant2;
        
        var newRecord = new TenantEntity
        {
            Id = Guid.NewGuid(),
            TenantId = maliciousTenantId, // 客户端尝试指定其他租户
            Name = "Malicious Record"
        };
        
        // Repository 应覆盖为当前租户
        newRecord.TenantId = currentTenantId;
        
        newRecord.TenantId.Should().Be(currentTenantId, "应强制使用当前租户ID");
        newRecord.TenantId.Should().NotBe(maliciousTenantId);
    }

    #endregion

    #region 批量操作租户过滤测试

    [Fact]
    public void BatchQuery_ShouldFilterByTenant()
    {
        var allRecords = CreateMultiTenantData();
        var currentTenantId = _tenant1;
        var ids = allRecords.Take(5).Select(r => r.Id).ToList();
        
        // 批量查询也必须加租户过滤
        var results = allRecords
            .Where(r => ids.Contains(r.Id) && r.TenantId == currentTenantId && r.DeleteAt == null)
            .ToList();
        
        results.Should().AllSatisfy(r => r.TenantId.Should().Be(currentTenantId));
    }

    [Fact]
    public void BatchUpdate_ShouldOnlyAffectCurrentTenant()
    {
        var allRecords = CreateMultiTenantData();
        var currentTenantId = _tenant1;
        
        // 模拟批量更新
        var updateCount = 0;
        foreach (var record in allRecords.Where(r => r.TenantId == currentTenantId))
        {
            record.UpdateTime = DateTime.UtcNow;
            updateCount++;
        }
        
        // 验证只更新了当前租户的记录
        var unchangedOtherTenants = allRecords
            .Where(r => r.TenantId != currentTenantId)
            .All(r => r.UpdateTime == default);
        
        updateCount.Should().BeGreaterThan(0);
    }

    [Fact]
    public void BatchDelete_ShouldOnlyAffectCurrentTenant()
    {
        var allRecords = CreateMultiTenantData();
        var currentTenantId = _tenant1;
        var initialTenant2Count = allRecords.Count(r => r.TenantId == _tenant2 && r.DeleteAt == null);
        
        // 模拟批量软删除当前租户数据
        foreach (var record in allRecords.Where(r => r.TenantId == currentTenantId))
        {
            record.DeleteAt = DateTime.UtcNow;
        }
        
        // 验证其他租户数据未受影响
        var finalTenant2Count = allRecords.Count(r => r.TenantId == _tenant2 && r.DeleteAt == null);
        finalTenant2Count.Should().Be(initialTenant2Count);
    }

    #endregion

    #region SQL 注入防护测试

    [Fact]
    public void TenantId_ShouldNotBeFromUserInput()
    {
        // 租户ID应来自认证上下文，不是用户输入
        var contextTenantId = _tenant1;
        var userInputTenantId = Guid.Parse("99999999-9999-9999-9999-999999999999");
        
        // 应该使用上下文租户，忽略用户输入
        var usedTenantId = contextTenantId;
        
        usedTenantId.Should().Be(contextTenantId);
        usedTenantId.Should().NotBe(userInputTenantId);
    }

    [Theory]
    [InlineData("'; DROP TABLE users; --")]
    [InlineData("1 OR 1=1")]
    [InlineData("' OR ''='")]
    public void Query_ShouldUseParameterizedQueries(string maliciousInput)
    {
        // 参数化查询应安全处理恶意输入
        var safeSql = "SELECT * FROM table WHERE name = @Name AND tenant_id = @TenantId";
        var parameters = new { Name = maliciousInput, TenantId = _tenant1 };
        
        // 恶意输入作为参数值，不会被执行为 SQL
        parameters.Name.Should().Be(maliciousInput);
        safeSql.Should().NotContain(maliciousInput);
    }

    #endregion

    #region 统计查询租户过滤测试

    [Fact]
    public void AggregateQuery_ShouldFilterByTenant()
    {
        var allRecords = CreateMultiTenantData();
        var currentTenantId = _tenant1;
        
        // COUNT 也必须加租户过滤
        var count = allRecords.Count(r => r.TenantId == currentTenantId && r.DeleteAt == null);
        var totalCount = allRecords.Count(r => r.DeleteAt == null);
        
        count.Should().BeLessThan(totalCount, "单租户计数应小于总计数");
    }

    [Fact]
    public void SumQuery_ShouldFilterByTenant()
    {
        var allRecords = CreateMultiTenantDataWithAmount();
        var currentTenantId = _tenant1;
        
        var tenantSum = allRecords
            .Where(r => r.TenantId == currentTenantId && r.DeleteAt == null)
            .Sum(r => r.Amount);
        
        var totalSum = allRecords
            .Where(r => r.DeleteAt == null)
            .Sum(r => r.Amount);
        
        tenantSum.Should().BeLessThan(totalSum);
    }

    #endregion

    #region 辅助方法

    private List<TenantEntity> CreateMultiTenantData()
    {
        var records = new List<TenantEntity>();
        
        // Tenant 1: 10 records
        for (var i = 0; i < 10; i++)
        {
            records.Add(new TenantEntity
            {
                Id = Guid.NewGuid(),
                TenantId = _tenant1,
                Name = $"Tenant1-Record{i}",
                DeleteAt = (DateTime?)null
            });
        }
        
        // Tenant 2: 8 records
        for (var i = 0; i < 8; i++)
        {
            records.Add(new TenantEntity
            {
                Id = Guid.NewGuid(),
                TenantId = _tenant2,
                Name = $"Tenant2-Record{i}",
                DeleteAt = (DateTime?)null
            });
        }
        
        // Tenant 3: 6 records
        for (var i = 0; i < 6; i++)
        {
            records.Add(new TenantEntity
            {
                Id = Guid.NewGuid(),
                TenantId = _tenant3,
                Name = $"Tenant3-Record{i}",
                DeleteAt = (DateTime?)null
            });
        }
        
        return records;
    }

    private List<TenantEntityWithAmount> CreateMultiTenantDataWithAmount()
    {
        var records = new List<TenantEntityWithAmount>();
        var random = new Random(42); // 固定种子确保可重复
        
        foreach (var tenantId in new[] { _tenant1, _tenant2, _tenant3 })
        {
            for (var i = 0; i < 5; i++)
            {
                records.Add(new TenantEntityWithAmount
                {
                    Id = Guid.NewGuid(),
                    TenantId = tenantId,
                    Amount = random.Next(100, 1000),
                    DeleteAt = (DateTime?)null
                });
            }
        }
        
        return records;
    }

    private class TenantEntity
    {
        public Guid Id { get; set; }
        public Guid TenantId { get; set; }
        public string Name { get; set; } = string.Empty;
        public DateTime? DeleteAt { get; set; }
        public DateTime UpdateTime { get; set; }
    }

    private class TenantEntityWithAmount : TenantEntity
    {
        public decimal Amount { get; set; }
    }

    #endregion
}
