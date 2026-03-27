#!/usr/bin/env python3
"""
Resource Synchronization Manager
Syncs resources from GitHub to local cache for offline/faster access
Manages: struct.json, curriculum data, exemplars, etc.
"""

import argparse
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent

# Resource definitions
RESOURCES = {
    "struct": {
        "sources": [
            "https://raw.githubusercontent.com/NagusameCS/IVY/main/struct.json",  # Primary
        ],
        "local_path": ROOT / "ib-practice-platform" / "data" / "struct.json",
        "cache_dir": ROOT / "ib-practice-platform" / "bots" / "web_struct_cache.json",
        "expires": 7 * 24,  # 7 days in hours
    },
    "exemplars_struct": {
        "sources": [
            "https://raw.githubusercontent.com/NagusameCS/Exemplars/main/struct.json",
        ],
        "local_path": ROOT / "public_html" / "data" / "exemplars_struct.json",
        "cache_dir": ROOT / "ib-practice-platform" / "bots" / "exemplars_struct_cache.json",
        "expires": 7 * 24,
    },
    "curriculum": {
        "sources": [
            "https://raw.githubusercontent.com/NagusameCS/IVY/main/curriculum.json",
        ],
        "local_path": ROOT / "ib-practice-platform" / "data" / "curriculum.json",
        "cache_dir": ROOT / "ib-practice-platform" / "bots" / "curriculum_cache.json",
        "expires": 7 * 24,
    },
}

# Privacy/terms/contact files
MARKDOWN_RESOURCES = {
    "privacy": "https://raw.githubusercontent.com/NagusameCS/IVY/main/privacy.md",
    "terms": "https://raw.githubusercontent.com/NagusameCS/IVY/main/terms.md",
    "contact": "https://raw.githubusercontent.com/NagusameCS/IVY/main/contact.md",
}


def download_resource(url, timeout=10):
    """Download resource from URL"""
    try:
        print(f"  📥 Downloading: {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "IVY-Sync/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except urllib.error.URLError as e:
        print(f"  ❌ Download failed: {e}")
        return None
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def is_cache_expired(cache_path, hours_max):
    """Check if cache file is expired"""
    if not cache_path.exists():
        return True

    mtime = cache_path.stat().st_mtime
    age_hours = (datetime.now().timestamp() - mtime) / 3600
    return age_hours > hours_max


def save_resource(path, content):
    """Save resource to file"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  ✓ Saved: {path.name}")
    return True


def sync_resource(resource_key):
    """Sync a single resource"""
    if resource_key not in RESOURCES:
        print(f"Unknown resource: {resource_key}")
        return False

    config = RESOURCES[resource_key]
    cache_path = Path(config["cache_dir"])

    # Check if cache is still fresh
    if not is_cache_expired(cache_path, config["expires"]):
        print(f"✓ {resource_key}: Cache still fresh")
        return True

    print(f"\n📦 Syncing {resource_key}...")

    # Try each source
    for url in config["sources"]:
        content = download_resource(url)
        if content:
            # Validate JSON if applicable
            if resource_key in ["struct", "exemplars_struct", "curriculum"]:
                try:
                    json.loads(content)
                except json.JSONDecodeError:
                    print(f"  ⚠️ Invalid JSON from {url}")
                    continue

            # Save to cache
            save_resource(cache_path, content)

            # Also save to main data directory
            local_path = Path(config["local_path"])
            save_resource(local_path, content)

            return True

    print(f"  ✗ Failed to sync {resource_key} from any source")
    return False


def sync_markdown_resources():
    """Sync markdown files for privacy/terms/contact"""
    print("\n📄 Syncing markdown resources...")

    md_dir = ROOT / "public_html" / "data" / "pages"
    md_dir.mkdir(parents=True, exist_ok=True)

    for key, url in MARKDOWN_RESOURCES.items():
        content = download_resource(url)
        if content:
            save_resource(md_dir / f"{key}.md", content)
        else:
            print(f"  ⚠️ Failed to sync {key}")


def sync_all(force=False):
    """Sync all resources"""
    print("🔄 Starting resource synchronization...")

    if force:
        print("  (Force sync - ignoring cache)")

    success_count = 0
    for key in RESOURCES:
        if force:
            # Clear cache
            cache_path = Path(RESOURCES[key]["cache_dir"])
            if cache_path.exists():
                cache_path.unlink()

        if sync_resource(key):
            success_count += 1

    sync_markdown_resources()

    print(f"\n✅ Synchronization complete ({success_count}/{len(RESOURCES)} resources)")
    return success_count == len(RESOURCES)


def verify_resources():
    """Verify all resources are cached locally"""
    print("\n📋 Verifying cached resources...")

    all_ok = True
    for key, config in RESOURCES.items():
        cache_path = Path(config["cache_dir"])
        local_path = Path(config["local_path"])

        cache_exists = cache_path.exists()
        local_exists = local_path.exists()

        status = "✓" if (cache_exists and local_exists) else "✗"
        print(f"  {status} {key}: cache={cache_exists}, local={local_exists}")

        if not (cache_exists or local_exists):
            all_ok = False

    return all_ok


def get_fallback_chain(resource_type):
    """Get fallback chain for a resource type"""
    if resource_type not in RESOURCES:
        return []

    config = RESOURCES[resource_type]
    return [
        Path(config["local_path"]),  # Local copy (primary)
        Path(config["cache_dir"]),  # Cache copy (fallback)
        config["sources"][0],  # Original URL (last resort)
    ]


def setup_cron_sync():
    """Provide instructions for daily sync via cron/scheduler"""
    print("""
    🕐 Automatic Synchronization Setup
    ==================================

    To sync resources automatically, add to cron (Linux/Mac):
        0 2 * * * cd {root} && python3 resource-sync.py sync

    Or Windows Task Scheduler:
        1. Open Task Scheduler
        2. Create Basic Task → "IVY Resource Sync"
        3. Trigger: Daily at 2:00 AM
        4. Action: Start program
           - Program: python.exe
           - Arguments: resource-sync.py sync
           - Start in: {root}
    """.format(root=ROOT))


def main():
    parser = argparse.ArgumentParser(description="IVY Resource Synchronization Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Synchronize resources from GitHub")
    sync_parser.add_argument("--force", action="store_true", help="Force re-download ignoring cache")
    sync_parser.add_argument("--resource", help="Sync specific resource only")

    # Verify command
    subparsers.add_parser("verify", help="Verify all resources are cached")

    # Cron setup
    subparsers.add_parser("setup-cron", help="Show cron setup instructions")

    # Fallback chain
    chain_parser = subparsers.add_parser("chain", help="Show fallback chain for resource")
    chain_parser.add_argument("resource", help="Resource type (struct, exemplars_struct, curriculum)")

    args = parser.parse_args()

    if args.command == "sync":
        if args.resource:
            sync_resource(args.resource)
        else:
            sync_all(force=args.force)
    elif args.command == "verify":
        verify_resources()
    elif args.command == "setup-cron":
        setup_cron_sync()
    elif args.command == "chain":
        chain = get_fallback_chain(args.resource)
        print(f"\nFallback chain for {args.resource}:")
        for i, item in enumerate(chain, 1):
            print(f"  {i}. {item}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
