#!/usr/bin/env python3
"""
IVY Setup Wizard
Interactive setup for deployment and CDN configuration
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def title(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def section(text):
    print(f"\n→ {text}")
    print("-" * 60)

def check(text):
    print(f"  ✓ {text}")

def warning(text):
    print(f"  ⚠️  {text}")

def error(text):
    print(f"  ❌ {text}")

def prompt(text, default=None):
    suffix = f" [{default}]" if default else ""
    response = input(f"  ? {text}{suffix}: ").strip()
    return response or default

def run(command, desc=None):
    """Run command and return success"""
    try:
        if desc:
            print(f"  Running: {desc}...")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True, result.stdout
        return False, result.stderr
    except Exception as e:
        return False, str(e)

def setup_ssh():
    """Setup SSH connection"""
    section("SSH Setup")
    
    print("Testing SSH connection to cPanel server...")
    success, output = run("python deploy.py test", "SSH test")
    
    if success and "successful" in output:
        check("SSH connection working!")
        return True
    else:
        error("SSH connection failed")
        print(output)
        
        choice = prompt("Try alternate connection method?", "password")
        if choice == "password":
            print("\nNote: Using password in code is not recommended for production.")
            print("Consider setting up SSH keys - run 'python deploy.py ssh-key-setup' for instructions.")
        
        return False

def setup_resources():
    """Setup resource synchronization"""
    section("Resource Synchronization")
    
    print("Syncing resources from GitHub to local cache...")
    success, output = run("python resource-sync.py sync", "Resource sync")
    
    if success:
        check("Resources synchronized!")
        
        # Verify
        print("\nVerifying cached resources...")
        success, output = run("python resource-sync.py verify", "Verify cache")
        if success:
            check("All resources verified!")
        return True
    else:
        warning("Resource sync had issues:")
        print(output)
        return False

def setup_deployment():
    """Setup deployment configuration"""
    section("Deployment Configuration")
    
    print("Initializing deployment configuration...")
    success, output = run("python deploy.py init", "Init deployment")
    
    if success:
        check("Deployment config initialized!")
        return True
    else:
        warning("Could not initialize deployment config")
        return False

def test_deployment():
    """Test deployment"""
    section("Test Deployment")
    
    print("Checking deployment status on remote server...")
    success, output = run("python deploy.py status", "Check status")
    
    if success:
        check("Remote server accessible!")
        print(output[:500])  # Show first part
        return True
    else:
        warning("Could not access remote server")
        return False

def setup_cron():
    """Setup automatic resource sync"""
    section("Automatic Resource Sync")
    
    if sys.platform == "win32":
        print("Windows detected - setting up Task Scheduler...")
        
        choice = prompt("Create automatic daily sync task?", "y")
        if choice.lower() == "y":
            try:
                # Create task
                task_cmd = """
                $trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
                $action = New-ScheduledTaskAction -Execute "python.exe" -Argument "resource-sync.py sync" -WorkingDirectory "{root}"
                Register-ScheduledTask -TaskName "IVY Resource Sync" -Trigger $trigger -Action $action -Force
                """.format(root=ROOT)
                
                success, _ = run(task_cmd, "Create scheduled task")
                if success:
                    check("Automatic sync scheduled for 2:00 AM daily")
                else:
                    warning("Could not create scheduled task - continue manually")
            except Exception as e:
                warning(f"Task creation error: {e}")
    else:
        print("Unix-like system detected - setting up cron...")
        
        choice = prompt("Show cron setup instructions?", "y")
        if choice.lower() == "y":
            run("python resource-sync.py setup-cron", "Show cron setup")

def final_summary(checks):
    """Show final summary"""
    title("Setup Summary")
    
    total = len(checks)
    passed = sum(1 for _, success in checks if success)
    
    print("Autoparametercompleted tasks:\n")
    for task, success in checks:
        status = "✓" if success else "✗"
        print(f"  {status} {task}")
    
    print(f"\nProgress: {passed}/{total} tasks completed")
    
    if passed == total:
        check("All setup tasks completed!")
        print("\nNext steps:")
        print("  1. Generate questions using bot queue (if needed)")
        print("  2. Run: python deploy.py deploy --target all")
        print("  3. Visit your live website")
        print("  4. Resources will sync automatically daily")
    else:
        warning("Some tasks incomplete - review errors above")

def main():
    title("IVY Setup Wizard")
    
    print("This wizard will help you:")
    print("  • Test SSH connection to cPanel")
    print("  • Sync resources locally (GitHub → cache)")
    print("  • Initialize deployment configuration")
    print("  • Test remote server access")
    print("  • Setup automatic resource syncing")
    
    ready = prompt("Continue with setup?", "y")
    if ready.lower() != "y":
        print("\nSetup cancelled. You can run this wizard anytime:")
        print("  python setup-wizard.py")
        return
    
    checks = []
    
    # SSH Setup
    title("Step 1: SSH Connection")
    checks.append(("SSH Connection Test", setup_ssh()))
    
    # Resources
    title("Step 2: Resource Sync")
    checks.append(("Resource Synchronization", setup_resources()))
    
    # Deployment
    title("Step 3: Deployment Config")
    checks.append(("Deployment Configuration", setup_deployment()))
    
    # Test deployment
    title("Step 4: Remote Access")
    if not checks[0][1]:  # Skip if SSH failed
        warning("Skipping remote access test - SSH connection failed")
        checks.append(("Remote Server Access", False))
    else:
        checks.append(("Remote Server Access", test_deployment()))
    
    # Cron
    title("Step 5: Automatic Sync")
    setup_cron()
    checks.append(("Automatic Resource Sync", True))
    
    # Summary
    final_summary(checks)
    
    print("\n" + "="*60)
    print("Setup wizard complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
