# ============================================
# EMOTE WEB API - Backend with Web Panel
# ============================================

from flask import Flask, request, jsonify, send_from_directory, render_template_string, send_file
from flask_cors import CORS
from flask_sock import Sock
import queue
import json
import time
import asyncio
import threading
import re
import subprocess
import sys
import os
import signal
import atexit
import os
from pathlib import Path
from collections import deque
import subprocess, threading, time, random, re

COLORS = [
    "\033[91m", "\033[92m", "\033[93m",
    "\033[94m", "\033[95m", "\033[96m"
]
RESET = "\033[0m"

def animated_print(text, delay=0.05):
    for ch in text:
        print(random.choice(COLORS) + ch + RESET, end="", flush=True)
        time.sleep(delay)
    print()

def start_cloudflare(port):
    animated_print(f"\n🚀 Starting Cloudflare Tunnel on PORT {port}...\n")

    cmd = ["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{port}"]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in process.stdout:
        if "trycloudflare.com" in line:
            match = re.search(r"https://[^\s]+", line)
            if match:
                animated_print("\npublic🌍LINK.....................................................................👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉👉🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏🙏\n")
                animated_print(match.group(0), 0.03)
                break
app = Flask(__name__, static_folder='static')
CORS(app)
sock = Sock(app)

command_queue = queue.Queue()
websocket_clients = []

# Emote data - HARDCODED DIRECTLY
emote_list = []
EMOTE_LOCAL_PATH = "/storage/emulated/0/html/emote/api/emote_pngs/"
EMOTE_WEB_PATH = "/local-emotes/"

# Persistent mode state
persistent_mode_active = False
current_persistent_team = None
persistent_mode_uid = None

# Emote sending state management
is_sending_emote = False
last_emote_sent = None
current_emote_to_send = None
emote_send_lock = threading.Lock()

# ============================================
# HARDCODED EMOTE LIST
# ============================================

def initialize_emotes():
    """Initialize all emotes directly without parsing file"""
    global emote_list
    
    # Hardcoded emote list from your emote.txt
    emote_data = [
        (1, '909000001'), (2, '909000002'), (3, '909000003'), (4, '909000004'), 
        (5, '909000005'), (6, '909000006'), (7, '909000007'), (8, '909000008'), 
        (9, '909000009'), (10, '909000010'), (11, '909000011'), (12, '909000012'), 
        (13, '909000013'), (14, '909000014'), (15, '909000015'), (16, '909000016'), 
        (17, '909000017'), (18, '909000018'), (19, '909000019'), (20, '909000020'), 
        (21, '909000021'), (22, '909000022'), (23, '909000023'), (24, '909000024'), 
        (25, '909000025'), (26, '909000026'), (27, '909000027'), (28, '909000028'), 
        (29, '909000029'), (30, '909000031'), (31, '909000032'), (32, '909000033'), 
        (33, '909000034'), (34, '909000035'), (35, '909000036'), (36, '909000037'), 
        (37, '909000038'), (38, '909000039'), (39, '909000040'), (40, '909000041'), 
        (41, '909000042'), (42, '909000043'), (43, '909000044'), (44, '909000045'), 
        (45, '909000046'), (46, '909000047'), (47, '909000048'), (48, '909000049'), 
        (49, '909000051'), (50, '909000052'), (51, '909000053'), (52, '909000054'), 
        (53, '909000055'), (54, '909000056'), (55, '909000057'), (56, '909000058'), 
        (57, '909000059'), (58, '909000060'), (59, '909000061'), (60, '909000062'), 
        (61, '909000063'), (62, '909000064'), (63, '909000065'), (64, '909000066'), 
        (65, '909000067'), (66, '909000068'), (67, '909000069'), (68, '909000070'), 
        (69, '909000071'), (70, '909000072'), (71, '909000073'), (72, '909000074'), 
        (73, '909000075'), (74, '909000076'), (75, '909000077'), (76, '909000078'), 
        (77, '909000079'), (78, '909000080'), (79, '909000081'), (80, '909000082'), 
        (81, '909000083'), (82, '909000084'), (83, '909000085'), (84, '909000086'), 
        (85, '909000087'), (86, '909000088'), (87, '909000089'), (88, '909000090'), 
        (89, '909000091'), (90, '909000092'), (91, '909000093'), (92, '909000094'), 
        (93, '909000095'), (94, '909000096'), (95, '909000097'), (106, '909000108'), 
        (119, '909000121'), (120, '909000122'), (121, '909000123'), (122, '909000124'), 
        (123, '909000125'), (124, '909000126'), (125, '909000127'), (126, '909000128'), 
        (127, '909000129'), (128, '909000130'), (129, '909000131'), (130, '909000132'), 
        (131, '909000133'), (132, '909000134'), (133, '909000135'), (134, '909000136'), 
        (135, '909000137'), (136, '909000138'), (137, '909000139'), (138, '909000140'), 
        (139, '909000141'), (140, '909000142'), (142, '909000144'), (143, '909000145'), 
        (144, '909000150'), (145, '909033001'), (146, '909033002'), (147, '909033003'), 
        (148, '909033004'), (149, '909033005'), (150, '909033006'), (151, '909033007'), 
        (152, '909033008'), (153, '909033009'), (154, '909033010'), (155, '909034001'), 
        (156, '909034002'), (157, '909034003'), (158, '909034004'), (159, '909034005'), 
        (160, '909034006'), (161, '909034007'), (162, '909034008'), (163, '909034009'), 
        (164, '909034010'), (165, '909034011'), (166, '909034012'), (167, '909034013'), 
        (168, '909034014'), (169, '909035001'), (173, '909035005'), (174, '909035006'), 
        (175, '909035007'), (176, '909035008'), (177, '909035009'), (178, '909035010'), 
        (179, '909035011'), (180, '909035012'), (181, '909035013'), (182, '909035014'), 
        (183, '909035015'), (184, '909036001'), (185, '909036002'), (186, '909036003'), 
        (187, '909036004'), (188, '909036005'), (189, '909036006'), (190, '909036008'), 
        (191, '909036009'), (192, '909036010'), (193, '909036011'), (194, '909036012'), 
        (195, '909036014'), (196, '909037001'), (197, '909037002'), (198, '909037003'), 
        (199, '909037004'), (200, '909037005'), (201, '909037006'), (202, '909037007'), 
        (203, '909037008'), (204, '909037009'), (205, '909037010'), (206, '909037011'), 
        (207, '909037012'), (208, '909038001'), (210, '909038003'), (211, '909038004'), 
        (212, '909038005'), (213, '909038006'), (214, '909038008'), (215, '909038009'), 
        (216, '909038010'), (217, '909038011'), (218, '909038012'), (219, '909038013'), 
        (220, '909039001'), (221, '909039002'), (222, '909039003'), (223, '909039004'), 
        (224, '909039005'), (225, '909039006'), (226, '909039007'), (227, '909039008'), 
        (228, '909039009'), (229, '909039010'), (230, '909039011'), (231, '909039012'), 
        (232, '909039013'), (233, '909039014'), (234, '909040001'), (235, '909040002'), 
        (236, '909040003'), (237, '909040004'), (238, '909040005'), (239, '909040006'), 
        (240, '909040008'), (241, '909040009'), (242, '909040010'), (243, '909040011'), 
        (244, '909040012'), (245, '909040013'), (247, '909041001'), (248, '909041002'), 
        (249, '909041003'), (250, '909041004'), (251, '909041005'), (252, '909041006'), 
        (253, '909041007'), (254, '909041008'), (255, '909041009'), (256, '909041010'), 
        (257, '909041011'), (258, '909041012'), (259, '909041013'), (260, '909041014'), 
        (261, '909041015'), (262, '909042001'), (263, '909042002'), (264, '909042003'), 
        (265, '909042004'), (266, '909042005'), (267, '909042006'), (268, '909042007'), 
        (269, '909042008'), (270, '909042009'), (271, '909042011'), (272, '909042012'), 
        (274, '909042016'), (275, '909042017'), (276, '909042018'), (277, '909043001'), 
        (278, '909043002'), (279, '909043003'), (280, '909043004'), (281, '909043005'), 
        (282, '909043006'), (283, '909043007'), (284, '909043008'), (285, '909043009'), 
        (288, '909044001'), (289, '909044002'), (290, '909044003'), (291, '909044004'), 
        (292, '909044005'), (294, '909044007'), (295, '909044008'), (296, '909044009'), 
        (297, '909044010'), (298, '909044011'), (299, '909044012'), (300, '909044015'), 
        (301, '909044016'), (302, '909045001'), (303, '909045002'), (304, '909045003'), 
        (305, '909045004'), (306, '909045005'), (307, '909045006'), (308, '909045007'), 
        (309, '909045008'), (310, '909045009'), (311, '909045010'), (312, '909045011'), 
        (314, '909045015'), (315, '909045016'), (316, '909045017'), (317, '909046001'), 
        (318, '909046002'), (319, '909046003'), (322, '909046006'), (323, '909046007'), 
        (324, '909046008'), (325, '909046009'), (326, '909046010'), (327, '909046011'), 
        (328, '909046012'), (329, '909046013'), (330, '909046014'), (331, '909046015'), 
        (332, '909046016'), (333, '909046017'), (334, '909047001'), (337, '909047004'), 
        (338, '909047005'), (339, '909047006'), (340, '909047007'), (341, '909047008'), 
        (342, '909047009'), (343, '909047010'), (344, '909047011'), (345, '909047012'), 
        (346, '909047013'), (347, '909047015'), (348, '909047016'), (349, '909047017'), 
        (350, '909047018'), (351, '909047019'), (353, '909048002'), (354, '909048003'), 
        (355, '909048004'), (356, '909048005'), (357, '909048006'), (358, '909048007'), 
        (359, '909048008'), (361, '909048010'), (362, '909048011'), (363, '909048012'), 
        (364, '909048013'), (365, '909048014'), (366, '909048015'), (367, '909048016'), 
        (368, '909048017'), (369, '909048018'), (370, '909049001'), (371, '909049002'), 
        (372, '909049003'), (373, '909049004'), (374, '909049005'), (375, '909049006'), 
        (376, '909049007'), (378, '909049009'), (379, '909049010'), (380, '909049011'), 
        (381, '909049012'), (382, '909049013'), (383, '909049014'), (384, '909049015'), 
        (385, '909049016'), (386, '909049017'), (387, '909049018'), (388, '909049019'), 
        (389, '909049020'), (390, '909049021'), (391, '909050002'), (393, '909050004'), 
        (394, '909050005'), (395, '909050006'), (396, '909050008'), (397, '909050009'), 
        (398, '909050010'), (399, '909050011'), (400, '909050012'), (401, '909050013'), 
        (402, '909050014'), (403, '909050015'), (404, '909050016'), (405, '909050017'), 
        (406, '909050018'), (407, '909050019'), (408, '909050020'), (409, '909050021'), 
        (410, '909050026'), (411, '909050027'), (412, '909050028'), (413, '909050029'), 
        (414, '909050030'), (415, '909051001'), (416, '909051002'), (417, '909051003'), 
        (418, '909051004'), (419, '909051005'), (420, '909051006'), (421, '909051007'), 
        (422, '909051008'), (423, '909051009'), (424, '909051010'), (425, '909051011'), 
        (426, '909051012'), (427, '909051013'), (428, '909051014'), (429, '909051015'), 
        (430, '909051016'), (431, '909051017'), (432, '909051018'),  (433, '909043010')
    ]
    
    # Check if local directory exists
    local_path = Path(EMOTE_LOCAL_PATH)
    local_emotes_available = local_path.exists() and local_path.is_dir()
    
    if local_emotes_available:
        print(f"[EMOTE] Local emote directory found: {local_path}")
        # Get list of existing PNG files
        existing_files = list(local_path.glob("*.png"))
        existing_file_names = [f.stem for f in existing_files]
        print(f"[EMOTE] Found {len(existing_files)} PNG files locally")
    else:
        print(f"[EMOTE] WARNING: Local emote directory not found: {local_path}")
        existing_file_names = []
    
    emote_list.clear()
    
    for number, emote_id in emote_data:
        # Check if PNG exists locally
        has_local_png = emote_id in existing_file_names
        
        # Use local PNG if available, otherwise use CDN as fallback
        if has_local_png:
            image_url = f"{EMOTE_WEB_PATH}{emote_id}.png"
            source = "local"
        else:
            # Fallback to CDN if local file doesn't exist
            image_url = f"https://cdn.jsdelivr.net/gh/ShahGCreator/icon@main/PNG/{emote_id}.png"
            source = "cdn"
        
        emote_list.append({
            'number': number,
            'id': emote_id,
            'name': f'Emote {number}',
            'image': image_url,
            'cdn_url': f"https://cdn.jsdelivr.net/gh/ShahGCreator/icon@main/PNG/{emote_id}.png",
            'source': source,
            'has_local': has_local_png
        })
    
    # Count local vs CDN emotes
    local_count = sum(1 for emote in emote_list if emote['has_local'])
    cdn_count = len(emote_list) - local_count
    
    print(f"[EMOTE] Initialized {len(emote_list)} emotes")
    print(f"[EMOTE] Local PNGs: {local_count}, CDN fallbacks: {cdn_count}")
    
    return emote_list

# Initialize emotes on startup
initialize_emotes()

# ============================================
# SERVE LOCAL EMOTE FILES
# ============================================

@app.route('/local-emotes/<filename>')
def serve_local_emote(filename):
    """Serve emote PNG files from local directory"""
    try:
        # Security check - only allow .png files
        if not filename.endswith('.png'):
            return jsonify({'error': 'Invalid file type'}), 400
        
        file_path = Path(EMOTE_LOCAL_PATH) / filename
        
        if not file_path.exists():
            print(f"[EMOTE SERVE] File not found: {file_path}")
            # Return a placeholder image
            return send_file(
                Path(__file__).parent / 'static' / 'placeholder.png',
                mimetype='image/png'
            )
        
        print(f"[EMOTE SERVE] Serving local emote: {filename}")
        return send_file(str(file_path), mimetype='image/png')
        
    except Exception as e:
        print(f"[EMOTE SERVE ERROR] Failed to serve {filename}: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# DIRECT BOT FUNCTION CALLS
# ============================================

async def direct_join_team(teamcode, max_retries=3, timeout=5):
    """Directly join a team with retry and verification"""
    try:
        from Hexozenta_Apis import online_writer, key, iv, team_collection_active
        
        if not online_writer:
            print(f"[DIRECT JOIN] Failed - Bot not connected")
            return False
        
        if not key or not iv:
            print(f"[DIRECT JOIN] Failed - No encryption keys")
            return False
        
        print(f"[DIRECT JOIN] Attempting to join team: {teamcode}")
        
        for attempt in range(max_retries):
            try:
                from xC4 import GenJoinSquadsPacket
                
                packet = await GenJoinSquadsPacket(teamcode, key, iv)
                online_writer.write(packet)
                await online_writer.drain()
                
                print(f"[DIRECT JOIN] ✓ Join packet sent (Attempt {attempt + 1}/{max_retries})")
                
                # Wait for team to actually join
                wait_time = 0
                while wait_time < timeout * 1000:  # Convert to ms
                    await asyncio.sleep(0.1)
                    wait_time += 100
                    
                    if team_collection_active:
                        print(f"[DIRECT JOIN] ✓ Successfully joined team after {wait_time}ms")
                        return True
                
                print(f"[DIRECT JOIN] ⚠ Still not in team after {timeout}s, retrying...")
                
            except Exception as e:
                print(f"[DIRECT JOIN] ✗ Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(1)
        
        print(f"[DIRECT JOIN] ✗ Failed to join after {max_retries} attempts")
        return False
        
    except Exception as e:
        print(f"[DIRECT JOIN] ✗ Error: {e}")
        return False

async def direct_send_emote(uid, emote_code, max_retries=2):
    """Directly send emote to a player with retry"""
    try:
        from Hexozenta_Apis import online_writer, key, iv, region, team_collection_active
        from xC4 import Emote_k
        
        if not online_writer:
            print(f"[DIRECT EMOTE] Failed - Bot not connected")
            return False
        
        if not key or not iv or not region:
            print(f"[DIRECT EMOTE] Failed - Bot not ready")
            return False
        
        # Check if bot is in a team
        if not team_collection_active:
            print(f"[DIRECT EMOTE] ✗ Bot not in any team")
            return False
        
        print(f"[DIRECT EMOTE] Sending emote {emote_code} to UID {uid}")
        
        for attempt in range(max_retries):
            try:
                packet = await Emote_k(int(uid), int(emote_code), key, iv, region)
                online_writer.write(packet)
                await online_writer.drain()
                
                print(f"[DIRECT EMOTE] ✓ Emote packet sent (Attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(0.5)  # Small delay between retries if needed
                return True
                
            except Exception as e:
                print(f"[DIRECT EMOTE] ✗ Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5)
        
        print(f"[DIRECT EMOTE] ✗ Failed after {max_retries} attempts")
        return False
        
    except Exception as e:
        print(f"[DIRECT EMOTE] ✗ Error: {e}")
        return False

async def direct_leave_team():
    """Directly leave current team"""
    try:
        from Hexozenta_Apis import online_writer, key, iv
        from xC4 import ExiT
        
        if not online_writer:
            print(f"[DIRECT LEAVE] Failed - Bot not connected")
            return False
        
        print(f"[DIRECT LEAVE] Leaving team")
        
        bot_uid = 11686472351
        packet = await ExiT(bot_uid, key, iv)
        online_writer.write(packet)
        await online_writer.drain()
        
        print(f"[DIRECT LEAVE] ✓ Leave packet sent")
        await asyncio.sleep(0.5)
        return True
        
    except Exception as e:
        print(f"[DIRECT LEAVE] ✗ Error: {e}")
        return False

async def direct_join_emote_leave(teamcode, uid, emote_code, extra_teamcodes=None):
    """Directly handle join → emote → leave sequence with extra teams"""
    print(f"[DIRECT JEL] Starting: Team {teamcode} → UID {uid} → Emote {emote_code}")
    
    results = []
    
    # List of teams to process
    teams_to_process = [teamcode]
    if extra_teamcodes:
        teams_to_process.extend(extra_teamcodes)
    
    for i, current_teamcode in enumerate(teams_to_process):
        print(f"[DIRECT JEL] Processing team {i+1}/{len(teams_to_process)}: {current_teamcode}")
        
        # 1. Join team
        join_success = await direct_join_team(current_teamcode)
        if not join_success:
            results.append(f"Failed to join team {current_teamcode}")
            continue
        
        # Wait 2-3 seconds to ensure fully joined
        print(f"[DIRECT JEL] Waiting for team to stabilize...")
        await asyncio.sleep(1)
        
        # 2. Send emote
        emote_success = await direct_send_emote(uid, emote_code)
        
        if emote_success:
            results.append(f"Success in team {current_teamcode}")
        else:
            results.append(f"Emote failed in team {current_teamcode}")
        
        # 3. Leave team only if not last team
        leave_success = await direct_leave_team()
        if leave_success:
            print(f"[DIRECT JEL] Left team {current_teamcode}")
            await asyncio.sleep(1)  # Wait after leaving
    
    return results

# ============================================
# PERSISTENT MODE FUNCTIONS
# ============================================

async def persistent_join_team(teamcode, uid):
    """Join team and stay in persistent mode"""
    global persistent_mode_active, current_persistent_team, persistent_mode_uid
    
    try:
        success = await direct_join_team(teamcode)
        if success:
            persistent_mode_active = True
            current_persistent_team = teamcode
            persistent_mode_uid = uid
            print(f"[PERSISTENT] ✓ Joined team {teamcode} for UID {uid}")
            print(f"[PERSISTENT] Mode: ACTIVE (Bot will stay in team)")
            return True
        return False
    except Exception as e:
        print(f"[PERSISTENT] ✗ Error joining team: {e}")
        return False

async def persistent_send_emote(uid, emote_code):
    """Send emote in persistent mode (bot already in team)"""
    try:
        from Hexozenta_Apis import online_writer, key, iv, region, team_collection_active
        from xC4 import Emote_k
        
        if not online_writer:
            print(f"[PERSISTENT EMOTE] Failed - Bot not connected")
            return False
        
        if not key or not iv or not region:
            print(f"[PERSISTENT EMOTE] Failed - Bot not ready")
            return False
        
        # Check if bot is actually in a team
        if not team_collection_active:
            print(f"[PERSISTENT EMOTE] Bot not in any team")
            return False
        
        print(f"[PERSISTENT EMOTE] Sending emote {emote_code} to UID {uid}")
        
        packet = await Emote_k(int(uid), int(emote_code), key, iv, region)
        online_writer.write(packet)
        await online_writer.drain()
        
        print(f"[PERSISTENT EMOTE] ✓ Emote packet sent")
        await asyncio.sleep(0.3)
        return True
        
    except Exception as e:
        print(f"[PERSISTENT EMOTE] ✗ Error: {e}")
        return False

async def persistent_leave_team():
    """Leave team and exit persistent mode"""
    global persistent_mode_active, current_persistent_team, persistent_mode_uid
    
    try:
        success = await direct_leave_team()
        if success:
            persistent_mode_active = False
            current_persistent_team = None
            persistent_mode_uid = None
            print(f"[PERSISTENT] ✗ Left team and exited persistent mode")
            return True
        return False
    except Exception as e:
        print(f"[PERSISTENT] ✗ Error leaving team: {e}")
        return False

# ============================================
# LOCKED EMOTE SENDING FUNCTIONS
# ============================================

async def send_emote_with_lock(uid, emote_code, mode='normal', teamcode=None):
    """Send emote with locking to prevent duplicates and race conditions"""
    global is_sending_emote, last_emote_sent, current_emote_to_send
    
    with emote_send_lock:
        if is_sending_emote:
            print(f"[EMOTE LOCK] Already sending emote, skipping duplicate")
            return False
        
        is_sending_emote = True
        current_emote_to_send = emote_code
    
    try:
        print(f"[EMOTE LOCK] Starting send: {emote_code} to {uid} (mode: {mode})")
        
        success = False
        if mode == 'persistent':
            success = await persistent_send_emote(uid, emote_code)
        elif mode == 'normal' and teamcode:
            # Use direct mode with team join
            success = await direct_send_emote(uid, emote_code)
            if success:
                await asyncio.sleep(0.5)
                await direct_leave_team()
        else:
            success = await direct_send_emote(uid, emote_code)
        
        if success:
            last_emote_sent = emote_code
            print(f"[EMOTE LOCK] ✓ Emote {emote_code} sent successfully")
        else:
            print(f"[EMOTE LOCK] ✗ Failed to send emote {emote_code}")
        
        return success
        
    except Exception as e:
        print(f"[EMOTE LOCK] ✗ Error: {e}")
        return False
    finally:
        with emote_send_lock:
            is_sending_emote = False
            current_emote_to_send = None

# ============================================
# STATIC FILE ROUTES
# ============================================

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# Create static folder if it doesn't exist
if not os.path.exists('static'):
    os.makedirs('static')

# ============================================
# WEB PANEL ROUTES
# ============================================

@app.route('/')
@app.route('/panel')
def web_panel():
    """Serve the main web panel"""
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>😈 RAVI-VIP EMOTE PANEL- Gaming Emote Panel</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            * { 
                margin: 0; 
                padding: 0; 
                box-sizing: border-box; 
            }
            
            :root {
                --primary: #00ffff;
                --secondary: #ff00ff;
                --accent: #ffd700;
                --dark: #0a0a0a;
                --darker: #050505;
                --light: #ffffff;
                --gray: #888;
                --success: #00ff00;
                --error: #ff5555;
                --warning: #ffd700;
                --card-bg: rgba(20, 20, 30, 0.9);
                --border: rgba(0, 255, 255, 0.3);
                --shadow: rgba(0, 255, 255, 0.2);
                --local-badge: #4CAF50;
                --cdn-badge: #FF9800;
            }
            
            body {
                font-family: 'Segoe UI', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, var(--darker) 0%, #1a1a2e 100%);
                color: var(--light);
                min-height: 100vh;
                overflow-x: hidden;
            }
            
            /* Particle Background */
            #particles-js {
                position: fixed;
                width: 100%;
                height: 100%;
                z-index: -1;
            }
            
            /* Main Dashboard */
            .dashboard {
                padding: 20px;
                max-width: 1600px;
                margin: 0 auto;
            }
            
            /* Header */
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px;
                background: var(--card-bg);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                margin-bottom: 30px;
                border: 1px solid var(--border);
                box-shadow: 0 10px 30px var(--shadow);
            }
            
            .logo {
                display: flex;
                align-items: center;
                gap: 15px;
            }
            
            .logo-icon {
                font-size: 2.5rem;
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
            }
            
            .logo-text {
                font-size: 2rem;
                font-weight: 800;
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
                text-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
            }
            
            .status-badge {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 8px 15px;
                background: rgba(0, 255, 255, 0.1);
                border: 1px solid var(--border);
                border-radius: 10px;
                font-size: 0.9rem;
            }
            
            .status-dot {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: var(--success);
                box-shadow: 0 0 10px var(--success);
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            /* Main Grid Layout */
            .main-grid {
                display: grid;
                grid-template-columns: 1fr 2fr;
                gap: 30px;
                margin-bottom: 30px;
            }
            
            @media (max-width: 1200px) {
                .main-grid {
                    grid-template-columns: 1fr;
                }
            }
            
            /* Control Panels */
            .panel {
                background: var(--card-bg);
                backdrop-filter: blur(10px);
                border: 1px solid var(--border);
                border-radius: 20px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px var(--shadow);
            }
            
            .panel-header {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 25px;
                padding-bottom: 15px;
                border-bottom: 1px solid var(--border);
            }
            
            .panel-icon {
                font-size: 1.5rem;
                color: var(--primary);
            }
            
            .panel-title {
                font-size: 1.3rem;
                font-weight: 600;
                color: var(--light);
            }
            
            /* Input Groups */
            .input-group {
                margin-bottom: 20px;
            }
            
            .input-label {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 8px;
                color: var(--primary);
                font-weight: 600;
                font-size: 0.95rem;
            }
            
            .input-label i {
                font-size: 0.9rem;
            }
            
            .input-field {
                width: 100%;
                padding: 14px;
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid var(--border);
                border-radius: 12px;
                color: var(--light);
                font-size: 1rem;
                transition: all 0.3s ease;
            }
            
            .input-field:focus {
                outline: none;
                border-color: var(--primary);
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
                background: rgba(255, 255, 255, 0.08);
            }
            
            .input-field::placeholder {
                color: var(--gray);
            }
            
            /* Buttons */
            .btn {
                width: 100%;
                padding: 15px;
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                border: none;
                border-radius: 12px;
                color: var(--darker);
                font-size: 1.1rem;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                margin-top: 10px;
            }
            
            .btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 15px 30px rgba(0, 255, 255, 0.4);
            }
            
            .btn:active {
                transform: translateY(0);
            }
            
            .btn-secondary {
                background: rgba(255, 215, 0, 0.2);
                color: var(--accent);
                border: 1px solid rgba(255, 215, 0, 0.3);
            }
            
            .btn-secondary:hover {
                background: rgba(255, 215, 0, 0.3);
                box-shadow: 0 15px 30px rgba(255, 215, 0, 0.3);
            }
            
            .btn-danger {
                background: rgba(255, 85, 85, 0.2);
                color: var(--error);
                border: 1px solid rgba(255, 85, 85, 0.3);
            }
            
            .btn-danger:hover {
                background: rgba(255, 85, 85, 0.3);
                box-shadow: 0 15px 30px rgba(255, 85, 85, 0.3);
            }
            
            .btn-small {
                padding: 8px 15px;
                font-size: 0.9rem;
                width: auto;
            }
            
            .btn-group {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-top: 20px;
            }
            
            /* Stats Panel */
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin-bottom: 30px;
            }
            
            @media (max-width: 768px) {
                .stats-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
            
            .stat-card {
                background: var(--card-bg);
                backdrop-filter: blur(10px);
                border: 1px solid var(--border);
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                transition: transform 0.3s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
            }
            
            .stat-value {
                font-size: 2.5rem;
                font-weight: 800;
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
                line-height: 1;
                margin-bottom: 5px;
            }
            
            .stat-label {
                font-size: 0.9rem;
                color: var(--gray);
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .stat-icon {
                font-size: 2rem;
                margin-bottom: 10px;
                opacity: 0.7;
            }
            
            /* Emote Grid */
            .emote-grid-container {
                background: var(--card-bg);
                backdrop-filter: blur(10px);
                border: 1px solid var(--border);
                border-radius: 20px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px var(--shadow);
            }
            
            .search-box {
                margin-bottom: 25px;
            }
            
            .search-input {
                width: 100%;
                padding: 14px 20px 14px 50px;
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid var(--border);
                border-radius: 12px;
                color: var(--light);
                font-size: 1rem;
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%2300ffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'%3E%3C/circle%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'%3E%3C/line%3E%3C/svg%3E");
                background-repeat: no-repeat;
                background-position: 20px center;
                background-size: 20px;
            }
            
            .search-input:focus {
                outline: none;
                border-color: var(--primary);
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
            }
            
            .emote-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
                gap: 20px;
            }
            
            @media (max-width: 768px) {
                .emote-grid {
                    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                }
            }
            
            .emote-card {
                background: rgba(30, 30, 40, 0.9);
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 2px solid transparent;
                position: relative;
                overflow: hidden;
                user-select: none;
            }
            
            .emote-card:hover {
                transform: translateY(-10px) scale(1.05);
                border-color: var(--primary);
                box-shadow: 0 15px 35px rgba(0, 255, 255, 0.3);
            }
            
            .emote-card.persistent {
                border-color: var(--accent);
                background: rgba(255, 215, 0, 0.05);
            }
            
            .emote-card.disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none !important;
            }
            
            .emote-badge {
                position: absolute;
                top: 10px;
                left: 10px;
                background: rgba(0, 0, 0, 0.8);
                color: var(--light);
                padding: 4px 10px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
                z-index: 2;
            }
            
            .emote-persistent-badge {
                position: absolute;
                top: 10px;
                right: 10px;
                background: rgba(255, 215, 0, 0.9);
                color: var(--darker);
                padding: 4px 8px;
                border-radius: 20px;
                font-size: 0.7rem;
                font-weight: 700;
                z-index: 2;
            }
            
            .emote-source-badge {
                position: absolute;
                bottom: 10px;
                left: 10px;
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 0.6rem;
                font-weight: 700;
                z-index: 2;
            }
            
            .source-local {
                background: var(--local-badge);
                color: white;
            }
            
            .source-cdn {
                background: var(--cdn-badge);
                color: black;
            }
            
            .emote-image {
                width: 120px;
                height: 120px;
                object-fit: contain;
                margin-bottom: 15px;
                border-radius: 10px;
                background: rgba(0, 0, 0, 0.3);
                padding: 10px;
                transition: transform 0.3s ease;
            }
            
            .emote-card:hover .emote-image {
                transform: scale(1.1);
            }
            
            .emote-name {
                font-size: 0.9rem;
                color: var(--gray);
                margin-bottom: 5px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            
            .emote-id {
                font-size: 0.85rem;
                color: var(--primary);
                font-weight: 600;
                font-family: monospace;
                background: rgba(0, 255, 255, 0.1);
                padding: 4px 8px;
                border-radius: 6px;
                display: inline-block;
            }
            
            /* Toast Notifications */
            .toast-container {
                position: fixed;
                top: 30px;
                right: 30px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            
            .toast {
                padding: 18px 25px;
                background: var(--card-bg);
                border-left: 5px solid var(--primary);
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(10px);
                transform: translateX(400px);
                transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
                min-width: 300px;
                max-width: 400px;
            }
            
            .toast.show {
                transform: translateX(0);
            }
            
            .toast.success {
                border-left-color: var(--success);
            }
            
            .toast.error {
                border-left-color: var(--error);
            }
            
            .toast.warning {
                border-left-color: var(--warning);
            }
            
            .toast-header {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 8px;
            }
            
            .toast-icon {
                font-size: 1.2rem;
            }
            
            .toast-title {
                font-weight: 600;
                font-size: 1rem;
            }
            
            .toast-message {
                font-size: 0.9rem;
                color: var(--gray);
                line-height: 1.4;
            }
            
            /* Loading Overlay */
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.9);
                z-index: 99999;
                display: none;
                justify-content: center;
                align-items: center;
                flex-direction: column;
                backdrop-filter: blur(5px);
            }
            
            .loading-spinner {
                width: 70px;
                height: 70px;
                border: 5px solid rgba(0, 255, 255, 0.3);
                border-top-color: var(--primary);
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 25px;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            .loading-text {
                font-size: 1.2rem;
                color: var(--primary);
                font-weight: 600;
            }
            
            /* Mode Toggle */
            .mode-toggle {
                display: flex;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 5px;
                margin-bottom: 25px;
            }
            
            .mode-btn {
                flex: 1;
                padding: 12px;
                text-align: center;
                cursor: pointer;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            .mode-btn.active {
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                color: var(--darker);
                box-shadow: 0 5px 15px var(--shadow);
            }
            

            
            /* Scroll to Top */
            .scroll-top {
                position: fixed;
                bottom: 30px;
                right: 30px;
                width: 50px;
                height: 50px;
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                border: none;
                border-radius: 50%;
                color: var(--darker);
                font-size: 1.2rem;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transform: translateY(20px);
                transition: all 0.3s ease;
                z-index: 100;
                box-shadow: 0 5px 20px rgba(0, 255, 255, 0.3);
            }
            
            .scroll-top.show {
                opacity: 1;
                transform: translateY(0);
            }
            
            .scroll-top:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(0, 255, 255, 0.5);
            }
            
            /* Click Animation */
            .click-animation {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: rgba(0, 255, 255, 0.3);
                animation: clickPulse 0.6s ease-out;
                pointer-events: none;
                z-index: 1;
            }
            
            @keyframes clickPulse {
                0% { transform: translate(-50%, -50%) scale(0); opacity: 1; }
                100% { transform: translate(-50%, -50%) scale(2); opacity: 0; }
            }
        </style>
        <!-- Particles.js -->
        <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    </head>
    <body>
        <!-- Particle Background -->
        <div id="particles-js"></div>
        
        <!-- Toast Container -->
        <div class="toast-container" id="toastContainer"></div>
        
        <!-- Loading Overlay -->
        <div class="loading-overlay" id="loadingOverlay">
            <div class="loading-spinner"></div>
            <div class="loading-text" id="loadingText">Sending emote...</div>
        </div>
        
        <!-- Main Dashboard -->
        <div class="dashboard">
            <!-- Header -->
            <div class="header">
                <div class="logo">
                    <div class="logo-icon">👑</div>
                    <div class="logo-text">RAVI-EMOTE WEB</div>
                </div>
                <div class="status-badge">
                    <div class="status-dot"></div>
                    <span>Bot Status: <strong>Connected</strong></span>
                </div>
            </div>
            
            <!-- Stats -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-value" id="totalEmotes">0</div>
                    <div class="stat-label">Total Emotes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⚡</div>
                    <div class="stat-value" id="lastSent">--</div>
                    <div class="stat-label">Last Sent</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">💾</div>
                    <div class="stat-value" id="localEmotes">0</div>
                    <div class="stat-label">Local PNGs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🌐</div>
                    <div class="stat-value" id="cdnEmotes">0</div>
                    <div class="stat-label">CDN Fallbacks</div>
                </div>
            </div>
            
            <div class="main-grid">
                <!-- Left Column: Controls -->
                <div class="left-column">
                    <!-- Mode Selection -->
                    <div class="panel">
                        <div class="panel-header">
                            <div class="panel-icon">🎯</div>
                            <div class="panel-title">Sending Mode</div>
                        </div>
                        
                        <div class="mode-toggle">
                            <div class="mode-btn active" id="normalModeBtn" onclick="setMode('normal')">
                                <i class="fas fa-exchange-alt"></i> Normal Mode
                            </div>
                            <div class="mode-btn" id="persistentModeBtn" onclick="setMode('persistent')">
                                <i class="fas fa-bolt"></i> Persistent Mode
                            </div>
                        </div>
                        
                        <div class="mode-description" id="modeDescription">
                            <p style="color: var(--gray); font-size: 0.9rem; margin-top: 10px;">
                                <i class="fas fa-info-circle"></i> 
                                <span id="modeDescText">Bot joins → sends emote → leaves team</span>
                            </p>
                        </div>
                    </div>
                    
                    <!-- Send Controls -->
                    <div class="panel">
                        <div class="panel-header">
                            <div class="panel-icon">🚀</div>
                            <div class="panel-title">Send Emote</div>
                        </div>
                        
                        <div class="input-group">
                            <label class="input-label">
                                <i class="fas fa-users"></i> Team Code
                            </label>
                            <input type="text" class="input-field" id="teamCode" placeholder="Enter team code (e.g., 6029711)">
                        </div>
                        
                        <div class="input-group">
                            <label class="input-label">
                                <i class="fas fa-user"></i> Player UID
                            </label>
                            <input type="text" class="input-field" id="uid" placeholder="Enter player UID (RAVI )">
                        </div>
                        
                        <div class="input-group">
                            <label class="input-label">
                                <i class="fas fa-icons"></i> Emote ID (Optional)
                            </label>
                            <input type="text" class="input-field" id="emoteId" placeholder="Enter emote ID (RAVI)">
                        </div>
                        
                        <button class="btn" onclick="sendManualEmote()">
                            <i class="fas fa-paper-plane"></i> EMOTE SENDING..
                        </button>
                        
                        <div class="btn-group">

                        </div>
                    </div>
                    

                </div>
                
                <!-- Right Column: Emote Grid -->
                <div class="right-column">
                    <div class="emote-grid-container">
                        <div class="panel-header">
                            <div class="panel-icon">🎭</div>
                            <div class="panel-title">Emote Library <span style="font-size: 0.9rem; color: var(--gray); margin-left: 10px;">(433 emotes loaded)</span></div>
                        </div>
                        
                        <div class="search-box">
                            <input type="text" class="search-input" id="searchInput" 
                                   placeholder="Search 433 emotes by number or ID...">
                        </div>
                        
                        <div class="emote-grid" id="emoteGrid">
                            <!-- Emotes will be loaded here -->
                            <div style="grid-column: 1 / -1; text-align: center; padding: 60px; color: var(--gray);">
                                <i class="fas fa-spinner fa-spin" style="font-size: 2rem; margin-bottom: 20px;"></i>
                                <div>Loading 433 emotes...</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Scroll to Top Button -->
        <div class="scroll-top" id="scrollTop" onclick="scrollToTop()">
            <i class="fas fa-arrow-up"></i>
        </div>
        <!-- Scroll to Bottom Button -->
        <div class="scroll-bottom" id="scrollBottom" onclick="scrollToBottom()">
            <i class="fas fa-arrow-down"></i>
        </div>
        <!-- Sound Effects (optional) -->
        <audio id="clickSound" preload="auto">
            <source src="https://assets.mixkit.co/sfx/preview/mixkit-select-click-1109.mp3" type="audio/mpeg">
        </audio>
        <audio id="successSound" preload="auto">
            <source src="https://assets.mixkit.co/sfx/preview/mixkit-winning-chimes-2015.mp3" type="audio/mpeg">
        </audio>
        
        <script>
            // Global State
            let allEmotes = [];
            let displayedEmotes = [];
            let loadedImagesCount = 0;
            let localEmotesCount = 0;
            let cdnEmotesCount = 0;
            let currentMode = 'normal'; // 'normal' or 'persistent'
            let isProcessingClick = false;
            let lastClickTime = 0;
            const CLICK_DEBOUNCE_MS = 1500;
            
            // Initialize particles
            particlesJS('particles-js', {
                particles: {
                    number: { value: 100, density: { enable: true, value_area: 1000 } },
                    color: { value: "#00ffff" },
                    shape: { type: "circle" },
                    opacity: { value: 0.5, random: true },
                    size: { value: 3, random: true },
                    line_linked: {
                        enable: true,
                        distance: 150,
                        color: "#ff00ff",
                        opacity: 0.4,
                        width: 1
                    },
                    move: {
                        enable: true,
                        speed: 2,
                        direction: "none",
                        random: true,
                        straight: false,
                        out_mode: "out",
                        bounce: false
                    }
                },
                interactivity: {
                    detect_on: "canvas",
                    events: {
                        onhover: { enable: true, mode: "repulse" },
                        onclick: { enable: true, mode: "push" }
                    }
                },
                retina_detect: true
            });
            
            // Show toast notification
            function showToast(title, message, type = 'info') {
                const container = document.getElementById('toastContainer');
                const icons = {
                    info: 'ℹ️',
                    success: '✅',
                    error: '❌',
                    warning: '⚠️'
                };
                
                const toast = document.createElement('div');
                toast.className = `toast ${type}`;
                toast.innerHTML = `
                    <div class="toast-header">
                        <div class="toast-icon">${icons[type] || icons.info}</div>
                        <div class="toast-title">${title}</div>
                    </div>
                    <div class="toast-message">${message}</div>
                `;
                
                container.appendChild(toast);
                
                // Show toast
                setTimeout(() => toast.classList.add('show'), 10);
                
                // Remove after delay
                setTimeout(() => {
                    toast.classList.remove('show');
                    setTimeout(() => {
                        if (container.contains(toast)) {
                            container.removeChild(toast);
                        }
                    }, 400);
                }, 4000);
            }
            
            // Play sound
            function playSound(soundId) {
                try {
                    const sound = document.getElementById(soundId);
                    if (sound) {
                        sound.currentTime = 0;
                        sound.play();
                    }
                } catch (e) {
                    console.log("Sound play failed:", e);
                }
            }
            
            // Set mode (normal/persistent)
            function setMode(mode) {
                currentMode = mode;
                
                // Update button states
                document.getElementById('normalModeBtn').classList.toggle('active', mode === 'normal');
                document.getElementById('persistentModeBtn').classList.toggle('active', mode === 'persistent');
                
                // Update description
                const descText = document.getElementById('modeDescText');
                if (mode === 'normal') {
                    descText.textContent = 'Bot joins → sends emote → leaves team';
                    showToast('Mode Changed', 'Normal Mode activated', 'info');
                } else {
                    descText.textContent = 'Bot stays in team for instant emote sending';
                    showToast('Mode Changed', 'Persistent Mode activated', 'warning');
                }
                
                // Update emote cards
                updateEmoteCardsMode();
            }
            
            // Update emote cards for current mode
            function updateEmoteCardsMode() {
                const cards = document.querySelectorAll('.emote-card');
                cards.forEach(card => {
                    if (currentMode === 'persistent') {
                        card.classList.add('persistent');
                    } else {
                        card.classList.remove('persistent');
                    }
                });
            }
            
            // Load emotes from API
            async function loadEmotes() {
                try {
                    const response = await fetch('/api/emotes');
                    allEmotes = await response.json();
                    displayedEmotes = [...allEmotes];
                    
                    // Count local vs CDN emotes
                    localEmotesCount = allEmotes.filter(e => e.source === 'local').length;
                    cdnEmotesCount = allEmotes.filter(e => e.source === 'cdn').length;
                    
                    // Update stats
                    document.getElementById('totalEmotes').textContent = allEmotes.length;
                    document.getElementById('localEmotes').textContent = localEmotesCount;
                    document.getElementById('cdnEmotes').textContent = cdnEmotesCount;
                    
                    renderEmotes();
                    
                    if (localEmotesCount > 0) {
                        showToast('Emotes Loaded', `${allEmotes.length} emotes loaded (${localEmotesCount} local)`, 'success');
                    } else {
                        showToast('Emotes Loaded', `${allEmotes.length} emotes loaded from CDN`, 'warning');
                    }
                    
                } catch (error) {
                    console.error('Failed to load emotes:', error);
                    showToast('Error', 'Failed to load emotes', 'error');
                }
            }
            
            // Search emotes
            function searchEmotes() {
                const searchTerm = document.getElementById('searchInput').value.toLowerCase();
                
                if (searchTerm === '') {
                    displayedEmotes = [...allEmotes];
                } else {
                    displayedEmotes = allEmotes.filter(emote => 
                        emote.number.toString().includes(searchTerm) || 
                        emote.id.includes(searchTerm)
                    );
                }
                
                renderEmotes();
            }
            
            // Clear search
            function clearSearch() {
                document.getElementById('searchInput').value = '';
                searchEmotes();
                playSound('clickSound');
                showToast('Search Cleared', 'Showing all emotes', 'info');
            }
            
            // Render emotes to grid
            function renderEmotes() {
                const grid = document.getElementById('emoteGrid');
                
                if (displayedEmotes.length === 0) {
                    grid.innerHTML = `
                        <div style="grid-column: 1 / -1; text-align: center; padding: 60px; color: var(--gray);">
                            <i class="fas fa-search" style="font-size: 2rem; margin-bottom: 20px;"></i>
                            <div>No emotes found</div>
                            <button class="quick-btn" onclick="clearSearch()" style="margin-top: 20px;">
                                <i class="fas fa-times"></i> Clear Search
                            </button>
                        </div>
                    `;
                    return;
                }
                
                // Reset image counter
                loadedImagesCount = 0;
                
                let html = '';
                displayedEmotes.forEach(emote => {
                    const persistentBadge = currentMode === 'persistent' 
                        ? '<div class="emote-persistent-badge">⚡</div>' 
                        : '';
                    
                    const sourceBadge = emote.source === 'local' 
                        ? '<div class="emote-source-badge source-local">Hexozenta_Apis</div>'
                        : '<div class="emote-source-badge source-cdn">CDN</div>';
                    
                    html += `
                    <div class="emote-card ${currentMode === 'persistent' ? 'persistent' : ''}" 
                         data-emote-id="${emote.id}" 
                         onclick="handleEmoteClick('${emote.id}')">
                        ${persistentBadge}
                        ${sourceBadge}
                        <div class="emote-badge">#${emote.number}</div>
                        <img class="emote-image" 
                             src="${emote.image}" 
                             alt="Emote ${emote.number}" 
                             loading="lazy"
                             onload="imageLoaded()"
                             onerror="imageError(this, '${emote.id}')">
                        <div class="emote-name">Emote #${emote.number}</div>
                        <div class="emote-id">${emote.id}</div>
                    </div>
                    `;
                });
                
                grid.innerHTML = html;
                updateImageCount();
            }
            
            // Show click animation
            function showClickAnimation(element) {
                const animation = document.createElement('div');
                animation.className = 'click-animation';
                element.appendChild(animation);
                
                setTimeout(() => {
                    if (element.contains(animation)) {
                        element.removeChild(animation);
                    }
                }, 600);
            }
            
            // Handle emote click
            function handleEmoteClick(emoteId) {
                // Debounce check
                const now = Date.now();
                if (isProcessingClick || (now - lastClickTime < CLICK_DEBOUNCE_MS)) {
                    showToast('Wait', 'Please wait before clicking again', 'warning');
                    return;
                }
                
                // Show visual feedback
                showClickAnimation(event.currentTarget);
                playSound('clickSound');
                
                // Call appropriate function
                if (currentMode === 'persistent') {
                    sendPersistentEmote(emoteId);
                } else {
                    sendNormalEmote(emoteId);
                }
            }
            
            // Send normal emote
            async function sendNormalEmote(emoteId) {
                const teamCode = document.getElementById('teamCode').value;
                const uid = document.getElementById('uid').value;
                
                if (!teamCode || !uid) {
                    showToast('Error', 'Please enter Team Code and UID', 'error');
                    return;
                }
                
                // Update state
                isProcessingClick = true;
                lastClickTime = Date.now();
                
                // Show loading
                document.getElementById('loadingText').textContent = 'Sending emote...';
                document.getElementById('loadingOverlay').style.display = 'flex';
                
                try {
                    const response = await fetch(`/api/send-locked?teamcode=${teamCode}&uid=${uid}&emote_id=${emoteId}&mode=normal`);
                    const data = await response.json();
                    
                    if (data.success) {
                        document.getElementById('lastSent').textContent = emoteId;
                        showToast('Success', `Emote ${emoteId} sent successfully!`, 'success');
                        playSound('successSound');
                    } else {
                        showToast('Error', `Failed: ${data.message}`, 'error');
                    }
                } catch (error) {
                    showToast('Error', `Network error: ${error.message}`, 'error');
                } finally {
                    document.getElementById('loadingOverlay').style.display = 'none';
                    setTimeout(() => { isProcessingClick = false; }, 500);
                }
            }
            
            // Send persistent emote
            async function sendPersistentEmote(emoteId) {
                const teamCode = document.getElementById('teamCode').value;
                const uid = document.getElementById('uid').value;
                
                if (!teamCode || !uid) {
                    showToast('Error', 'Please enter Team Code and UID', 'error');
                    return;
                }
                
                // First, check if we need to join team
                try {
                    const statusResponse = await fetch('/api/persistent/status');
                    const status = await statusResponse.json();
                    
                    if (!status.active || status.team !== teamCode || status.uid !== uid) {
                        // Need to join first
                        document.getElementById('loadingText').textContent = 'Joining team...';
                        document.getElementById('loadingOverlay').style.display = 'flex';
                        
                        const joinResponse = await fetch(`/api/persistent/join?teamcode=${teamCode}&uid=${uid}`);
                        const joinData = await joinResponse.json();
                        
                        if (!joinData.success) {
                            showToast('Error', `Failed to join team: ${joinData.message}`, 'error');
                            document.getElementById('loadingOverlay').style.display = 'none';
                            return;
                        }
                    }
                    
                    // Now send the emote
                    document.getElementById('loadingText').textContent = 'Sending emote...';
                    
                    const emoteResponse = await fetch(`/api/persistent/emote?uid=${uid}&emote_id=${emoteId}`);
                    const emoteData = await emoteResponse.json();
                    
                    if (emoteData.success) {
                        document.getElementById('lastSent').textContent = emoteId + ' (P)';
                        showToast('Success', `Emote sent in Persistent Mode!`, 'success');
                        playSound('successSound');
                    } else {
                        showToast('Error', `Failed to send emote: ${emoteData.message}`, 'error');
                    }
                    
                } catch (error) {
                    showToast('Error', `Network error: ${error.message}`, 'error');
                } finally {
                    document.getElementById('loadingOverlay').style.display = 'none';
                    isProcessingClick = false;
                }
            }
            
            // Send manual emote
            async function sendManualEmote() {
                playSound('clickSound');
                
                const teamCode = document.getElementById('teamCode').value;
                const uid = document.getElementById('uid').value;
                const emoteId = document.getElementById('emoteId').value;
                
                if (!teamCode || !uid) {
                    showToast('Error', 'Please enter Team Code and UID', 'error');
                    return;
                }
                
                if (!emoteId) {
                    showToast('Error', 'Please enter an Emote ID', 'error');
                    return;
                }
                
                if (currentMode === 'persistent') {
                    await sendPersistentEmote(emoteId);
                } else {
                    await sendNormalEmote(emoteId);
                }
            }
            
            // Quick join persistent
            async function quickJoinPersistent() {
                const teamCode = document.getElementById('teamCode').value;
                const uid = document.getElementById('uid').value;
                
                if (!teamCode || !uid) {
                    showToast('Error', 'Please enter Team Code and UID first', 'error');
                    return;
                }
                
                setMode('persistent');
                
                document.getElementById('loadingText').textContent = 'Joining team (Persistent Mode)...';
                document.getElementById('loadingOverlay').style.display = 'flex';
                
                try {
                    const response = await fetch(`/api/persistent/join?teamcode=${teamCode}&uid=${uid}`);
                    const data = await response.json();
                    
                    if (data.success) {
                        showToast('Success', 'Persistent Mode activated! Bot joined team.', 'success');
                        playSound('successSound');
                    } else {
                        showToast('Error', `Failed: ${data.message}`, 'error');
                    }
                } catch (error) {
                    showToast('Error', `Network error: ${error.message}`, 'error');
                } finally {
                    document.getElementById('loadingOverlay').style.display = 'none';
                }
            }
            
            // Leave team
            async function leaveTeam() {
                playSound('clickSound');
                
                document.getElementById('loadingText').textContent = 'Leaving team...';
                document.getElementById('loadingOverlay').style.display = 'flex';
                
                try {
                    const response = await fetch('/api/persistent/leave');
                    const data = await response.json();
                    
                    if (data.success) {
                        showToast('Success', 'Bot left the team', 'success');
                    } else {
                        showToast('Error', `Failed: ${data.message}`, 'error');
                    }
                } catch (error) {
                    showToast('Error', `Network error: ${error.message}`, 'error');
                } finally {
                    document.getElementById('loadingOverlay').style.display = 'none';
                }
            }

            

            
            // Image loaded callback
            function imageLoaded() {
                loadedImagesCount++;
                updateImageCount();
            }
            
            // Image error callback
            function imageError(img, emoteId) {
                console.log(`Failed to load image for emote ${emoteId}`);
                
                // Try to load from CDN as fallback
                if (img.src.includes('/local-emotes/')) {
                    img.src = `https://cdn.jsdelivr.net/gh/ShahGCreator/icon@main/PNG/${emoteId}.png`;
                } else {
                    // Final fallback - show placeholder
                    img.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120"><rect width="120" height="120" fill="%23222233"/><text x="60" y="60" font-family="Arial" font-size="10" fill="%2300ffff" text-anchor="middle" dy=".3em">' + emoteId + '</text></svg>';
                }
                
                imageLoaded(); // Count it anyway
            }
            
            // Update image count
            function updateImageCount() {
                document.getElementById('loadedImages').textContent = loadedImagesCount;
            }
            
            // Scroll to top
            function scrollToTop() {
                window.scrollTo({ top: 0, behavior: 'smooth' });
                playSound('clickSound');
            }
            
            // Show/hide scroll to top button
            window.addEventListener('scroll', function() {
                const scrollTop = document.getElementById('scrollTop');
                if (window.scrollY > 300) {
                    scrollTop.classList.add('show');
                } else {
                    scrollTop.classList.remove('show');
                }
            });
            
            // Search on input
            document.getElementById('searchInput').addEventListener('input', searchEmotes);
            
            // Enter key for inputs
            document.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.target.classList.contains('input-field')) {
                    sendManualEmote();
                }
            });
            
            // Initialize on load
            window.addEventListener('load', function() {
                loadEmotes();
                
                // Check persistent status
                fetch('/api/persistent/status')
                    .then(res => res.json())
                    .then(status => {
                        if (status.active) {
                            document.getElementById('teamCode').value = status.team || '';
                            document.getElementById('uid').value = status.uid || '';
                            setMode('persistent');
                            showToast('Status', 'Persistent mode is active', 'warning');
                        }
                    })
                    .catch(console.error);
                
                showToast('Welcome', 'Emote Web Panel Ready!', 'success');
            });
        </script>
    </body>
    </html>
    '''
    return html

# ============================================
# NEW API ENDPOINTS WITH LOCKING
# ============================================

@app.route('/api/send-locked', methods=['GET'])
def api_send_locked():
    """Send emote with locking mechanism"""
    try:
        uid = request.args.get('uid')
        emote_code = request.args.get('emote_id')
        mode = request.args.get('mode', 'normal')
        teamcode = request.args.get('teamcode')
        
        if not uid or not emote_code:
            return jsonify({
                'success': False,
                'message': 'Missing uid or emote_id'
            }), 400
        
        if mode == 'normal' and not teamcode:
            return jsonify({
                'success': False,
                'message': 'Missing teamcode for normal mode'
            }), 400
        
        def run_async_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    
            if mode == 'persistent':
                success = loop.run_until_complete(send_emote_with_lock(uid, emote_code, 'persistent'))
            else:
                # For normal mode, we need to join team first
                success = loop.run_until_complete(direct_join_team(teamcode))
                if success:
                    loop.run_until_complete(asyncio.sleep(2))
                    success = loop.run_until_complete(send_emote_with_lock(uid, emote_code, 'normal'))
                    # Leave team after sending
                    loop.run_until_complete(direct_leave_team())
    
            loop.close()
            return success
        
        # Run in background thread
        task_thread = threading.Thread(target=run_async_task, daemon=True)
        task_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Emote process started with locking',
            'mode': mode,
            'emote': emote_code,
            'uid': uid
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ============================================
# PERSISTENT MODE API ENDPOINTS
# ============================================

@app.route('/api/persistent/join', methods=['GET'])
def api_persistent_join():
    """Join team and activate persistent mode"""
    try:
        teamcode = request.args.get('teamcode')
        uid = request.args.get('uid')
        
        if not teamcode or not uid:
            return jsonify({
                'success': False,
                'message': 'Missing teamcode or uid'
            }), 400
        
        def run_async_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(persistent_join_team(teamcode, uid))
            loop.close()
            return success
        
        task_thread = threading.Thread(target=run_async_task, daemon=True)
        task_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Persistent mode activated',
            'team': teamcode,
            'uid': uid,
            'info': 'Bot joined team and will stay. Send emotes instantly!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/persistent/emote', methods=['GET'])
def api_persistent_emote():
    """Send emote in persistent mode"""
    try:
        uid = request.args.get('uid')
        emote_code = request.args.get('emote_id')
        
        if not uid or not emote_code:
            return jsonify({
                'success': False,
                'message': 'Missing uid or emote_id'
            }), 400
        
        def run_async_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(send_emote_with_lock(uid, emote_code, 'persistent'))
            loop.close()
            return success
        
        task_thread = threading.Thread(target=run_async_task, daemon=True)
        task_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Emote sent in persistent mode',
            'uid': uid,
            'emote_code': emote_code,
            'mode': 'persistent'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/persistent/leave', methods=['GET'])
def api_persistent_leave():
    """Leave team and deactivate persistent mode"""
    try:
        def run_async_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(persistent_leave_team())
            loop.close()
            return success
        
        task_thread = threading.Thread(target=run_async_task, daemon=True)
        task_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Persistent mode deactivated',
            'info': 'Bot left the team'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/persistent/status', methods=['GET'])
def api_persistent_status():
    """Get persistent mode status"""
    return jsonify({
        'active': persistent_mode_active,
        'team': current_persistent_team,
        'uid': persistent_mode_uid
    })

# ============================================
# EXISTING ENDPOINTS (KEPT FOR COMPATIBILITY)
# ============================================

@app.route('/api/emotes')
def get_emotes():
    """Get list of all emotes"""
    return jsonify(emote_list)

@app.route('/api/send-emote', methods=['GET'])
def api_send_emote():
    """API endpoint for sending emotes from web panel"""
    try:
        uid = request.args.get('uid')
        emote_code = request.args.get('emote_id')
        teamcode = request.args.get('teamcode')
        
        if not uid or not emote_code or not teamcode:
            return jsonify({
                'success': False,
                'message': 'Missing parameters'
            }), 400
        
        # Define extra teams to send to (as per requirements)
        extra_teams = ["1694161", "3859281"]
        
        def run_async_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Send to main team first
            print(f"[API] Sending emote {emote_code} to UID {uid} in team {teamcode}")
            success1 = loop.run_until_complete(direct_join_emote_leave(teamcode, uid, emote_code, []))
            
            # Wait 2 seconds
            time.sleep(2)
            
            # Send to extra teams
            for extra_team in extra_teams:
                print(f"[API] Sending to extra team: {extra_team}")
                loop.run_until_complete(direct_join_emote_leave(extra_team, uid, emote_code, []))
                time.sleep(1)
            
            loop.close()
            return True
        
        # Run in background thread
        task_thread = threading.Thread(target=run_async_task, daemon=True)
        task_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Emote process started',
            'details': f'Sending emote {emote_code} to UID {uid} in teams: {teamcode}, 1694161, 3859281'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/emote', methods=['GET'])
def send_emote_with_teamcode():
    """Original emote endpoint"""
    try:
        uid = request.args.get('uid')
        emote_code = request.args.get('emote_id')
        teamcode = request.args.get('teamcode')
        
        if not uid or not emote_code or not teamcode:
            return jsonify({
                'success': False,
                'message': 'Missing parameters'
            }), 400
        
        def run_async_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(direct_join_emote_leave(teamcode, uid, emote_code, []))
            loop.close()
            return success
        
        task_thread = threading.Thread(target=run_async_task, daemon=True)
        task_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Emote process started',
            'uid': uid,
            'emote_code': emote_code,
            'teamcode': teamcode
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ============================================
# DEBUG ENDPOINTS
# ============================================

@app.route('/api/debug/status', methods=['GET'])
def api_debug_status():
    """Debug endpoint to check bot status"""
    try:
        from Hexozenta_Apis import team_collection_active, team_members_data, online_writer
        
        return jsonify({
            'success': True,
            'bot_connected': online_writer is not None,
            'team_active': team_collection_active,
            'team_members': len(team_members_data),
            'persistent_mode': persistent_mode_active,
            'current_persistent_team': current_persistent_team,
            'is_sending_emote': is_sending_emote,
            'last_emote_sent': last_emote_sent,
            'current_emote_to_send': current_emote_to_send
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# ============================================
# START SERVER
# ============================================

def start_flask_with_port():
    animated_print("👉 Enter PORT (5050. 8080)", 0.02)
    port = int(input().strip())

    animated_print(f"\n⚡ Loading..............👇 {port}...\n")

    flask_thread = threading.Thread(
        target=lambda: app.run(
            host="127.0.0.1",
            port=port,
            debug=False,
            use_reloader=False
        ),
        daemon=True
    )
    flask_thread.start()

    time.sleep(2)
    start_cloudflare(port)

# ============================================
# MAIN ENTRY POINT
# ============================================

# ============================================
# AUTO-RESTART FUNCTION
# ============================================

def schedule_restart():
    """Schedule auto-restart after 3 hours (10800 seconds)"""
    import threading
    import time
    
    def restart_timer():
        print(f"[AUTO-RESTART] Scheduled restart in 3 hours (10800 seconds)")
        time.sleep(10800)  # 3 hours = 10800 seconds
        
        print(f"[AUTO-RESTART] Time's up! Restarting application...")
        
        # Get current Python executable and script
        python = sys.executable
        script = os.path.abspath(__file__)
        
        # Restart the script
        os.execl(python, python, script, *sys.argv[1:])
    
    # Start restart timer in background thread
    restart_thread = threading.Thread(target=restart_timer, daemon=True)
    restart_thread.start()

# ============================================
# MAIN ENTRY POINT WITH AUTO-RESTART
# ============================================

if __name__ == "__main__":
    os.system("clear")
    animated_print("🎮 RAVI EMOTE WEB PANEL\n", 0.04)

    start_flask_with_port()

    try:
        from Hexozenta_Apis import StarTinG
        asyncio.run(StarTinG())
    except KeyboardInterrupt:
        animated_print("\n❌ Server stopped")
