#!/usr/bin/env python3
"""
cPanel Deployment Manager
Handles pushing code to ivy server and managing deployment via FTP
Connects to: 192.64.118.16 (user: ivysfyoq)
"""

import argparse
import ftplib
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
DEPLOYMENT_CONFIG = ROOT / "deployment.json"
DEPLOY_STATE_FILE = ROOT / ".deploy-state.json"

# cPanel server details
CPANEL_HOST = "192.64.118.16"
CPANEL_USER = "ivysfyoq"
CPANEL_PASSWORD = "k8KcdO08EL6g"
REMOTE_BASE = "public_html"

VOLATILE_REL_PATHS = {
    "error_log",
    "api/stderr.log",
    ".ssl-manager/logs/debug.log",
    "bots/queue.db",
    "bots/web_struct_cache.json",
}


def sha256_file(path):
    """Compute SHA256 hash for a file"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_signature(path):
    """Return a cheap file signature (size + mtime ns)."""
    st = Path(path).stat()
    return int(st.st_size), int(st.st_mtime_ns)


def is_volatile_relpath(rel_posix):
    rel_posix = rel_posix.replace("\\", "/")
    if rel_posix in VOLATILE_REL_PATHS:
        return True
    if rel_posix.endswith(".db") or rel_posix.endswith(".db-wal") or rel_posix.endswith(".db-shm") or rel_posix.endswith(".db-journal"):
        return True
    if rel_posix.endswith(".pyc"):
        return True
    if "__pycache__/" in rel_posix or rel_posix.startswith("__pycache__/"):
        return True
    return False


def load_deploy_state():
    """Load local deploy state used for incremental uploads"""
    if DEPLOY_STATE_FILE.exists():
        try:
            return json.loads(DEPLOY_STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"files": {}}
    return {"files": {}}


def save_deploy_state(state):
    """Persist local deploy state"""
    merged = {"files": {}}
    if DEPLOY_STATE_FILE.exists():
        try:
            merged = json.loads(DEPLOY_STATE_FILE.read_text(encoding="utf-8"))
            if "files" not in merged or not isinstance(merged["files"], dict):
                merged = {"files": {}}
        except Exception:
            merged = {"files": {}}

    merged.setdefault("files", {}).update(state.get("files", {}))
    DEPLOY_STATE_FILE.write_text(json.dumps(merged, indent=2), encoding="utf-8")


def iter_files(local_dir):
    """Yield all files under local_dir recursively"""
    local_dir = Path(local_dir)
    for item in local_dir.rglob("*"):
        if item.is_file():
            yield item


def get_ftp():
    """Connect and return an FTP session"""
    ftp = ftplib.FTP()
    ftp.connect(CPANEL_HOST, 21, timeout=30)
    ftp.login(CPANEL_USER, CPANEL_PASSWORD)
    ftp.set_pasv(True)
    return ftp


def ftp_makedirs(ftp, remote_dir):
    """Recursively create remote directories"""
    parts = remote_dir.replace("\\", "/").split("/")
    current = ""
    for part in parts:
        if not part:
            continue
        current = f"{current}/{part}" if current else part
        try:
            ftp.mkd(current)
        except ftplib.error_perm:
            pass  # Already exists


def ftp_upload_file(ftp, local_path, remote_path):
    """Upload a single file via FTP"""
    remote_dir = "/".join(remote_path.replace("\\", "/").split("/")[:-1])
    if remote_dir:
        ftp_makedirs(ftp, remote_dir)
    with open(local_path, "rb") as f:
        ftp.storbinary(f"STOR {remote_path}", f)


def ftp_upload_dir(ftp, local_dir, remote_dir):
    """Recursively upload a directory via FTP (legacy full upload path)"""
    local_dir = Path(local_dir)
    ftp_makedirs(ftp, remote_dir)
    count = 0
    for item in iter_files(local_dir):
        rel = item.relative_to(local_dir)
        remote_path = f"{remote_dir}/{str(rel).replace(os.sep, '/')}"
        print(f"  ↑ {rel}")
        ftp_upload_file(ftp, str(item), remote_path)
        count += 1
    return count


def ftp_upload_dir_incremental(ftp, local_dir, remote_dir, deploy_state, force_full=False, include_volatile=False):
    """Upload only changed files from a directory based on local hash state"""
    local_dir = Path(local_dir)
    ftp_makedirs(ftp, remote_dir)

    uploaded = 0
    scanned = 0
    state_files = deploy_state.setdefault("files", {})

    for item in iter_files(local_dir):
        scanned += 1
        rel = item.relative_to(local_dir)
        rel_posix = str(rel).replace(os.sep, "/")
        if (not include_volatile) and is_volatile_relpath(rel_posix):
            continue

        remote_path = f"{remote_dir}/{rel_posix}"
        state_key = remote_path

        size, mtime_ns = file_signature(item)
        previous = state_files.get(state_key)
        previous_hash = None

        if isinstance(previous, dict):
            prev_size = int(previous.get("size", -1))
            prev_mtime = int(previous.get("mtime_ns", -1))
            if (not force_full) and prev_size == size and prev_mtime == mtime_ns:
                continue
            previous_hash = previous.get("hash")
        elif isinstance(previous, str):
            previous_hash = previous

        file_hash = sha256_file(item)
        if (not force_full) and previous_hash == file_hash:
            # Content unchanged; refresh cheap signature and skip upload.
            state_files[state_key] = {"hash": file_hash, "size": size, "mtime_ns": mtime_ns}
            continue

        print(f"  ↑ {rel_posix}")
        ftp_upload_file(ftp, str(item), remote_path)
        state_files[state_key] = {"hash": file_hash, "size": size, "mtime_ns": mtime_ns}
        uploaded += 1

    return uploaded, scanned


def test_connection():
    """Test FTP connection to cPanel server"""
    print("🔗 Testing FTP connection to cPanel...")
    try:
        ftp = get_ftp()
        print(f"✅ Connected! Server: {ftp.getwelcome()}")
        ftp.quit()
        return True
    except Exception as e:
        print(f"❌ FTP connection failed: {e}")
        return False


def get_deployment_status():
    """List remote public_html contents"""
    print("📊 Checking remote deployment status...")
    try:
        ftp = get_ftp()
        ftp.cwd(REMOTE_BASE)
        items = []
        ftp.retrlines("LIST", items.append)
        print("\n✓ public_html contents:")
        for item in items:
            print(" ", item)
        ftp.quit()
    except Exception as e:
        print(f"❌ Failed: {e}")


def deploy_files(target="all", force=False, full=False, include_volatile=False):
    """Deploy files to cPanel server via FTP"""
    print(f"📤 Starting FTP deployment (target: {target})...")

    local_public = ROOT / "public_html"
    local_practice = ROOT / "ib-practice-platform"

    targets = {
        "all": [
            (local_public, REMOTE_BASE, True),
            (local_practice, f"{REMOTE_BASE}/ib-practice-platform", True),
        ],
        "public": [(local_public, REMOTE_BASE, True)],
        "practice": [(local_practice, f"{REMOTE_BASE}/ib-practice-platform", True)],
        "questions": [(local_practice / "questions.json", f"{REMOTE_BASE}/ib-practice-platform/questions.json", False)],
    }

    if target not in targets:
        print(f"Unknown target: {target}")
        return False

    deploy_state = load_deploy_state()

    try:
        ftp = get_ftp()
        print("✅ FTP connected\n")
    except Exception as e:
        print(f"❌ FTP connection failed: {e}")
        return False

    total = 0
    try:
        for local_path, remote_path, is_dir in targets[target]:
            local_path = Path(local_path)
            if not local_path.exists():
                print(f"⚠️  Not found locally: {local_path}")
                continue
            print(f"📤 Uploading {local_path.name} → {remote_path}")
            if is_dir:
                count, scanned = ftp_upload_dir_incremental(
                    ftp,
                    local_path,
                    remote_path,
                    deploy_state,
                    force_full=full,
                    include_volatile=include_volatile,
                )
                print(f"✅ Uploaded {count} changed files from {local_path.name} (scanned {scanned})")
                total += count
            else:
                rel_name = local_path.name
                if (not include_volatile) and is_volatile_relpath(rel_name):
                    print(f"↷ Skipped volatile file {rel_name}")
                    continue

                size, mtime_ns = file_signature(local_path)
                file_hash = sha256_file(local_path)
                prev_entry = deploy_state.setdefault("files", {}).get(remote_path)
                prev_hash = prev_entry.get("hash") if isinstance(prev_entry, dict) else prev_entry
                if full or prev_hash != file_hash:
                    ftp_upload_file(ftp, str(local_path), remote_path)
                    deploy_state["files"][remote_path] = {"hash": file_hash, "size": size, "mtime_ns": mtime_ns}
                    print(f"✅ Uploaded {local_path.name}")
                    total += 1
                else:
                    deploy_state["files"][remote_path] = {"hash": file_hash, "size": size, "mtime_ns": mtime_ns}
                    print(f"↷ Skipped unchanged file {local_path.name}")
    except Exception as e:
        print(f"❌ Upload error: {e}")
        ftp.quit()
        return False

    ftp.quit()
    save_deploy_state(deploy_state)
    print(f"\n✅ Deployment complete! ({total} files uploaded)")
    return True


def setup_deployment_config():
    """Initialize deployment configuration"""
    config = {
        "host": CPANEL_HOST,
        "user": CPANEL_USER,
        "remote_base": REMOTE_BASE,
        "last_deployment": None,
        "deployment_history": [],
    }

    with open(DEPLOYMENT_CONFIG, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Deployment config created: {DEPLOYMENT_CONFIG}")


def main():
    parser = argparse.ArgumentParser(description="cPanel FTP Deployment Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    subparsers.add_parser("test", help="Test FTP connection to cPanel")
    subparsers.add_parser("status", help="List remote public_html contents")

    deploy_parser = subparsers.add_parser("deploy", help="Deploy files to cPanel via FTP")
    deploy_parser.add_argument("--target", choices=["all", "public", "practice", "questions"], default="all", help="What to deploy")
    deploy_parser.add_argument("--force", action="store_true", help="Skip confirmations")
    deploy_parser.add_argument("--full", action="store_true", help="Upload all files, not only changed files")
    deploy_parser.add_argument("--include-volatile", action="store_true", help="Include volatile files such as logs, db, and caches")

    subparsers.add_parser("init", help="Initialize deployment configuration")

    args = parser.parse_args()

    if args.command == "test":
        test_connection()
    elif args.command == "status":
        get_deployment_status()
    elif args.command == "deploy":
        deploy_files(target=args.target, force=args.force, full=args.full, include_volatile=args.include_volatile)
    elif args.command == "init":
        setup_deployment_config()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
