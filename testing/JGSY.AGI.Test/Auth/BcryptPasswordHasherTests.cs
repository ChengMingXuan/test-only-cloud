using FluentAssertions;
using JGSY.AGI.Common.Core.Security;
using Xunit;

namespace JGSY.AGI.Test.Auth
{
    public class BcryptPasswordHasherTests
    {
        private readonly BcryptPasswordHasher _hasher = new();

        [Fact]
        public void HashPassword_ShouldReturnBcryptFormat()
        {
            var hash = _hasher.HashPassword("test-password");

            hash.Should().NotBeNullOrEmpty();
            hash.Should().StartWith("$2"); // bcrypt prefix
        }

        [Fact]
        public void HashPassword_ShouldGenerateDifferentHashesForSamePassword()
        {
            var hash1 = _hasher.HashPassword("same-password");
            var hash2 = _hasher.HashPassword("same-password");

            // Due to random salt, hashes should differ
            hash1.Should().NotBe(hash2);
        }

        [Fact]
        public void VerifyPassword_CorrectPassword_ShouldReturnTrue()
        {
            var password = "P@ssw0rd!123";
            var hash = _hasher.HashPassword(password);

            _hasher.VerifyPassword(password, hash).Should().BeTrue();
        }

        [Fact]
        public void VerifyPassword_WrongPassword_ShouldReturnFalse()
        {
            var hash = _hasher.HashPassword("correct-password");

            _hasher.VerifyPassword("wrong-password", hash).Should().BeFalse();
        }

        [Fact]
        public void VerifyPassword_EmptyPassword_ShouldReturnFalse()
        {
            var hash = _hasher.HashPassword("some-password");

            _hasher.VerifyPassword("", hash).Should().BeFalse();
        }

        [Fact]
        public void HashPassword_EmptyString_ShouldWork()
        {
            var hash = _hasher.HashPassword("");
            hash.Should().NotBeNullOrEmpty();
            _hasher.VerifyPassword("", hash).Should().BeTrue();
        }

        [Fact]
        public void HashPassword_UnicodePassword_ShouldWork()
        {
            var password = "密码🔑Test123";
            var hash = _hasher.HashPassword(password);

            _hasher.VerifyPassword(password, hash).Should().BeTrue();
        }

        [Fact]
        public void HashPassword_LongPassword_ShouldWork()
        {
            var password = new string('a', 200);
            var hash = _hasher.HashPassword(password);

            _hasher.VerifyPassword(password, hash).Should().BeTrue();
        }

        [Fact]
        public void VerifyPassword_SimilarPasswords_ShouldReturnFalse()
        {
            var hash = _hasher.HashPassword("password123");

            _hasher.VerifyPassword("Password123", hash).Should().BeFalse(); // case sensitive
            _hasher.VerifyPassword("password124", hash).Should().BeFalse(); // one char diff
            _hasher.VerifyPassword("password123 ", hash).Should().BeFalse(); // trailing space
        }

        [Fact]
        public void HashPassword_WorkFactor12_ShouldHaveCorrectPrefix()
        {
            var hash = _hasher.HashPassword("test");

            // WorkFactor = 12 → $2a$12$ or $2b$12$
            hash.Should().MatchRegex(@"^\$2[ab]\$12\$");
        }
    }
}
