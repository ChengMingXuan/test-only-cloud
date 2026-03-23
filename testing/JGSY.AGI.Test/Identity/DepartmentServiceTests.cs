using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Moq;
using Xunit;
using JGSY.AGI.Common.Core.Exceptions;
using JGSY.AGI.User.Business;
using JGSY.AGI.User.Entities;
using JGSY.AGI.User.Interfaces;

namespace JGSY.AGI.Test.Identity;

/// <summary>
/// 部门服务单元测试
/// </summary>
public class DepartmentServiceTests
{
    private readonly Mock<IDepartmentRepository> _deptRepoMock;
    private readonly Mock<IUserRepository> _userRepoMock;
    private readonly DepartmentService _service;

    public DepartmentServiceTests()
    {
        _deptRepoMock = new Mock<IDepartmentRepository>();
        _userRepoMock = new Mock<IUserRepository>();
        _service = new DepartmentService(_deptRepoMock.Object, _userRepoMock.Object);
    }

    #region GetByIdAsync

    [Fact]
    public async Task GetByIdAsync_Exists_ReturnsDtoWithUserCount()
    {
        // Arrange
        var id = Guid.NewGuid();
        var dept = CreateTestDepartment(id, "研发部", "RD001");
        _deptRepoMock.Setup(r => r.GetByIdAsync(id, It.IsAny<CancellationToken>()))
            .ReturnsAsync(dept);
        _userRepoMock.Setup(r => r.GetUserCountByDepartmentAsync(id, false, It.IsAny<CancellationToken>()))
            .ReturnsAsync(15);

        // Act
        var result = await _service.GetByIdAsync(id);

        // Assert
        result.Should().NotBeNull();
        result!.DepartmentName.Should().Be("研发部");
        result.DepartmentCode.Should().Be("RD001");
    }

    [Fact]
    public async Task GetByIdAsync_NotFound_ReturnsNull()
    {
        // Arrange
        _deptRepoMock.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((Department?)null);

        // Act
        var result = await _service.GetByIdAsync(Guid.NewGuid());

        // Assert
        result.Should().BeNull();
    }

    #endregion

    #region CreateAsync

    [Fact]
    public async Task CreateAsync_DuplicateCode_ThrowsBusinessException()
    {
        // Arrange
        _deptRepoMock.Setup(r => r.GetDeletedByCodeAsync("DUP01", It.IsAny<CancellationToken>()))
            .ReturnsAsync((Department?)null);
        _deptRepoMock.Setup(r => r.ExistsCodeAsync("DUP01", null, It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var request = new DepartmentCreateRequest
        {
            DepartmentName = "测试部门",
            DepartmentCode = "DUP01"
        };

        // Act & Assert
        await _service.Invoking(s => s.CreateAsync(request))
            .Should().ThrowAsync<BusinessException>();
    }

    [Fact]
    public async Task CreateAsync_DuplicateNameUnderSameParent_ThrowsBusinessException()
    {
        // Arrange
        _deptRepoMock.Setup(r => r.GetDeletedByCodeAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((Department?)null);
        _deptRepoMock.Setup(r => r.ExistsCodeAsync(It.IsAny<string>(), null, It.IsAny<CancellationToken>()))
            .ReturnsAsync(false);
        _deptRepoMock.Setup(r => r.ExistsNameAsync("重名部门", null, null, It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var request = new DepartmentCreateRequest
        {
            DepartmentName = "重名部门",
            DepartmentCode = "NEW01"
        };

        // Act & Assert
        await _service.Invoking(s => s.CreateAsync(request))
            .Should().ThrowAsync<BusinessException>();
    }

    [Fact]
    public async Task CreateAsync_ParentNotFound_ThrowsNotFoundException()
    {
        // Arrange
        var parentId = Guid.NewGuid();
        _deptRepoMock.Setup(r => r.GetDeletedByCodeAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((Department?)null);
        _deptRepoMock.Setup(r => r.ExistsCodeAsync(It.IsAny<string>(), null, It.IsAny<CancellationToken>()))
            .ReturnsAsync(false);
        _deptRepoMock.Setup(r => r.ExistsNameAsync(It.IsAny<string>(), parentId, null, It.IsAny<CancellationToken>()))
            .ReturnsAsync(false);
        _deptRepoMock.Setup(r => r.GetByIdAsync(parentId, It.IsAny<CancellationToken>()))
            .ReturnsAsync((Department?)null);

        var request = new DepartmentCreateRequest
        {
            DepartmentName = "子部门",
            DepartmentCode = "SUB01",
            ParentId = parentId
        };

        // Act & Assert
        await _service.Invoking(s => s.CreateAsync(request))
            .Should().ThrowAsync<NotFoundException>();
    }

    #endregion

    #region DeleteAsync

    [Fact]
    public async Task DeleteAsync_NotFound_ThrowsNotFoundException()
    {
        // Arrange
        _deptRepoMock.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((Department?)null);

        // Act & Assert
        await _service.Invoking(s => s.DeleteAsync(Guid.NewGuid()))
            .Should().ThrowAsync<NotFoundException>();
    }

    [Fact]
    public async Task DeleteAsync_HasChildren_ThrowsBusinessException()
    {
        // Arrange
        var id = Guid.NewGuid();
        var dept = CreateTestDepartment(id, "父部门", "P001");
        _deptRepoMock.Setup(r => r.GetByIdAsync(id, It.IsAny<CancellationToken>())).ReturnsAsync(dept);
        _deptRepoMock.Setup(r => r.HasChildrenAsync(id, It.IsAny<CancellationToken>())).ReturnsAsync(true);

        // Act & Assert
        await _service.Invoking(s => s.DeleteAsync(id))
            .Should().ThrowAsync<BusinessException>();
    }

    [Fact]
    public async Task DeleteAsync_HasUsers_ThrowsBusinessException()
    {
        // Arrange
        var id = Guid.NewGuid();
        var dept = CreateTestDepartment(id, "有用户部门", "U001");
        _deptRepoMock.Setup(r => r.GetByIdAsync(id, It.IsAny<CancellationToken>())).ReturnsAsync(dept);
        _deptRepoMock.Setup(r => r.HasChildrenAsync(id, It.IsAny<CancellationToken>())).ReturnsAsync(false);
        _deptRepoMock.Setup(r => r.HasUsersAsync(id, It.IsAny<CancellationToken>())).ReturnsAsync(true);

        // Act & Assert
        await _service.Invoking(s => s.DeleteAsync(id))
            .Should().ThrowAsync<BusinessException>();
    }

    [Fact]
    public async Task DeleteAsync_Valid_CallsRepoDelete()
    {
        // Arrange
        var id = Guid.NewGuid();
        var dept = CreateTestDepartment(id, "可删部门", "D001");
        _deptRepoMock.Setup(r => r.GetByIdAsync(id, It.IsAny<CancellationToken>())).ReturnsAsync(dept);
        _deptRepoMock.Setup(r => r.HasChildrenAsync(id, It.IsAny<CancellationToken>())).ReturnsAsync(false);
        _deptRepoMock.Setup(r => r.HasUsersAsync(id, It.IsAny<CancellationToken>())).ReturnsAsync(false);

        // Act
        await _service.DeleteAsync(id);

        // Assert
        _deptRepoMock.Verify(r => r.DeleteAsync(id, It.IsAny<CancellationToken>()), Times.Once);
    }

    #endregion

    #region GetTreeAsync

    [Fact]
    public async Task GetTreeAsync_DelegatesToRepo()
    {
        // Arrange
        var tree = new List<DepartmentTreeNode>
        {
            new() { Id = Guid.NewGuid(), DepartmentName = "根部门" }
        };
        _deptRepoMock.Setup(r => r.GetTreeAsync(It.IsAny<CancellationToken>()))
            .ReturnsAsync(tree);

        // Act
        var result = await _service.GetTreeAsync();

        // Assert
        result.Should().HaveCount(1);
    }

    #endregion

    #region GetStatisticsAsync

    [Fact]
    public async Task GetStatisticsAsync_DelegatesToRepo()
    {
        // Arrange
        var stats = new DepartmentStatistics();
        _deptRepoMock.Setup(r => r.GetStatisticsAsync(It.IsAny<CancellationToken>()))
            .ReturnsAsync(stats);

        // Act
        var result = await _service.GetStatisticsAsync();

        // Assert
        result.Should().NotBeNull();
    }

    #endregion

    #region GetUserCountAsync

    [Fact]
    public async Task GetUserCountAsync_DelegatesToUserRepo()
    {
        // Arrange
        var deptId = Guid.NewGuid();
        _userRepoMock.Setup(r => r.GetUserCountByDepartmentAsync(deptId, true, It.IsAny<CancellationToken>()))
            .ReturnsAsync(25);

        // Act
        var result = await _service.GetUserCountAsync(deptId, true);

        // Assert
        result.Should().Be(25);
    }

    #endregion

    #region DisableAsync

    [Fact]
    public async Task DisableAsync_NotFound_ThrowsNotFoundException()
    {
        // Arrange
        _deptRepoMock.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((Department?)null);

        // Act & Assert
        await _service.Invoking(s => s.DisableAsync(Guid.NewGuid()))
            .Should().ThrowAsync<NotFoundException>();
    }

    #endregion

    #region EnableAsync

    [Fact]
    public async Task EnableAsync_NotFound_ThrowsNotFoundException()
    {
        // Arrange
        _deptRepoMock.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((Department?)null);

        // Act & Assert
        await _service.Invoking(s => s.EnableAsync(Guid.NewGuid()))
            .Should().ThrowAsync<NotFoundException>();
    }

    #endregion

    #region MoveAsync

    [Fact]
    public async Task MoveAsync_NotFound_ThrowsNotFoundException()
    {
        // Arrange
        _deptRepoMock.Setup(r => r.GetByIdAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((Department?)null);

        // Act & Assert
        await _service.Invoking(s => s.MoveAsync(Guid.NewGuid(), new DepartmentMoveRequest()))
            .Should().ThrowAsync<NotFoundException>();
    }

    #endregion

    #region 辅助方法

    private static Department CreateTestDepartment(Guid id, string name, string code)
    {
        return new Department
        {
            Id = id,
            DepartmentName = name,
            DepartmentCode = code,
            Status = (int)DepartmentStatus.Active,
            SortOrder = 0,
            Level = 1
        };
    }

    #endregion
}
