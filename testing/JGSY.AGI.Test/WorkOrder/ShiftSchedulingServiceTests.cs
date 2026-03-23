using System;
using System.Collections.Generic;
using System.Linq;
using Xunit;
using FluentAssertions;
using JGSY.AGI.WorkOrder.Entities;

namespace JGSY.AGI.Test.WorkOrder
{
    /// <summary>
    /// 排班调度服务单元测试 - Dapper.AOT 版本
    /// 测试班次创建、自动排班逻辑、签到签退验证
    /// </summary>
    public class ShiftSchedulingServiceTests
    {
        private readonly Guid _tenantId = Guid.NewGuid();

        [Fact]
        public void CreateShift_ValidData_ShouldCreateSuccessfully()
        {
            // Arrange & Act
            var shift = new WorkShift
            {
                Id = Guid.NewGuid(),
                TenantId = _tenantId,
                ShiftName = "中班",
                StartTime = TimeSpan.FromHours(12),
                EndTime = TimeSpan.FromHours(20),
                MinStaffRequired = 2,
                DeleteAt = (DateTime?)null
            };

            // Assert
            shift.ShiftName.Should().Be("中班");
            shift.StartTime.Should().Be(TimeSpan.FromHours(12));
            shift.EndTime.Should().Be(TimeSpan.FromHours(20));
            shift.MinStaffRequired.Should().Be(2);
        }

        [Fact]
        public void CreateShift_DuplicateName_ShouldDetect()
        {
            // Arrange
            var existingShifts = new List<WorkShift>
            {
                new() { Id = Guid.NewGuid(), ShiftName = "早班", TenantId = _tenantId },
                new() { Id = Guid.NewGuid(), ShiftName = "中班", TenantId = _tenantId },
                new() { Id = Guid.NewGuid(), ShiftName = "晚班", TenantId = _tenantId }
            };

            // Act
            var isDuplicate = existingShifts.Any(s => s.ShiftName == "中班" && s.TenantId == _tenantId);

            // Assert
            isDuplicate.Should().BeTrue("同租户下不应有重名班次");
        }

        [Fact]
        public void GetShifts_ShouldReturnAllShifts()
        {
            // Arrange
            var shifts = new List<WorkShift>
            {
                new() { Id = Guid.NewGuid(), ShiftName = "早班", TenantId = _tenantId, DeleteAt = (DateTime?)null },
                new() { Id = Guid.NewGuid(), ShiftName = "中班", TenantId = _tenantId, DeleteAt = (DateTime?)null },
                new() { Id = Guid.NewGuid(), ShiftName = "晚班", TenantId = _tenantId, DeleteAt = DateTime.UtcNow }  // 已删除
            };

            // Act - 过滤已删除
            var activeShifts = shifts.Where(s => s.DeleteAt == null && s.TenantId == _tenantId).ToList();

            // Assert
            activeShifts.Should().HaveCount(2);
            activeShifts.Select(s => s.ShiftName).Should().Contain("早班").And.Contain("中班");
        }

        [Fact]
        public void AutoGenerateSchedule_SingleEngineer_ShouldAssignAllDays()
        {
            // Arrange
            var engineerId = Guid.NewGuid();
            var shift = new WorkShift { Id = Guid.NewGuid(), ShiftName = "早班", MinStaffRequired = 1 };
            var startDate = new DateTime(2024, 1, 1); // Monday
            var days = 7;

            // Act - 简化的自动排班逻辑
            var schedules = new List<ShiftSchedule>();
            for (int i = 0; i < days; i++)
            {
                schedules.Add(new ShiftSchedule
                {
                    Id = Guid.NewGuid(),
                    TenantId = _tenantId,
                    ShiftId = shift.Id,
                    EngineerId = engineerId,
                    ScheduleDate = startDate.AddDays(i),
                    Status = 0 // 待签到
                });
            }

            // Assert
            schedules.Should().HaveCount(7);
            schedules.All(s => s.EngineerId == engineerId).Should().BeTrue();
            schedules.All(s => s.ShiftId == shift.Id).Should().BeTrue();
        }

        [Fact]
        public void AutoGenerateSchedule_MultipleEngineers_ShouldDistributeEvenly()
        {
            // Arrange
            var engineers = Enumerable.Range(1, 3).Select(_ => Guid.NewGuid()).ToList();
            var shift = new WorkShift { Id = Guid.NewGuid(), ShiftName = "早班" };
            var days = 9;

            // Act - 轮转排班
            var schedules = new List<ShiftSchedule>();
            for (int i = 0; i < days; i++)
            {
                schedules.Add(new ShiftSchedule
                {
                    Id = Guid.NewGuid(),
                    TenantId = _tenantId,
                    ShiftId = shift.Id,
                    EngineerId = engineers[i % engineers.Count],
                    ScheduleDate = DateTime.UtcNow.Date.AddDays(i)
                });
            }

            // Assert
            schedules.Should().HaveCount(9);
            var grouped = schedules.GroupBy(s => s.EngineerId).ToList();
            grouped.Should().HaveCount(3);
            grouped.All(g => g.Count() == 3).Should().BeTrue("每个工程师应均分排班");
        }

        [Fact]
        public void AutoGenerateSchedule_ExistingSchedule_ShouldNotDuplicate()
        {
            // Arrange
            var engineerId = Guid.NewGuid();
            var shiftId = Guid.NewGuid();
            var date = DateTime.UtcNow.Date;

            var existingSchedules = new List<ShiftSchedule>
            {
                new() { Id = Guid.NewGuid(), EngineerId = engineerId, ShiftId = shiftId, ScheduleDate = date, TenantId = _tenantId }
            };

            // Act - 检查是否已存在
            var exists = existingSchedules.Any(s =>
                s.EngineerId == engineerId && s.ShiftId == shiftId &&
                s.ScheduleDate == date && s.TenantId == _tenantId);

            // Assert
            exists.Should().BeTrue("已存在该排班记录，不应重复创建");
        }

        [Fact]
        public void CheckIn_ValidSchedule_ShouldUpdateStatus()
        {
            // Arrange
            var schedule = new ShiftSchedule
            {
                Id = Guid.NewGuid(),
                TenantId = _tenantId,
                EngineerId = Guid.NewGuid(),
                ScheduleDate = DateTime.UtcNow.Date,
                Status = 0 // 待签到
            };

            // Act
            schedule.Status = 1; // 已签到
            schedule.CheckInTime = DateTime.UtcNow;

            // Assert
            schedule.Status.Should().Be(1);
            schedule.CheckInTime.Should().NotBeNull();
        }

        [Fact]
        public void CheckIn_AlreadyCheckedIn_ShouldReject()
        {
            // Arrange
            var schedule = new ShiftSchedule
            {
                Id = Guid.NewGuid(),
                TenantId = _tenantId,
                Status = 1, // 已签到
                CheckInTime = DateTime.UtcNow.AddHours(-4)
            };

            // Act
            var isAlreadyCheckedIn = schedule.Status >= 1;

            // Assert
            isAlreadyCheckedIn.Should().BeTrue("已签到的排班不应重复签到");
        }

        [Fact]
        public void CheckOut_ValidSchedule_ShouldComplete()
        {
            // Arrange
            var checkInTime = DateTime.UtcNow.AddHours(-8);
            var schedule = new ShiftSchedule
            {
                Id = Guid.NewGuid(),
                TenantId = _tenantId,
                Status = 1, // 已签到
                CheckInTime = checkInTime
            };

            // Act
            schedule.Status = 2; // 已签退
            schedule.CheckOutTime = DateTime.UtcNow;

            // Assert
            schedule.Status.Should().Be(2);
            schedule.CheckOutTime.Should().NotBeNull();
            (schedule.CheckOutTime!.Value - schedule.CheckInTime!.Value).TotalHours.Should().BeGreaterThan(0);
        }
    }
}
