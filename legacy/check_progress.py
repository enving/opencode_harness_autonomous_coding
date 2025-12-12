#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check OpenCode Agent Progress
=============================

Monitor the autonomous agent's progress:
- Check if feature_list.json exists
- Show current session status
- Display progress statistics
"""

import asyncio
import json
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from opencode_ai import AsyncOpencode


async def check_progress(project_dir: str = "./testx"):
    """Check agent progress."""
    project_path = Path(project_dir)
    
    print("=" * 70)
    print("  OpenCode Agent Progress Monitor")
    print("=" * 70)
    print(f"\nProject: {project_path.resolve()}")
    print()
    
    # 1. Check feature_list.json
    feature_list = project_path / "feature_list.json"
    print("[1/3] Checking feature_list.json...")
    
    if feature_list.exists():
        try:
            with open(feature_list) as f:
                features = json.load(f)
            
            total = len(features)
            passed = sum(1 for f in features if f.get("passes", False))
            pending = total - passed
            
            print(f"      [OK] Found feature_list.json")
            print(f"      Total features: {total}")
            print(f"      Completed: {passed} ({passed/total*100:.1f}%)")
            print(f"      Pending: {pending}")
            
            # Show first 5 pending features
            pending_features = [f for f in features if not f.get("passes", False)][:5]
            if pending_features:
                print(f"\n      Next features to implement:")
                for i, feat in enumerate(pending_features, 1):
                    name = feat.get("name", "Unknown")
                    print(f"        {i}. {name}")
        except Exception as e:
            print(f"      [ERROR] Could not read feature_list.json: {e}")
    else:
        print(f"      [WAITING] feature_list.json not yet created")
        print(f"      The initializer agent is still working...")
    print()
    
    # 2. Check active sessions
    print("[2/3] Checking active sessions...")
    try:
        base_url = "http://localhost:4096"
        client = AsyncOpencode(base_url=base_url, timeout=10.0)
        
        sessions = await client.session.list()
        
        # Filter sessions for this project
        project_sessions = [
            s for s in sessions 
            if hasattr(s, 'directory') and str(project_path.resolve()).lower() in s.directory.lower()
        ]
        
        if project_sessions:
            print(f"      [OK] Found {len(project_sessions)} active session(s)")
            for s in project_sessions[:3]:  # Show first 3
                title = s.title if hasattr(s, 'title') else 'Unknown'
                session_id = s.id if hasattr(s, 'id') else 'unknown'
                print(f"        - {title[:60]}")
                print(f"          ID: {session_id}")
                
                # Check if session has recent activity
                if hasattr(s, 'time') and hasattr(s.time, 'updated'):
                    import datetime
                    updated = datetime.datetime.fromtimestamp(s.time.updated / 1000)
                    now = datetime.datetime.now()
                    age = (now - updated).total_seconds()
                    if age < 60:
                        print(f"          Status: ACTIVE (updated {int(age)}s ago)")
                    elif age < 300:
                        print(f"          Status: Recent (updated {int(age/60)}min ago)")
                    else:
                        print(f"          Status: Idle (updated {int(age/60)}min ago)")
        else:
            print(f"      [INFO] No active sessions for this project")
            print(f"      Start the agent with:")
            print(f"      python autonomous_agent_demo.py --project-dir {project_dir}")
    except Exception as e:
        print(f"      [ERROR] Could not check sessions: {e}")
    print()
    
    # 3. Check project files
    print("[3/3] Checking project files...")
    
    if project_path.exists():
        files = list(project_path.glob("*"))
        print(f"      [OK] Project directory exists")
        print(f"      Files/folders: {len(files)}")
        
        # Show interesting files
        interesting = [
            "feature_list.json",
            "package.json",
            "README.md",
            "init.sh",
            ".opencode.json"
        ]
        
        found_interesting = [f.name for f in files if f.name in interesting]
        if found_interesting:
            print(f"      Key files found:")
            for fname in found_interesting:
                fpath = project_path / fname
                size = fpath.stat().st_size if fpath.is_file() else 0
                print(f"        - {fname} ({size} bytes)")
    else:
        print(f"      [WAITING] Project directory not yet created")
    print()
    
    print("=" * 70)
    print("  Tips:")
    print("=" * 70)
    print()
    print("1. If feature_list.json doesn't exist yet:")
    print("   -> The initializer agent is still running (10-20+ minutes)")
    print("   -> Check OpenCode server logs for activity")
    print()
    print("2. To watch logs in real-time:")
    print("   -> Check the terminal where you started autonomous_agent_demo.py")
    print("   -> Look for [Tool: ...] messages showing agent activity")
    print()
    print("3. To restart if stuck:")
    print("   -> Ctrl+C to stop the agent")
    print("   -> Delete testx/feature_list.json if you want a fresh start")
    print("   -> Run: python autonomous_agent_demo.py --project-dir testx")


if __name__ == "__main__":
    import sys
    project = sys.argv[1] if len(sys.argv) > 1 else "./testx"
    asyncio.run(check_progress(project))
