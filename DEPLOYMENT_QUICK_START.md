# Deployment & CDN Setup - Quick Start Guide

## What's New

✅ **cPanel SSH Integration** - Direct deployment to ivy server (192.64.118.16)
✅ **CDN Rework** - GitHub dependence reduced, intelligent fallback routing  
✅ **Resource Caching** - Local cache for offline/faster access
✅ **Automated Sync** - Daily automatic resource synchronization
✅ **Two-Server Architecture** - Personal (generation) + IVY (production)

---

## Quick Start (5 minutes)

### 1. Test SSH Connection
```powershell
python deploy.py test
```
✅ Expected: "SSH connection successful!"

### 2. Sync Resources from GitHub
```powershell
python resource-sync.py sync
```
✅ Expected: "Synchronization complete (3/3 resources)"

### 3. Deploy Everything to cPanel
```powershell
python deploy.py deploy --target all
```
✅ Expected: "Deployment complete!"

### 4. Check Live Website
- Visit: https://192.64.118.16/public_html/
- Check practice: https://192.64.118.16/ib-practice-platform/

Done! 🎉

---

## Files Created/Modified

### New Deployment Tools
```
deploy.py                   # Main deployment script
resource-sync.py           # Resource synchronization (GitHub → local)
setup-wizard.py            # Interactive setup wizard
.htaccess                  # Server configuration for cPanel
```

### New CDN Infrastructure
```
ib-practice-platform/js/cdn-router.js      # Practice platform CDN router
public_html/js/cdn-router.js               # Main site CDN router
```

### Updated Files
```
ib-practice-platform/bots/queue.py         # Updated to use local resources
ib-practice-platform/index.html            # CDN router added
public_html/index.html                     # CDN router added
public_html/exemplars/index.html           # CDN router added
```

---

## Common Commands

### Deploy Code Changes
```powershell
python deploy.py deploy --target all              # Full deploy
python deploy.py deploy --target public           # Website only
python deploy.py deploy --target practice         # Practice app only
python deploy.py deploy --target questions        # Data only (fastest)
```

### Resource Management
```powershell
python resource-sync.py sync                      # Sync all resources
python resource-sync.py sync --force             # Force fresh download
python resource-sync.py verify                    # Check what's cached
python resource-sync.py chain struct             # Show resource fallback
```

### Check Status
```powershell
python deploy.py status                           # View live server status
python deploy.py init                             # Initialize deployment config
python deploy.py ssh-key-setup                    # Instructions for SSH keys
```

### Setup (First Time)
```powershell
python setup-wizard.py                            # Interactive setup wizard
```

---

## CDN Architecture (How It Works)

### Before (GitHub-dependent)
```
All requests → GitHub CDN → User browser
         ↓
    If GitHub down → Site broken
```

### After (Intelligent routing)
```
Request for KaTeX, Tailwind, etc.
  ↓
1. Local Cache (/cdn-cache/) → Fastest
  ↓ (not found)
2. Cloudflare Cache → Fast
  ↓ (not configured)
3. Alternative CDN Mirror → Medium
  ↓ (not found)
4. Original CDN → Slowest
```

### Fallback Chain for struct.json
```
1. Local: /ib-practice-platform/data/struct.json
2. Cache: /ib-practice-platform/bots/web_struct_cache.json
3. Network: https://raw.githubusercontent.com/...
```

---

## Two-Server Workflow

### Personal Server (Your Machine)
```
1. Run: python queue.py worker --poll 2
2. Generates questions, lesson plans, etc.
3. Outputs: questions.json, plan_*.json files
```

### Push to IVY Server
```
4. Run: python deploy.py deploy --target all
5. Uploads generated data via SSH
6. Creates backup of previous version
7. Logs deployment timestamp
```

### IVY Server (192.64.118.16)
```
8. Serves website to users
9. Caches in browser via CDN router
10. Falls back to local if external unavailable
```

---

## Resource Sync (Automated)

### How It Works
- **GitHub Sources**: struct.json, curriculum.json, exemplars, markdown files
- **Local Cache**: `/bots/web_struct_cache.json` and data directories
- **Fallback**: If GitHub down, queue uses cached copy
- **Auto Sync**: Daily at 2:00 AM (Windows Task Scheduler or cron)

### Manual Sync
```powershell
# First time (sync everything from GitHub)
python resource-sync.py sync

# Verify everything cached
python resource-sync.py verify

# Force re-download (internet restore)
python resource-sync.py sync --force
```

---

## Browser Console (Monitoring)

```javascript
// Check CDN performance
console.log(cdnRouter.getStats());

// Output example:
// {
//   localHits: 5,
//   cloudflareHits: 0,
//   cdnHits: 3,
//   failures: 0,
//   total: 8,
//   successRate: "100%"
// }

// Manual resource load
cdnRouter.getResourceUrl("https://cdn.tailwindcss.com");

// See what's cached
console.log(qLoader.cache.keys());
```

---

## SSH Key Setup (Recommended for Production)

```powershell
# Generate SSH key
ssh-keygen -t ed25519 -f ~/.ssh/cpanel_key -N ""

# Copy to cPanel
type ~/.ssh/cpanel_key.pub | ssh ivysfyoq@192.64.118.16 "cat >> ~/.ssh/authorized_keys"

# Test key auth
ssh -i ~/.ssh/cpanel_key ivysfyoq@192.64.118.16 "echo Connected"

# Update deploy.py to use key instead of password
# Change: ssh_cmd = f'ssh -i ~/.ssh/cpanel_key {CPANEL_USER}@{CPANEL_HOST} ...'
```

---

## Troubleshooting

### SSH Connection Failed
```powershell
# Test manually
ssh ivysfyoq@192.64.118.16
# Should prompt for password: k8KcdO08EL6g

# If fails:
# - Check internet connection
# - Verify IP: 192.64.118.16 is reachable
# - Confirm password is correct
# - Check if port 22 is open
```

### Resources Not Cached
```powershell
# Re-sync everything
python resource-sync.py sync --force

# Check what's cached
python resource-sync.py verify

# Look for errors in output
```

### Deployment Fails
```powershell
# Check remote server status
python deploy.py status

# If SCP slow (large questions.json):
python deploy.py deploy --target questions --force
# This uploads data only, skips website

# Check deployment logs on remote
ssh ivysfyoq@192.64.118.16
tail -50 logs/deployment.log
```

---

## Performance Impact

### Before Optimization
- Generate questions on personal server ✓
- Manually upload via FTP (tedious)
- Users load all questions at once (freezes on 80k+)
- jQuery from GitHub CDN only (single point of failure)

### After Optimization  
- **Deployment**: `python deploy.py deploy --target all` (automated via SSH)
- **CDN**: Intelligent fallback (local → Cloudflare → CDN → original)
- **Practice**: Lazy loads by subject (no freeze on 80k)
- **Reliability**: Works offline (browser cache) or with degraded internet

---

## Security Notes

⚠️ **Current**: Password stored in deploy.py (OK for dev, not production)
✅ **Recommended**: Use SSH keys + `.env` file for credentials
✅ **Best**: Use GitHub Actions + deploy keys for CI/CD

---

## Next Steps

1. ✅ Run `python setup-wizard.py` for guided setup
2. ✅ Generate questions using bot queue (if needed)
3. ✅ Run `python deploy.py deploy --target all` to push live
4. ✅ Set up automatic daily resource sync via Task Scheduler
5. ✅ Monitor CDN performance in browser console

---

## File Explorer Hints

**Key Directories**:
- `c:\...\ivystudy\` - Root (where you run deploy.py)
- `public_html\` - Main website (user-facing)
- `ib-practice-platform\` - Practice app
- `ib-practice-platform\bots\` - Generation queue + caches
- `ib-practice-platform\data\` - Questions and plans

**After Deployment**:
- Remote `/home/ivysfyoq/public_html/` - Your live website
- Remote `/home/ivysfyoq/backups/` - Timestamped backups
- Remote `/home/ivysfyoq/logs/deployment.log` - Deployment history

---

Need help? Run: `python setup-wizard.py` or check `DEPLOYMENT_GUIDE.md` for full details.
