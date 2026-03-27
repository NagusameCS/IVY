# cPanel Deployment & CDN Infrastructure Guide

## Overview

This guide covers:
1. **SSH Setup** to cPanel (192.64.118.16)
2. **Automatic Deployment** of code changes
3. **CDN Rework** to reduce GitHub dependence
4. **Resource Synchronization** for offline capability

---

## Part 1: SSH Setup to cPanel

### Connection Details
- **Host**: 192.64.118.16
- **User**: ivysfyoq
- **Remote Path**: /home/ivysfyoq/public_html
- **Data Path**: /home/ivysfyoq/personal_server (personal server for generation)

### Step 1: Test SSH Connection

**Windows** (PowerShell):
```powershell
python deploy.py test
```

**Mac/Linux**:
```bash
python3 deploy.py test
```

Expected output:
```
🔗 Testing SSH connection to cPanel...
✅ SSH connection successful!
Connection successful
```

### Step 2: Verify cPanel Structure

```powershell
# Check remote structure
python deploy.py status

# Should show:
# - public_html/ (your main website)
# - ib-practice-platform/ (practice app data)
# - personal_server/ (generation runs here)
# - logs/ (deployment logs)
```

### Step 3: (Recommended) Set Up SSH Keys

For production, use SSH keys instead of password auth:

```powershell
# Generate SSH key
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\cpanel_key -N ""

# Get public key
type $env:USERPROFILE\.ssh\cpanel_key.pub

# Paste this on cPanel - copy to ~/.ssh/authorized_keys
ssh ivysfyoq@192.64.118.16
mkdir -p ~/.ssh
# Paste key content into ~/.ssh/authorized_keys

# Test key auth
ssh -i ~/.ssh/cpanel_key ivysfyoq@192.64.118.16 "echo Connected"
```

Then modify `deploy.py` to use key auth instead of password.

---

## Part 2: Automatic Deployment

### Deploy Everything

```powershell
# Full deployment (both public_html and practice platform)
python deploy.py deploy --target all

# With confirmation skipped
python deploy.py deploy --target all --force
```

### Deploy Specific Components

```powershell
# Deploy only public-facing website
python deploy.py deploy --target public

# Deploy only practice platform (new questions)
python deploy.py deploy --target practice

# Deploy only generated questions (data only)
python deploy.py deploy --target questions
```

### Deployment Process

1. **Backup** - Creates timestamped backup on remote server
2. **Upload** - Uses SCP to upload files
3. **Verify** - Confirms upload completed
4. **Log** - Records deployment in remote logs

### Check Deployment Status

```powershell
# View recent deployments
python deploy.py status

# Expected output:
# 📊 Checking remote deployment status...
# ✓ Current directory: /home/ivysfyoq
# ✓ Public HTML contents: [list of files]
# ✓ Practice platform contents: [list of files]
# ✓ Recent deployment logs: [timestamps]
```

---

## Part 3: CDN Rework (GitHub → Local/Cloudflare)

### Problem: Current State

**Before**: All CDN requests go through:
- jsDelivr (cdn.jsdelivr.net)
- cdnjs.cloudflare.com
- GitHub raw.githubusercontent.com (struct.json, exemplars, etc.)

**Issues**:
- Single point of failure (GitHub down = app broken)
- Scale limits (GitHub rate limiting at high traffic)
- Slow if GitHub CDN unreachable
- Requires internet for development

### Solution: Multi-Layer CDN Strategy

```
Request for resource
  ↓
1. Check Local Cache (/cdn-cache/)
  ↓ (miss)
2. Check Cloudflare Cache (if configured)
  ↓ (miss)
3. Try Alternative CDN Mirror
  ↓ (miss)
4. Fall back to Original (last resort)
```

### Step 1: Initialize Resource Sync

```powershell
# Sync all resources from GitHub to local cache
python resource-sync.py sync

# Output:
# 🔄 Starting resource synchronization...
# 📦 Syncing struct...
# 📥 Downloading: https://raw.githubusercontent.com/...
# ✓ Saved: struct.json
# ✅ Synchronization complete (3/3 resources)
```

### Step 2: Enable Local CDN Router

The CDN router is automatically enabled in:
- `ib-practice-platform/js/cdn-router.js`

The router intelligently routes requests:
```javascript
// In browser console:
console.log(cdnRouter.getStats());
// Output:
// {
//   localHits: 15,
//   cloudflareHits: 0,
//   cdnHits: 8,
//   failures: 0,
//   total: 23,
//   successRate: "100%"
// }
```

### Step 3: Serve Resources Locally (Optional)

Create a local CDN server to serve cached resources:

**Python (Flask)**:
```python
from flask import Flask, send_from_directory
app = Flask(__name__)

@app.route('/cdn-cache/<path:filename>')
def serve_cdn(filename):
    return send_from_directory('cdn-cache', filename)

if __name__ == '__main__':
    app.run(port=8080)
```

**Apache (.htaccess)**:
```apache
# Serve local cache before external CDN
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^cdn-cache/(.+)$ cdn-cache/$1 [L]
</IfModule>
```

### Step 4: Update HTML to Use CDN Router

*Already included in index.html*:
```html
<script src="js/cdn-router.js"></script>
```

Router automatically manages KaTeX, Tailwind, and other CDN resources.

### Step 5: Set Up Cloudflare (Optional but Recommended)

For production, configure Cloudflare as middle layer:

1. **Sign up**: https://cloudflare.com
2. **Add domain**: ivystudy.com (or your domain)
3. **DNS**: Point to Cloudflare nameservers
4. **Caching**: Enable aggressive caching
5. **Rules**: Cache struct.json, exemplars, etc.

---

## Part 4: Resource Synchronization

### Automatic Daily Sync

Resources are synced automatically from GitHub to local cache daily.

#### Windows Task Scheduler

```powershell
# Create scheduled task
$trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "resource-sync.py sync" -WorkingDirectory "C:\path\to\ivystudy"
Register-ScheduledTask -TaskName "IVY Resource Sync" -Trigger $trigger -Action $action -RunLevel Highest
```

#### Manual Sync

```powershell
# Sync specific resource
python resource-sync.py sync --resource struct

# Force re-download (ignore cache)
python resource-sync.py sync --force

# Verify all resources cached
python resource-sync.py verify

# Show fallback chain
python resource-sync.py chain struct
```

### Fallback Chain (struct.json example)

```
1. Local: /ib-practice-platform/data/struct.json
   ↓ (if not found)
2. Cache: /ib-practice-platform/bots/web_struct_cache.json
   ↓ (if not found)
3. Network: https://raw.githubusercontent.com/NagusameCS/IVY/main/struct.json
   ↓ (if fails)
4. Error: Raise exception
```

---

## Part 5: Two-Server Architecture

### Personal Server (Generation)

- **Purpose**: Generate questions, lesson plans, missing lessons
- **Uses**: Bot queue system (queue.py)
- **Runs**: `python queue.py worker --poll 2`
- **Output**: questions.json, plan_*.json, plan_missing_*.json

### IVY Server (Production)

- **Purpose**: Serve website and practice platform to users
- **Address**: 192.64.118.16 (ivysfyoq)
- **Receives**: Generated data from personal server via deployment
- **Serves**: public_html/, ib-practice-platform/

### Workflow

```
Personal Server (Your Machine)
  ├─ Generate questions
  ├─ Generate lesson plans
  ├─ Generate missing lessons
  └─ Output: questions.json + plans
         ↓
    [You run: python deploy.py deploy]
         ↓
IVY Server (cPanel)
  ├─ Receive updated data
  ├─ Serve to users
  └─ Cache in browser
```

---

## Part 6: Complete Deployment Checklist

### Pre-Deployment

- [ ] SSH connection tested: `python deploy.py test`
- [ ] Local changes complete and tested
- [ ] Generation queue finished or paused
- [ ] Backup status checked: `python deploy.py status`

### Deployment

- [ ] Run full deployment: `python deploy.py deploy --target all`
- [ ] Check status on remote: `python deploy.py status`
- [ ] Verify files uploaded correctly (check in file manager)

### Post-Deployment

- [ ] Visit https://yoursite.com and test
- [ ] Check practice platform: /ib-practice-platform/
- [ ] Monitor browser console for CDN logs
- [ ] Run performance check: `profiler.report()` in console

### Resource Sync

- [ ] Run initial sync: `python resource-sync.py sync`
- [ ] Verify resources cached: `python resource-sync.py verify`
- [ ] Set up automatic daily sync (see Task Scheduler section)

---

## Part 7: Troubleshooting

### SSH Connection Failed

```powershell
# Test SSH manually
ssh ivysfyoq@192.64.118.16

# If fails, check:
1. Internet connectivity
2. VPN (if required)
3. Password correct: k8KcdO08EL6g
4. Host IP correct: 192.64.118.16
5. User correct: ivysfyoq
```

### SCP Upload Slow

- Check internet bandwidth
- Large files (questions.json >50MB) take time
- Use `--target questions` for data-only deployment (faster)

### CDN Resources Not Caching

```javascript
// Check in browser console:
console.log(cdnRouter.getStats());

// If localHits = 0:
1. Ensure resource-sync.py ran successfully
2. Check network tab for 404s
3. Verify cdn-cache/ directory exists
4. Check browser IndexedDB quota
```

### Remote File Permissions

```bash
# Fix if needed (SSH to remote)
ssh ivysfyoq@192.64.118.16

# Make scripts executable
chmod +x ~/public_html/*.sh

# Fix directory permissions
chmod 755 ~/public_html
find ~/public_html -type d -exec chmod 755 {} \;
find ~/public_html -type f -exec chmod 644 {} \;
```

---

## Part 8: Summary Commands

### Quick Reference

```powershell
# SETUP (first time)
python deploy.py test              # Test SSH
python resource-sync.py sync       # Cache resources
python deploy.py init              # Initialize config

# REGULAR DEPLOYMENT
python deploy.py deploy --target all      # Full deploy
python deploy.py deploy --target questions # Data only
python deploy.py status                    # Check status

# RESOURCE MANAGEMENT
python resource-sync.py sync --force   # Force refresh
python resource-sync.py verify         # Check cache
python resource-sync.py chain struct   # View fallback

# SSH SETUP (advanced)
python deploy.py ssh-key-setup  # Generate SSH keys
```

---

## Notes

- **Credentials stored**: deploy.py has password embedded - for production, move to `.env` file or use SSH keys only
- **Backups**: Remote server keeps timestamped backups in `/backups/`
- **Logs**: Deployment logs in `/logs/deployment.log` on remote server
- **Data sync**: Generated questions.json can be 80MB+ - deploy via `--target questions` for speed

---

## Next Steps

1. ✅ Run `python deploy.py test`
2. ✅ Run `python resource-sync.py sync`
3. ✅ Run `python deploy.py deploy --target all`
4. ✅ Visit your live website
5. ✅ Set up daily resource sync via Task Scheduler
