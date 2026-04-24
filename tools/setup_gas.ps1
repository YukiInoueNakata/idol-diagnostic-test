# GAS + Spreadsheet を clasp で自動セットアップ
#
# 事前準備 (1回だけ):
#   1. Apps Script API を有効化
#      https://script.google.com/home/usersettings を開いて「Google Apps Script API」を ON
#   2. clasp login
#      PowerShellで `clasp login` を実行 → ブラウザで Google アカウント認証
#
# 実行:
#   cd "D:\OneDrive\01プログラム作成\アイドル診断テスト\アイドル診断テスト2026"
#   powershell -ExecutionPolicy Bypass -File tools/setup_gas.ps1

$ErrorActionPreference = "Stop"

$REPO_ROOT = Split-Path -Parent $PSScriptRoot
$GAS_DIR = Join-Path $REPO_ROOT "gas"
$SRC_CONFIG = Join-Path $REPO_ROOT "src\config.json"

Write-Host "== 1. clasp 認証チェック" -ForegroundColor Cyan
$claspAuthPath = Join-Path $env:USERPROFILE ".clasprc.json"
if (-not (Test-Path $claspAuthPath)) {
    Write-Error @"
clasp にログインされていません．以下を先に実行してください:
    clasp login
その後にこのスクリプトを再実行．
"@
}
Write-Host "  OK: $claspAuthPath"

# appsscript.json はウェブアプリ公開設定を含める
$appsscriptManifest = @'
{
  "timeZone": "Asia/Tokyo",
  "dependencies": {},
  "exceptionLogging": "STACKDRIVER",
  "runtimeVersion": "V8",
  "webapp": {
    "access": "ANYONE_ANONYMOUS",
    "executeAs": "USER_DEPLOYING"
  }
}
'@

Push-Location $GAS_DIR
try {
    Write-Host "`n== 2. clasp プロジェクトの確認/作成" -ForegroundColor Cyan
    if (Test-Path ".clasp.json") {
        Write-Host "  既存の .clasp.json を検出．再利用します"
        $clasp = Get-Content ".clasp.json" | ConvertFrom-Json
        $scriptId = $clasp.scriptId
        Write-Host "  scriptId = $scriptId"
    } else {
        Write-Host "  新規スプレッドシート＋Apps Scriptプロジェクトを作成中..."
        clasp create --type sheets --title "アイドル診断テスト 2026 記録" --rootDir .
        if ($LASTEXITCODE -ne 0) { throw "clasp create に失敗" }
    }

    Write-Host "`n== 3. appsscript.json を差し替え (ウェブアプリ公開設定)" -ForegroundColor Cyan
    # clasp は BOM付きJSONを invalid manifest と判定するので BOM なしで書く
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) "appsscript.json"), $appsscriptManifest, $utf8NoBom)
    Write-Host "  OK"

    Write-Host "`n== 4. recorder.gs を push" -ForegroundColor Cyan
    clasp push --force
    if ($LASTEXITCODE -ne 0) { throw "clasp push に失敗" }

    Write-Host "`n== 5. setupSheet() をリモート実行 (初回のみヘッダ行作成)" -ForegroundColor Cyan
    # clasp run は Apps Script API v1 を使う．失敗しても続行．
    try {
        clasp run setupSheet 2>&1 | Out-Host
    } catch {
        Write-Host "  setupSheet の自動実行は失敗しました．ブラウザで 1 回だけ実行してください:" -ForegroundColor Yellow
        Write-Host "    clasp open" -ForegroundColor Yellow
    }

    Write-Host "`n== 6. ウェブアプリとしてデプロイ" -ForegroundColor Cyan
    $deployOut = clasp deploy --description "idol-recorder v1" 2>&1 | Out-String
    Write-Host $deployOut
    # clasp v3 出力例: "Deployed AKfycb... @1" / "- AKfycb... @HEAD" (list) の両方に対応
    $match = [regex]::Match($deployOut, "(?:Deployed|-)\s+(AKfycb[a-zA-Z0-9_-]+)\s+@(\d+)")
    $deploymentId = if ($match.Success) { $match.Groups[1].Value } else { $null }
    if (-not $deploymentId) {
        # 既存デプロイから探す (@HEAD 以外の versioned を優先)
        $list = clasp list-deployments 2>&1 | Out-String
        $match = [regex]::Match($list, "-\s+(AKfycb[a-zA-Z0-9_-]+)\s+@(\d+)")
        if ($match.Success) { $deploymentId = $match.Groups[1].Value }
    }

    if (-not $deploymentId) { throw "deploymentId を取得できませんでした．clasp list-deployments を目視確認してください" }
    $webAppUrl = "https://script.google.com/macros/s/$deploymentId/exec"

    Write-Host "`n== 7. src/config.json に URL を書き込み" -ForegroundColor Cyan
    # UTF-8 で読み書き (Set-Content の既定エンコーディング問題を回避)
    $cfgJson = [System.IO.File]::ReadAllText($SRC_CONFIG, [System.Text.Encoding]::UTF8)
    $cfg = $cfgJson | ConvertFrom-Json
    $cfg.gasEndpoint = $webAppUrl
    $newJson = $cfg | ConvertTo-Json -Depth 4
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($SRC_CONFIG, $newJson, $utf8NoBom)
    Write-Host "  OK: $webAppUrl"

    Write-Host "`n== 完了 ==" -ForegroundColor Green
    Write-Host "ウェブアプリURL : $webAppUrl"
    Write-Host "スプレッドシート: (clasp open --webapp でブラウザ確認できます)"
    Write-Host "動作確認:"
    Write-Host "  curl $webAppUrl"
} finally {
    Pop-Location
}
