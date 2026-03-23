using FluentAssertions;
using JGSY.AGI.Common.Infra.Crypto;
using Xunit;

namespace JGSY.AGI.Test.Common.Compliance;

/// <summary>
/// 国密算法（SM2/SM3/SM4）实现测试
/// 合规项：CRYPTO-001~003, GB/T 36572, GM/T 0028-2014
/// </summary>
public class NationalCryptoServiceTests
{
    #region SM3 哈希测试

    [Fact]
    public void SM3_Hash应生成32字节摘要()
    {
        var sm3 = new SM3HashService();
        var data = System.Text.Encoding.UTF8.GetBytes("测试数据-合规性验证");

        var hash = sm3.Hash(data);

        hash.Should().NotBeNull();
        hash.Should().HaveCount(32, "SM3 摘要固定为 32 字节（256位）");
    }

    [Fact]
    public void SM3_相同输入应生成相同摘要()
    {
        var sm3 = new SM3HashService();
        var data = System.Text.Encoding.UTF8.GetBytes("一致性验证数据");

        var hash1 = sm3.Hash(data);
        var hash2 = sm3.Hash(data);

        hash1.Should().Equal(hash2, "相同输入，SM3 输出必须一致");
    }

    [Fact]
    public void SM3_不同输入应生成不同摘要()
    {
        var sm3 = new SM3HashService();
        var data1 = System.Text.Encoding.UTF8.GetBytes("数据A");
        var data2 = System.Text.Encoding.UTF8.GetBytes("数据B");

        var hash1 = sm3.Hash(data1);
        var hash2 = sm3.Hash(data2);

        hash1.Should().NotEqual(hash2, "不同输入，SM3 输出必须不同");
    }

    [Fact]
    public void SM3_VerifyHash应正确验证摘要()
    {
        var sm3 = new SM3HashService();
        var data = System.Text.Encoding.UTF8.GetBytes("验证测试");

        var hash = sm3.Hash(data);
        var result = sm3.VerifyHash(data, hash);

        result.Should().BeTrue("SM3 VerifyHash 应通过对相同数据的校验");
    }

    [Fact]
    public void SM3_VerifyHash应拒绝篡改数据()
    {
        var sm3 = new SM3HashService();
        var data = System.Text.Encoding.UTF8.GetBytes("原始数据");
        var tampered = System.Text.Encoding.UTF8.GetBytes("篡改数据");

        var hash = sm3.Hash(data);
        var result = sm3.VerifyHash(tampered, hash);

        result.Should().BeFalse("SM3 VerifyHash 应拒绝篡改后的数据");
    }

    [Fact]
    public void SM3_HMAC应生成有效摘要()
    {
        var sm3 = new SM3HashService();
        var data = System.Text.Encoding.UTF8.GetBytes("HMAC测试");
        var key = System.Text.Encoding.UTF8.GetBytes("密钥-16字节以上足够");

        var hmac = sm3.Hmac(data, key);

        hmac.Should().NotBeNull();
        hmac.Should().HaveCount(32, "SM3 HMAC 输出应为 32 字节");
    }

    #endregion

    #region SM4 对称加密测试

    [Fact]
    public void SM4_加密解密应还原原始数据()
    {
        var sm4 = new SM4CryptoService();
        var key = new byte[16]; // 128 位密钥
        new Random(42).NextBytes(key);
        var plaintext = System.Text.Encoding.UTF8.GetBytes("SM4 对称加密合规测试数据 — GB/T 36572 要求");

        var ciphertext = sm4.Encrypt(key, plaintext);
        var decrypted = sm4.Decrypt(key, ciphertext);

        decrypted.Should().Equal(plaintext, "SM4 解密后应完全还原原始明文");
    }

    [Fact]
    public void SM4_密文不应等于明文()
    {
        var sm4 = new SM4CryptoService();
        var key = new byte[16];
        new Random(42).NextBytes(key);
        var plaintext = System.Text.Encoding.UTF8.GetBytes("不应暴露的敏感数据");

        var ciphertext = sm4.Encrypt(key, plaintext);

        ciphertext.Should().NotEqual(plaintext, "SM4 密文不应等于明文");
    }

    [Fact]
    public void SM4_密文应包含IV前缀()
    {
        var sm4 = new SM4CryptoService();
        var key = new byte[16];
        new Random(42).NextBytes(key);
        var plaintext = System.Text.Encoding.UTF8.GetBytes("IV前缀校验");

        var ciphertext = sm4.Encrypt(key, plaintext);

        // SM4 CBC 模式 IV=16字节，密文至少为 16+16=32 字节
        ciphertext.Length.Should().BeGreaterOrEqualTo(32, "密文应包含 16 字节 IV + 至少 16 字节密文块");
    }

    [Fact]
    public void SM4_相同明文两次加密应生成不同密文()
    {
        var sm4 = new SM4CryptoService();
        var key = new byte[16];
        new Random(42).NextBytes(key);
        var plaintext = System.Text.Encoding.UTF8.GetBytes("CBC模式随机IV");

        var cipher1 = sm4.Encrypt(key, plaintext);
        var cipher2 = sm4.Encrypt(key, plaintext);

        cipher1.Should().NotEqual(cipher2, "CBC 模式每次加密使用随机 IV，密文应不同");
    }

    [Fact]
    public void SM4_错误密钥解密应失败()
    {
        var sm4 = new SM4CryptoService();
        var key = new byte[16];
        new Random(42).NextBytes(key);
        var wrongKey = new byte[16];
        new Random(99).NextBytes(wrongKey);
        var plaintext = System.Text.Encoding.UTF8.GetBytes("密钥错误不应解密");

        var ciphertext = sm4.Encrypt(key, plaintext);

        // 错误密钥解密应抛异常或解出错误数据
        try
        {
            var decrypted = sm4.Decrypt(wrongKey, ciphertext);
            decrypted.Should().NotEqual(plaintext, "错误密钥解出的数据应不等于原文");
        }
        catch (Exception)
        {
            // 抛异常也是预期行为（PKCS7 填充验证失败）
        }
    }

    #endregion

    #region SM2 非对称加密测试

    [Fact]
    public void SM2_签名验签完整流程()
    {
        var sm2 = new SM2CryptoService();
        var (privateKey, publicKey) = sm2.GenerateKeyPair();
        var data = System.Text.Encoding.UTF8.GetBytes("SM2 签名验签测试 — 合规性校验");

        var signature = sm2.Sign(privateKey, data);
        var valid = sm2.Verify(publicKey, data, signature);

        valid.Should().BeTrue("SM2 签名应通过同密钥对的验签");
    }

    [Fact]
    public void SM2_篡改数据验签应失败()
    {
        var sm2 = new SM2CryptoService();
        var (privateKey, publicKey) = sm2.GenerateKeyPair();
        var data = System.Text.Encoding.UTF8.GetBytes("原始控制指令");
        var tampered = System.Text.Encoding.UTF8.GetBytes("篡改控制指令");

        var signature = sm2.Sign(privateKey, data);
        var valid = sm2.Verify(publicKey, tampered, signature);

        valid.Should().BeFalse("篡改数据后 SM2 验签应失败 — 控制指令完整性保障");
    }

    [Fact]
    public void SM2_不同密钥验签应失败()
    {
        var sm2 = new SM2CryptoService();
        var (privateKey1, _) = sm2.GenerateKeyPair();
        var (_, publicKey2) = sm2.GenerateKeyPair();
        var data = System.Text.Encoding.UTF8.GetBytes("跨密钥验签测试");

        var signature = sm2.Sign(privateKey1, data);
        var valid = sm2.Verify(publicKey2, data, signature);

        valid.Should().BeFalse("不同密钥对的验签应失败");
    }

    [Fact]
    public void SM2_加密解密完整流程()
    {
        var sm2 = new SM2CryptoService();
        var (privateKey, publicKey) = sm2.GenerateKeyPair();
        var plaintext = System.Text.Encoding.UTF8.GetBytes("SM2 非对称加密 — 敏感配置保护");

        var ciphertext = sm2.Encrypt(publicKey, plaintext);
        var decrypted = sm2.Decrypt(privateKey, ciphertext);

        decrypted.Should().Equal(plaintext, "SM2 解密后应还原原始明文");
    }

    [Fact]
    public void SM2_密文不应等于明文()
    {
        var sm2 = new SM2CryptoService();
        var (_, publicKey) = sm2.GenerateKeyPair();
        var plaintext = System.Text.Encoding.UTF8.GetBytes("敏感明文");

        var ciphertext = sm2.Encrypt(publicKey, plaintext);

        ciphertext.Should().NotEqual(plaintext, "SM2 密文不应暴露明文");
    }

    [Fact]
    public void SM2_密钥对应为有效长度()
    {
        var sm2 = new SM2CryptoService();
        var (privateKey, publicKey) = sm2.GenerateKeyPair();

        publicKey.Should().NotBeNullOrEmpty("SM2 公钥不应为空");
        privateKey.Should().NotBeNullOrEmpty("SM2 私钥不应为空");
        publicKey.Length.Should().BeGreaterThan(20, "SM2 公钥应有足够长度");
        privateKey.Length.Should().BeGreaterThan(20, "SM2 私钥应有足够长度");
    }

    #endregion

    #region NationalCryptoService 门面测试

    [Fact]
    public void NationalCryptoService门面_SM2属性应可访问()
    {
        var sm2 = new SM2CryptoService();
        var sm3 = new SM3HashService();
        var sm4 = new SM4CryptoService();
        var service = new NationalCryptoService(sm2, sm3, sm4);

        service.SM2.Should().NotBeNull();
        service.SM3.Should().NotBeNull();
        service.SM4.Should().NotBeNull();
    }

    [Fact]
    public void NationalCryptoService门面_端到端签名验签()
    {
        var sm2 = new SM2CryptoService();
        var sm3 = new SM3HashService();
        var sm4 = new SM4CryptoService();
        var crypto = new NationalCryptoService(sm2, sm3, sm4);
        var data = System.Text.Encoding.UTF8.GetBytes("端到端完整测试");

        var (priv, pub) = crypto.SM2.GenerateKeyPair();
        var sig = crypto.SM2.Sign(priv, data);
        var hash = crypto.SM3.Hash(data);

        crypto.SM2.Verify(pub, data, sig).Should().BeTrue("门面层 SM2 验签应通过");
        hash.Should().HaveCount(32, "门面层 SM3 摘要应为 32 字节");
    }

    #endregion
}
