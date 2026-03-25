$env:FULL_RUN = "1"
Set-Location D:\2026\aiops.v2\testing\tests\playwright-tests

$specs = @(
    "tests/generated/supplement/e2e-111-blockchain-certs.spec.ts",
    "tests/generated/supplement/e2e-112-blockchain-verify.spec.ts",
    "tests/generated/supplement/e2e-113-blockchain-records.spec.ts",
    "tests/generated/supplement/e2e-114-blockchain-explorer.spec.ts"
)

$result = & npx playwright test @specs 2>&1
$result | Out-File "d:\2026\aiops.v2\TestResults\playwright-run.log" -Encoding UTF8
Write-Host "EXIT: $LASTEXITCODE"
$result | Select-Object -Last 10 | ForEach-Object { Write-Host $_ }
