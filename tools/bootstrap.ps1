# ワンショット認証スクリプト
#
# ここで必要な外部サービス認証をまとめて行う:
#   - gcloud (Vision API 用) — CLI認証 + ADC認証 + Vision API 有効化
#   - clasp (GAS デプロイ用)

$ErrorActionPreference = "Stop"
$GCLOUD = Join-Path $env:LOCALAPPDATA "Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"

# gcloud stdout だけ受け取る (PS 5.1 の native stderr ラッピング回避のため cmd 経由)
function Invoke-GcloudStdout {
    param([Parameter(Mandatory)][string[]]$Args)
    $quotedArgs = ($Args | ForEach-Object { if ($_ -match '\s|=') { '"' + $_ + '"' } else { $_ } }) -join ' '
    $cmdline = "`"$GCLOUD`" $quotedArgs 2>nul"
    $out = & cmd.exe /c $cmdline
    if ($null -eq $out) { return "" }
    if ($out -is [array]) { return ($out -join "`n").Trim() }
    return "$out".Trim()
}

# gcloud を対話的に走らせ，stdout/stderr を画面に出す
# 戻り値は emit しない (呼び出し側は $LASTEXITCODE を参照する)
function Invoke-Gcloud {
    param([Parameter(Mandatory)][string[]]$Args)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $GCLOUD @Args
    } finally {
        $ErrorActionPreference = $prev
    }
}


Write-Host "== Step 1/3: Apps Script API の有効化確認 (手動)" -ForegroundColor Cyan
Write-Host "  以下のURLをブラウザで開き，「Google Apps Script API」を ON にしてください"
Write-Host "    https://script.google.com/home/usersettings"
$null = Read-Host "有効化済みなら [Enter] を押してください (中断は Ctrl+C)"


Write-Host "`n== Step 2/3: gcloud 認証 (Vision API用)" -ForegroundColor Cyan
if (-not (Test-Path $GCLOUD)) {
    Write-Error "gcloud が見つかりません: $GCLOUD"
}

# (2a) CLI 用ログイン
$activeAccount = Invoke-GcloudStdout -Args @("auth", "list", "--filter=status:ACTIVE", "--format=value(account)")
if ($activeAccount) {
    Write-Host "  [2a] CLI 認証済み: $activeAccount  (スキップ)"
} else {
    Write-Host "  [2a] gcloud auth login (CLI用)" -ForegroundColor Yellow
    Invoke-Gcloud -Args @("auth", "login")
    if ($LASTEXITCODE -ne 0) { throw "gcloud auth login に失敗" }
}

# (2b) ADC 用ログイン
$adcPath = Join-Path $env:APPDATA "gcloud\application_default_credentials.json"
if (Test-Path $adcPath) {
    Write-Host "  [2b] ADC 認証済み: $adcPath  (スキップ)"
} else {
    Write-Host "  [2b] gcloud auth application-default login (ADC用)" -ForegroundColor Yellow
    Write-Host "       ★重要★ コンセント画面では『すべて選択』にチェックを入れてください" -ForegroundColor Yellow
    Invoke-Gcloud -Args @("auth", "application-default", "login")
    if ($LASTEXITCODE -ne 0) { throw "gcloud auth application-default login に失敗" }
}

# 現在のプロジェクトを取得
Write-Host "`n  現在の gcloud プロジェクトを確認中..."
$project = Invoke-GcloudStdout -Args @("config", "get-value", "project")
if ($project -eq "(unset)" -or -not $project) {
    Write-Host "  プロジェクトが未設定．利用可能なプロジェクト一覧:" -ForegroundColor Yellow
    $listing = Invoke-GcloudStdout -Args @("projects", "list", "--format=value(projectId)")
    if (-not $listing) {
        Write-Host "  (プロジェクトがひとつもありません)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  中断して以下を先に実行してから再実行してください:" -ForegroundColor Yellow
        Write-Host "    gcloud projects create ID --name=`"NAME`"" -ForegroundColor Yellow
        throw "プロジェクト未作成"
    }
    $listing -split "`n" | ForEach-Object { Write-Host "    - $_" }
    $project = Read-Host "  使用する projectId を入力"
    if (-not $project) { throw "projectId が入力されませんでした" }
    Invoke-Gcloud -Args @("config", "set", "project", $project)
    if ($LASTEXITCODE -ne 0) { throw "gcloud config set project に失敗" }
}
Write-Host "  project = $project" -ForegroundColor Green

Write-Host "`n  Vision API を有効化中..."
Invoke-Gcloud -Args @("services", "enable", "vision.googleapis.com", "--project=$project")
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Vision API の有効化に失敗しました．以下を手動で開いて有効化してください:"
    Write-Warning "  https://console.cloud.google.com/apis/library/vision.googleapis.com?project=$project"
    Write-Warning "課金アカウント未設定の場合は先に以下で紐付け:"
    Write-Warning "  https://console.cloud.google.com/billing?project=$project"
} else {
    Write-Host "  Vision API 有効化 OK" -ForegroundColor Green
}

# ADC のクォータプロジェクトを設定
Write-Host "`n  ADC の quota-project を設定中..."
Invoke-Gcloud -Args @("auth", "application-default", "set-quota-project", $project)


Write-Host "`n== Step 3/3: clasp login (Apps Script デプロイ用)" -ForegroundColor Cyan
$claspAuth = Join-Path $env:USERPROFILE ".clasprc.json"
if (Test-Path $claspAuth) {
    Write-Host "  既に clasp login 済み: $claspAuth  (スキップ)"
} else {
    clasp login
    if ($LASTEXITCODE -ne 0) { throw "clasp login に失敗" }
}

Write-Host "`n== 認証セットアップ完了 ==" -ForegroundColor Green
Write-Host "次の実行:"
Write-Host "  1. python tools\ocr_descriptions.py      (Vision API で説明文抽出)"
Write-Host "  2. powershell -File tools\setup_gas.ps1  (Sheet + GAS を自動構築)"
