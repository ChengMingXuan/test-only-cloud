using System;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using Moq;
using Xunit;
using JGSY.AGI.Auth.Business;
using JGSY.AGI.Auth.Interfaces;
using JGSY.AGI.Common.Core.Interfaces;

namespace JGSY.AGI.Test.Identity;

/// <summary>
/// 验证码服务单元测试
/// </summary>
public class CaptchaServiceTests
{
    private readonly Mock<ICacheManager> _cacheMock;
    private readonly CaptchaOptions _options;
    private readonly CaptchaService _service;

    public CaptchaServiceTests()
    {
        _cacheMock = new Mock<ICacheManager>();
        _options = new CaptchaOptions
        {
            Enabled = true,
            CodeLength = 4,
            ExpirationSeconds = 300,
            AttemptsBeforeCaptcha = 3,
            IpAttemptsBeforeCaptcha = 10,
            AttemptsWindowMinutes = 30,
            MockEnabled = false
        };

        _service = new CaptchaService(
            _cacheMock.Object,
            Options.Create(_options),
            NullLogger<CaptchaService>.Instance);
    }

    #region GenerateImageCaptchaAsync

    [Fact]
    public async Task GenerateImageCaptchaAsync_ReturnsResultWithKeyAndImage()
    {
        // Arrange
        _cacheMock.Setup(c => c.SetAsync(
                It.IsAny<string>(), It.IsAny<string>(),
                It.IsAny<TimeSpan>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.GenerateImageCaptchaAsync();

        // Assert
        result.Should().NotBeNull();
        result.Key.Should().NotBeNullOrEmpty();
        result.ImageBase64.Should().StartWith("data:image/png;base64,");
        result.ExpiresAt.Should().BeAfter(DateTime.UtcNow);
    }

    [Fact]
    public async Task GenerateImageCaptchaAsync_StoresCodeInCache()
    {
        // Arrange & Act
        await _service.GenerateImageCaptchaAsync();

        // Assert - 验证缓存被调用，存储了验证码
        _cacheMock.Verify(c => c.SetAsync(
            It.Is<string>(k => k.StartsWith("captcha:")),
            It.IsAny<string>(),
            TimeSpan.FromSeconds(300),
            It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task GenerateImageCaptchaAsync_MockMode_UsesFixedCode()
    {
        // Arrange
        var mockOptions = new CaptchaOptions { MockEnabled = true, MockCode = "ABCD", LogCode = true };
        var mockService = new CaptchaService(_cacheMock.Object, Options.Create(mockOptions), NullLogger<CaptchaService>.Instance);

        _cacheMock.Setup(c => c.SetAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<TimeSpan>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        await mockService.GenerateImageCaptchaAsync();

        // Assert - Mock 模式应存储小写的模拟验证码
        _cacheMock.Verify(c => c.SetAsync(
            It.IsAny<string>(),
            "abcd",
            It.IsAny<TimeSpan>(),
            It.IsAny<CancellationToken>()), Times.Once);
    }

    #endregion

    #region ValidateImageCaptchaAsync

    [Fact]
    public async Task ValidateImageCaptchaAsync_CorrectCode_ReturnsTrue()
    {
        // Arrange
        var key = "test-key";
        _cacheMock.Setup(c => c.GetAsync<string>($"captcha:{key}", It.IsAny<CancellationToken>()))
            .ReturnsAsync("abcd");
        _cacheMock.Setup(c => c.RemoveAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.ValidateImageCaptchaAsync(key, "ABCD");

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public async Task ValidateImageCaptchaAsync_CaseInsensitive_ReturnsTrue()
    {
        // Arrange
        var key = "test-key";
        _cacheMock.Setup(c => c.GetAsync<string>($"captcha:{key}", It.IsAny<CancellationToken>()))
            .ReturnsAsync("abcd");
        _cacheMock.Setup(c => c.RemoveAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.ValidateImageCaptchaAsync(key, "AbCd");

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public async Task ValidateImageCaptchaAsync_WrongCode_ReturnsFalse()
    {
        // Arrange
        var key = "test-key";
        _cacheMock.Setup(c => c.GetAsync<string>($"captcha:{key}", It.IsAny<CancellationToken>()))
            .ReturnsAsync("abcd");
        _cacheMock.Setup(c => c.RemoveAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.ValidateImageCaptchaAsync(key, "WXYZ");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task ValidateImageCaptchaAsync_ExpiredCode_ReturnsFalse()
    {
        // Arrange
        _cacheMock.Setup(c => c.GetAsync<string>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((string?)null);

        // Act
        var result = await _service.ValidateImageCaptchaAsync("expired-key", "ABCD");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task ValidateImageCaptchaAsync_NullKey_ReturnsFalse()
    {
        var result = await _service.ValidateImageCaptchaAsync(null!, "ABCD");
        result.Should().BeFalse();
    }

    [Fact]
    public async Task ValidateImageCaptchaAsync_EmptyCode_ReturnsFalse()
    {
        var result = await _service.ValidateImageCaptchaAsync("key", "");
        result.Should().BeFalse();
    }

    [Fact]
    public async Task ValidateImageCaptchaAsync_RemovesCacheAfterValidation()
    {
        // Arrange
        var key = "test-key";
        _cacheMock.Setup(c => c.GetAsync<string>($"captcha:{key}", It.IsAny<CancellationToken>()))
            .ReturnsAsync("abcd");
        _cacheMock.Setup(c => c.RemoveAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        await _service.ValidateImageCaptchaAsync(key, "ABCD");

        // Assert - 验证后应立即删除缓存
        _cacheMock.Verify(c => c.RemoveAsync($"captcha:{key}", It.IsAny<CancellationToken>()), Times.Once);
    }

    #endregion

    #region ValidateSliderCaptchaAsync

    [Fact]
    public async Task ValidateSliderCaptchaAsync_ExactPosition_ReturnsTrue()
    {
        // Arrange
        var key = "slider-key";
        _cacheMock.Setup(c => c.GetAsync<int?>($"captcha:slider:{key}", It.IsAny<CancellationToken>()))
            .ReturnsAsync(150);
        _cacheMock.Setup(c => c.RemoveAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.ValidateSliderCaptchaAsync(key, 150);

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public async Task ValidateSliderCaptchaAsync_WithinTolerance_ReturnsTrue()
    {
        // Arrange
        var key = "slider-key";
        _cacheMock.Setup(c => c.GetAsync<int?>($"captcha:slider:{key}", It.IsAny<CancellationToken>()))
            .ReturnsAsync(150);
        _cacheMock.Setup(c => c.RemoveAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act - 默认容差 5
        var result = await _service.ValidateSliderCaptchaAsync(key, 153);

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public async Task ValidateSliderCaptchaAsync_OutOfTolerance_ReturnsFalse()
    {
        // Arrange
        var key = "slider-key";
        _cacheMock.Setup(c => c.GetAsync<int?>($"captcha:slider:{key}", It.IsAny<CancellationToken>()))
            .ReturnsAsync(150);
        _cacheMock.Setup(c => c.RemoveAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act - 超出默认容差 5
        var result = await _service.ValidateSliderCaptchaAsync(key, 160);

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task ValidateSliderCaptchaAsync_ExpiredKey_ReturnsFalse()
    {
        // Arrange
        _cacheMock.Setup(c => c.GetAsync<int?>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((int?)null);

        // Act
        var result = await _service.ValidateSliderCaptchaAsync("expired-key", 150);

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task ValidateSliderCaptchaAsync_EmptyKey_ReturnsFalse()
    {
        var result = await _service.ValidateSliderCaptchaAsync("", 150);
        result.Should().BeFalse();
    }

    #endregion

    #region RequiresCaptchaAsync

    [Fact]
    public async Task RequiresCaptchaAsync_Disabled_ReturnsFalse()
    {
        // Arrange
        var disabledOptions = new CaptchaOptions { Enabled = false };
        var service = new CaptchaService(_cacheMock.Object, Options.Create(disabledOptions), NullLogger<CaptchaService>.Instance);

        // Act
        var result = await service.RequiresCaptchaAsync("user1", "1.2.3.4");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task RequiresCaptchaAsync_BelowThreshold_ReturnsFalse()
    {
        // Arrange - 用户尝试次数为2（低于阈值3）
        _cacheMock.Setup(c => c.GetAsync<int>("captcha_attempts:user1", It.IsAny<CancellationToken>()))
            .ReturnsAsync(2);
        _cacheMock.Setup(c => c.GetAsync<int>("captcha_attempts:1.2.3.4", It.IsAny<CancellationToken>()))
            .ReturnsAsync(1);

        // Act
        var result = await _service.RequiresCaptchaAsync("user1", "1.2.3.4");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task RequiresCaptchaAsync_UserExceedsThreshold_ReturnsTrue()
    {
        // Arrange - 用户尝试次数达到阈值
        _cacheMock.Setup(c => c.GetAsync<int>("captcha_attempts:user1", It.IsAny<CancellationToken>()))
            .ReturnsAsync(3);
        _cacheMock.Setup(c => c.GetAsync<int>("captcha_attempts:1.2.3.4", It.IsAny<CancellationToken>()))
            .ReturnsAsync(1);

        // Act
        var result = await _service.RequiresCaptchaAsync("user1", "1.2.3.4");

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public async Task RequiresCaptchaAsync_IpExceedsThreshold_ReturnsTrue()
    {
        // Arrange - IP尝试次数达到阈值
        _cacheMock.Setup(c => c.GetAsync<int>("captcha_attempts:user1", It.IsAny<CancellationToken>()))
            .ReturnsAsync(1);
        _cacheMock.Setup(c => c.GetAsync<int>("captcha_attempts:1.2.3.4", It.IsAny<CancellationToken>()))
            .ReturnsAsync(10);

        // Act
        var result = await _service.RequiresCaptchaAsync("user1", "1.2.3.4");

        // Assert
        result.Should().BeTrue();
    }

    #endregion

    #region RecordAttemptAsync

    [Fact]
    public async Task RecordAttemptAsync_Success_ClearsAttempts()
    {
        // Arrange
        _cacheMock.Setup(c => c.RemoveAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        await _service.RecordAttemptAsync("user1", "1.2.3.4", success: true);

        // Assert - 成功后应清除用户和IP的尝试记录
        _cacheMock.Verify(c => c.RemoveAsync("captcha_attempts:user1", It.IsAny<CancellationToken>()), Times.Once);
        _cacheMock.Verify(c => c.RemoveAsync("captcha_attempts:1.2.3.4", It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task RecordAttemptAsync_Failure_IncrementsAttempts()
    {
        // Arrange
        _cacheMock.Setup(c => c.GetAsync<int>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(2);
        _cacheMock.Setup(c => c.SetAsync(It.IsAny<string>(), It.IsAny<int>(), It.IsAny<TimeSpan>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        await _service.RecordAttemptAsync("user1", "1.2.3.4", success: false);

        // Assert - 失败应增加尝试次数
        _cacheMock.Verify(c => c.SetAsync(
            "captcha_attempts:user1",
            3, // 2+1
            TimeSpan.FromMinutes(30),
            It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task RecordAttemptAsync_SuccessNoIp_OnlyClearsUsername()
    {
        // Arrange
        _cacheMock.Setup(c => c.RemoveAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        await _service.RecordAttemptAsync("user1", null, success: true);

        // Assert
        _cacheMock.Verify(c => c.RemoveAsync("captcha_attempts:user1", It.IsAny<CancellationToken>()), Times.Once);
        _cacheMock.Verify(c => c.RemoveAsync("captcha_attempts:", It.IsAny<CancellationToken>()), Times.Never);
    }

    #endregion

    #region CaptchaOptions

    [Fact]
    public void CaptchaOptions_ResolveCode_MockEnabled_ReturnsFixedCode()
    {
        var options = new CaptchaOptions { MockEnabled = true, MockCode = "TEST" };
        var code = options.ResolveCode(() => "RANDOM");
        code.Should().Be("TEST");
    }

    [Fact]
    public void CaptchaOptions_ResolveCode_MockDisabled_CallsGenerator()
    {
        var options = new CaptchaOptions { MockEnabled = false };
        var code = options.ResolveCode(() => "GENERATED");
        code.Should().Be("GENERATED");
    }

    [Fact]
    public void CaptchaOptions_ResolveCode_MockEnabledEmptyCode_Returns123456()
    {
        var options = new CaptchaOptions { MockEnabled = true, MockCode = "" };
        var code = options.ResolveCode(() => "RANDOM");
        code.Should().Be("123456");
    }

    [Fact]
    public void CaptchaOptions_DefaultValues_AreCorrect()
    {
        var options = new CaptchaOptions();
        options.Enabled.Should().BeTrue();
        options.CodeLength.Should().Be(4);
        options.ExpirationSeconds.Should().Be(300);
        options.AttemptsBeforeCaptcha.Should().Be(3);
        options.IpAttemptsBeforeCaptcha.Should().Be(10);
        options.AttemptsWindowMinutes.Should().Be(30);
        options.MockEnabled.Should().BeFalse();
        options.MockCode.Should().Be("123456");
    }

    #endregion

    #region GenerateSliderCaptchaAsync

    [Fact]
    public async Task GenerateSliderCaptchaAsync_ReturnsValidResult()
    {
        // Arrange
        _cacheMock.Setup(c => c.SetAsync(It.IsAny<string>(), It.IsAny<int>(), It.IsAny<TimeSpan>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.GenerateSliderCaptchaAsync();

        // Assert
        result.Should().NotBeNull();
        result.Key.Should().NotBeNullOrEmpty();
        result.BackgroundImage.Should().StartWith("data:image/png;base64,");
        result.SliderImage.Should().StartWith("data:image/png;base64,");
        result.YPosition.Should().BeInRange(50, 100);
        result.ExpiresAt.Should().BeAfter(DateTime.UtcNow);
    }

    [Fact]
    public async Task GenerateSliderCaptchaAsync_StoresPositionInCache()
    {
        // Arrange
        _cacheMock.Setup(c => c.SetAsync(It.IsAny<string>(), It.IsAny<int>(), It.IsAny<TimeSpan>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        await _service.GenerateSliderCaptchaAsync();

        // Assert
        _cacheMock.Verify(c => c.SetAsync(
            It.Is<string>(k => k.StartsWith("captcha:slider:")),
            It.Is<int>(v => v >= 100 && v <= 250),
            TimeSpan.FromSeconds(300),
            It.IsAny<CancellationToken>()), Times.Once);
    }

    #endregion
}
