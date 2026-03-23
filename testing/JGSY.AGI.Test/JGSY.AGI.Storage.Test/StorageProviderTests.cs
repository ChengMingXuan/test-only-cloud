using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Xunit;
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using JGSY.AGI.Storage.Entities;
using JGSY.AGI.Storage.Interfaces;
using JGSY.AGI.Storage.Strategies;

namespace JGSY.AGI.Test.JGSY.AGI.Storage.Test
{
    /// <summary>
    /// 存储服务单元测试
    /// </summary>
    public class StorageProviderTests
    {
        #region LocalStorageProvider Tests

        private LocalStorageProvider CreateLocalStorageProvider(string basePath)
        {
            var options = Options.Create(new LocalStorageOptions
            {
                RootPath = basePath,
                BaseUrl = "http://localhost/files"
            });
            var logger = new Mock<ILogger<LocalStorageProvider>>().Object;
            return new LocalStorageProvider(options, logger);
        }

        [Fact]
        public async Task LocalStorageProvider_Upload_Should_Save_File()
        {
            // Arrange
            var tempPath = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempPath);

            try
            {
                var provider = CreateLocalStorageProvider(tempPath);
                var content = "Test file content"u8.ToArray();
                using var stream = new MemoryStream(content);
                var objectKey = "test/file.txt";

                // Act
                var result = await provider.UploadAsync(stream, objectKey, "text/plain");

                // Assert
                result.Should().NotBeNull();
                result.Success.Should().BeTrue();
                result.ObjectKey.Should().Be(objectKey);
                File.Exists(Path.Combine(tempPath, objectKey)).Should().BeTrue();
            }
            finally
            {
                // Cleanup
                if (Directory.Exists(tempPath))
                    Directory.Delete(tempPath, true);
            }
        }

        [Fact]
        public async Task LocalStorageProvider_Download_Should_Return_File_Stream()
        {
            // Arrange
            var tempPath = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempPath);

            try
            {
                var provider = CreateLocalStorageProvider(tempPath);
                var content = "Test file content";
                var objectKey = "test/file.txt";
                var filePath = Path.Combine(tempPath, objectKey);
                Directory.CreateDirectory(Path.GetDirectoryName(filePath)!);
                await File.WriteAllTextAsync(filePath, content);

                // Act
                var stream = await provider.DownloadAsync(objectKey);

                // Assert
                stream.Should().NotBeNull();
                using var reader = new StreamReader(stream!);
                var downloadedContent = await reader.ReadToEndAsync();
                downloadedContent.Should().Be(content);
            }
            finally
            {
                if (Directory.Exists(tempPath))
                    Directory.Delete(tempPath, true);
            }
        }

        [Fact]
        public async Task LocalStorageProvider_Delete_Should_Remove_File()
        {
            // Arrange
            var tempPath = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempPath);

            try
            {
                var provider = CreateLocalStorageProvider(tempPath);
                var objectKey = "test/delete.txt";
                var filePath = Path.Combine(tempPath, objectKey);
                Directory.CreateDirectory(Path.GetDirectoryName(filePath)!);
                await File.WriteAllTextAsync(filePath, "to be deleted");

                // Act
                var result = await provider.DeleteAsync(objectKey);

                // Assert
                result.Should().BeTrue();
                File.Exists(filePath).Should().BeFalse();
            }
            finally
            {
                if (Directory.Exists(tempPath))
                    Directory.Delete(tempPath, true);
            }
        }

        [Fact]
        public async Task LocalStorageProvider_Exists_Should_Return_True_When_File_Exists()
        {
            // Arrange
            var tempPath = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempPath);

            try
            {
                var provider = CreateLocalStorageProvider(tempPath);
                var objectKey = "test/exists.txt";
                var filePath = Path.Combine(tempPath, objectKey);
                Directory.CreateDirectory(Path.GetDirectoryName(filePath)!);
                await File.WriteAllTextAsync(filePath, "test");

                // Act
                var exists = await provider.ExistsAsync(objectKey);

                // Assert
                exists.Should().BeTrue();
            }
            finally
            {
                if (Directory.Exists(tempPath))
                    Directory.Delete(tempPath, true);
            }
        }

        [Fact]
        public async Task LocalStorageProvider_Exists_Should_Return_False_When_File_Not_Exists()
        {
            // Arrange
            var tempPath = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempPath);

            try
            {
                var provider = CreateLocalStorageProvider(tempPath);

                // Act
                var exists = await provider.ExistsAsync("nonexistent.txt");

                // Assert
                exists.Should().BeFalse();
            }
            finally
            {
                if (Directory.Exists(tempPath))
                    Directory.Delete(tempPath, true);
            }
        }

        [Fact]
        public async Task LocalStorageProvider_Copy_Should_Create_Copy_Of_File()
        {
            // Arrange
            var tempPath = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempPath);

            try
            {
                var provider = CreateLocalStorageProvider(tempPath);
                var sourceKey = "source/file.txt";
                var destKey = "dest/file.txt";
                var sourcePath = Path.Combine(tempPath, sourceKey);
                Directory.CreateDirectory(Path.GetDirectoryName(sourcePath)!);
                await File.WriteAllTextAsync(sourcePath, "original content");

                // Act
                var result = await provider.CopyAsync(sourceKey, destKey);

                // Assert
                result.Should().BeTrue();
                File.Exists(Path.Combine(tempPath, destKey)).Should().BeTrue();
            }
            finally
            {
                if (Directory.Exists(tempPath))
                    Directory.Delete(tempPath, true);
            }
        }

        [Fact]
        public void LocalStorageProvider_StorageType_Should_Be_Local()
        {
            // Arrange
            var tempPath = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());

            try
            {
                var provider = CreateLocalStorageProvider(tempPath);

                // Assert
                provider.StorageType.Should().Be(StorageType.Local);
            }
            finally
            {
                if (Directory.Exists(tempPath))
                    Directory.Delete(tempPath, true);
            }
        }

        #endregion
    }

    /// <summary>
    /// 文件存储服务集成测试
    /// </summary>
    public class FileStorageServiceTests
    {
        [Fact]
        public void FileStorage_Entity_Should_Have_Required_Properties()
        {
            // Arrange & Act
            var fileStorage = new FileStorage
            {
                Id = Guid.NewGuid(),
                FileName = "test.txt",
                StorageFileName = "uuid-test.txt",
                ContentType = "text/plain",
                FileSize = 1024,
                StorageType = (int)StorageType.Local,
                FilePath = "files/test.txt",
                AccessLevel = (int)FileAccessLevel.Private,
                Md5Hash = "abc123",
                TenantId = Guid.NewGuid()
            };

            // Assert
            fileStorage.Id.Should().NotBeEmpty();
            fileStorage.FileName.Should().Be("test.txt");
            fileStorage.OriginalFileName.Should().Be("test.txt"); // 兼容属性
            fileStorage.ContentType.Should().Be("text/plain");
            fileStorage.FileSize.Should().Be(1024);
            fileStorage.StorageType.Should().Be((int)StorageType.Local);
            fileStorage.FilePath.Should().Be("files/test.txt");
            fileStorage.AccessLevel.Should().Be((int)FileAccessLevel.Private);
            fileStorage.Md5Hash.Should().Be("abc123");
            fileStorage.TenantId.Should().NotBeEmpty();
        }

        [Theory]
        [InlineData(StorageType.Local)]
        [InlineData(StorageType.AliyunOss)]
        [InlineData(StorageType.AwsS3)]
        [InlineData(StorageType.MinIO)]
        [InlineData(StorageType.TencentCos)]
        public void StorageType_Enum_Should_Have_Expected_Values(StorageType storageType)
        {
            // Assert
            Enum.IsDefined(typeof(StorageType), storageType).Should().BeTrue();
        }

        [Theory]
        [InlineData(FileAccessLevel.Private)]
        [InlineData(FileAccessLevel.PublicRead)]
        [InlineData(FileAccessLevel.PublicReadWrite)]
        public void FileAccessLevel_Enum_Should_Have_Expected_Values(FileAccessLevel accessLevel)
        {
            // Assert
            Enum.IsDefined(typeof(FileAccessLevel), accessLevel).Should().BeTrue();
        }
    }
}
