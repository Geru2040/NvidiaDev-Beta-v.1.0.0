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

def cmd_attach():
    """Attach agent to a game with auto-reconnect detection"""
    global private_agent_id, last_known_place_id

    if not private_agent_id:
        clear()
        banner()
        print("\n  \033[38;5;196m✗ No private agent connected\033[0m")
        print("  \033[38;5;93m→ Run 'agent' command first\033[0m\n")
        input("\n  Press Enter to continue...")
        return

    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║           ATTACH AGENT TO GAME                ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    print(f"  \033[38;5;93m→ Agent ID: {private_agent_id}\033[0m")
    print("  \033[38;5;135m→ Enter Game Place ID to attach\033[0m")
    print("  \033[38;5;93m→ Type 'cancel' to go back\033[0m\n")

    place_id = input("  Place ID → ").strip()

    if not place_id or place_id.lower() == "cancel":
        print("\n  → Cancelled\n")
        time.sleep(0.8)
        return

    try:
        place_id_int = int(place_id)
    except ValueError:
        print("\n  \033[38;5;196m✗ Invalid Place ID (must be a number)\033[0m")
        input("\n  Press Enter to continue...")
        return

    print("\n  \033[38;5;93m→ Auto-execute script after joining? (optional)\033[0m")
    print("  \033[38;5;93m→ Enter script URL or press Enter to skip\033[0m\n")
    auto_script = input("  Script URL → ").strip()

    print(f"\n  \033[38;5;135m→ Sending attach command to agent...\033[0m")

    args = {
        "place_id": place_id
    }
    if auto_script:
        args["auto_script"] = auto_script

    result = send_agent_command(private_agent_id, "agent_attach", args)

    if not result.get("success"):
        print("\n  \033[38;5;196m✗ Failed to send attach command\033[0m")
        print(f"  Error: {result.get('error', 'Unknown')}")
        input("\n  Press Enter to continue...")
        return

    data = result.get("data", {})
    method = data.get("method", "Unknown")
    print(f"  \033[38;5;141m✓ Teleport initiated!\033[0m")
    print(f"  \033[38;5;93m→ Method: {method}\033[0m")

    # Check if it's a manual method (Clipboard or Browser)
    if "clipboard" in method.lower() or "manual" in method.lower() or "browser" in method.lower():
        print(f"\n  \033[38;5;135m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
        print(f"  \033[38;5;135m📋 Manual Teleport Method Active\033[0m")
        print(f"  \033[38;5;135m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n")
        print(f"  \033[38;5;141m→ Method:\033[0m {method}")
        if data.get('note'):
            print(f"  \033[38;5;141m→ Note:\033[0m {data.get('note')}")
        print(f"\n  \033[38;5;93m⚠️  Agent teleport triggered!\033[0m")
        print(f"  \033[38;5;93m→ Check the agent's device for teleport GUI\033[0m")
        print(f"  \033[38;5;93m→ If URL was copied, paste it in Roblox\033[0m")
        print(f"  \033[38;5;93m→ Use 'agentstatus' to verify connection\033[0m\n")
        input("\n  Press Enter to continue...")
        return

    # For DeepLink and TeleportService methods, wait for reconnect
    if "deeplink" in method.lower() or "teleportservice" in method.lower():
        print(f"\n  \033[38;5;135m→ Deep link teleport triggered!\033[0m")
        print(f"  \033[38;5;93m→ Agent should be joining game now...\033[0m")

        success, game_info = wait_for_agent_reconnect(private_agent_id, place_id_int, max_wait=60)

        if success and game_info:
            last_known_place_id = place_id_int
            print(f"\n  \033[38;5;141m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
            print(f"  \033[38;5;141m✓ AGENT SUCCESSFULLY ATTACHED!\033[0m")
            print(f"  \033[38;5;141m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n")
            print(f"  \033[38;5;135m📍 Game Name:\033[0m {game_info.get('name', 'Unknown')}")
            print(f"  \033[38;5;135m📍 Place ID:\033[0m {place_id}")
            print(f"  \033[38;5;135m👥 Players:\033[0m {game_info.get('players', 'Unknown')}")
            print(f"  \033[38;5;135m🛡️  Anti-AFK:\033[0m Active")
            if auto_script:
                print(f"  \033[38;5;135m📜 Auto-Script:\033[0m Executed")
            print()
        else:
            print(f"\n  \033[38;5;93m⚠️  Could not verify connection within 60 seconds\033[0m")
            print(f"  \033[38;5;93m→ Agent may still be loading the game\033[0m")
            print(f"  \033[38;5;93m→ Use 'agentstatus' command to check manually\033[0m")
    else:
        # Unknown method, just show info
        print(f"\n  \033[38;5;135m→ Teleport command sent\033[0m")
        print(f"  \033[38;5;93m→ Use 'agentstatus' to verify connection\033[0m")

    input("\n  Press Enter to continue...")

def cmd_agent_status():
    """Check agent status and control"""
    global private_agent_id

    if not private_agent_id:
        clear()
        banner()
        print("\n  \033[38;5;196m✗ No private agent connected\033[0m")
        print("  \033[38;5;93m→ Run 'agent' command first\033[0m\n")
        input("\n  Press Enter to continue...")
        return

    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║            AGENT STATUS & CONTROL             ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    print(f"  \033[38;5;135m→ Fetching agent status...\033[0m\n")

    status = get_agent_status(private_agent_id)

    if not status:
        print("  \033[38;5;196m✗ Could not fetch agent status\033[0m")
        input("\n  Press Enter to continue...")
        return

    print(f"  \033[38;5;141m✓ Agent ID:\033[0m {private_agent_id}")
    print(f"  \033[38;5;141m✓ Status:\033[0m {status.get('status', 'Unknown')}")
    print(f"  \033[38;5;141m✓ Uptime:\033[0m {status.get('uptime', 0)} minutes")

    if status.get('current_game'):
        game = status['current_game']
        print(f"\n  \033[38;5;135m📍 Current Game:\033[0m")
        print(f"     Name: {game.get('name', 'Unknown')}")
        print(f"     Place ID: {game.get('place_id', 'Unknown')}")
        print(f"     Players: {game.get('players', 'Unknown')}")
        print(f"     Time in game: {game.get('time_in_game', 0)} minutes")
    else:
        print(f"\n  \033[38;5;93m→ Not currently in a game\033[0m")

    if status.get('anti_afk_active'):
        print(f"\n  \033[38;5;141m✓ Anti-AFK:\033[0m Active")

    print("\n  \033[38;5;93m" + "─"*45 + "\033[0m\n")
    print("  \033[38;5;93m[1]\033[0m Leave Current Game")
    print("  \033[38;5;93m[2]\033[0m Execute Script on Agent")
    print("  \033[38;5;93m[3]\033[0m Get Game Data")
    print("  \033[38;5;93m[4]\033[0m Back\n")

    choice = input("  Select → ").strip()

    if choice == "1":
        print(f"\n  \033[38;5;135m→ Instructing agent to leave game...\033[0m")
        result = send_agent_command(private_agent_id, "agent_leave_game")
        if result.get("success"):
            print("  \033[38;5;141m✓ Agent left the game\033[0m")
        else:
            print("  \033[38;5;196m✗ Failed to leave game\033[0m")
        time.sleep(1.5)

    elif choice == "2":
        print("\n  \033[38;5;135m→ Enter script URL or Lua code\033[0m\n")
        script = input("  Script → ").strip()
        if script:
            print(f"\n  \033[38;5;135m→ Executing on agent...\033[0m")
            result = send_agent_command(private_agent_id, "agent_execute", {"script": script})
            if result.get("success"):
                print("  \033[38;5;141m✓ Script executed\033[0m")
            else:
                print("  \033[38;5;196m✗ Execution failed\033[0m")
            time.sleep(1.5)

    elif choice == "3":
        print(f"\n  \033[38;5;135m→ Collecting game data from agent...\033[0m")
        result = send_agent_command(private_agent_id, "agent_collect_data")
        if result.get("success"):
            data = result.get("data", {})
            print("\n  \033[38;5;141m✓ Data collected!\033[0m\n")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dumps/agent_data_{private_agent_id}_{timestamp}.json"
            if not os.path.exists('dumps'):
                os.makedirs('dumps')

            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"  \033[38;5;141m✓ Saved to:\033[0m {filename}")
        else:
            print("  \033[38;5;196m✗ Failed to collect data\033[0m")

        input("\n  Press Enter to continue...")

def cmd_nameagent():
    """Name an agent"""
    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║              NAME AGENT                       ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    agents = load_agents()

    if not agents:
        print("  \033[38;5;196m✗ No saved agents found\033[0m")
        input("\n  Press Enter to continue...")
        return

    print("  \033[38;5;135mSaved Agents:\033[0m\n")
    for i, agent in enumerate(agents, 1):
        agent_name = agent.get('name')
        name_display = f" ({agent_name})" if agent_name else ""
        print(f"  \033[38;5;93m[{i}]\033[0m {agent['id']}{name_display}")

    print("\n  \033[38;5;93mEnter agent ID or number:\033[0m")
    agent_input = input("  Agent → ").strip()

    if not agent_input:
        return

    # Find agent by number or ID
    target_agent = None
    try:
        agent_num = int(agent_input)
        if 1 <= agent_num <= len(agents):
            target_agent = agents[agent_num - 1]
    except ValueError:
        # Try to find by ID
        for agent in agents:
            if agent['id'] == agent_input:
                target_agent = agent
                break

    if not target_agent:
        print("\n  \033[38;5;196m✗ Agent not found\033[0m")
        time.sleep(1.5)
        return

    print(f"\n  \033[38;5;135mEnter custom name for agent {target_agent['id']}:\033[0m")
    custom_name = input("  Name → ").strip()

    if not custom_name:
        print("\n  \033[38;5;196m✗ Name cannot be empty\033[0m")
        time.sleep(1.5)
        return

    if set_agent_name(target_agent['id'], custom_name):
        print(f"\n  \033[38;5;141m✓ Agent named: {custom_name}\033[0m")
    else:
        print("\n  \033[38;5;196m✗ Failed to set name\033[0m")

    time.sleep(1.5)

def cmd_staragent():
    """Star/favorite an agent"""
    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║              STAR AGENT                       ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    agents = load_agents()

    if not agents:
        print("  \033[38;5;196m✗ No saved agents found\033[0m")
        input("\n  Press Enter to continue...")
        return

    print("  \033[38;5;135mSaved Agents:\033[0m\n")
    for i, agent in enumerate(agents, 1):
        agent_name = agent.get('name')
        is_starred = agent.get('starred', False)
        star_icon = "⭐ " if is_starred else "   "
        name_display = f" ({agent_name})" if agent_name else ""
        print(f"  {star_icon}\033[38;5;93m[{i}]\033[0m {agent['id']}{name_display}")

    print("\n  \033[38;5;93mEnter agent ID, name, or number to star:\033[0m")
    agent_input = input("  Agent → ").strip()

    if not agent_input:
        return

    # Try to find by number first
    target_identifier = None
    try:
        agent_num = int(agent_input)
        if 1 <= agent_num <= len(agents):
            target_identifier = agents[agent_num - 1]['id']
    except ValueError:
        target_identifier = agent_input

    if target_identifier:
        success, result = star_agent(target_identifier)
        if success:
            agent_display = result.get('name') or result['id']
            print(f"\n  \033[38;5;141m✓ Starred agent: {agent_display} ⭐\033[0m")
        else:
            print(f"\n  \033[38;5;196m✗ {result}\033[0m")
    else:
        print("\n  \033[38;5;196m✗ Invalid input\033[0m")

    time.sleep(1.5)

def cmd_agent_starlist():
    """Show and connect to starred agent"""
    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║            STARRED AGENT                      ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    starred = get_starred_agent()

    if not starred:
        print("  \033[38;5;196m✗ No agent is currently starred\033[0m")
        print("  \033[38;5;93m→ Use 'staragent' to mark a favorite agent\033[0m\n")
        input("\n  Press Enter to continue...")
        return

    agent_id = starred['id']
    agent_name = starred.get('name')

    print("  \033[38;5;141m⭐ Starred Agent:\033[0m\n")

    name_display = f" ({agent_name})" if agent_name else ""
    print(f"  \033[38;5;135mAgent ID:\033[0m {agent_id}{name_display}")

    try:
        added_on = datetime.fromisoformat(starred['added_on']).strftime("%Y-%m-%d %H:%M")
        print(f"  \033[38;5;93mAdded:\033[0m {added_on}")
    except:
        pass

    try:
        last_used = datetime.fromisoformat(starred['last_used']).strftime("%Y-%m-%d %H:%M")
        print(f"  \033[38;5;93mLast Used:\033[0m {last_used}")
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

    # Call the pre-defined Lua function in agent.lua
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

    # Wait for capture to complete (60 seconds max)
    time.sleep(5)

    url = "PENDING"
    for attempt in range(15):  # 75 seconds total
        dots = "." * ((attempt % 3) + 1) + " " * (2 - (attempt % 3))
        print(f"  \033[38;5;135m⏳ Processing{dots}\033[0m", end='\r', flush=True)
        time.sleep(5)

        # Check the global variable on target
        check_script = "return _G.LUMEN_SCREENSHOT_URL"
        if use_agent:
            check_result = send_agent_command(target_id, "exe", {"script": check_script})
        else:
            check_result = send_command(target_id, "exe", {"script": check_script})

        if check_result.get("success"):
            data = check_result.get("data")
            # Parse the URL from the response
            found_url = None
            if isinstance(data, str) and data.startswith("http"):
                found_url = data
            elif isinstance(data, dict):
                res_val = data.get("response", data.get("data", data.get("url")))
                if isinstance(res_val, dict):
                    res_val = res_val.get("url", res_val.get("data", res_val.get("response")))
                if isinstance(res_val, str) and res_val.startswith("http"):
                    found_url = res_val
            
            if found_url:
                url = found_url
                break
            
            if isinstance(data, str) and "ERROR" in data:
                url = data
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
def cmd_runport():
    """Establish connection with client"""
    global connected_account

    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║            CONNECTION MANAGER                 ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    account_id = input("  Roblox Account ID → ").strip()

    if not account_id:
        print("\n  ✗ Invalid account ID")
        time.sleep(1.5)
        return

    print(f"\n  \033[38;5;135m→ Establishing connection to {account_id}...\033[0m")
    time.sleep(1)

    result = send_command(account_id, "ping")
    if result.get("success"):
        connected_account = account_id
        print(f"  \033[38;5;141m✓ Connected successfully!\033[0m")
        print(f"  \033[38;5;93m→ Port active for account: {account_id}\033[0m\n")
    else:
        print(f"  \033[38;5;196m✗ Connection failed\033[0m")
        print(f"  \033[38;5;93m→ Make sure client is running\033[0m\n")

    input("\n  Press Enter to continue...")

def cmd_hotspot():
    """Scan and rank scripts by size/complexity"""
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
    print("\033[38;5;141m║            SCRIPT HOTSPOT SCANNER             ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    print(f"  \033[38;5;93m→ Connected to: {target_id} {'(Agent)' if use_agent else ''}\033[0m")
    print("\033[38;5;135m  → Scanning all scripts for hotspots...\033[0m")
    print("\033[38;5;93m  → This may take a few seconds...\033[0m\n")

    if use_agent:
        result = send_agent_command(target_id, "hotspot")
    else:
        result = send_command(target_id, "hotspot")

    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║            SCRIPT HOTSPOT SCANNER             ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    if result.get("success"):
        data = result.get("data", {})
        report = data.get("report", "")
        stats = data.get("stats", {})

        print("  \033[38;5;141m✓ Hotspot scan complete!\033[0m\n")
        print("  \033[38;5;93m" + "─"*45 + "\033[0m\n")

        for line in report.split('\n'):
            print("  " + line)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dumps/hotspot_{target_id}_{timestamp}.txt"
        if not os.path.exists('dumps'):
            os.makedirs('dumps')

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
            f.write(f"\n\nFull JSON Data:\n{json.dumps(data, indent=2)}")

        print(f"\n  \033[38;5;141m✓ Full report saved to:\033[0m {filename}")
    else:
        print("  \033[38;5;196m✗ Failed to scan hotspots\033[0m")
        print(f"  Error: {result.get('error', 'Unknown')}")

    input("\n  Press Enter to continue...")

def cmd_moduletracker():
    """Track all ModuleScripts and their dependencies"""
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
    print("\033[38;5;141m║          MODULE DEPENDENCY TRACKER            ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    print(f"  \033[38;5;93m→ Connected to: {target_id} {'(Agent)' if use_agent else ''}\033[0m")
    print("\033[38;5;135m  → Tracking all ModuleScripts...\033[0m")
    print("\033[38;5;93m  → Analyzing dependencies...\033[0m\n")

    if use_agent:
        result = send_agent_command(target_id, "moduletracker")
    else:
        result = send_command(target_id, "moduletracker")

    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║          MODULE DEPENDENCY TRACKER            ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    if result.get("success"):
        data = result.get("data", {})
        report = data.get("report", "")

        print("  \033[38;5;141m✓ Module tracking complete!\033[0m\n")
        print("  \033[38;5;93m" + "─"*45 + "\033[0m\n")

        for line in report.split('\n'):
            print("  " + line)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dumps/modules_{target_id}_{timestamp}.txt"
        if not os.path.exists('dumps'):
            os.makedirs('dumps')

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
            f.write(f"\n\nFull JSON Data:\n{json.dumps(data, indent=2)}")

        print(f"\n  \033[38;5;141m✓ Full report saved to:\033[0m {filename}")
    else:
        print("  \033[38;5;196m✗ Failed to track modules\033[0m")
        print(f"  Error: {result.get('error', 'Unknown')}")

    input("\n  Press Enter to continue...")

def cmd_flowwatch():
    """Live tracking of game changes for specific player"""
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
    print("\033[38;5;141m║          FLOWWATCH LIVE TRACKER               ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    print(f"  \033[38;5;93m→ Connected to: {target_id} {'(Agent)' if use_agent else ''}\033[0m")
    print("\033[38;5;135m  → Enter target player username or UserID\033[0m")
    print("\033[38;5;93m  → Type 'cancel' to go back\033[0m\n")

    target_user = input("  Target Player → ").strip()

    if not target_user or target_user.lower() == "cancel":
        return

    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║          FLOWWATCH LIVE TRACKER               ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    print(f"  \033[38;5;135m🔹 Connecting to player: {target_user}\033[0m")

    if use_agent:
        result = send_agent_command(target_id, "flowwatch", {"user": target_user})
    else:
        result = send_command(target_id, "flowwatch", {"user": target_user})

    if not result.get("success"):
        print(f"\n  \033[38;5;196m✗ Failed to start FlowWatch\033[0m")
        print(f"  Error: {result.get('error', 'Unknown')}")
        input("\n  Press Enter to continue...")
        return

    player_name = result.get("data", {}).get("player", target_user)
    user_id = result.get("data", {}).get("userId", "Unknown")

    print(f"  \033[38;5;141m🔹 Connected to {player_name} (ID: {user_id})\033[0m")
    print(f"  \033[38;5;141m🔹 Monitoring game...\033[0m\n")
    print("  \033[38;5;93m──────────────────────────────────────────\033[0m\n")
    print("  \033[38;5;93mCommands: 'stop' | 'exit'\033[0m")
    print("  \033[38;5;93m(Press Ctrl+C to enter command)\033[0m\n")

    monitoring = True
    while monitoring:
        try:
            time.sleep(2)

            if use_agent:
                poll_result = send_agent_command(target_id, "flowwatch_poll")
            else:
                poll_result = send_command(target_id, "flowwatch_poll")

            if not poll_result.get("success"):
                continue

            changes_list = poll_result.get("data", {}).get("changes", [])

            if changes_list:
                for changes in changes_list:
                    timestamp = datetime.now().strftime("%H:%M:%S")

                    for item in changes.get("added", []):
                        class_name = item.get("class", "Unknown")
                        name = item.get("name", "Unknown")
                        parent = item.get("parent", "Unknown")

                        if class_name == "Folder":
                            print(f"  \033[38;5;141m[{timestamp}] [+] Folder Created:\033[0m {name}")
                        else:
                            print(f"  \033[38;5;141m[{timestamp}] [+] New Script Added:\033[0m {name} ({class_name})")
                        print(f"      \033[38;5;93m↳ Parent: {parent}\033[0m")

                    for item in changes.get("removed", []):
                        class_name = item.get("class", "Unknown")
                        name = item.get("name", "Unknown")

                        if class_name == "Folder":
                            print(f"  \033[38;5;196m[{timestamp}] [-] Folder Removed:\033[0m {name}")
                        else:
                            print(f"  \033[38;5;196m[{timestamp}] [-] Script Removed:\033[0m {name} ({class_name})")

                    if changes.get("added") or changes.get("removed"):
                        print()

        except KeyboardInterrupt:
            print("\n")
            cmd = input("  lumen> ").strip().lower()

            if cmd == "exit" or cmd == "stop":
                print("\n  \033[38;5;135m→ Stopping FlowWatch...\033[0m")
                if use_agent:
                    send_agent_command(target_id, "flowwatch_stop")
                else:
                    send_command(target_id, "flowwatch_stop")
                monitoring = False
                time.sleep(0.8)
            elif cmd:
                print(f"  \033[38;5;196m✗ Unknown command: {cmd}\033[0m")
                print("  \033[38;5;93m💡 Resuming monitoring...\033[0m\n")

    print("\n  \033[38;5;141m✓ FlowWatch stopped\033[0m\n")
    input("  Press Enter to continue...")

def cmd_buildmap():
    """Build game tree visualization"""
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
    print("\033[38;5;141m║              GAME TREE BUILDER                ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    print(f"  \033[38;5;93m→ Connected to: {target_id} {'(Agent)' if use_agent else ''}\033[0m")
    print("\033[38;5;135m  → Mapping entire game structure...\033[0m")
    print("\033[38;5;93m  → This may take a few seconds...\033[0m\n")

    if use_agent:
        result = send_agent_command(target_id, "buildmap")
    else:
        result = send_command(target_id, "buildmap")

    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║              GAME TREE BUILDER                ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    if result.get("success"):
        data = result.get("data", {})
        tree = data.get("tree", "")
        stats = data.get("stats", {})

        print("  \033[38;5;141m✓ Map generated successfully!\033[0m\n")

        if stats:
            print(f"  \033[38;5;135mTotal Instances:\033[0m {stats.get('totalInstances', 'N/A')}")
            print(f"  \033[38;5;135mPlayers Online:\033[0m {stats.get('players', 'N/A')}\n")

        print("  \033[38;5;93m" + "─"*45 + "\033[0m\n")

        tree_lines = tree.split('\n')
        if len(tree_lines) > 100:
            for line in tree_lines[:100]:
                print("  " + line)
            print(f"\n  \033[38;5;93m... ({len(tree_lines) - 100} more lines)\033[0m")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dumps/game_map_{target_id}_{timestamp}.txt"
            if not os.path.exists('dumps'):
                os.makedirs('dumps')

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(tree)
                f.write(f"\n\nFull JSON Data:\n{json.dumps(data.get('data', {}), indent=2)}")

            print(f"  \033[38;5;141m✓ Full map saved to:\033[0m {filename}")
        else:
            for line in tree_lines:
                print("  " + line)
    else:
        print("  \033[38;5;196m✗ Failed to build map\033[0m")
        print(f"  Error: {result.get('error', 'Unknown')}")

    input("\n  Press Enter to continue...")

def cmd_exe():
    """Execute custom script"""
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
    print("\033[38;5;141m║            SCRIPT EXECUTOR                    ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    print(f"  \033[38;5;93m→ Connected to: {target_id} {'(Agent)' if use_agent else ''}\033[0m")
    print("\033[38;5;135m  → Options:\033[0m")
    print("  \033[38;5;93m[1]\033[0m Enter URL")
    print("  \033[38;5;93m[2]\033[0m Paste Multi-line Script")
    print("  \033[38;5;93m[3]\033[0m Load from File")
    print("  \033[38;5;93m[4]\033[0m Cancel\n")

    choice = input("  Select → ").strip()

    script = None

    if choice == "1":
        print("\n  \033[38;5;135m→ Enter script URL:\033[0m")
        script = input("  URL → ").strip()

    elif choice == "2":
        print("\n  \033[38;5;135m→ Paste your script below\033[0m")
        print("  \033[38;5;93m→ Type 'END' on a new line when done\033[0m")
        print("  \033[38;5;93m→ Or press Ctrl+D (Unix) / Ctrl+Z (Windows)\033[0m\n")

        lines = []
        try:
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
        except EOFError:
            pass

        script = '\n'.join(lines)

    elif choice == "3":
        print("\n  \033[38;5;135m→ Enter file path:\033[0m")
        filepath = input("  Path → ").strip()

        try:
            with open(filepath, 'r') as f:
                script = f.read()
            print(f"  \033[38;5;141m✓ Loaded {len(script)} characters from file\033[0m")
        except FileNotFoundError:
            print(f"  \033[38;5;196m✗ File not found: {filepath}\033[0m")
            input("\n  Press Enter to continue...")
            return
        except Exception as e:
            print(f"  \033[38;5;196m✗ Error reading file: {e}\033[0m")
            input("\n  Press Enter to continue...")
            return

    elif choice == "4":
        return

    else:
        print("\n  \033[38;5;196m✗ Invalid option\033[0m")
        time.sleep(1)
        return

    if not script or script.lower() == "cancel":
        return

    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║            SCRIPT EXECUTOR                    ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    print(f"  \033[38;5;135m→ Executing script ({len(script)} chars)...\033[0m\n")

    if use_agent:
        result = send_agent_command(target_id, "exe", {"script": script})
    else:
        result = send_command(target_id, "exe", {"script": script})

    if result.get("success"):
        print("  \033[38;5;141m✓ Script executed successfully!\033[0m")
        print("  \033[38;5;93m→ Check your game for results\033[0m")
    else:
        print("  \033[38;5;196m✗ Failed to execute script\033[0m")
        print(f"  Error: {result.get('error', 'Unknown')}")

    input("\n  Press Enter to continue...")

def cmd_dex(revamp=False):
    """DEX explorer module"""
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
    print("\033[38;5;141m║                DEX EXPLORER                   ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    print(f"  \033[38;5;93m→ Connected to: {target_id} {'(Agent)' if use_agent else ''}\033[0m")
    if revamp:
        print("\033[38;5;135m  → Launching DEX Mobile (Revamped)...\033[0m\n")
    else:
        print("\033[38;5;135m  → Launching Dark DEX Mobile...\033[0m\n")

    if use_agent:
        result = send_agent_command(target_id, "dex", {"revamp": revamp})
    else:
        result = send_command(target_id, "dex", {"revamp": revamp})

    clear()
    banner()
    print("\033[38;5;141m╔═══════════════════════════════════════════════╗\033[0m")
    print("\033[38;5;141m║                DEX EXPLORER                   ║\033[0m")
    print("\033[38;5;141m╚═══════════════════════════════════════════════╝\033[0m\n")

    if result.get("success"):
        print("  \033[38;5;141m✓ DEX launched successfully!\033[0m")
        print("  \033[38;5;93m→ Check your game for DEX interface\033[0m")
    else:
        print("  \033[38;5;196m✗ Failed to launch DEX\033[0m")
        print(f"  Error: {result.get('error', 'Unknown')}")

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
        print("  \033[38;5;93m• runport\033[0m       → Connect to client")
        print("  \033[38;5;93m• hotspot\033[0m       → Top 10 largest scripts")
        print("  \033[38;5;93m• moduletracker\033[0m → List all ModuleScripts")
        print("  \033[38;5;93m• flowwatch\033[0m     → Live player game tracker")
        print("  \033[38;5;93m• buildmap\033[0m      → Full game tree (slow)")
        print("  \033[38;5;93m• dex\033[0m           → Launch Dark DEX Mobile")
        print("  \033[38;5;93m• exe\033[0m           → Execute custom script")
        print("  \033[38;5;93m• screenshot\033[0m    → Silent screenshot capture")

        print("\n  \033[38;5;135mAGENT COMMANDS:\033[0m")
        print("  \033[38;5;141m• agent\033[0m         → Setup private agent")
        print("  \033[38;5;141m• agent --list\033[0m  → List saved agents")
        print("  \033[38;5;141m• agent --starlist\033[0m → View starred agent")
        print("  \033[38;5;141m• attach\033[0m        → Attach agent to game")
        print("  \033[38;5;141m• agentstatus\033[0m   → View agent status")
        print("  \033[38;5;141m• nameagent\033[0m     → Name an agent")
        print("  \033[38;5;141m• staragent\033[0m     → Star favorite agent")

        print("\n  \033[38;5;93m• exit\033[0m          → Exit Lumen")
        print("\n  ───────────────────────────────────────────\n")

        choice = input("  Select → ").strip().lower()

        if choice == "exit":
            clear()
            print("\n  Thanks for using Lumen!")
            print("  ───────────────────────────\n")
            sys.exit(0)
        elif choice == "runport":
            cmd_runport()
        elif choice == "hotspot":
            cmd_hotspot()
        elif choice == "moduletracker":
            cmd_moduletracker()
        elif choice == "flowwatch":
            cmd_flowwatch()
        elif choice == "buildmap":
            cmd_buildmap()
        elif choice == "dex":
            cmd_dex()
        elif choice == "exe":
            cmd_exe()
        elif choice == "screenshot":
            cmd_screenshot()
        elif choice == "agent":
            cmd_agent()
        elif choice == "agent --list":
            cmd_agent_list()
        elif choice == "agent --starlist":
            cmd_agent_starlist()
        elif choice == "attach":
            cmd_attach()
        elif choice == "agentstatus":
            cmd_agent_status()
        elif choice == "nameagent":
            cmd_nameagent()
        elif choice == "staragent":
            cmd_staragent()
        else:
            print("\n  ✗ Invalid option")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  → Shutting down Lumen\n")
        sys.exit(0)
