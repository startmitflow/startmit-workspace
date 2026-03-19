---
name: here-now
description: >
  Publish files and folders to the web instantly. Static hosting for HTML sites,
  images, PDFs, and any file type. Use when asked to "publish this", "host this",
  "deploy this", "share this on the web", "make a website", "put this online",
  "upload to the web", "create a webpage", "share a link", "serve this site",
  or "generate a URL". Outputs a live, shareable URL at {slug}.here.now.
---

# here.now

**Skill version: 1.8.3**

Create a live URL from any file or folder. Static hosting only.

## Requirements

- Windows PowerShell 5.1+ or PowerShell 7+
- Optional environment variable: `$env:HERENOW_API_KEY`
- Optional credentials file: `~/.herenow/credentials`

## Create a site

```powershell
.\scripts\publish.ps1 {file-or-dir}
```

Outputs the live URL (e.g. `https://bright-canvas-a7k2.here.now/`).

Without an API key this creates an **anonymous site** that expires in 24 hours.
With a saved API key, the site is permanent.

## Update an existing site

```powershell
.\scripts\publish.ps1 {file-or-dir} -Slug {slug}
```

## API key storage

The publish script reads the API key from these sources (first match wins):

1. `-ApiKey {key}` parameter (CI/scripting only)
2. `$env:HERENOW_API_KEY` environment variable
3. `~/.herenow/credentials` file (recommended)

To store a key:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.herenow"
"YOUR_API_KEY" | Set-Content "$env:USERPROFILE\.herenow\credentials" -NoNewline
```

## Limits

|                | Anonymous          | Authenticated                |
| -------------- | ------------------ | ---------------------------- |
| Max file size  | 250 MB             | 5 GB                         |
| Expiry         | 24 hours           | Permanent                    |
| Rate limit     | 5 / hour / IP      | 60 / hour free, 200 / hour hobby |

## Getting an API key

1. Request a one-time sign-in code:
```powershell
Invoke-RestMethod -Uri "https://here.now/api/auth/agent/request-code" -Method POST -ContentType "application/json" -Body '{"email": "user@example.com"}'
```

2. Verify the code:
```powershell
Invoke-RestMethod -Uri "https://here.now/api/auth/agent/verify-code" -Method POST -ContentType "application/json" -Body '{"email":"user@example.com","code":"ABCD-2345"}'
```

3. Save the returned `apiKey`.

Full docs: https://here.now/docs
