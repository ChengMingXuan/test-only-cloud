using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Xunit;
using JGSY.AGI.Auth.Business;
using JGSY.AGI.Auth.Entities;
using JGSY.AGI.Auth.Interfaces;

namespace JGSY.AGI.Test.Identity;

/// <summary>
/// MFA多因素认证服务单元测试（MfaService 是纯 Facade 模式，委托给5个子服务）
/// </summary>
public class MfaServiceTests
{
    private readonly Mock<IMfaConfigService> _configMock;
    private readonly Mock<ITotpMfaService> _totpMock;
    private readonly Mock<ISmsEmailMfaService> _smsEmailMock;
    private readonly Mock<IRecoveryCodeService> _recoveryMock;
    private readonly Mock<IMfaVerificationService> _verificationMock;
    private readonly MfaService _service;

    public MfaServiceTests()
    {
        _configMock = new Mock<IMfaConfigService>();
        _totpMock = new Mock<ITotpMfaService>();
        _smsEmailMock = new Mock<ISmsEmailMfaService>();
        _recoveryMock = new Mock<IRecoveryCodeService>();
        _verificationMock = new Mock<IMfaVerificationService>();

        _service = new MfaService(
            _configMock.Object,
            _totpMock.Object,
            _smsEmailMock.Object,
            _recoveryMock.Object,
            _verificationMock.Object,
            NullLogger<MfaService>.Instance);
    }

    #region GetUserMfaConfigsAsync（委托 configService）

    [Fact]
    public async Task GetUserMfaConfigsAsync_DelegatesToConfigService()
    {
        // Arrange
        var userId = Guid.NewGuid();
        var expected = new List<UserMfaConfigDto> { new() { Id = Guid.NewGuid(), MfaType = MfaType.Totp, IsEnabled = true } };
        _configMock.Setup(c => c.GetUserMfaConfigsAsync(userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(expected);

        // Act
        var result = await _service.GetUserMfaConfigsAsync(userId);

        // Assert
        result.Should().BeSameAs(expected);
        _configMock.Verify(c => c.GetUserMfaConfigsAsync(userId, It.IsAny<CancellationToken>()), Times.Once);
    }

    #endregion

    #region IsMfaEnabledAsync（委托 configService）

    [Fact]
    public async Task IsMfaEnabledAsync_Enabled_ReturnsTrue()
    {
        var userId = Guid.NewGuid();
        _configMock.Setup(c => c.IsMfaEnabledAsync(userId, It.IsAny<CancellationToken>())).ReturnsAsync(true);
        (await _service.IsMfaEnabledAsync(userId)).Should().BeTrue();
    }

    [Fact]
    public async Task IsMfaEnabledAsync_Disabled_ReturnsFalse()
    {
        var userId = Guid.NewGuid();
        _configMock.Setup(c => c.IsMfaEnabledAsync(userId, It.IsAny<CancellationToken>())).ReturnsAsync(false);
        (await _service.IsMfaEnabledAsync(userId)).Should().BeFalse();
    }

    #endregion

    #region GenerateTotpSetupAsync（委托 totpService）

    [Fact]
    public async Task GenerateTotpSetupAsync_DelegatesToTotpService()
    {
        var userId = Guid.NewGuid();
        var expected = new TotpSetupResult { SecretKey = "TESTKEY", QrCodeImage = "base64data", OtpAuthUri = "otpauth://..." };
        _totpMock.Setup(t => t.GenerateTotpSetupAsync(userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(expected);

        var result = await _service.GenerateTotpSetupAsync(userId);
        result.Should().BeSameAs(expected);
    }

    #endregion

    #region EnableTotpAsync（委托 totpService）

    [Fact]
    public async Task EnableTotpAsync_ValidCode_ReturnsTrue()
    {
        var userId = Guid.NewGuid();
        _totpMock.Setup(t => t.EnableTotpAsync(userId, "setup-token", "123456", It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var result = await _service.EnableTotpAsync(userId, "setup-token", "123456");
        result.Should().BeTrue();
    }

    [Fact]
    public async Task EnableTotpAsync_InvalidCode_ReturnsFalse()
    {
        var userId = Guid.NewGuid();
        _totpMock.Setup(t => t.EnableTotpAsync(userId, "setup-token", "000000", It.IsAny<CancellationToken>()))
            .ReturnsAsync(false);

        var result = await _service.EnableTotpAsync(userId, "setup-token", "000000");
        result.Should().BeFalse();
    }

    #endregion

    #region DisableTotpAsync（委托 totpService）

    [Fact]
    public async Task DisableTotpAsync_DelegatesToTotpService()
    {
        var userId = Guid.NewGuid();
        _totpMock.Setup(t => t.DisableTotpAsync(userId, "123456", It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var result = await _service.DisableTotpAsync(userId, "123456");
        result.Should().BeTrue();
        _totpMock.Verify(t => t.DisableTotpAsync(userId, "123456", It.IsAny<CancellationToken>()), Times.Once);
    }

    #endregion

    #region EnableSmsMfaAsync / DisableSmsMfaAsync（委托 smsEmailService）

    [Fact]
    public async Task EnableSmsMfaAsync_DelegatesToSmsEmailService()
    {
        var userId = Guid.NewGuid();
        _smsEmailMock.Setup(s => s.EnableSmsMfaAsync(userId, "13812345678", "123456", It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var result = await _service.EnableSmsMfaAsync(userId, "13812345678", "123456");
        result.Should().BeTrue();
    }

    [Fact]
    public async Task DisableSmsMfaAsync_DelegatesToSmsEmailService()
    {
        var userId = Guid.NewGuid();
        _smsEmailMock.Setup(s => s.DisableSmsMfaAsync(userId, "123456", It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var result = await _service.DisableSmsMfaAsync(userId, "123456");
        result.Should().BeTrue();
    }

    #endregion

    #region EnableEmailMfaAsync / DisableEmailMfaAsync（委托 smsEmailService）

    [Fact]
    public async Task EnableEmailMfaAsync_DelegatesToSmsEmailService()
    {
        var userId = Guid.NewGuid();
        _smsEmailMock.Setup(s => s.EnableEmailMfaAsync(userId, "test@example.com", "123456", It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var result = await _service.EnableEmailMfaAsync(userId, "test@example.com", "123456");
        result.Should().BeTrue();
    }

    [Fact]
    public async Task DisableEmailMfaAsync_DelegatesToSmsEmailService()
    {
        var userId = Guid.NewGuid();
        _smsEmailMock.Setup(s => s.DisableEmailMfaAsync(userId, "123456", It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var result = await _service.DisableEmailMfaAsync(userId, "123456");
        result.Should().BeTrue();
    }

    #endregion

    #region SendMfaCodeAsync（委托 smsEmailService）

    [Fact]
    public async Task SendMfaCodeAsync_Sms_DelegatesToSmsEmailService()
    {
        var userId = Guid.NewGuid();
        _smsEmailMock.Setup(s => s.SendMfaCodeAsync(userId, MfaType.Sms, MfaScene.Login, It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var result = await _service.SendMfaCodeAsync(userId, MfaType.Sms, MfaScene.Login);
        result.Should().BeTrue();
    }

    #endregion

    #region VerifyMfaAsync（委托 verificationService）

    [Fact]
    public async Task VerifyMfaAsync_ValidRequest_ReturnsSuccessResult()
    {
        var userId = Guid.NewGuid();
        var request = new MfaVerifyRequest { Code = "123456" };
        var expected = new MfaVerifyResult { Success = true };
        _verificationMock.Setup(v => v.VerifyMfaAsync(userId, request, It.IsAny<CancellationToken>()))
            .ReturnsAsync(expected);

        var result = await _service.VerifyMfaAsync(userId, request);
        result.Success.Should().BeTrue();
    }

    [Fact]
    public async Task VerifyMfaAsync_InvalidCode_ReturnsFailureResult()
    {
        var userId = Guid.NewGuid();
        var request = new MfaVerifyRequest { Code = "wrong" };
        var expected = new MfaVerifyResult { Success = false, Message = "验证码错误" };
        _verificationMock.Setup(v => v.VerifyMfaAsync(userId, request, It.IsAny<CancellationToken>()))
            .ReturnsAsync(expected);

        var result = await _service.VerifyMfaAsync(userId, request);
        result.Success.Should().BeFalse();
    }

    #endregion

    #region GenerateRecoveryCodesAsync（委托 recoveryCodeService）

    [Fact]
    public async Task GenerateRecoveryCodesAsync_DefaultCount_ReturnsCodeList()
    {
        var userId = Guid.NewGuid();
        var codes = new List<string> { "AAAA-BBBB", "CCCC-DDDD", "EEEE-FFFF" };
        _recoveryMock.Setup(r => r.GenerateRecoveryCodesAsync(userId, 10, It.IsAny<CancellationToken>()))
            .ReturnsAsync(codes);

        var result = await _service.GenerateRecoveryCodesAsync(userId);
        result.Should().HaveCount(3);
        result.Should().Contain("AAAA-BBBB");
    }

    [Fact]
    public async Task GenerateRecoveryCodesAsync_CustomCount_PassesCorrectCount()
    {
        var userId = Guid.NewGuid();
        var codes = new List<string> { "A1", "A2", "A3", "A4", "A5" };
        _recoveryMock.Setup(r => r.GenerateRecoveryCodesAsync(userId, 5, It.IsAny<CancellationToken>()))
            .ReturnsAsync(codes);

        var result = await _service.GenerateRecoveryCodesAsync(userId, 5);
        result.Should().HaveCount(5);
    }

    #endregion

    #region CreateMfaSessionAsync（委托 verificationService）

    [Fact]
    public async Task CreateMfaSessionAsync_DelegatesToVerificationService()
    {
        var userId = Guid.NewGuid();
        _verificationMock.Setup(v => v.CreateMfaSessionAsync(userId, MfaScene.Login, It.IsAny<CancellationToken>()))
            .ReturnsAsync("session-token-123");

        var result = await _service.CreateMfaSessionAsync(userId, MfaScene.Login);
        result.Should().Be("session-token-123");
    }

    #endregion

    #region ValidateMfaSessionAsync（委托 verificationService）

    [Fact]
    public async Task ValidateMfaSessionAsync_ValidSession_ReturnsTrue()
    {
        var userId = Guid.NewGuid();
        _verificationMock.Setup(v => v.ValidateMfaSessionAsync(userId, "token", MfaScene.Login, It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var result = await _service.ValidateMfaSessionAsync(userId, "token", MfaScene.Login);
        result.Should().BeTrue();
    }

    #endregion

    #region RequiresMfaAsync（委托 configService）

    [Fact]
    public async Task RequiresMfaAsync_DelegatesToConfigService()
    {
        var userId = Guid.NewGuid();
        _configMock.Setup(c => c.RequiresMfaAsync("delete_user", userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var result = await _service.RequiresMfaAsync("delete_user", userId);
        result.Should().BeTrue();
    }

    #endregion

    #region AdminResetMfaAsync（委托 configService）

    [Fact]
    public async Task AdminResetMfaAsync_DelegatesToConfigService()
    {
        var userId = Guid.NewGuid();
        _configMock.Setup(c => c.AdminResetMfaAsync(userId, "用户丢失手机", It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var result = await _service.AdminResetMfaAsync(userId, "用户丢失手机");
        result.Should().BeTrue();
    }

    #endregion

    #region GetVerificationLogsAsync（委托 verificationService）

    [Fact]
    public async Task GetVerificationLogsAsync_DelegatesToVerificationService()
    {
        var userId = Guid.NewGuid();
        var logs = new List<MfaVerificationLogDto>
        {
            new() { Id = Guid.NewGuid(), MfaType = MfaType.Totp, IsSuccess = true }
        };
        _verificationMock.Setup(v => v.GetVerificationLogsAsync(userId, 1, 20, It.IsAny<CancellationToken>()))
            .ReturnsAsync(logs);

        var result = await _service.GetVerificationLogsAsync(userId);
        result.Should().HaveCount(1);
    }

    #endregion
}
