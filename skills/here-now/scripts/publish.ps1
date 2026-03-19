#Requires -Version 5.1
<#
.SYNOPSIS
    Publish files and folders to here.now instant web hosting

.EXAMPLE
    .\publish.ps1 C:\path\to\site
    .\publish.ps1 C:\path\to\file.pdf -Title "My Document"
    .\publish.ps1 C:\path\to\site -Slug bright-canvas-a7k2
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Path,

    [string]$Slug,
    [string]$ClaimToken,
    [string]$Title,
    [string]$Description,
    [int]$Ttl,
    [string]$Client,
    [string]$ApiKey,
    [string]$BaseUrl = "https://here.now"
)

$ErrorActionPreference = "Stop"

# Configuration
$BaseUrl = $BaseUrl.TrimEnd('/')
$CredentialsFile = "$env:USERPROFILE\.herenow\credentials"
$StateDir = ".herenow"
$StateFile = "$StateDir\state.json"

# Determine API key source
$script:ApiKeySource = "none"
$EffectiveApiKey = $ApiKey

if ($EffectiveApiKey) {
    $script:ApiKeySource = "flag"
} elseif ($env:HERENOW_API_KEY) {
    $EffectiveApiKey = $env:HERENOW_API_KEY
    $script:ApiKeySource = "env"
} elseif (Test-Path $CredentialsFile) {
    $EffectiveApiKey = Get-Content $CredentialsFile -Raw
    $EffectiveApiKey = $EffectiveApiKey.Trim()
    if ($EffectiveApiKey) {
        $script:ApiKeySource = "credentials"
    }
}

# Validate path
if (-not (Test-Path $Path)) {
    throw "Path does not exist: $Path"
}

# Determine auth mode
$AuthMode = if ($EffectiveApiKey) { "authenticated" } else { "anonymous" }

# Auto-load claim token from state file for anonymous updates
if ($Slug -and -not $ClaimToken -and -not $EffectiveApiKey -and (Test-Path $StateFile)) {
    try {
        $state = Get-Content $StateFile -Raw | ConvertFrom-Json
        $ClaimToken = $state.publishes.$Slug.claimToken
    } catch {}
}

# Build file manifest
function Get-FileHash256($filePath) {
    $stream = [System.IO.File]::OpenRead($filePath)
    $hash = [System.BitConverter]::ToString($sha256.ComputeHash($stream)).Replace("-", "").ToLower()
    $stream.Close()
    return $hash
}

$sha256 = [System.Security.Cryptography.SHA256]::Create()
$files = @()
$fileMap = @{}

if (Test-Path $Path -PathType Leaf) {
    # Single file
    $item = Get-Item $Path
    $files += @{
        path = $item.Name
        size = $item.Length
        contentType = "application/octet-stream"
        hash = (Get-FileHash256 $Path)
    }
    $fileMap[$item.Name] = $Path
} else {
    # Directory
    Get-ChildItem $Path -Recurse -File | Where-Object { $_.Name -ne ".DS_Store" } | ForEach-Object {
        $relPath = $_.FullName.Substring((Resolve-Path $Path).Path.Length + 1).Replace("\", "/")
        $files += @{
            path = $relPath
            size = $_.Length
            contentType = "application/octet-stream"
            hash = (Get-FileHash256 $_.FullName)
        }
        $fileMap[$relPath] = $_.FullName
    }
}

$sha256.Dispose()

if ($files.Count -eq 0) {
    throw "No files found"
}

Write-Host "Creating publish ($($files.Count) files)..." -ForegroundColor Cyan

# Build request body
$body = @{ files = $files }

if ($Ttl) {
    $body.ttlSeconds = $Ttl
}

if ($Title -or $Description) {
    $body.viewer = @{}
    if ($Title) { $body.viewer.title = $Title }
    if ($Description) { $body.viewer.description = $Description }
}

if ($ClaimToken -and $Slug -and -not $EffectiveApiKey) {
    $body.claimToken = $ClaimToken
}

# Determine endpoint
$headers = @{ "content-type" = "application/json" }
if ($EffectiveApiKey) {
    $headers["authorization"] = "Bearer $EffectiveApiKey"
}

$clientValue = if ($Client) { "$Client/publish-ps" } else { "here-now-publish-ps" }
$headers["x-herenow-client"] = $clientValue

if ($Slug) {
    $url = "$BaseUrl/api/v1/publish/$Slug"
    $method = "PUT"
} else {
    $url = "$BaseUrl/api/v1/publish"
    $method = "POST"
}

# Step 1: Create/update publish
try {
    $response = Invoke-RestMethod -Uri $url -Method $method -Headers $headers -Body ($body | ConvertTo-Json -Depth 10)
} catch {
    throw "Failed to create publish: $_"
}

$outSlug = $response.slug
$versionId = $response.upload.versionId
$finalizeUrl = $response.upload.finalizeUrl
$siteUrl = $response.siteUrl
$uploads = $response.upload.uploads
$skipped = $response.upload.skipped

Write-Host "Uploading $($uploads.Count) files ($($skipped.Count) unchanged)..." -ForegroundColor Cyan

# Step 2: Upload files
$uploadErrors = 0
foreach ($upload in $uploads) {
    $uploadPath = $upload.path
    $uploadUrl = $upload.url
    $localFile = $fileMap[$uploadPath]
    
    if (-not $localFile -or -not (Test-Path $localFile)) {
        Write-Warning "Missing local file for $uploadPath"
        $uploadErrors++
        continue
    }
    
    try {
        $fileBytes = [System.IO.File]::ReadAllBytes($localFile)
        $uploadHeaders = @{}
        if ($upload.headers."Content-Type") {
            $uploadHeaders["Content-Type"] = $upload.headers."Content-Type"
        }
        Invoke-RestMethod -Uri $uploadUrl -Method PUT -Body $fileBytes -Headers $uploadHeaders | Out-Null
    } catch {
        Write-Warning "Upload failed for $uploadPath`: $_"
        $uploadErrors++
    }
}

if ($uploadErrors -gt 0) {
    throw "$uploadErrors file(s) failed to upload"
}

# Step 3: Finalize
Write-Host "Finalizing..." -ForegroundColor Cyan
try {
    $finResponse = Invoke-RestMethod -Uri $finalizeUrl -Method POST -Headers $headers -Body (@{ versionId = $versionId } | ConvertTo-Json)
} catch {
    throw "Finalize failed: $_"
}

# Save state
if (-not (Test-Path $StateDir)) {
    New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
}

$state = @{ publishes = @{} }
if (Test-Path $StateFile) {
    try {
        $state = Get-Content $StateFile -Raw | ConvertFrom-Json -AsHashtable
    } catch {
        $state = @{ publishes = @{} }
    }
}

$entry = @{ siteUrl = $siteUrl }
if ($response.claimToken) { $entry.claimToken = $response.claimToken }
if ($response.claimUrl) { $entry.claimUrl = $response.claimUrl }
if ($response.expiresAt) { $entry.expiresAt = $response.expiresAt }

$state.publishes[$outSlug] = $entry
$state | ConvertTo-Json -Depth 10 | Set-Content $StateFile

# Output
Write-Host "`n$siteUrl" -ForegroundColor Green

$persistence = if ($AuthMode -eq "authenticated") { "permanent" } else { "expires_24h" }

Write-Host "`npublish_result.site_url=$siteUrl" -ForegroundColor DarkGray
Write-Host "publish_result.auth_mode=$AuthMode" -ForegroundColor DarkGray
Write-Host "publish_result.api_key_source=$script:ApiKeySource" -ForegroundColor DarkGray
Write-Host "publish_result.persistence=$persistence" -ForegroundColor DarkGray

if ($AuthMode -eq "authenticated") {
    Write-Host "`nAuthenticated publish (permanent, saved to your account)" -ForegroundColor Green
} else {
    Write-Host "`nAnonymous publish (expires in 24h)" -ForegroundColor Yellow
    if ($response.claimUrl) {
        Write-Host "Claim URL: $($response.claimUrl)" -ForegroundColor Cyan
    }
}
