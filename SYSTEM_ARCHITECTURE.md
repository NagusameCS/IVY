# IVY System Architecture & Deployment Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        USER BROWSER (Client Side)                           │
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐    │
│  │   Main Website   │  │ Practice Platform│  │  Exemplars / Timer   │    │
│  │  (public_html/)  │  │ (ib-practice-    │  │  (public_html/sub/)  │    │
│  │                  │  │  platform/)      │  │                      │    │
│  └────────┬─────────┘  └────────┬─────────┘  └──────────┬───────────┘    │
│           │                     │                        │                │
│           └─────────┬───────────┴────────────┬───────────┘                │
│                     │                        │                            │
│              ┌──────▼────────────────────────▼───────┐                    │
│              │  CDN Router (cdn-router.js)           │                    │
│              │  Smart fallback routing layer         │                    │
│              └──────┬──────────────────────┬─────────┘                    │
│                     │                      │                              │
│    ┌────────────────┴──┐    ┌──────────────┴──────────┐                  │
│    │ Browser IndexedDB │    │  Browser Memory Cache   │                  │
│    │ (persistent 24h)  │    │  (session-based)        │                  │
│    └────────────────┬──┘    └──────────────┬──────────┘                  │
│                     │                      │                              │
└─────────────────────┼──────────────────────┼──────────────────────────────┘
                      │ (Request if miss)    │
┌─────────────────────┼──────────────────────┼──────────────────────────────┐
│              NETWORK ROUTING (Intelligent Fallback)                       │
│                                                                           │
│  1. Local Cache (/cdn-cache/)  ← Fastest (if available)                  │
│  2. Cloudflare Cache           ← Fast (if configured)                    │
│  3. Alternative CDN Mirrors    ← Medium (jsDelivr, cdnjs, etc.)         │
│  4. Original CDN               ← Slowest (GitHub, jsdelivr, etc.)        │
│                                                                           │
└───────────────────────┬──────────────────┬──────────────────────────────┘
                        │                  │
        ┌───────────────┴──┐      ┌────────┴────────────┐
        │                  │      │                     │
    ┌───▼────────┐  ┌──────▼──┐  ▼─────────────────┐
    │ Cloudflare │  │ jsDelivr│  │ Original Sources │
    │   Cache    │  │ / cdnjs │  │  (GitHub, etc.)  │
    └────────────┘  └─────────┘  └──────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│              PERSONAL SERVER (Your Machine - Data Generation)               │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │  Bot Queue System (ib-practice-platform/bots/)                   │     │
│  │                                                                  │     │
│  │  ┌─────────────────┐  ┌──────────────────────────────────────┐ │     │
│  │  │  queue.py       │  │  Job Types (29 per batch)            │ │     │
│  │  │  (orchestrator) │  │  - practice_generation (8 subjects)  │ │     │
│  │  │                 │  │  - lesson_planning (8 subjects)      │ │     │
│  │  │  queue.db       │  │  - missing_lesson_generation (8)     │ │     │
│  │  │  (SQLite)       │  │  - verification (5 checks)           │ │     │
│  │  └────────┬────────┘  └──────────────────────────────────────┘ │     │
│  │           │                                                      │     │
│  │  ┌────────▼────────────────┐  ┌──────────────────────────────┐ │     │
│  │  │  Worker Process         │  │  Output Data                 │ │     │
│  │  │  (python queue.py       │  │                              │ │     │
│  │  │   worker --poll 2)      │  │  - questions.json (~80k)     │ │     │
│  │  │                         │  │  - plan_*.json (lessons)     │ │     │
│  │  │  Status: Running        │  │  - plan_missing_*.json       │ │     │
│  │  └────────┬────────────────┘  │  - web_struct_cache.json     │ │     │
│  │           │                   │  - exemplars_struct_cache    │ │     │
│  │           │                   │  - curriculum_cache.json     │ │     │
│  │           │                   │  - Verification logs         │ │     │
│  │           │                   └──────────┬───────────────────┘ │     │
│  │           │ (Generate)                   │                     │     │
│  │           │                              │                     │     │
│  │  ┌────────▼──────────────────────────────▼──────────────────┐  │     │
│  │  │  Data Directory (ib-practice-platform/data/)             │  │     │
│  │  │  - questions.json (from generation)                      │  │     │
│  │  │  - struct.json (from GitHub sync)                        │  │     │
│  │  │  - curriculum.json (from GitHub sync)                    │  │     │
│  │  │  - templates/ (templates for generation)                 │  │     │
│  │  └────────┬──────────────────────────────────────────────────┘  │     │
│  │           │                                                      │     │
│  └───────────┼──────────────────────────────────────────────────────┘     │
│              │                                                            │
│  ┌───────────▼──────────────────────────────────────────────────────┐    │
│  │  Deploy Command: python deploy.py deploy --target all           │    │
│  │  - Creates SSH connection                                       │    │
│  │  - Backs up remote server                                       │    │
│  │  - Uploads via SCP                                              │    │
│  │  - Logs deployment                                              │    │
│  └───────────┬──────────────────────────────────────────────────────┘    │
│              │                                                            │
└──────────────┼────────────────────────────────────────────────────────────┘
               │ (SSH Push)

┌──────────────▼────────────────────────────────────────────────────────────┐
│              IVY SERVER (Cloud - User-Facing Website)                      │
│              Host: 192.64.118.16  User: ivysfyoq                          │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  /home/ivysfyoq/                                                  │  │
│  │  ├── public_html/                    (Main website)               │  │
│  │  │   ├── index.html                  (Homepage)                   │  │
│  │  │   ├── timer/ exemplars/ info/     (Sub-apps)                   │  │
│  │  │   ├── js/ cdn-router.js           (CDN routing script)         │  │
│  │  │   └── data/                       (Cached resources)           │  │
│  │  │                                                                │  │
│  │  ├── ib-practice-platform/           (Practice app)              │  │
│  │  │   ├── index.html                  (Practice UI)               │  │
│  │  │   ├── js/                         (Optimization scripts)       │  │
│  │  │   │   ├── question-loader.js      (Lazy loading)              │  │
│  │  │   │   ├── optimization-adapter.js (Integration)               │  │
│  │  │   │   ├── cdn-router.js           (CDN routing)               │  │
│  │  │   │   └── performance-profiler.js (Debugging)                 │  │
│  │  │   ├── questions.json              (Generated questions)       │  │
│  │  │   ├── data/                       (Structures, plans)         │  │
│  │  │   └── bots/                       (Cache, logs)               │  │
│  │  │                                                                │  │
│  │  ├── backups/                        (Timestamped backups)       │  │
│  │  │   ├── backup-20260326-140500/     (Previous deploy)           │  │
│  │  │   └── backup-20260325-020000/     (Older backup)              │  │
│  │  │                                                                │  │
│  │  └── logs/                           (Deployment logs)           │  │
│  │      └── deployment.log              ("Deployed X items...")     │  │
│  │                                                                  │  │
│  ├── .htaccess                          (Server config)             │  │
│  │   ├── HTTPS redirect                                            │  │
│  │   ├── Cache control (31 days for assets, 1 hour for data)      │  │
│  │   ├── Gzip compression                                          │  │
│  │   └── CORS headers                                              │  │
│  │                                                                  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                              │                                            │
│                ┌─────────────┴──────────────┐                             │
│                │                            │                             │
│         ┌──────▼──────────┐        ┌────────▼─────────┐                  │
│         │  Browser Cache  │        │  Browser Network │                  │
│         │  (24h assets)   │        │  (requests new)  │                  │
│         └─────────────────┘        └──────────────────┘                  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

### Question Answering Flow
```
User opens practice platform
    ↓
Browser loads index.html
    ↓
JavaScript initializes QuestionLoader
    ↓
User selects subject (e.g., Math AI)
    ↓
QuestionLoader.loadSubject("math_ai")
    ├─ Check memory cache? → Return (instant)
    ├─ Check IndexedDB? → Load & cache (100-300ms)
    ├─ Fetch from network
    │  ├─ Try: /questions-math_ai.json (subject-specific file)
    │  └─ Fall back to: /questions.json (full file, filtered)
    │
    └─ Store in IndexedDB for next time
       ↓
Questions displayed in browser
    ↓
User filters by difficulty/topic
    ↓
applyFiltersDebounced() (300ms wait to avoid flicker)
    ↓
Filtered questions rendered
```

### Deployment Flow
```
Personal Server                              IVY Server (Cloud)
─────────────────────                        ──────────────────

1. Generate questions
   └─ output: questions.json
              plan_*.json
              plan_missing_*.json
                     │
                     │ (in data/bots/)
                     │
2. Run deploy command
   └─ python deploy.py deploy --target all
                     │
                     ├─ Create SSH connection (deploy.py)
                     │
                     ├─ Create backup
                     │  └─ /backups/backup-TIMESTAMP/
                     │
                     ├─ Upload public_html/
                     │─ Upload ib-practice-platform/
                     │  └─ includes questions.json
                     │
                     ├─ Log deployment
                     │  └─ /logs/deployment.log
                     │
                     └─ Notify user: ✅ Deployment complete
                                              │
                                              ├─ Users fetch live website
                                              │
                                              ├─ Browser caches via IndexedDB
                                              │  (Questions loaded by subject)
                                              │
                                              └─ CDN router routes optimally
                                                 (local → Cloudflare → original)
```

### Resource Synchronization Flow
```
GitHub Repositories
├─ NagusameCS/IVY (struct.json, curriculum.json, etc.)
├─ NagusameCS/Exemplars (exemplars structure)
└─ NagusameCS/IVY (privacy.md, terms.md, contact.md)
       │
       │ python resource-sync.py sync
       │
       ├─ Download: struct.json → /data/struct.json
       ├─ Download: curriculum.json → /data/curriculum.json  
       └─ Download: exemplars struct → /data/exemplars_struct.json
              │
              ├─ Cache copy: /bots/web_struct_cache.json
              │  (fallback if GitHub down)
              │
              └─ Queue uses priority:
                 1. Local file (fastest)
                 2. Cache file (if local missing)
                 3. Network fetch (if both missing)
                 4. Error (if all missing)
                    │
                    └─ Deployed to ivy server via deploy.py
```

---

## File Structure (Post-Deployment)

### Personal Server (Your Machine)
```
c:\Users\legom\OneDrive\Desktop\New folder\ivystudy\
├── deploy.py                          # Deployment to cPanel
├── resource-sync.py                   # GitHub → local cache sync
├── setup-wizard.py                    # Interactive setup
├── .htaccess                          # Server config (copy to remote)
│
├── public_html/
│   ├── index.html                     # Main site
│   ├── timer/ exemplars/ info/        # Sub-apps
│   ├── js/
│   │   ├── cdn-router.js              # Smart CDN routing
│   │   └── themeManager.js
│   └── data/                          # Cached resources
│
├── ib-practice-platform/
│   ├── index.html                     # Practice app
│   ├── questions.json                 # Generated questions (~80k)
│   ├── js/
│   │   ├── cdn-router.js              # CDN router
│   │   ├── question-loader.js         # Lazy loading engine
│   │   ├── optimization-adapter.js    # Integration layer
│   │   └── performance-profiler.js    # Debugging tool
│   ├── data/
│   │   ├── struct.json                # Synced from GitHub
│   │   ├── curriculum.json
│   │   ├── plan_*.json                # Generated lesson plans
│   │   └── plan_missing_*.json        # Generated missing lessons
│   │
│   └── bots/
│       ├── queue.py                   # Bot orchestrator
│       ├── queue.db                   # SQLite job queue
│       ├── generate.py                # Question generator
│       └── web_struct_cache.json      # Cached struct (fallback)
│
└── docs/
    ├── DEPLOYMENT_GUIDE.md            # Full deployment guide
    ├── DEPLOYMENT_QUICK_START.md      # Quick reference
    ├── OPTIMIZATION.md                # Performance optimization
    └── VERIFICATION_GUIDE.md          # Testing guide
```

### IVY Server (192.64.118.16/ivysfyoq)
```
/home/ivysfyoq/
├── public_html/                       # → synced from personal server
│   ├── index.html
│   ├── timer/ exemplars/ info/
│   ├── js/ cdn-router.js
│   └── data/
│
├── ib-practice-platform/              # → synced from personal server
│   ├── index.html
│   ├── questions.json                 # Latest generated (~80k)
│   ├── js/ (cdn-router, loaders, etc)
│   ├── data/ (plans, curriculum, structures)
│   └── bots/ (cache, logs)
│
├── backups/
│   ├── backup-20260326-140500/        # Before deployment 2
│   ├── backup-20260325-020000/        # Before deployment 1
│   └── ...
│
├── logs/
│   └── deployment.log                 # Deployment history
│
└── .htaccess                          # Server config
```

---

## Key Concepts

### Why Two Servers?

**Personal Server (Your Machine)**
- High CPU/disk for generation (question generation is compute-intensive)
- Testing/iteration safe (no live users)
- Can be offline between deployments
- Runs 24/7 bot worker (resource-intensive)

**IVY Server (Cloud - 192.64.118.16)**
- Always online, reliable, CDN-backed
- Serves live users
- Low resource requests (pre-generated questions)
- Automated scaling

### CDN Router Tiers

1. **Local Cache** (fastest)
   - Browser IndexedDB (persistence across sessions)
   - Browser memory cache (fast for repeated access)

2. **Cloudflare** (fast, optional)
   - Requires Cloudflare account setup
   - Global edge network
   - Caches automatically

3. **Alternative Mirrors** (medium)
   - jsDelivr (fastly.jsdelivr.net)
   - cdnjs (cloudflare.com/ajax/libs)
   - Fallback if primary unavailable

4. **Original** (slowest)
   - GitHub raw.githubusercontent.com
   - jsdelivr cdn.jsdelivr.net
   - CDN.js cdnjs.cloudflare.com
   - Last resort if all else fails

### Bot Queue Execution

```
Queue State:
- 66 jobs completed (done)
- 22 jobs queued (waiting)
- 3 jobs running (in progress)
- 87 jobs total

Batches:
- Latest batch: 8 done, 1 running (87% complete)
- Questions generated: ~50k in latest batch
- Target: 80k total questions
```

---

## Deployment Checklist

- [ ] Personal server generation complete
- [ ] Resource sync successful: `python resource-sync.py sync`
- [ ] SSH test passes: `python deploy.py test`
- [ ] Backup created automatically on remote
- [ ] Files uploaded: `python deploy.py deploy --target all`
- [ ] Deployment logged: check `/logs/deployment.log`
- [ ] Live website active: https://192.64.118.16/
- [ ] Practice platform accessible: https://192.64.118.16/ib-practice-platform/
- [ ] CDN router working: check console for route messages
- [ ] Automatic sync scheduled: Task Scheduler set for 2:00 AM daily

---

## Performance Metrics (Post-Deployment)

### Expected Times
- Page load: <500ms
- First subject load: 2-5s
- Cached subject load: 100-300ms
- Filter changes: <100ms (debounced)
- Browser memory: 50-100MB (for 50 questions)

### Cache Hit Rates
- First 30 minutes: 20-30% (initial population)
- After 1 hour: 70-80% (most subjects cached)
- After 1 day: 95%+ (persistent IndexedDB)

---

## Troubleshooting Guide

See `DEPLOYMENT_GUIDE.md` for detailed troubleshooting of:
- SSH connection issues
- SCP upload problems
- CDN caching errors
- Resource sync failures
- Browser console errors

---

## Summary

**Before**: Manual FTP uploads, GitHub-dependent, 80k questions freeze browser
**After**: One-command deployment, intelligent CDN routing, scaled to handle 80k+ questions efficiently

```powershell
# Complete deployment: 3 commands
python resource-sync.py sync              # Cache resources (2 min)
python deploy.py deploy --target all      # Push to live (5 min)
# ✅ Done! Website is live and optimized
```
