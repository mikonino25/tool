# ================= AUTO INSTALL =================
import subprocess, sys

def pip_install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as e:
        print(f"Lỗi khi cài {package}: {e}")

required = {
    "aiohttp": "aiohttp>=3.9.0"
}

for module, pkg in required.items():
    try:
        __import__(module)
        print(f"[OK] {pkg} đã có sẵn")
    except ImportError:
        print(f"[INSTALL] Thiếu {pkg} → Đang cài đặt...")
        pip_install(pkg)

# =================================================


import asyncio
import aiohttp
import random
import re
import string
import os

# ========== CONFIG ==========
BASE_URL = "https://snote.vip/notes/"
CONCURRENT = 10
CODE_LENGTH = 6
CHARSET = string.ascii_uppercase + string.digits
PAUSE_MINUTES = 20
PAUSE_SECONDS = PAUSE_MINUTES * 60

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1403667787943120996/PA-03eIqcD8f8zT5YQD8eN0T9afY7wI6S5rT-ra1BU_9SfI4FVgQdnrAQ8z0a52jtYSs"

CHECKED_FILE = "checked_urls.txt"
LOG_DIR = "logs"
VALID_FILE = os.path.join(LOG_DIR, "all_valid_links.txt")
TG_FILE = os.path.join(LOG_DIR, "telegram_links.txt")

checked_urls = set()
file_lock = asyncio.Lock()
stats = {"scan": 0, "found": 0}


# ========== Helper ==========
def gen_code():
    return "".join(random.choices(CHARSET, k=CODE_LENGTH))

def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)

def load_checked_urls():
    if os.path.exists(CHECKED_FILE):
        with open(CHECKED_FILE, "r", encoding="utf-8") as f:
            for line in f:
                checked_urls.add(line.strip())
    print(f"[INIT] Loaded {len(checked_urls)} URLs đã quét.")

async def append_line(fp, text):
    folder = os.path.dirname(fp)
    if folder:
        os.makedirs(folder, exist_ok=True)

    async with file_lock:
        with open(fp, "a", encoding="utf-8") as f:
            f.write(text + "\n")

async def notify(msg):
    if not DISCORD_WEBHOOK_URL.startswith("http"):
        return
    try:
        async with aiohttp.ClientSession() as s:
            await s.post(DISCORD_WEBHOOK_URL, json={"content": msg})
    except:
        pass


# ========== Scanner ==========
async def scan_one(session):
    code = gen_code()
    url = BASE_URL + code

    if url in checked_urls:
        return False
    checked_urls.add(url)
    await append_line(CHECKED_FILE, url)

    await asyncio.sleep(random.uniform(0.5, 1.8))

    try:
        async with session.get(url, timeout=10) as res:
            text = await res.text(errors="ignore")
            stats["scan"] += 1

            if res.status in (429, 403):
                msg = f"🛑 Rate-limit! {url}"
                print(msg)
                await notify(msg)
                return True

            if res.status == 200:
                await append_line(VALID_FILE, url)

                if "t.me" in text:
                    matches = re.findall(r'https://t\.me/[^\s"<>]+', text)
                    if matches:
                        stats["found"] += 1
                        msg = f"🔥 Telegram FOUND #{stats['found']}:\n{url}"
                        print(msg)
                        await append_line(TG_FILE, url)
                        await notify(msg)

            if stats["scan"] % 100 == 0:
                print(f"📊 Scanned {stats['scan']} | Found {stats['found']}")

    except Exception as e:
        print("ERR:", e)

    return False


# ========== Main Loop ==========
async def main():
    ensure_log_dir()
    load_checked_urls()
    await notify("🚀 Scanner STARTED")

    async with aiohttp.ClientSession() as session:
        while True:
            results = await asyncio.gather(*(scan_one(session) for _ in range(CONCURRENT)))

            if any(results):
                msg = f"⏸ Dừng {PAUSE_MINUTES} phút tránh limit"
                print(msg)
                await notify(msg)
                await asyncio.sleep(PAUSE_SECONDS)
                print("▶️ Resume")



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 STOP bởi user")
        asyncio.run(notify("⛔ Scanner STOP"))