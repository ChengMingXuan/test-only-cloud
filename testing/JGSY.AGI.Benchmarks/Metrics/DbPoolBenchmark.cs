using System;
using System.Collections.Concurrent;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using Npgsql;
using Xunit;

namespace JGSY.AGI.Benchmarks.Metrics
{
    public class DbPoolBenchmark
    {
        private static string GetConn(string defaultDb)
        {
            var env = Environment.GetEnvironmentVariable("BENCH_CONN");
            if (!string.IsNullOrWhiteSpace(env)) return env;
            var password = Environment.GetEnvironmentVariable("POSTGRES_PASSWORD") ?? throw new InvalidOperationException("必须配置环境变量 POSTGRES_PASSWORD");
            return $"Host=localhost;Port=5432;Database={defaultDb};Username=postgres;Password={password};Pooling=true;Minimum Pool Size=10;Maximum Pool Size=100;Connection Idle Lifetime=300;Command Timeout=60";
        }

        [Trait("Category", "Benchmark")]
        [Fact]
        public async Task ConnectionPool_ConcurrencyBenchmark()
        {
            var database = Environment.GetEnvironmentVariable("BENCH_DB") ?? "jgsy_account";
            int concurrency = int.TryParse(Environment.GetEnvironmentVariable("BENCH_CONCURRENCY"), out var c) ? c : 50;
            int iterationsPerWorker = int.TryParse(Environment.GetEnvironmentVariable("BENCH_ITER"), out var it) ? it : 20;

            string connString = GetConn(database);

            var durations = new ConcurrentBag<long>();
            var errors = new ConcurrentBag<Exception>();

            async Task Worker(int id)
            {
                try
                {
                    for (int i = 0; i < iterationsPerWorker; i++)
                    {
                        var sw = Stopwatch.StartNew();
                        await using var conn = new NpgsqlConnection(connString);
                        await conn.OpenAsync();
                        await using var cmd = new NpgsqlCommand("SET search_path TO account; SELECT COUNT(*) FROM account_user_membership;", conn);
                        _ = await cmd.ExecuteScalarAsync();
                        sw.Stop();
                        durations.Add(sw.ElapsedMilliseconds);
                    }
                }
                catch (Exception ex)
                {
                    errors.Add(ex);
                }
            }

            var start = Stopwatch.StartNew();
            var tasks = Enumerable.Range(0, concurrency).Select(Worker).ToArray();
            await Task.WhenAll(tasks);
            start.Stop();

            if (!durations.Any())
            {
                Assert.False(true, $"No measurements recorded. Errors: {string.Join(" | ", errors.Select(e => e.Message))}");
            }

            var totalOps = durations.Count;
            var avg = durations.Average();
            var ordered = durations.OrderBy(x => x).ToArray();
            double p95 = ordered[(int)Math.Floor(ordered.Length * 0.95)];
            double p99 = ordered[(int)Math.Floor(ordered.Length * 0.99)];
            double throughputQps = totalOps / (start.Elapsed.TotalSeconds);

            Console.WriteLine($"DB: {database} | Concurrency: {concurrency} | Iter/Worker: {iterationsPerWorker}");
            Console.WriteLine($"Total Ops: {totalOps} | Total Time: {start.Elapsed.TotalSeconds:F2}s | Throughput: {throughputQps:F1} ops/s");
            Console.WriteLine($"Avg: {avg:F1} ms | P95: {p95:F1} ms | P99: {p99:F1} ms | Errors: {errors.Count}");

            Assert.True(throughputQps > 50, "Throughput too low, pool may not be effective.");
            Assert.True(avg < 50, "Average latency too high; investigate indexes/pool config.");
            Assert.True(errors.Count == 0, $"Errors occurred: {string.Join(" | ", errors.Select(e => e.Message))}");
        }
    }
}
