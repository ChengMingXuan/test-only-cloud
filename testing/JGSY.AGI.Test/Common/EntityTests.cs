using FluentAssertions;
using JGSY.AGI.Common.Core.Entities;
using JGSY.AGI.Common.Core.Interfaces;
using Xunit;

namespace JGSY.AGI.Test.Common
{
    // Concrete implementation for testing abstract BaseEntity
    public class TestEntity : BaseEntity { }
    public class TestAuditedEntity : AuditedEntity { }

    public class BaseEntityTests
    {
        [Fact]
        public void BaseEntity_Id_DefaultShouldBeEmpty()
        {
            var entity = new TestEntity();
            entity.Id.Should().Be(Guid.Empty);
        }

        [Fact]
        public void BaseEntity_IsDeleted_DefaultShouldBeFalse()
        {
            var entity = new TestEntity();
            entity.DeleteAt.Should().BeNull();
        }

        [Fact]
        public void BaseEntity_CreateTime_DefaultShouldBeRecentUtc()
        {
            var before = DateTime.UtcNow.AddSeconds(-1);
            var entity = new TestEntity();
            var after = DateTime.UtcNow.AddSeconds(1);

            entity.CreateTime.Should().BeAfter(before);
            entity.CreateTime.Should().BeBefore(after);
        }

        [Fact]
        public void BaseEntity_CreatedAt_DefaultShouldBeRecentUtc()
        {
            var before = DateTime.UtcNow.AddSeconds(-1);
            var entity = new TestEntity();

            entity.CreateTime.Should().BeAfter(before);
        }

        [Fact]
        public void BaseEntity_TenantId_ShouldBeSettable()
        {
            var tenantId = Guid.NewGuid();
            var entity = new TestEntity { TenantId = tenantId };

            entity.TenantId.Should().Be(tenantId);
        }

        [Fact]
        public void BaseEntity_CreatorId_ShouldBeSettable()
        {
            var CreateBy = Guid.NewGuid();
            var entity = new TestEntity { CreateBy = CreateBy };

            entity.CreateBy.Should().Be(CreateBy);
        }

        [Fact]
        public void BaseEntity_ModifierId_ShouldBeSettable()
        {
            var UpdateBy = Guid.NewGuid();
            var entity = new TestEntity { UpdateBy = UpdateBy };

            entity.UpdateBy.Should().Be(UpdateBy);
        }

        [Fact]
        public void BaseEntity_IsDeleted_ShouldBeSettable()
        {
            var entity = new TestEntity { DeleteAt = DateTime.UtcNow };
            entity.DeleteAt.Should().NotBeNull();
        }

        [Fact]
        public void BaseEntity_ShouldImplementIFullAuditedTenantEntity()
        {
            var entity = new TestEntity();
            entity.Should().BeAssignableTo<IFullAuditedTenantEntity>();
        }

        [Fact]
        public void BaseEntity_ModifyTime_DefaultShouldBeRecentUtc()
        {
            var entity = new TestEntity();
            entity.UpdateTime.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(2));
        }

        [Fact]
        public void BaseEntity_UpdatedAt_DefaultShouldBeRecentUtc()
        {
            var entity = new TestEntity();
            entity.UpdateTime.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(2));
        }
    }

    public class AuditedEntityTests
    {
        [Fact]
        public void AuditedEntity_ShouldInheritFromBaseEntity()
        {
            var entity = new TestAuditedEntity();
            entity.Should().BeAssignableTo<BaseEntity>();
        }

        [Fact]
        public void AuditedEntity_ShouldHaveAllBaseProperties()
        {
            var entity = new TestAuditedEntity();

            entity.Id.Should().Be(Guid.Empty);
            entity.TenantId.Should().Be(Guid.Empty);
            entity.DeleteAt.Should().BeNull();
        }

        [Fact]
        public void AuditedEntity_DeletedTime_DefaultShouldBeNull()
        {
            var entity = new TestAuditedEntity();
            entity.DeleteAt.Should().BeNull();
        }

        [Fact]
        public void AuditedEntity_DeletedBy_DefaultShouldBeNull()
        {
            var entity = new TestAuditedEntity();
            entity.UpdateBy.Should().BeEmpty();
        }

        [Fact]
        public void AuditedEntity_RowVersion_DefaultShouldBeZero()
        {
            var entity = new TestAuditedEntity();
            entity.RowVersion.Should().Be(0);
        }

        [Fact]
        public void AuditedEntity_DeletedTime_ShouldBeSettable()
        {
            var now = DateTime.UtcNow;
            var entity = new TestAuditedEntity { DeleteAt = now };
            entity.DeleteAt.Should().Be(now);
        }

        [Fact]
        public void AuditedEntity_DeletedBy_ShouldBeSettable()
        {
            var userId = Guid.NewGuid();
            var entity = new TestAuditedEntity { UpdateBy = userId };
            entity.UpdateBy.Should().Be(userId);
        }

        [Fact]
        public void AuditedEntity_RowVersion_ShouldBeSettable()
        {
            var version = 1234L;
            var entity = new TestAuditedEntity { RowVersion = version };
            entity.RowVersion.Should().Be(version);
        }

        [Fact]
        public void AuditedEntity_FullPropertyRoundTrip()
        {
            var id = Guid.NewGuid();
            var tenantId = Guid.NewGuid();
            var CreateBy = Guid.NewGuid();
            var now = DateTime.UtcNow;

            var entity = new TestAuditedEntity
            {
                Id = id,
                TenantId = tenantId,
                CreateBy = CreateBy,
                UpdateBy = CreateBy,
                CreateTime = now,
                DeleteAt = (DateTime?)null,
                RowVersion = 255L
            };

            entity.Id.Should().Be(id);
            entity.TenantId.Should().Be(tenantId);
            entity.CreateBy.Should().Be(CreateBy);
            entity.CreateTime.Should().Be(now);
            entity.RowVersion.Should().Be(255L);
        }

        [Fact]
        public void AuditedEntity_SoftDelete_FullWorkflow()
        {
            var entity = new TestAuditedEntity
            {
                Id = Guid.NewGuid(),
                TenantId = Guid.NewGuid(),
                CreateBy = Guid.NewGuid()
            };

            // Initially not deleted
            entity.DeleteAt.Should().BeNull();
            entity.DeleteAt.Should().BeNull();
            entity.UpdateBy.Should().BeEmpty();

            // Soft delete
            var deleterId = Guid.NewGuid();
            var deleteTime = DateTime.UtcNow;
            entity.DeleteAt = DateTime.UtcNow;
            entity.DeleteAt = deleteTime;
            entity.UpdateBy = deleterId;

            entity.DeleteAt.Should().NotBeNull();
            entity.DeleteAt.Should().Be(deleteTime);
            entity.UpdateBy.Should().Be(deleterId);
        }
    }
}
