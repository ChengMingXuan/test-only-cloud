using FluentAssertions;
using JGSY.AGI.Common.Core.Utils;
using Xunit;

namespace JGSY.AGI.Test.Common
{
    public class ApiResultTests
    {
        #region ApiResult<T> 泛型版本

        [Fact]
        public void Ok_WithData_ShouldReturnSuccessResult()
        {
            var result = ApiResult<string>.Ok("test-data");

            result.Success.Should().BeTrue();
            result.Data.Should().Be("test-data");
            result.Code.Should().Be("200");
            result.Message.Should().Be("成功");
        }

        [Fact]
        public void Ok_WithCustomMessage_ShouldReturnCorrectMessage()
        {
            var result = ApiResult<int>.Ok(42, "操作完成");

            result.Success.Should().BeTrue();
            result.Data.Should().Be(42);
            result.Message.Should().Be("操作完成");
            result.Code.Should().Be("200");
        }

        [Fact]
        public void Ok_WithCustomCode_ShouldReturnCorrectCode()
        {
            var result = ApiResult<string>.Ok("data", "成功", 201);

            result.Success.Should().BeTrue();
            result.Code.Should().Be("201");
        }

        [Fact]
        public void Ok_WithStringCode_ShouldReturnCorrectCode()
        {
            var result = ApiResult<string>.Ok("data", "成功", "CUSTOM_200");

            result.Success.Should().BeTrue();
            result.Code.Should().Be("CUSTOM_200");
        }

        [Fact]
        public void Ok_WithNullData_ShouldSucceed()
        {
            var result = ApiResult<object>.Ok(null!);

            result.Success.Should().BeTrue();
            result.Data.Should().BeNull();
        }

        [Fact]
        public void Fail_Default_ShouldReturnFailResult()
        {
            var result = ApiResult<string>.Fail();

            result.Success.Should().BeFalse();
            result.Message.Should().Be("失败");
            result.Code.Should().Be("400");
            result.Data.Should().BeNull();
        }

        [Fact]
        public void Fail_WithCustomMessage_ShouldReturnCorrectMessage()
        {
            var result = ApiResult<string>.Fail("参数错误", 422);

            result.Success.Should().BeFalse();
            result.Message.Should().Be("参数错误");
            result.Code.Should().Be("422");
        }

        [Fact]
        public void Fail_WithStringCode_ShouldReturnCorrectCode()
        {
            var result = ApiResult<string>.Fail("业务错误", "BIZ_001");

            result.Success.Should().BeFalse();
            result.Code.Should().Be("BIZ_001");
        }

        [Fact]
        public void Unauthorized_Default_ShouldReturn401()
        {
            var result = ApiResult<string>.Unauthorized();

            result.Success.Should().BeFalse();
            result.Code.Should().Be("401");
            result.Message.Should().Be("未授权");
        }

        [Fact]
        public void Unauthorized_WithCustomMessage_ShouldReturnMessage()
        {
            var result = ApiResult<string>.Unauthorized("Token已过期");

            result.Success.Should().BeFalse();
            result.Code.Should().Be("401");
            result.Message.Should().Be("Token已过期");
        }

        [Fact]
        public void Forbidden_Default_ShouldReturn403()
        {
            var result = ApiResult<string>.Forbidden();

            result.Success.Should().BeFalse();
            result.Code.Should().Be("403");
            result.Message.Should().Be("禁止访问");
        }

        [Fact]
        public void Forbidden_WithCustomMessage_ShouldReturnMessage()
        {
            var result = ApiResult<string>.Forbidden("权限不足");

            result.Message.Should().Be("权限不足");
        }

        [Fact]
        public void NotFound_Default_ShouldReturn404()
        {
            var result = ApiResult<string>.NotFound();

            result.Success.Should().BeFalse();
            result.Code.Should().Be("404");
            result.Message.Should().Be("资源不存在");
        }

        [Fact]
        public void NotFound_WithCustomMessage_ShouldReturnMessage()
        {
            var result = ApiResult<string>.NotFound("用户不存在");

            result.Message.Should().Be("用户不存在");
        }

        [Fact]
        public void Timestamp_ShouldBeIso8601Format()
        {
            var result = ApiResult<string>.Ok("data");

            result.Timestamp.Should().NotBeNullOrEmpty();
            result.Timestamp.Should().EndWith("Z");
            result.Timestamp.Should().Contain("T");
        }

        [Fact]
        public void TraceId_ShouldNotBeNull()
        {
            var result = ApiResult<string>.Ok("data");

            result.TraceId.Should().NotBeNullOrEmpty();
        }

        [Fact]
        public void Ok_WithComplexType_ShouldPreserveData()
        {
            var data = new { Name = "Test", Value = 123 };
            var result = ApiResult<object>.Ok(data);

            result.Data.Should().Be(data);
        }

        [Fact]
        public void Ok_WithListData_ShouldPreserveList()
        {
            var data = new List<string> { "a", "b", "c" };
            var result = ApiResult<List<string>>.Ok(data);

            result.Data.Should().HaveCount(3);
            result.Data.Should().Contain("b");
        }

        #endregion

        #region ApiResult 非泛型版本

        [Fact]
        public void NonGeneric_Ok_ShouldReturnSuccessWithNullData()
        {
            var result = ApiResult.Ok();

            result.Success.Should().BeTrue();
            result.Data.Should().BeNull();
            result.Message.Should().Be("成功");
            result.Code.Should().Be("200");
        }

        [Fact]
        public void NonGeneric_Ok_WithCustomMessage_ShouldWork()
        {
            var result = ApiResult.Ok("操作成功", 200);

            result.Success.Should().BeTrue();
            result.Message.Should().Be("操作成功");
        }

        [Fact]
        public void NonGeneric_Fail_ShouldReturnFailWithNullData()
        {
            var result = ApiResult.Fail();

            result.Success.Should().BeFalse();
            result.Data.Should().BeNull();
            result.Message.Should().Be("失败");
            result.Code.Should().Be("400");
        }

        [Fact]
        public void NonGeneric_Fail_WithCustomMessage_ShouldWork()
        {
            var result = ApiResult.Fail("系统繁忙", 503);

            result.Success.Should().BeFalse();
            result.Message.Should().Be("系统繁忙");
            result.Code.Should().Be("503");
        }

        #endregion

        #region 类型正确性

        [Fact]
        public void ApiResult_ShouldInheritFromGenericApiResult()
        {
            var result = ApiResult.Ok();

            result.Should().BeAssignableTo<ApiResult<object>>();
        }

        [Theory]
        [InlineData(200)]
        [InlineData(201)]
        [InlineData(400)]
        [InlineData(404)]
        [InlineData(500)]
        public void Ok_WithVariousCodes_ShouldConvertToString(int code)
        {
            var result = ApiResult<string>.Ok("test", "msg", code);
            result.Code.Should().Be(code.ToString());
        }

        [Theory]
        [InlineData(400)]
        [InlineData(422)]
        [InlineData(500)]
        [InlineData(503)]
        public void Fail_WithVariousCodes_ShouldConvertToString(int code)
        {
            var result = ApiResult<string>.Fail("error", code);
            result.Code.Should().Be(code.ToString());
        }

        #endregion
    }
}
