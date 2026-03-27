param(
    [int]$IntervalSeconds = 900,
    [string]$Model = "smollm2:135m"
)

$RepoRoot = "C:\Users\legom\OneDrive\Desktop\New folder\ivystudy"
$PracticeRoot = Join-Path $RepoRoot "ib-practice-platform"
$QueueDb = Join-Path $PracticeRoot "bots\queue.db"
$OpenCsLessons = "/home/ivysfyoq/public_html/ib-practice-platform/data/lessons"
$OpenCsData = "/home/ivysfyoq/public_html/ib-practice-platform/data"

function Get-PendingLessons {
    if (-not (Test-Path $QueueDb)) { return 0 }
    $out = python -c "import sqlite3; c=sqlite3.connect(r'''$QueueDb'''); cur=c.cursor(); cur.execute('select count(*) from lessons where status=?', ('pending',)); print(cur.fetchone()[0]); c.close()"
    if ($LASTEXITCODE -ne 0) { return 0 }
    return [int]$out
}

Write-Output "[auto-sync] Starting continuous generate-and-sync loop"
Write-Output "[auto-sync] Model=$Model Interval=${IntervalSeconds}s"

while ($true) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Output "[$ts] Tick"

    $pending = Get-PendingLessons
    Write-Output "[$ts] Pending lessons: $pending"

    if ($pending -gt 0) {
        Write-Output "[$ts] Generating pending lessons..."
        Set-Location $PracticeRoot
        python lesson_generator.py --all --model $Model

        Write-Output "[$ts] Deploying to cPanel (practice target)..."
        Set-Location $RepoRoot
        $env:PYTHONIOENCODING = "utf-8"
        python deploy.py deploy --target practice

        Write-Output "[$ts] Syncing generated lessons to OpenCS..."
        ssh opencs "mkdir -p $OpenCsLessons $OpenCsData"
        scp -r "ib-practice-platform/data/lessons" "opencs:$OpenCsData/"
        scp "ib-practice-platform/data/lesson_quality_report.json" "ib-practice-platform/data/lesson_quality_report.md" "opencs:$OpenCsData/"

        Write-Output "[$ts] Cycle complete"
    }

    Start-Sleep -Seconds $IntervalSeconds
}
