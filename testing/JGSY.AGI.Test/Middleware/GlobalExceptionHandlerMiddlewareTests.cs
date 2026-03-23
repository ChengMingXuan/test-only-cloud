using FluentAssertions;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using System.Net;
using System.Text;
using System.Text.Json;
using JGSY.AGI.Common.Core.Middleware;
using Xunit;

namespace JGSY.AGI.Test.Middleware
{
    public class GlobalExceptionHandlerMiddlewareTests
    {
        private readonly ILogger<GlobalExceptionHandlerMiddleware> _logger =
            NullLogger<GlobalExceptionHandlerMiddleware>.Instance;

        private GlobalExceptionHandlerMiddleware CreateMiddleware(RequestDelegate next)
        {
            return new GlobalExceptionHandlerMiddleware(next, _logger);
        }

        [Fact]
        public async Task InvokeAsync_NoException_ShouldCallNextAndReturn()
        {
            var nextCalled = false;
            var middleware = CreateMiddleware(ctx =>
            {
                nextCalled = true;
                return Task.CompletedTask;
            });

            var context = new DefaultHttpContext();
            context.Response.Body = new MemoryStream();

            await middleware.InvokeAsync(context);

            nextCalled.Should().BeTrue();
        }

        [Fact]
        public async Task InvokeAsync_UnauthorizedAccessException_ShouldReturn401()
        {
            var middleware = CreateMiddleware(_ => throw new UnauthorizedAccessException("No access"));
            var context = CreateHttpContext();

            await middleware.InvokeAsync(context);

            context.Response.StatusCode.Should().Be((int)HttpStatusCode.Unauthorized);
            var body = await ReadResponseBody(context);
            body.Should().Contain("401");
        }

        [Fact]
        public async Task InvokeAsync_KeyNotFoundException_ShouldReturn404()
        {
            var middleware = CreateMiddleware(_ => throw new KeyNotFoundException("Not found"));
            var context = CreateHttpContext();

            await middleware.InvokeAsync(context);

            context.Response.StatusCode.Should().Be((int)HttpStatusCode.NotFound);
            var body = await ReadResponseBody(context);
            body.Should().Contain("404");
        }

        [Fact]
        public async Task InvokeAsync_ArgumentException_ShouldReturn400()
        {
            var middleware = CreateMiddleware(_ => throw new ArgumentException("Bad arg"));
            var context = CreateHttpContext();

            await middleware.InvokeAsync(context);

            context.Response.StatusCode.Should().Be((int)HttpStatusCode.BadRequest);
            var body = await ReadResponseBody(context);
            body.Should().Contain("400");
        }

        [Fact]
        public async Task InvokeAsync_ArgumentNullException_ShouldReturn400()
        {
            var middleware = CreateMiddleware(_ => throw new ArgumentNullException("param"));
            var context = CreateHttpContext();

            await middleware.InvokeAsync(context);

            context.Response.StatusCode.Should().Be((int)HttpStatusCode.BadRequest);
        }

        [Fact]
        public async Task InvokeAsync_InvalidOperationException_ShouldReturn500()
        {
            var middleware = CreateMiddleware(_ => throw new InvalidOperationException("Invalid"));
            var context = CreateHttpContext();

            await middleware.InvokeAsync(context);

            context.Response.StatusCode.Should().Be((int)HttpStatusCode.InternalServerError);
            var body = await ReadResponseBody(context);
            body.Should().Contain("500");
        }

        [Fact]
        public async Task InvokeAsync_NotImplementedException_ShouldReturn501()
        {
            var middleware = CreateMiddleware(_ => throw new NotImplementedException("Not impl"));
            var context = CreateHttpContext();

            await middleware.InvokeAsync(context);

            context.Response.StatusCode.Should().Be((int)HttpStatusCode.NotImplemented);
        }

        [Fact]
        public async Task InvokeAsync_TimeoutException_ShouldReturn408()
        {
            var middleware = CreateMiddleware(_ => throw new TimeoutException("Timed out"));
            var context = CreateHttpContext();

            await middleware.InvokeAsync(context);

            context.Response.StatusCode.Should().Be((int)HttpStatusCode.RequestTimeout);
        }

        [Fact]
        public async Task InvokeAsync_GenericException_ShouldReturn500()
        {
            var middleware = CreateMiddleware(_ => throw new Exception("Unknown error"));
            var context = CreateHttpContext();

            await middleware.InvokeAsync(context);

            context.Response.StatusCode.Should().Be((int)HttpStatusCode.InternalServerError);
        }

        [Fact]
        public async Task InvokeAsync_Response_ShouldBeJson()
        {
            var middleware = CreateMiddleware(_ => throw new Exception("error"));
            var context = CreateHttpContext();

            await middleware.InvokeAsync(context);

            context.Response.ContentType.Should().Contain("application/json");
        }

        [Fact]
        public async Task InvokeAsync_Response_ShouldContainSuccessFalse()
        {
            var middleware = CreateMiddleware(_ => throw new Exception("error"));
            var context = CreateHttpContext();

            await middleware.InvokeAsync(context);

            var body = await ReadResponseBody(context);
            body.Should().Contain("\"success\":false");
        }

        [Fact]
        public async Task InvokeAsync_Response_ShouldContainTraceId()
        {
            var middleware = CreateMiddleware(_ => throw new Exception("error"));
            var context = CreateHttpContext();

            await middleware.InvokeAsync(context);

            var body = await ReadResponseBody(context);
            body.Should().Contain("traceId");
        }

        [Fact]
        public async Task InvokeAsync_Response_ShouldContainTimestamp()
        {
            var middleware = CreateMiddleware(_ => throw new Exception("error"));
            var context = CreateHttpContext();

            await middleware.InvokeAsync(context);

            var body = await ReadResponseBody(context);
            body.Should().Contain("timestamp");
        }

        private static DefaultHttpContext CreateHttpContext()
        {
            var context = new DefaultHttpContext();
            context.Response.Body = new MemoryStream();
            return context;
        }

        private static async Task<string> ReadResponseBody(DefaultHttpContext context)
        {
            context.Response.Body.Seek(0, SeekOrigin.Begin);
            using var reader = new StreamReader(context.Response.Body);
            return await reader.ReadToEndAsync();
        }
    }
}
