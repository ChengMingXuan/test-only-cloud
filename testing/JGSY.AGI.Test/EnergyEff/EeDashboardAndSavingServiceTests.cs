using Xunit;
using Moq;
using FluentAssertions;
using JGSY.AGI.Operations.Modules.EnergyEff.Business;
using JGSY.AGI.Operations.Modules.EnergyEff.Interfaces;
using JGSY.AGI.Operations.Modules.EnergyEff.Entities;
using JGSY.AGI.Operations.Modules.EnergyEff.Models;
using JGSY.AGI.Common.Core.Interfaces;

namespace JGSY.AGI.Test.EnergyEff;

/// <summary>
/// 能效 Dashboard 服务单元测试
/// 覆盖: 聚合计算、能力等级判定(L0/L1/L2/L3)
/// </summary>
public class EeDashboardServiceTests
{
    private readonly Mock<IMeterConfigRepository> _meterRepo = new();
    private readonly Mock<IConsumptionRepository> _consumptionRepo = new();
    private readonly Mock<ISavingRecordRepository> _savingRepo = new();
    private readonly Mock<IDiagnosisReportRepository> _diagnosisRepo = new();
    private readonly Mock<ITenantContext> _ctx = new();
    private readonly EeDashboardService _service;

    private readonly Guid _tenantId = Guid.NewGuid();

    public EeDashboardServiceTests()
    {
        _ctx.Setup(c => c.TenantId).Returns(_tenantId);
        _service = new EeDashboardService(_meterRepo.Object, _consumptionRepo.Object,
            _savingRepo.Object, _diagnosisRepo.Object, _ctx.Object);
    }

    [Fact]
    public async Task GetDashboardAsync_AllData_ReturnsL3()
    {
        // Arrange — 有节能记录 + 诊断报告 → L3
        _meterRepo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(10);
        _meterRepo.Setup(r => r.GetOnlineCountAsync(_tenantId)).ReturnsAsync(8);
        _consumptionRepo.Setup(r => r.GetTotalKwhAsync(_tenantId, null)).ReturnsAsync(50000m);
        _savingRepo.Setup(r => r.GetTotalSavingKwhAsync(_tenantId)).ReturnsAsync(5000m);
        _diagnosisRepo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(3);
        _savingRepo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(2);

        // Act
        var result = await _service.GetDashboardAsync();

        // Assert
        result.MeterCount.Should().Be(10);
        result.OnlineMeterCount.Should().Be(8);
        result.TotalConsumptionKwh.Should().Be(50000m);
        result.TotalSavingKwh.Should().Be(5000m);
        result.DiagnosisCount.Should().Be(3);
        result.CapabilityLevel.Should().Be("L3");
    }

    [Fact]
    public async Task GetDashboardAsync_OnlyDiagnosis_ReturnsL2()
    {
        // Arrange — 有诊断但无节能记录 → L2
        _meterRepo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(5);
        _meterRepo.Setup(r => r.GetOnlineCountAsync(_tenantId)).ReturnsAsync(3);
        _consumptionRepo.Setup(r => r.GetTotalKwhAsync(_tenantId, null)).ReturnsAsync(10000m);
        _savingRepo.Setup(r => r.GetTotalSavingKwhAsync(_tenantId)).ReturnsAsync(0m);
        _diagnosisRepo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(2);
        _savingRepo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(0);

        // Act
        var result = await _service.GetDashboardAsync();

        // Assert
        result.CapabilityLevel.Should().Be("L2");
    }

    [Fact]
    public async Task GetDashboardAsync_OnlyMeters_ReturnsL1()
    {
        // Arrange — 有计量表但无诊断和节能 → L1
        _meterRepo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(3);
        _meterRepo.Setup(r => r.GetOnlineCountAsync(_tenantId)).ReturnsAsync(2);
        _consumptionRepo.Setup(r => r.GetTotalKwhAsync(_tenantId, null)).ReturnsAsync(1000m);
        _savingRepo.Setup(r => r.GetTotalSavingKwhAsync(_tenantId)).ReturnsAsync(0m);
        _diagnosisRepo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(0);
        _savingRepo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(0);

        // Act
        var result = await _service.GetDashboardAsync();

        // Assert
        result.CapabilityLevel.Should().Be("L1");
    }

    [Fact]
    public async Task GetDashboardAsync_NoData_ReturnsL0()
    {
        // Arrange — 无任何数据 → L0
        _meterRepo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(0);
        _meterRepo.Setup(r => r.GetOnlineCountAsync(_tenantId)).ReturnsAsync(0);
        _consumptionRepo.Setup(r => r.GetTotalKwhAsync(_tenantId, null)).ReturnsAsync(0m);
        _savingRepo.Setup(r => r.GetTotalSavingKwhAsync(_tenantId)).ReturnsAsync(0m);
        _diagnosisRepo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(0);
        _savingRepo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(0);

        // Act
        var result = await _service.GetDashboardAsync();

        // Assert
        result.CapabilityLevel.Should().Be("L0");
        result.MeterCount.Should().Be(0);
    }

    [Fact]
    public async Task GetDashboardAsync_SavingWithoutDiagnosis_ReturnsL1()
    {
        // Arrange — 有节能记录但无诊断 → L1 (savingCount>0 && diagnosisCount>0 才是 L3)
        _meterRepo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(5);
        _meterRepo.Setup(r => r.GetOnlineCountAsync(_tenantId)).ReturnsAsync(3);
        _consumptionRepo.Setup(r => r.GetTotalKwhAsync(_tenantId, null)).ReturnsAsync(20000m);
        _savingRepo.Setup(r => r.GetTotalSavingKwhAsync(_tenantId)).ReturnsAsync(1000m);
        _diagnosisRepo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(0);
        _savingRepo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(3);

        // Act
        var result = await _service.GetDashboardAsync();

        // Assert — 有 meters → L1 (diagnosisCount=0 → 不是 L2, savingCount>0 但 diagnosisCount=0 → 不是 L3)
        result.CapabilityLevel.Should().Be("L1");
    }
}

/// <summary>
/// 能效节能记录服务单元测试
/// 覆盖: 节能率/节能量计算、创建记录
/// </summary>
public class SavingServiceTests
{
    private readonly Mock<ISavingRecordRepository> _repo = new();
    private readonly Mock<ITenantContext> _ctx = new();
    private readonly SavingService _service;

    private readonly Guid _tenantId = Guid.NewGuid();

    public SavingServiceTests()
    {
        _ctx.Setup(c => c.TenantId).Returns(_tenantId);
        _ctx.Setup(c => c.UserId).Returns(Guid.NewGuid());
        _service = new SavingService(_repo.Object, _ctx.Object);
    }

    [Fact]
    public async Task CreateAsync_CalculatesSavingKwhAndRate()
    {
        // Arrange — baseline=1000, actual=800 → savingKwh=200, savingRate=20%
        var dto = new EeSavingRecordCreateDto
        {
            ProjectName = "LED改造项目",
            SavingType = 1,
            BaselineKwh = 1000m,
            ActualKwh = 800m,
            StartDate = DateTime.UtcNow.AddMonths(-1),
            EndDate = DateTime.UtcNow
        };

        // Act
        var id = await _service.CreateAsync(dto);

        // Assert
        id.Should().NotBeEmpty();
        _repo.Verify(r => r.InsertAsync(It.Is<EeSavingRecord>(e =>
            e.ProjectName == "LED改造项目" &&
            e.SavingKwh == 200m &&
            e.SavingRate == 20m && // (200/1000)*100 = 20
            e.SavingYuan == 0m && // 固定为 0
            e.TenantId == _tenantId)), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_ZeroBaseline_SavingRateIsZero()
    {
        // Arrange — baseline=0 → 不除零, savingRate=0
        var dto = new EeSavingRecordCreateDto
        {
            ProjectName = "新项目",
            SavingType = 2,
            BaselineKwh = 0m,
            ActualKwh = 100m
        };

        // Act
        var id = await _service.CreateAsync(dto);

        // Assert
        id.Should().NotBeEmpty();
        _repo.Verify(r => r.InsertAsync(It.Is<EeSavingRecord>(e =>
            e.SavingKwh == -100m && // 0 - 100 = -100
            e.SavingRate == 0m)), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_ActualExceedsBaseline_NegativeSaving()
    {
        // Arrange — actual > baseline → 负节能
        var dto = new EeSavingRecordCreateDto
        {
            ProjectName = "超标项目",
            SavingType = 1,
            BaselineKwh = 500m,
            ActualKwh = 600m
        };

        // Act
        var id = await _service.CreateAsync(dto);

        // Assert
        _repo.Verify(r => r.InsertAsync(It.Is<EeSavingRecord>(e =>
            e.SavingKwh == -100m && // 500 - 600 = -100
            e.SavingRate == -20m)), Times.Once); // (-100/500)*100 = -20
    }

    [Fact]
    public async Task GetListAsync_ReturnsMappedPagedResult()
    {
        // Arrange
        var records = new List<EeSavingRecord>
        {
            new() { Id = Guid.NewGuid(), ProjectName = "P1", SavingType = 1, BaselineKwh = 1000, ActualKwh = 800, SavingKwh = 200, SavingRate = 20, Verified = true },
            new() { Id = Guid.NewGuid(), ProjectName = "P2", SavingType = 2, BaselineKwh = 500, ActualKwh = 500, SavingKwh = 0, SavingRate = 0, Verified = false }
        };
        _repo.Setup(r => r.GetListAsync(_tenantId, null, 1, 10)).ReturnsAsync(records);
        _repo.Setup(r => r.GetCountAsync(_tenantId, null)).ReturnsAsync(5);

        // Act
        var result = await _service.GetListAsync(null, 1, 10);

        // Assert
        result.Items.Should().HaveCount(2);
        result.Total.Should().Be(5);
        result.Page.Should().Be(1);
        result.PageSize.Should().Be(10);
        result.Items[0].ProjectName.Should().Be("P1");
        result.Items[0].SavingKwh.Should().Be(200);
        result.Items[0].Verified.Should().BeTrue();
    }
}
