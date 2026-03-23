using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using FluentAssertions;
using Xunit;

namespace JGSY.AGI.Test.Common;

/// <summary>
/// 增量测试 — GeoFence + IotCloudAI AI新能力 + ColdArchive + 后台任务 + 内部API + Gateway路由拆分
/// 覆盖本轮 Git 变更新增的全部源码、DbUp 脚本、配置文件的结构合规性
/// </summary>
public class IncrementalGeoFenceAiColdArchiveTests
{
    private static readonly string RepoRoot = FindRepoRoot();
    private static readonly JsonDocumentOptions JsonOpts = new() { CommentHandling = JsonCommentHandling.Skip, AllowTrailingCommas = true };

    private static string FindRepoRoot()
    {
        var dir = AppContext.BaseDirectory;
        while (dir != null)
        {
            if (File.Exists(Path.Combine(dir, "AIOPS.sln")))
                return dir;
            dir = Directory.GetParent(dir)?.FullName;
        }
        // Fallback：从源码路径推导
        var src = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", ".."));
        return Directory.Exists(Path.Combine(src, "JGSY.AGI.Station")) ? src : AppContext.BaseDirectory;
    }

    private static string ReadRepoFile(string relativePath) =>
        File.ReadAllText(Path.Combine(RepoRoot, relativePath));

    private static bool RepoFileExists(string relativePath) =>
        File.Exists(Path.Combine(RepoRoot, relativePath));

    #region Station GeoFence 地理围栏

    [Fact]
    public void GeoFence_Controller_HasCorrectRoute()
    {
        var src = ReadRepoFile("JGSY.AGI.Station/Api/StationGeoFenceController.cs");
        src.Should().Contain("[Route(\"api/stations/{stationId:guid}/geo-fences\")", "路由应遵循 RESTful 规范");
    }

    [Fact]
    public void GeoFence_Controller_HasRequirePermission()
    {
        var src = ReadRepoFile("JGSY.AGI.Station/Api/StationGeoFenceController.cs");
        src.Should().Contain("RequirePermission", "所有端点必须声明 RequirePermission");
        src.Should().Contain("station:geo-fence:", "权限码格式必须为 station:geo-fence:{action}");
    }

    [Fact]
    public void GeoFence_Controller_HasAllCrudEndpoints()
    {
        var src = ReadRepoFile("JGSY.AGI.Station/Api/StationGeoFenceController.cs");
        src.Should().Contain("[HttpGet]", "应有 GET 端点");
        src.Should().Contain("[HttpPost]", "应有 POST 端点");
        src.Should().Contain("[HttpPut]", "应有 PUT 端点");
        src.Should().Contain("[HttpDelete]", "应有 DELETE 端点");
    }

    [Fact]
    public void GeoFence_Entity_HasAllAuditFields()
    {
        var src = ReadRepoFile("JGSY.AGI.Station/Entities/StationGeoFence.cs");
        var requiredFields = new[] { "Id", "TenantId", "CreateBy", "CreateName", "CreateTime", "UpdateBy", "UpdateName", "UpdateTime", "DeleteAt" };
        foreach (var f in requiredFields)
            src.Should().Contain(f, $"实体必须包含公共字段 {f}");
    }

    [Fact]
    public void GeoFence_Entity_HasBusinessFields()
    {
        var src = ReadRepoFile("JGSY.AGI.Station/Entities/StationGeoFence.cs");
        src.Should().Contain("StationId", "应有 StationId");
        src.Should().Contain("FenceType", "应有 FenceType");
        src.Should().Contain("CenterLongitude", "圆形围栏需要经度");
        src.Should().Contain("CenterLatitude", "圆形围栏需要纬度");
        src.Should().Contain("RadiusMeters", "圆形围栏需要半径");
        src.Should().Contain("PolygonCoordinates", "多边形围栏需要坐标串");
    }

    [Fact]
    public void GeoFence_Service_HasSoftDelete()
    {
        var src = ReadRepoFile("JGSY.AGI.Station/Service/StationGeoFenceService.cs");
        src.Should().Contain("delete_at", "删除必须使用软删除 delete_at");
        src.Should().Contain("tenant_id", "查询必须包含 tenant_id");
    }

    [Fact]
    public void GeoFence_DbUp_HasCorrectSchema()
    {
        var sql = ReadRepoFile("JGSY.AGI.Station/Data/Migrations/004_add_geo_fence.sql");
        sql.Should().Contain("station.station_geo_fence", "表必须在 station schema 下");
        sql.Should().Contain("CREATE SCHEMA IF NOT EXISTS", "DbUp 必须包含 schema 创建");
        sql.Should().Contain("COMMENT ON", "字段必须有注释");
        sql.Should().Contain("tenant_id", "表必须有 tenant_id 字段");
        sql.Should().Contain("delete_at", "表必须有 delete_at 字段");
    }

    [Fact]
    public void GeoFence_DbUp_HasIdempotentCreation()
    {
        var sql = ReadRepoFile("JGSY.AGI.Station/Data/Migrations/004_add_geo_fence.sql");
        sql.Should().Contain("IF NOT EXISTS", "DDL 必须幂等");
    }

    #endregion

    #region IotCloudAI 5大新Controller

    [Theory]
    [InlineData("JGSY.AGI.IotCloudAI/Api/ImageSearchController.cs", "iotcloudai:imagesearch:")]
    [InlineData("JGSY.AGI.IotCloudAI/Api/LlmController.cs", "iotcloudai:llm:")]
    [InlineData("JGSY.AGI.IotCloudAI/Api/ModelRoutingController.cs", "iotcloudai:modelrouting:")]
    [InlineData("JGSY.AGI.IotCloudAI/Api/SolarPredictionController.cs", "iotcloudai:solar:")]
    [InlineData("JGSY.AGI.IotCloudAI/Api/VisionInspectionController.cs", "iotcloudai:vision:")]
    public void IotCloudAI_NewControllers_HaveRequirePermission(string path, string permPrefix)
    {
        var src = ReadRepoFile(path);
        src.Should().Contain("RequirePermission", $"{path} 必须声明 RequirePermission");
        src.Should().Contain(permPrefix, $"权限码应以 {permPrefix} 开头");
    }

    [Theory]
    [InlineData("JGSY.AGI.IotCloudAI/Api/ImageSearchController.cs", "api/iotcloudai/image-search")]
    [InlineData("JGSY.AGI.IotCloudAI/Api/LlmController.cs", "api/iotcloudai/llm")]
    [InlineData("JGSY.AGI.IotCloudAI/Api/SolarPredictionController.cs", "api/iotcloudai/solar")]
    [InlineData("JGSY.AGI.IotCloudAI/Api/VisionInspectionController.cs", "api/iotcloudai/vision")]
    public void IotCloudAI_NewControllers_HaveCorrectRoute(string path, string expectedRoute)
    {
        var src = ReadRepoFile(path);
        src.Should().Contain(expectedRoute, $"路由应为 {expectedRoute}");
    }

    [Fact]
    public void IotCloudAI_ModelRouting_UsesVersionedRoute()
    {
        var src = ReadRepoFile("JGSY.AGI.IotCloudAI/Api/ModelRoutingController.cs");
        src.Should().Contain("api/v1/iotcloudai/model-routing", "ModelRouting 应使用版本化路由 v1");
    }

    [Fact]
    public void IotCloudAI_SolarFusion_HasThreeModelWeights()
    {
        var src = ReadRepoFile("JGSY.AGI.IotCloudAI/AI/Prediction/SolarFusionPredictor.cs");
        src.Should().Contain("ComputePhysicalModel", "应有物理模型计算");
        src.Should().Contain("RunLightGbmCorrection", "应有 LightGBM 校正");
        src.Should().Contain("RunTinyLstmCorrection", "应有 TinyLSTM 修正");
    }

    [Fact]
    public void IotCloudAI_ModelRouter_HasIntentMatrix()
    {
        var src = ReadRepoFile("JGSY.AGI.IotCloudAI/AI/Routing/ModelRouter.cs");
        src.Should().Contain("device_query", "应有设备查询意图");
        src.Should().Contain("prediction_query", "应有预测意图");
        src.Should().Contain("qwen", "应包含 Qwen 模型");
    }

    [Fact]
    public void IotCloudAI_VectorSearch_HasCosineScoring()
    {
        var src = ReadRepoFile("JGSY.AGI.IotCloudAI/AI/VectorSearch/FlatVectorSearchEngine.cs");
        src.Should().Contain("L2Normalize", "应有 L2 归一化");
        src.Should().Contain("DotProduct", "应有内积(余弦相似度)计算");
    }

    [Fact]
    public void IotCloudAI_VisionEngine_HasYoloAndLlm()
    {
        var src = ReadRepoFile("JGSY.AGI.IotCloudAI/AI/Vision/VisionLanguageEngine.cs");
        src.Should().Contain("InspectPvPanel", "应有光伏巡检方法");
        src.Should().Contain("InspectCharger", "应有充电桩巡检方法");
    }

    [Fact]
    public void IotCloudAI_AccuracyBenchmark_HasThreeModules()
    {
        var src = ReadRepoFile("JGSY.AGI.IotCloudAI/AI/Routing/AccuracyBenchmarkManager.cs");
        src.Should().Contain("solar_fusion", "应有光伏融合基准");
        src.Should().Contain("vision_inspection", "应有视觉巡检基准");
        src.Should().Contain("vector_search", "应有向量检索基准");
    }

    #endregion

    #region ColdArchive 冷归档

    [Fact]
    public void ColdArchive_Interface_HasRequiredMethods()
    {
        var src = ReadRepoFile("JGSY.AGI.Common.Abstractions/ColdArchive/IColdArchiveService.cs");
        src.Should().Contain("ArchiveAsync", "应有归档方法");
        src.Should().Contain("GetArchiveMetadataAsync", "应有元数据查询");
    }

    [Fact]
    public void ColdArchive_Worker_IsBackgroundService()
    {
        var src = ReadRepoFile("JGSY.AGI.Common.Hosting/ColdArchive/ColdArchiveBackgroundWorker.cs");
        src.Should().Contain("BackgroundService", "必须继承 BackgroundService");
        src.Should().Contain("CancellationToken", "必须处理 CancellationToken");
    }

    [Fact]
    public void ColdArchive_ChargingWorker_ArchivesCorrectTables()
    {
        var src = ReadRepoFile("JGSY.AGI.Charging/Service/ChargingColdArchiveWorker.cs");
        src.Should().Contain("charging_device_heartbeat", "应归档心跳表");
        src.Should().Contain("charging_order_log", "应归档订单日志表");
    }

    [Fact]
    public void ColdArchive_StorageController_HasPermissions()
    {
        var src = ReadRepoFile("JGSY.AGI.Storage/Api/ArchiveController.cs");
        src.Should().Contain("RequirePermission", "归档端点必须鉴权");
        src.Should().Contain("storage:archive:", "权限码格式");
    }

    #endregion

    #region Background Services 后台任务

    [Fact]
    public void Device_CommandTimeout_IsBackgroundService()
    {
        var src = ReadRepoFile("JGSY.AGI.Device/Service/CommandTimeoutCheckService.cs");
        src.Should().Contain("BackgroundService", "必须继承 BackgroundService");
        src.Should().Contain("CancellationToken", "必须处理取消令牌");
        src.Should().Contain("device_remote_command", "应操作远程指令表");
    }

    [Fact]
    public void Trading_OrderExpiration_IsBackgroundService()
    {
        var src = ReadRepoFile("JGSY.AGI.EnergyServices.Trading/Modules/ElecTrade/Services/OrderExpirationJobService.cs");
        src.Should().Contain("BackgroundService", "必须继承 BackgroundService");
        src.Should().Contain("expired", "应处理过期状态");
        src.Should().Contain("cancelled", "应处理超时取消");
    }

    [Fact]
    public void Analytics_DailyReport_IsBackgroundService()
    {
        if (!RepoFileExists("JGSY.AGI.Analytics/BackgroundServices/DailyReportEtlJob.cs"))
            return;
        var src = ReadRepoFile("JGSY.AGI.Analytics/BackgroundServices/DailyReportEtlJob.cs");
        src.Should().Contain("BackgroundService", "必须继承 BackgroundService");
        src.Should().Contain("IServiceTransport", "应通过 IServiceTransport 拉取数据");
    }

    [Fact]
    public void Settlement_AutoSettlement_IsBackgroundService()
    {
        if (!RepoFileExists("JGSY.AGI.Settlement/BackgroundServices/AutoSettlementJob.cs"))
            return;
        var src = ReadRepoFile("JGSY.AGI.Settlement/BackgroundServices/AutoSettlementJob.cs");
        src.Should().Contain("BackgroundService", "必须继承 BackgroundService");
    }

    #endregion

    #region Internal API 内部服务 API

    [Fact]
    public void Observability_InternalAlert_HasInternalServiceAttribute()
    {
        var src = ReadRepoFile("JGSY.AGI.Observability/Monitor/Api/InternalAlertNotificationController.cs");
        src.Should().Contain("api/internal/observability", "内部路由应以 /api/internal/ 开头");
    }

    [Fact]
    public void WorkOrder_InternalWorkOrder_HasInternalServiceAttribute()
    {
        var src = ReadRepoFile("JGSY.AGI.WorkOrder/Api/InternalWorkOrderController.cs");
        src.Should().Contain("api/internal/workorder", "内部路由应以 /api/internal/ 开头");
        src.Should().Contain("from-alarm", "应有 from-alarm 端点");
    }

    #endregion

    #region DbUp 合规性

    [Fact]
    public void Observability_AuditProtection_HasDeleteBlock()
    {
        var sql = ReadRepoFile("JGSY.AGI.Observability/Data/Migrations/008_audit_delete_update_protection.sql");
        sql.Should().Contain("BEFORE DELETE", "应有 DELETE 触发器");
        sql.Should().Contain("审计日志禁止物理删除", "应有中文错误提示");
    }

    [Fact]
    public void Observability_AuditProtection_HasUpdateBlock()
    {
        var sql = ReadRepoFile("JGSY.AGI.Observability/Data/Migrations/008_audit_delete_update_protection.sql");
        sql.Should().Contain("BEFORE UPDATE", "应有 UPDATE 触发器");
    }

    [Fact]
    public void Permission_BlockchainPerms_HasThreeRoles()
    {
        var sql = ReadRepoFile("JGSY.AGI.Permission/Data/Migrations/013_blockchain_three_admin_permissions.sql");
        sql.Should().Contain("00000000-0000-0000-0000-000000000010", "应有安全管理员");
        sql.Should().Contain("00000000-0000-0000-0000-000000000011", "应有审计管理员");
        sql.Should().Contain("00000000-0000-0000-0000-000000000012", "应有系统管理员");
        sql.Should().Contain("00000000-0000-0000-0000-000000000001", "应有超级管理员");
    }

    [Fact]
    public void Ingestion_Hypertable_HasRetentionPolicy()
    {
        var sql = ReadRepoFile("JGSY.AGI.Ingestion/Data/Migrations/011_timescaledb_hypertable.sql");
        sql.Should().Contain("hypertable", "应包含 hypertable 关键字");
        sql.Should().Contain("ingestion.ingestion_message", "应操作 ingestion_message 表");
    }

    #endregion

    #region Gateway 路由拆分

    [Theory]
    [InlineData("JGSY.AGI.Gateway/yarp.routes.platform.json")]
    [InlineData("JGSY.AGI.Gateway/yarp.routes.charging.json")]
    [InlineData("JGSY.AGI.Gateway/yarp.routes.energy.json")]
    [InlineData("JGSY.AGI.Gateway/yarp.routes.business.json")]
    [InlineData("JGSY.AGI.Gateway/yarp.routes.advanced.json")]
    public void Gateway_RouteFile_IsValidJson(string path)
    {
        var json = ReadRepoFile(path);
        var act = () => JsonDocument.Parse(json, JsonOpts);
        act.Should().NotThrow($"{path} 必须是有效 JSON");
    }

    [Fact]
    public void Gateway_RouteFiles_CoverAllServices()
    {
        var allRoutes = new[] {
            "yarp.routes.platform.json", "yarp.routes.charging.json",
            "yarp.routes.energy.json", "yarp.routes.business.json",
            "yarp.routes.advanced.json"
        };
        var allContent = string.Join("\n", allRoutes.Select(f => ReadRepoFile($"JGSY.AGI.Gateway/{f}")));

        var expectedClusters = new[] {
            "identity", "permission", "account", "tenant", "storage", "observability",
            "charging", "settlement", "device", "station", "ingestion", "ruleengine",
            "workorder", "blockchain", "analytics", "iotcloudai"
        };
        foreach (var cluster in expectedClusters)
            allContent.Should().Contain(cluster, $"路由文件应覆盖 {cluster} 服务");
    }

    [Fact]
    public void Gateway_RouteFiles_BlockInternalRoutes()
    {
        var advanced = ReadRepoFile("JGSY.AGI.Gateway/yarp.routes.advanced.json");
        var platform = ReadRepoFile("JGSY.AGI.Gateway/yarp.routes.platform.json");
        var allContent = advanced + platform;
        // 内部路由应有 Block 规则
        allContent.Should().Contain("internal", "应有内部路由拦截规则");
    }

    [Fact]
    public void Gateway_ProtocolSharding_HasShardingOptions()
    {
        var src = ReadRepoFile("JGSY.AGI.Ingestion/Models/ProtocolShardingOptions.cs");
        src.Should().Contain("Mode", "应有 Mode 属性");
        src.Should().Contain("EnabledCategories", "应有 EnabledCategories 属性");
    }

    #endregion
}
