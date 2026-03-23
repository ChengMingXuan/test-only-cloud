#pragma warning disable CS0619 // EncryptHelper 已标记 Obsolete(error:true)，测试验证废弃行为正确抛出异常
using FluentAssertions;
using JGSY.AGI.Common.Core.Utils;
using Xunit;

namespace JGSY.AGI.Test.Common
{
    /// <summary>
    /// EncryptHelper 已废弃（Padding Oracle 攻击风险），此测试验证调用时正确抛出 NotSupportedException
    /// </summary>
    public class EncryptHelperTests
    {
        private const string TestKey = "MySecretKey12345678901234567890!!";

        [Fact]
        public void AESEncrypt_ShouldThrowNotSupportedException()
        {
            var action = () => EncryptHelper.AESEncrypt("test", TestKey);
            action.Should().Throw<NotSupportedException>()
                .WithMessage("*已废弃*");
        }

        [Fact]
        public void AESDecrypt_ShouldThrowNotSupportedException()
        {
            var action = () => EncryptHelper.AESDecrypt("dGVzdA==", TestKey);
            action.Should().Throw<NotSupportedException>()
                .WithMessage("*已废弃*");
        }
    }
}
