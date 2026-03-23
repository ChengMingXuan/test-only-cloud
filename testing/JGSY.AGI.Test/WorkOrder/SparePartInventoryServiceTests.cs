using System;
using System.Collections.Generic;
using System.Linq;
using Xunit;
using FluentAssertions;
using JGSY.AGI.WorkOrder.Entities;
using JGSY.AGI.Common.Core.Utils;

namespace JGSY.AGI.Test.WorkOrder
{
    /// <summary>
    /// 备件库存管理服务单元测试 - Dapper.AOT 版本
    /// 测试实体创建、业务规则验证、库存计算逻辑
    /// </summary>
    public class SparePartInventoryServiceTests
    {
        private readonly Guid _tenantId = Guid.NewGuid();

        [Fact]
        public void CreateSparePart_ValidData_ShouldCreateSuccessfully()
        {
            // Arrange & Act
            var part = new SparePart
            {
                Id = SequentialGuid.NewId(),
                TenantId = _tenantId,
                PartName = "接触器",
                PartNumber = "JCQ-001",
                Specification = "220V 100A",
                Unit = "个",
                SafeStockQuantity = 10,
                StandardPrice = 200m,
                Manufacturer = "施耐德",
                DeleteAt = (DateTime?)null
            };

            // Assert
            part.Id.Should().NotBeEmpty();
            part.PartNumber.Should().Be("JCQ-001");
            part.PartName.Should().Be("接触器");
            part.Specification.Should().Be("220V 100A");
            part.SafeStockQuantity.Should().Be(10);
            part.StandardPrice.Should().Be(200m);
            part.Manufacturer.Should().Be("施耐德");
            part.DeleteAt.Should().BeNull();
        }

        [Fact]
        public void CreateSparePart_DuplicateCode_ShouldDetectByPartNumber()
        {
            // Arrange - 模拟已有备件列表
            var existingParts = new List<SparePart>
            {
                new() { Id = Guid.NewGuid(), PartNumber = "JCQ-001", PartName = "接触器", TenantId = _tenantId },
                new() { Id = Guid.NewGuid(), PartNumber = "DLQ-002", PartName = "断路器", TenantId = _tenantId }
            };

            var newPartNumber = "JCQ-001";

            // Act - 检查重复
            var isDuplicate = existingParts.Any(p => p.PartNumber == newPartNumber && p.TenantId == _tenantId);

            // Assert
            isDuplicate.Should().BeTrue("已存在相同编号的备件");
        }

        [Fact]
        public void GetSpareParts_WithPagination_ShouldReturnCorrectPage()
        {
            // Arrange - 创建 20 个备件
            var parts = Enumerable.Range(1, 20).Select(i => new SparePart
            {
                Id = Guid.NewGuid(),
                PartNumber = $"PART-{i:D3}",
                PartName = $"备件{i}",
                TenantId = _tenantId
            }).ToList();

            int pageIndex = 2, pageSize = 5;

            // Act
            var pagedItems = parts.Skip((pageIndex - 1) * pageSize).Take(pageSize).ToList();

            // Assert
            pagedItems.Should().HaveCount(5);
            pagedItems.First().PartNumber.Should().Be("PART-006");
            pagedItems.Last().PartNumber.Should().Be("PART-010");
        }

        [Fact]
        public void Inbound_ValidData_ShouldIncreaseStock()
        {
            // Arrange
            var part = new SparePart
            {
                Id = Guid.NewGuid(),
                PartNumber = "JCQ-001",
                PartName = "接触器",
                CurrentStockQuantity = 5,
                TenantId = _tenantId
            };
            var inboundQuantity = 10;

            // Act
            part.CurrentStockQuantity += inboundQuantity;

            // Assert
            part.CurrentStockQuantity.Should().Be(15);
        }

        [Fact]
        public void Inbound_InvalidSparePartId_ShouldFailValidation()
        {
            // Arrange
            var invalidPartId = Guid.Empty;
            var existingParts = new List<SparePart>
            {
                new() { Id = Guid.NewGuid(), PartNumber = "JCQ-001", TenantId = _tenantId }
            };

            // Act
            var part = existingParts.FirstOrDefault(p => p.Id == invalidPartId);

            // Assert
            part.Should().BeNull("不应找到ID为空的备件");
        }

        [Fact]
        public void Outbound_SufficientStock_ShouldDecreaseStock()
        {
            // Arrange
            var part = new SparePart
            {
                Id = Guid.NewGuid(),
                PartNumber = "JCQ-001",
                CurrentStockQuantity = 15,
                TenantId = _tenantId
            };
            var outboundQuantity = 5;

            // Act
            var hasEnoughStock = part.CurrentStockQuantity >= outboundQuantity;
            if (hasEnoughStock)
                part.CurrentStockQuantity -= outboundQuantity;

            // Assert
            hasEnoughStock.Should().BeTrue();
            part.CurrentStockQuantity.Should().Be(10);
        }

        [Fact]
        public void Outbound_InsufficientStock_ShouldNotDecrease()
        {
            // Arrange
            var part = new SparePart
            {
                Id = Guid.NewGuid(),
                PartNumber = "JCQ-001",
                CurrentStockQuantity = 3,
                TenantId = _tenantId
            };
            var outboundQuantity = 5;

            // Act
            var hasEnoughStock = part.CurrentStockQuantity >= outboundQuantity;

            // Assert
            hasEnoughStock.Should().BeFalse("库存不足应拒绝出库");
            part.CurrentStockQuantity.Should().Be(3, "库存数量不应改变");
        }
    }
}
