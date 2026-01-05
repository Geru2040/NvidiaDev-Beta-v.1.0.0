import requests
import json
from datetime import datetime
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# API Configuration
API_BASE = "https://lseypdqwyekqdndladsk.supabase.co/functions/v1"
CAPTURE_ENDPOINT = f"{API_BASE}/capture"
LISTEN_ENDPOINT = f"{API_BASE}/listen"
EXECUTE_ENDPOINT = f"{API_BASE}/execute"
COMMAND_STATUS_ENDPOINT = f"{API_BASE}/command-status"
AGENT_ENDPOINT = f"{API_BASE}/agent"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzZXlwZHF3eWVrcWRuZGxhZHNrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY4NzYyNzQsImV4cCI6MjA4MjQ1MjI3NH0.-Ebx3SwdHhEAkUg_TYPIxPktVI5Q-vRU1wxo69p7n90"

# Connection state
connected_account = None
private_agent_id = None
agent_status = None
last_known_place_id = None

# Agent storage file (local only, secure)
AGENTS_FILE = "agents.dat"

def load_agents():
    """Load saved agents from encrypted local file"""
    if not os.path.exists(AGENTS_FILE):
        return []

    try:
        with open(AGENTS_FILE, 'r') as f:
            encrypted = f.read()
            if not encrypted:
                return []
            key = "LUMEN_SECURE_KEY_2024"
            decrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(encrypted))
            return json.loads(decrypted)
    except:
        return []

def save_agents(agents):
    """Save agents to encrypted local file"""
    try:
        unique_agents = []
        seen_ids = set()
        for agent in agents:
            if agent['id'] not in seen_ids:
                unique_agents.append(agent)
                seen_ids.add(agent['id'])
        data = json.dumps(unique_agents)
        key = "LUMEN_SECURE_KEY_2024"
        encrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))
        with open(AGENTS_FILE, 'w') as f:
            f.write(encrypted)
        return True
    except Exception as e:
        print(f"  ⚠️  Failed to save agents: {e}")
        return False

def add_agent_to_storage(agent_id):
    agents = load_agents()
    for agent in agents:
        if agent['id'] == agent_id:
            agent['last_used'] = datetime.now().isoformat()
            save_agents(agents)
            return
    agents.append({
        'id': agent_id,
        'added_on': datetime.now().isoformat(),
        'last_used': datetime.now().isoformat(),
        'name': None,
        'starred': False
    })
    save_agents(agents)

def set_agent_name(agent_id, name):
    agents = load_agents()
    for agent in agents:
        if agent['id'] == agent_id:
            agent['name'] = name
            save_agents(agents)
            return True
    return False

def star_agent(agent_identifier):
    agents = load_agents()
    target_agent = None
    for agent in agents:
        if agent['id'] == agent_identifier or (agent.get('name') and agent['name'].lower() == agent_identifier.lower()):
            target_agent = agent
            break
    if target_agent is None:
        return False, "Agent not found"
    for agent in agents:
        agent['starred'] = False
    target_agent['starred'] = True
    save_agents(agents)
    return True, target_agent

def get_starred_agent():
    agents = load_agents()
    for agent in agents:
        if agent.get('starred', False):
            return agent
    return None

def remove_agent_from_storage(agent_id):
    agents = load_agents()
    agents = [a for a in agents if a['id'] != agent_id]
    save_agents(agents)

def gradient_text(text):
    lines = text.split('\n')
    colors = ['\033[38;5;141m', '\033[38;5;135m', '\033[38;5;129m', '\033[38;5;93m', '\033[38;5;57m', '\033[38;5;55m']
    result = []
    for i, line in enumerate(lines):
        color = colors[min(i, len(colors) - 1)]
        result.append(f"{color}{line}\033[0m")
    return '\n'.join(result)

def send_command(account_id, command, args=None):
    try:
        headers = {"Content-Type": "application/json", "apikey": API_KEY, "Authorization": f"Bearer {API_KEY}"}
        payload = {"roblox_account_id": account_id, "command": command, "args": args or {}}
        response = requests.post(EXECUTE_ENDPOINT, json=payload, headers=headers, timeout=30)
        if response.status_code != 200:
            return {"success": False, "error": f"Status {response.status_code}"}
        result = response.json()
        command_id = result.get("command_id")
        if not command_id:
            return {"success": False, "error": "No command_id returned"}
        max_attempts = 60
        for attempt in range(max_attempts):
            time.sleep(0.5)
            try:
                status_response = requests.get(f"{COMMAND_STATUS_ENDPOINT}?command_id={command_id}", headers=headers, timeout=10)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data.get("status") == "completed":
                        return {"success": True, "data": status_data.get("response", {})}
                    elif status_data.get("status") == "failed":
                        return {"success": False, "error": status_data.get("response", {}).get("error", "Command failed")}
            except:
                if attempt < max_attempts - 1: continue
                else: return {"success": False, "error": "Command status check timeout"}
        return {"success": False, "error": "Command timeout - no response received"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_agent_command(agent_id, command, args=None):
    return send_command(f"agent_{agent_id}", command, args)

def get_agent_status(agent_id):
    result = send_agent_command(agent_id, "agent_status")
    if result.get("success"):
        return result.get("data")
    return None

def get_agent_status_fast(agent_id):
    try:
        headers = {"Content-Type": "application/json", "apikey": API_KEY, "Authorization": f"Bearer {API_KEY}"}
        payload = {"roblox_account_id": f"agent_{agent_id}", "command": "agent_status", "args": {}}
        response = requests.post(EXECUTE_ENDPOINT, json=payload, headers=headers, timeout=3)
        if response.status_code != 200: return None
        result = response.json()
        command_id = result.get("command_id")
        if not command_id: return None
        for _ in range(6):
            time.sleep(0.5)
            try:
                status_response = requests.get(f"{COMMAND_STATUS_ENDPOINT}?command_id={command_id}", headers=headers, timeout=2)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data.get("status") == "completed":
                        return status_data.get("response", {})
            except: continue
        return None
    except: return None

def cmd_runport():
    global connected_account
    clear()
    banner()
    print("  Enter Roblox User ID to connect")
    account_id = input("  ID → ").strip()
    if account_id:
        connected_account = account_id
        print(f"\n  ✓ Connected to {account_id}")
        time.sleep(1.5)

def cmd_agent_list():
    clear()
    banner()
    agents = load_agents()
    if not agents:
        print("  → No saved agents found")
        input("\n  Press Enter to continue...")
        return
    print(f"  → Found {len(agents)} saved agent(s)")
    agent_statuses = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_agent = {executor.submit(get_agent_status_fast, agent['id']): agent['id'] for agent in agents}
        for future in as_completed(future_to_agent):
            agent_id = future_to_agent[future]
            try: agent_statuses[agent_id] = future.result()
            except: agent_statuses[agent_id] = None
    for i, agent in enumerate(agents, 1):
        status = agent_statuses.get(agent['id'])
        star = "⭐ " if agent.get('starred') else ""
        print(f"  [{i}] {star}Agent ID: {agent['id']}")
        if status: print("      ✓ Status: ONLINE")
        else: print("      ✗ Status: OFFLINE")
    print("\n  Type number to connect, 'remove <#>' to delete, or 'back'")
    choice = input("  → ").strip().lower()
    if choice == "back" or not choice: return
    if choice.startswith("remove "):
        try:
            idx = int(choice.split()[1]) - 1
            if 0 <= idx < len(agents):
                remove_agent_from_storage(agents[idx]['id'])
                print("\n  ✓ Removed")
                time.sleep(1)
        except: pass
        return cmd_agent_list()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(agents):
            global private_agent_id
            private_agent_id = agents[idx]['id']
            print(f"\n  ✓ Connected to {private_agent_id}")
            time.sleep(1.5)
    except: pass

def cmd_agent():
    global private_agent_id
    clear()
    banner()
    if private_agent_id:
        print(f"  ✓ Current Agent: {private_agent_id}")
        print("\n  [1] Change Agent\n  [2] Disconnect\n  [3] Back")
        choice = input("  Select → ").strip()
        if choice == "1": private_agent_id = None; return cmd_agent()
        if choice == "2": private_agent_id = None; print("  ✓ Disconnected"); time.sleep(1)
        return
    print("  Enter Agent User ID")
    agent_id = input("  ID → ").strip()
    if agent_id:
        result = send_agent_command(agent_id, "agent_ping")
        if result.get("success"):
            private_agent_id = agent_id
            add_agent_to_storage(agent_id)
            print("  ✓ Connected")
        else: print("  ✗ Failed")
        time.sleep(1.5)

def cmd_attach():
    global private_agent_id
    if not private_agent_id: print("  ✗ No agent"); time.sleep(1); return
    clear()
    banner()
    place_id = input("  Place ID → ").strip()
    if place_id:
        auto_script = input("  Auto Script URL (optional) → ").strip()
        send_agent_command(private_agent_id, "agent_attach", {"place_id": place_id, "auto_script": auto_script})
        print("  ✓ Sent")
        time.sleep(1.5)

def cmd_agent_status():
    global private_agent_id
    if not private_agent_id: print("  ✗ No agent"); time.sleep(1); return
    status = get_agent_status(private_agent_id)
    if status:
        print(f"\n  Status: {status.get('status', 'Unknown')}")
        if status.get('current_game'): print(f"  Game: {status['current_game']['name']}")
    else: print("  ✗ Failed")
    input("\n  Press Enter...")

def cmd_nameagent():
    global private_agent_id
    if not private_agent_id: print("  ✗ No agent"); time.sleep(1); return
    name = input("  New Name → ").strip()
    if name: set_agent_name(private_agent_id, name); print("  ✓ Done")
    time.sleep(1)

def cmd_staragent():
    clear()
    banner()
    agents = load_agents()
    if not agents: print("  ✗ No agents"); time.sleep(1); return
    for i, a in enumerate(agents, 1): print(f"  [{i}] {a['id']}")
    choice = input("  Select # to star → ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(agents):
            success, res = star_agent(agents[idx]['id'])
            if success: print("  ✓ Starred")
            else: print(f"  ✗ {res}")
    except: pass
    time.sleep(1)

def cmd_agent_starlist():
    agent = get_starred_agent()
    if agent: print(f"  ⭐ Starred: {agent['id']}")
    else: print("  ✗ None")
    input("\n  Press Enter...")

def cmd_screenrecord(args=None):
    global private_agent_id
    if not private_agent_id:
        print("\n  \033[38;5;196m✗ No private agent connected\033[0m")
        time.sleep(1.5)
        return
    duration = 5
    if args:
        for arg in args:
            if arg.startswith("--"):
                try: duration = min(int(arg[2:]), 5)
                except: pass
    result = send_agent_command(private_agent_id, "agent_screenrecord", {"duration": duration})
    if not result or not result.get("success"):
        print(f"\n  ✗ Failed: {result.get('error') if result else 'No response'}")
        time.sleep(2)
        return
    print(f"\n  🎬 Recording ({duration}s)...")
    for _ in range(120):
        time.sleep(1)
        status_result = send_agent_command(private_agent_id, "agent_screenrecord_status")
        if status_result and status_result.get("success"):
            video_url = status_result.get("data")
            if video_url and video_url != "PENDING":
                if "ERROR" not in video_url:
                    print(f"\n  ✓ Video: {video_url}")
                    input("\n  Press Enter...")
                else: print(f"\n  ✗ Failed: {video_url}"); time.sleep(2)
                break
    else: print("\n  ✗ Timeout"); time.sleep(2)

def cmd_screenshot():
    global connected_account, private_agent_id
    target_id = private_agent_id or connected_account
    if not target_id: return
    use_agent = private_agent_id is not None
    if use_agent: send_agent_command(target_id, "agent_screenshot")
    else: send_command(target_id, "screenshot")
    print("\n  📸 Capturing...")
    for _ in range(30):
        time.sleep(1)
        if use_agent: status = send_agent_command(target_id, "agent_screenshot_status")
        else: status = send_command(target_id, "screenshot_status")
        if status.get("success") and status.get("data") != "PENDING":
            print(f"\n  ✓ Screenshot: {status.get('data')}")
            input("\n  Press Enter...")
            break

def cmd_hotspot():
    global connected_account, private_agent_id
    target_id = private_agent_id or connected_account
    if not target_id: return
    if private_agent_id: res = send_agent_command(target_id, "hotspot")
    else: res = send_command(target_id, "hotspot")
    if res.get("success"): print(f"\n{res.get('report')}")
    input("\n  Press Enter...")

def cmd_moduletracker():
    global connected_account, private_agent_id
    target_id = private_agent_id or connected_account
    if not target_id: return
    if private_agent_id: res = send_agent_command(target_id, "moduletracker")
    else: res = send_command(target_id, "moduletracker")
    if res.get("success"): print(f"\n{res.get('report')}")
    input("\n  Press Enter...")

def cmd_flowwatch():
    global connected_account, private_agent_id
    target_id = private_agent_id or connected_account
    if not target_id: return
    user = input("  Target User ID/Name → ").strip()
    if user:
        if private_agent_id: res = send_agent_command(target_id, "flowwatch", {"user": user})
        else: res = send_command(target_id, "flowwatch", {"user": user})
        if res.get("success"): print("  ✓ Active")
    time.sleep(1)

def cmd_buildmap():
    global connected_account, private_agent_id
    target_id = private_agent_id or connected_account
    if not target_id: return
    if private_agent_id: res = send_agent_command(target_id, "buildmap")
    else: res = send_command(target_id, "buildmap")
    if res.get("success"): print("  ✓ Map built (JSON saved locally)")
    input("\n  Press Enter...")

def cmd_dex():
    global connected_account, private_agent_id
    target_id = private_agent_id or connected_account
    if not target_id: return
    if private_agent_id: send_agent_command(target_id, "dex")
    else: send_command(target_id, "dex")
    print("  ✓ DEX Sent")
    time.sleep(1)

def cmd_exe():
    global connected_account, private_agent_id
    target_id = private_agent_id or connected_account
    if not target_id: return
    script = input("  Script Content/URL → ").strip()
    if script:
        if private_agent_id: send_agent_command(target_id, "exe", {"script": script})
        else: send_command(target_id, "exe", {"script": script})
        print("  ✓ Executed")
    time.sleep(1)

def cmd_search(query=None):
    if not query: query = input("  Search → ").strip()
    if query:
        url = f"https://scriptblox.com/api/script/search?q={query}&max=10"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                scripts = r.json().get("result", {}).get("scripts", [])
                for i, s in enumerate(scripts, 1): print(f"  [{i}] {s.get('title')}")
        except: pass
    input("\n  Press Enter...")

def clear(): print("\033[2J\033[H", end="")

def banner():
    art = r"""   __   __  ____  ________  __
  / /  / / / /  |/  / __/ |/ /
 / /__/ /_/ / /|_/ / _//    / 
/____/\____/_/  /_/___/_/|_/  """
    print(gradient_text(art))
    print("  Game Data Capture & AI Analysis\n")

def main():
    while True:
        clear(); banner()
        print(f"  Connected: {connected_account or '✗'}")
        print(f"  Agent: {private_agent_id or '✗'}")
        print("\n  COMMANDS:\n  • runport, hotspot, moduletracker, flowwatch, buildmap, dex, exe, search, screenshot, screenrecord")
        print("\n  AGENT COMMANDS:\n  • agent, agent --list, agent --starlist, attach, agentstatus, nameagent, staragent, exit")
        choice = input("\n  Select → ").strip().lower()
        if choice == "exit": sys.exit(0)
        elif choice == "runport": cmd_runport()
        elif choice == "hotspot": cmd_hotspot()
        elif choice == "moduletracker": cmd_moduletracker()
        elif choice == "flowwatch": cmd_flowwatch()
        elif choice == "buildmap": cmd_buildmap()
        elif choice == "dex": cmd_dex()
        elif choice == "exe": cmd_exe()
        elif choice.startswith("search"): cmd_search(choice.replace("search", "", 1).strip())
        elif choice == "screenshot": cmd_screenshot()
        elif choice.startswith("screenrecord"): cmd_screenrecord(choice.split()[1:])
        elif choice == "agent": cmd_agent()
        elif choice == "agent --list": cmd_agent_list()
        elif choice == "agent --starlist": cmd_agent_starlist()
        elif choice == "attach": cmd_attach()
        elif choice == "agentstatus": cmd_agent_status()
        elif choice == "nameagent": cmd_nameagent()
        elif choice == "staragent": cmd_staragent()
        else: time.sleep(1)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)
