#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Viewer V2 - Premium Edition
===================================
- Auto install thư viện
"""
import subprocess
import sys

REQUIRED_PACKAGES = {
    "aiohttp": "aiohttp>=3.9.0",
    "requests": "requests>=2.31.0"
}

def install(pkg):
    try:
        print(f"📦 Đang cài {pkg} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
    except Exception as e:
        print(f"❌ Lỗi khi cài {pkg}: {e}")

# Tự động cài thư viện nếu thiếu
for module, pkg in REQUIRED_PACKAGES.items():
    try:
        __import__(module)
        print(f"✔ {pkg} đã có!")
    except ImportError:
        print(f"⚠ Thiếu {pkg} → Cài ngay...")
        install(pkg)

# ===============================================
# PHẦN CODE GỐC ĐÃ FIX IMPORT OS
# ===============================================
import os
os.environ['AIOHTTP_NO_EXTENSIONS'] = '1'

import sys
if sys.version_info < (3, 8):
    print("❌ Python 3.8+ is required!")
    sys.exit(1)

import aiohttp
import asyncio
import random
import requests
import re
import time
import secrets
import signal
from hashlib import md5
from time import time as T
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass, field
from collections import deque
from urllib.parse import urlencode
import logging
import socket
import json
import threading

PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('viewer_v2.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

VIEW_ENDPOINTS = [
    "https://api16-core-c-alisg.tiktokv.com/aweme/v1/aweme/stats/",
    "https://api16-core-c-useast1a.tiktokv.com/aweme/v1/aweme/stats/",
    "https://api16-core-c.tiktokv.com/aweme/v1/aweme/stats/",
    "https://api16-va.tiktokv.com/aweme/v1/aweme/stats/",
    "https://api16-va-alisg.tiktokv.com/aweme/v1/aweme/stats/",
    "https://api16-core.tiktokv.com/aweme/v1/aweme/stats/",
]

VERSION_CODES = ["400304", "400305", "400306", "400307"]
AIDS = ["1233", "1234", "1235", "1180"]
CHANNELS = ["googleplay", "appstore", "tiktok_ads"]
DEVICE_BRANDS = ['Google', 'Samsung', 'Xiaomi', 'Oppo', 'OnePlus', 'Realme', 'Vivo',
                 'Huawei', 'Honor', 'Motorola', 'Nokia', 'Sony', 'Asus', 'Tecno',
                 'Infinix', 'TCL', 'Nothing', 'Redmi', 'Poco', 'Meizu', 'Lenovo']
APP_LANGUAGES = ['vi', 'en', 'zh', 'th', 'id', 'ms', 'ja', 'ko', 'es', 'fr', 'de', 'pt']
REGIONS = ['VN', 'US', 'SG', 'MY', 'TH', 'ID', 'PH', 'TW', 'JP', 'KR', 'GB', 'DE', 'FR', 'ES', 'BR']
TIMEZONES = [
    'Asia%2FHo_Chi_Minh', 'America%2FNew_York', 'Asia%2FSingapore',
    'Asia%2FBangkok', 'Asia%2FKuala_Lumpur', 'Asia%2FJakarta', 'Asia%2FManila',
    'Asia%2FTokyo', 'Asia%2FSeoul', 'Europe%2FLondon', 'Europe%2FBerlin',
    'Europe%2FParis', 'Europe%2FMadrid', 'America%2FSao_Paulo'
]
ACCEPT_ENCODINGS = ["gzip, deflate, br", "gzip, deflate"]
ACCEPT_LANGUAGES = [
    "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "en-US,en;q=0.9",
    "vi,en-US;q=0.9,en;q=0.8",
    "ja-JP,ja;q=0.9,en-US;q=0.8",
    "ko-KR,ko;q=0.9,en-US;q=0.8",
]
ENTER_FROM_OPTIONS = ["homepage_hot", "homepage_follow", "search", "other", "personal_homepage", "video_detail"]

SCREEN_RESOLUTIONS = [
    {"width": 720, "height": 1600, "dpi": 320},
    {"width": 1080, "height": 1920, "dpi": 420},
    {"width": 1080, "height": 2340, "dpi": 400},
    {"width": 1080, "height": 2400, "dpi": 440},
    {"width": 1440, "height": 2560, "dpi": 560},
    {"width": 1440, "height": 3200, "dpi": 560},
]
RAM_SIZES = [3, 4, 6, 8, 12, 16, 18]

@dataclass
class DeviceInfo:
    """Thông tin device chi tiết"""
    model: str
    version: str
    api_level: int
    brand: str
    screen_width: int
    screen_height: int
    dpi: int
    ram_gb: int
    device_id: int
    iid: int
    device_type: str = ""

@dataclass
class UserProfile:
    """Thông tin user như thật"""
    age: int
    gender: str
    region: str
    language: str
    timezone: str
    interests: List[str] = field(default_factory=list)
    watch_history: List[str] = field(default_factory=list)  # Lịch sử xem

class AdvancedDeviceGenerator:
    """Generator devices với khả năng tạo hàng triệu devices"""
    
    BRANDS = DEVICE_BRANDS
    
    # Mở rộng model list
    BRAND_MODELS = {
        "Google": ["Pixel 6", "Pixel 7", "Pixel 8", "Pixel 6a", "Pixel 7a", "Pixel 8a", "Pixel Fold"],
        "Samsung": ["Galaxy S21", "Galaxy S22", "Galaxy S23", "Galaxy S24", "Galaxy A52", "Galaxy A54", 
                   "Galaxy A34", "Galaxy Note 20", "Galaxy Z Fold", "Galaxy Z Flip"],
        "Xiaomi": ["Mi 11", "Mi 12", "Mi 13", "Redmi Note 11", "Redmi Note 12", "Redmi Note 13",
                   "Poco X5", "Poco X6", "Poco F5", "Mi Mix 4"],
        "Oppo": ["Reno 8", "Reno 9", "Reno 10", "Find X5", "Find X6", "A96", "A98", "F21", "F23"],
        "OnePlus": ["OnePlus 9", "OnePlus 10", "OnePlus 11", "OnePlus 12", "Nord 2", "Nord 3", "Nord CE"],
        "Realme": ["GT 2", "GT 3", "GT 5", "Realme 9", "Realme 10", "Realme 11", "Narzo 50", "Narzo 60"],
        "Vivo": ["X70", "X80", "X90", "X100", "V23", "V27", "Y72", "Y76", "Y100"],
        "Huawei": ["P50", "P60", "P70", "Mate 50", "Mate 60", "Nova 10", "Nova 11", "Y90"],
        "Honor": ["Honor 70", "Honor 80", "Honor 90", "Magic 5", "Magic 6", "X40", "X50"],
        "Motorola": ["Edge 30", "Edge 40", "Moto G84", "Moto G94", "Razr 40"],
        "Nokia": ["Nokia G60", "Nokia X30", "Nokia XR21"],
        "Sony": ["Xperia 1 V", "Xperia 5 V", "Xperia 10 V"],
        "Asus": ["Zenfone 10", "ROG Phone 7", "ROG Phone 8"],
        "Tecno": ["Camon 20", "Spark 10", "Pova 5"],
        "Infinix": ["Note 30", "Hot 40", "Zero 30"],
        "TCL": ["TCL 40", "TCL 50"],
        "Nothing": ["Phone 1", "Phone 2"],
        "Redmi": ["Note 12", "Note 13", "K60", "K70"],
        "Poco": ["Poco X5", "Poco X6", "Poco F5", "Poco M5"],
        "Meizu": ["Meizu 20", "Meizu 21"],
        "Lenovo": ["Legion Y90", "K12", "A7"],
    }
    
    ANDROID_VERSIONS = {
        "11": 30,
        "12": 31,
        "13": 33,
        "14": 34
    }
    
    USER_AGENTS = [
        "com.ss.android.ugc.trill/400304",
        "com.ss.android.ugc.trill/400305",
        "com.ss.android.ugc.trill/400306",
        "com.ss.android.ugc.trill/400307",
        "com.zhiliaoapp.musically/400304",
        "com.zhiliaoapp.musically/400305",
        "com.ss.android.ugc.aweme/400304",
        "com.ss.android.ugc.aweme/400305",
        "com.ss.android.ugc.aweme/400306",
        "com.ss.android.ugc.aweme.lite/400304",
    ]
    
    # Thread-safe device pool với khả năng mở rộng lớn - 1 TỶ DEVICES
    _device_pool = deque(maxlen=1000000000)  # 1 TỶ devices
    _lock = threading.Lock()
    _generated_count = 0
    _max_generated = 1000000000  # Tối đa 1 TỶ devices
    _used_device_ids = set()  # Track device IDs đã dùng để đảm bảo unique
    _used_device_ids_max = 100000000  # Giới hạn tracking để tiết kiệm memory
    _session_id = int(time.time() * 1000)  # Session ID unique cho mỗi lần chạy
    
    @classmethod
    def generate_device(cls) -> DeviceInfo:
        """Generate device với đầy đủ thông tin - kết hợp session_id để đảm bảo khác nhau mỗi lần chạy"""
        brand = random.choice(cls.BRANDS)
        
        if brand in cls.BRAND_MODELS:
            base_model = random.choice(cls.BRAND_MODELS[brand])
            # Thêm variant để tăng số lượng
            if random.random() < 0.4:
                variants = ["Pro", "Ultra", "Max", "Plus", "SE", "Lite", "FE", "5G"]
                variant = random.choice(variants)
                model = f"{base_model} {variant}"
            else:
                model = base_model
        else:
            model = f"{brand} Phone"
        
        version = random.choice(list(cls.ANDROID_VERSIONS.keys()))
        api_level = cls.ANDROID_VERSIONS[version]
        
        screen = random.choice(SCREEN_RESOLUTIONS)
        ram = random.choice(RAM_SIZES)
        
        # Tạo device_id và iid unique - kết hợp session_id để đảm bảo khác nhau mỗi lần chạy
        base_device_id = random.randint(600000000000000, 999999999999999)
        base_iid = random.randint(7000000000000000000, 7999999999999999999)
        # Thêm session_id vào để đảm bảo unique mỗi lần chạy
        device_id = (base_device_id + cls._session_id) % 999999999999999
        if device_id < 600000000000000:
            device_id += 600000000000000
        iid = (base_iid + cls._session_id) % 7999999999999999999
        if iid < 7000000000000000000:
            iid += 7000000000000000000
        
        # Device type dựa trên model
        device_type = model.replace(' ', '+')
        
        return DeviceInfo(
            model=model,
            version=version,
            api_level=api_level,
            brand=brand,
            screen_width=screen["width"],
            screen_height=screen["height"],
            dpi=screen["dpi"],
            ram_gb=ram,
            device_id=device_id,
            iid=iid,
            device_type=device_type
        )
    
    @classmethod
    def generate_user_profile(cls) -> UserProfile:
        """Generate user profile như thật"""
        age = random.randint(13, 50)
        gender = random.choice(['male', 'female', 'other'])
        region = random.choice(REGIONS)
        
        region_lang_map = {
            'VN': 'vi', 'US': 'en', 'SG': 'en', 'MY': 'ms', 
            'TH': 'th', 'ID': 'id', 'PH': 'en', 'TW': 'zh',
            'JP': 'ja', 'KR': 'ko', 'GB': 'en', 'DE': 'de',
            'FR': 'fr', 'ES': 'es', 'BR': 'pt'
        }
        language = region_lang_map.get(region, 'en')
        
        region_tz_map = {
            'VN': 'Asia%2FHo_Chi_Minh', 'US': 'America%2FNew_York',
            'SG': 'Asia%2FSingapore', 'MY': 'Asia%2FKuala_Lumpur',
            'TH': 'Asia%2FBangkok', 'ID': 'Asia%2FJakarta',
            'PH': 'Asia%2FManila', 'TW': 'Asia%2FTaipei',
            'JP': 'Asia%2FTokyo', 'KR': 'Asia%2FSeoul',
            'GB': 'Europe%2FLondon', 'DE': 'Europe%2FBerlin',
            'FR': 'Europe%2FParis', 'ES': 'Europe%2FMadrid',
            'BR': 'America%2FSao_Paulo'
        }
        timezone = region_tz_map.get(region, 'Asia%2FHo_Chi_Minh')
        
        all_interests = ['music', 'dance', 'comedy', 'food', 'travel', 'fashion', 
                        'sports', 'gaming', 'tech', 'beauty', 'art', 'education',
                        'lifestyle', 'fitness', 'pets', 'cars']
        num_interests = random.randint(2, 6)
        interests = random.sample(all_interests, num_interests)
        
        return UserProfile(
            age=age,
            gender=gender,
            region=region,
            language=language,
            timezone=timezone,
            interests=interests
        )
    
    @classmethod
    def random_user_agent(cls) -> str:
        return random.choice(cls.USER_AGENTS)
    
    @classmethod
    def generate_batch_devices(cls, count: int = 1000000):
        """Pre-generate devices - có thể tạo hàng triệu đến 1 tỷ"""
        # Giới hạn số lượng để tránh đơ
        count = min(count, 500000)  # Tối đa 500k devices pre-generate
        
        print(f"🔄 Đang tạo {count:,} devices (có thể tạo đến 1 TỶ)...")
        print(f"📊 Device pool tối đa: 1,000,000,000 devices")
        print(f"🆔 Session ID: {cls._session_id} - Đảm bảo devices khác nhau mỗi lần chạy")
        start_time = time.time()
        
        for i in range(count):
            try:
                device = cls.generate_device()
                with cls._lock:
                    cls._device_pool.append(device)
                    cls._generated_count += 1
                
                # Update progress thường xuyên hơn để tránh đơ
                if (i + 1) % 50000 == 0:
                    elapsed = time.time() - start_time
                    rate = (i + 1) / elapsed if elapsed > 0 else 0
                    remaining = (count - i - 1) / rate if rate > 0 else 0
                    print(f"✅ Đã tạo {i + 1:,}/{count:,} devices... "
                          f"({rate:.0f} devices/s, còn ~{remaining:.0f}s)")
            except Exception as e:
                logger.warning(f"Error generating device {i}: {e}")
                continue
        
        print(f"✅ Hoàn thành! Đã tạo {len(cls._device_pool):,} devices trong pool\n")
    
    @classmethod
    def get_device_from_pool(cls) -> DeviceInfo:
        """Lấy device từ pool hoặc generate mới"""
        with cls._lock:
            if cls._device_pool:
                return cls._device_pool.popleft()
            # Nếu pool rỗng, generate mới
            return cls.generate_device()
    
    @classmethod
    def get_pool_size(cls) -> int:
        """Lấy kích thước pool"""
        with cls._lock:
            return len(cls._device_pool)

class Signature:
    """Generate TikTok API signature (X-Gorgon)"""
    KEY = [0xDF, 0x77, 0xB9, 0x40, 0xB9, 0x9B, 0x84, 0x83, 0xD1, 0xB9, 
           0xCB, 0xD1, 0xF7, 0xC2, 0xB9, 0x85, 0xC3, 0xD0, 0xFB, 0xC3]
    
    def __init__(self, params: str, data: str, cookies: str):
        self.params = params
        self.data = data
        self.cookies = cookies
    
    def _md5_hash(self, data: str) -> str:
        return md5(data.encode()).hexdigest()
    
    def _reverse_byte(self, n: int) -> int:
        return int(f"{n:02x}"[1:] + f"{n:02x}"[0], 16)
    
    def generate(self) -> Dict[str, str]:
        g = self._md5_hash(self.params)
        g += self._md5_hash(self.data) if self.data else "0" * 32
        g += self._md5_hash(self.cookies) if self.cookies else "0" * 32
        g += "0" * 32
        
        unix_timestamp = int(T())
        payload = []
        
        for i in range(0, 12, 4):
            chunk = g[8 * i:8 * (i + 1)]
            for j in range(4):
                payload.append(int(chunk[j * 2:(j + 1) * 2], 16))
        
        payload.extend([0x0, 0x6, 0xB, 0x1C])
        payload.extend([
            (unix_timestamp & 0xFF000000) >> 24,
            (unix_timestamp & 0x00FF0000) >> 16,
            (unix_timestamp & 0x0000FF00) >> 8,
            (unix_timestamp & 0x000000FF)
        ])
        
        encrypted = [a ^ b for a, b in zip(payload, self.KEY)]
        
        for i in range(0x14):
            C = self._reverse_byte(encrypted[i])
            D = encrypted[(i + 1) % 0x14]
            F = int(bin(C ^ D)[2:].zfill(8)[::-1], 2)
            H = ((F ^ 0xFFFFFFFF) ^ 0x14) & 0xFF
            encrypted[i] = H
        
        signature = "".join(f"{x:02x}" for x in encrypted)
        
        return {
            "X-Gorgon": "840280416000" + signature,
            "X-Khronos": str(unix_timestamp)
        }

class TikTokViewerV2:
    """TikTok Viewer V2 - Premium Edition"""
    
    def __init__(self, views_per_minute: int = 100, max_workers: int = 5000):
        """
        Args:
            views_per_minute: Số view mỗi phút
            max_workers: Số workers đồng thời (tối đa 5000)
        """
        self.views_per_minute = views_per_minute
        self.max_workers = min(max_workers, 5000)  # Giới hạn 5000 workers
        self.delay_between_views = 60.0 / views_per_minute
        
        self.count = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.start_time = 0
        self.is_running = False
        self.session = None
        
        # Long-term viewing tracking
        self.video_watch_count = {}  # Track số lần xem mỗi video
        self.user_profiles = deque(maxlen=10000)
        self._generate_user_profiles(5000)
        
        # Stats
        self.peak_speed = 0
        self.last_minute_views = deque(maxlen=60)  # Track views trong 60 giây qua
    
    def _generate_user_profiles(self, count: int):
        """Pre-generate user profiles"""
        for _ in range(count):
            profile = AdvancedDeviceGenerator.generate_user_profile()
            self.user_profiles.append(profile)
    
    def _get_user_profile(self) -> UserProfile:
        """Lấy user profile từ pool hoặc tạo mới"""
        if self.user_profiles:
            return self.user_profiles.popleft()
        return AdvancedDeviceGenerator.generate_user_profile()
    
    async def init_session(self):
        """Initialize aiohttp session với tối ưu cho nhiều connections"""
        timeout = aiohttp.ClientTimeout(
            total=12,
            connect=4,
            sock_read=8
        )
        
        connector = aiohttp.TCPConnector(
            limit=self.max_workers * 2,  # Cho phép nhiều connections
            limit_per_host=self.max_workers,
            ttl_dns_cache=3600,
            use_dns_cache=True,
            keepalive_timeout=120,
            enable_cleanup_closed=True,
            force_close=False
        )
        
        user_agent = AdvancedDeviceGenerator.random_user_agent()
        
        try:
            cookie_jar = aiohttp.DummyCookieJar()
        except:
            cookie_jar = None
        
        session_kwargs = {
            'timeout': timeout,
            'connector': connector,
            'headers': {'User-Agent': user_agent},
            'skip_auto_headers': {'User-Agent'},
            'connector_owner': True
        }
        
        if cookie_jar is not None:
            session_kwargs['cookie_jar'] = cookie_jar
        
        self.session = aiohttp.ClientSession(**session_kwargs)
    
    async def close_session(self):
        """Close session"""
        if self.session:
            try:
                await asyncio.wait_for(self.session.close(), timeout=3.0)
            except:
                pass
            finally:
                self.session = None
    
    def get_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from TikTok URL"""
        try:
            patterns = [
                r'/video/(\d+)',
                r'tiktok\.com/@[^/]+/(\d+)',
                r'(\d{18,19})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            response = requests.get(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                },
                timeout=15
            )
            
            patterns_page = [
                r'"video":\{"id":"(\d+)"',
                r'"id":"(\d+)"',
                r'video/(\d+)',
                r'(\d{19})',
                r'"aweme_id":"(\d+)"'
            ]
            
            for pattern in patterns_page:
                match = re.search(pattern, response.text)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            logger.error(f"Error getting video ID: {e}")
            return None
    
    def generate_advanced_view_data(self, video_id: str, device: DeviceInfo, user: UserProfile, 
                                    is_repeat_view: bool = False) -> Tuple[str, Dict, Dict, Dict]:
        """Generate view data với khả năng xem lại (long-term viewing)"""
        
        version_code = random.choice(VERSION_CODES)
        aid = random.choice(AIDS)
        channel = random.choice(CHANNELS)
        
        params = (
            f"channel={channel}&aid={aid}&app_name=musical_ly&version_code={version_code}"
            f"&device_platform=android&device_type={device.device_type}"
            f"&os_version={device.version}&device_id={device.device_id}"
            f"&os_api={device.api_level}&app_language={user.language}&tz_name={user.timezone}"
            f"&iid={device.iid}&device_brand={device.brand}"
            f"&language={user.language}&region={user.region}"
            f"&manifest_version_code={version_code}"
            f"&update_version_code={version_code}"
            f"&ac=wifi&channel_source=ads"
            f"&is_my_cn=0&fp={secrets.token_hex(16)}"
            f"&cdid={secrets.token_hex(16)}"
        )
        
        base_url = random.choice(VIEW_ENDPOINTS)
        url = f"{base_url}?{params}"
        
        # Long-term viewing: Nếu đã xem rồi, có thể xem lại với behavior khác
        if is_repeat_view:
            # Xem lại: có thể xem ít hơn hoặc nhiều hơn
            video_duration = random.randint(15, 90)
            watch_percentage = random.uniform(0.3, 0.9)  # 30-90% khi xem lại
            play_time = int(video_duration * watch_percentage)
        else:
            # Lần đầu xem: xem kỹ hơn
            video_duration = random.randint(15, 90)
            watch_percentage = random.uniform(0.7, 0.98)  # 70-98% lần đầu
            play_time = int(video_duration * watch_percentage)
        
        play_time = max(5, min(play_time, 90))  # 5-90 giây
        video_play_duration = play_time * 1000
        
        current_time = int(time.time())
        action_time = current_time + random.randint(-1, 1)
        
        # Behavior như thật
        if play_time > 30:
            pause_count = random.randint(1, 3)
        elif play_time > 15:
            pause_count = random.randint(0, 2)
        else:
            pause_count = random.randint(0, 1)
        
        scroll_count = random.randint(0, 3)
        
        # Enter from - có thể từ nhiều nguồn khác nhau
        enter_from = random.choice(ENTER_FROM_OPTIONS)
        
        data = {
            "item_id": video_id,
            "play_delta": 1,
            "action_time": action_time,
            "stats_channel": "video",
            "play_time": play_time,
            "enter_from": enter_from,
            "from_prefetch": 0,
            "video_play_duration": video_play_duration,
            "is_play": 1,
            "play_progress": int(watch_percentage * 100),
            "stay_time": play_time,
            "scroll_count": scroll_count,
            "pause_count": pause_count,
        }
        
        cookies = {
            "sessionid": secrets.token_hex(16),
            "sid_guard": secrets.token_hex(32),
            "uid_tt": str(random.randint(1000000000000000000, 9999999999999999999)),
            "sid_tt": secrets.token_hex(16),
        }
        
        timestamp_ms = int(time.time() * 1000)
        req_ticket = timestamp_ms + random.randint(0, 1000)
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": AdvancedDeviceGenerator.random_user_agent(),
            "Accept-Encoding": random.choice(ACCEPT_ENCODINGS),
            "Accept-Language": random.choice(ACCEPT_LANGUAGES),
            "Connection": "keep-alive",
            "X-SS-REQ-TICKET": str(req_ticket),
            "X-Tt-Token": "",
            "sdk-version": random.choice(["1", "2", "3"]),
            "X-VC-BDT": str(timestamp_ms),
            "X-Tt-Trace-Id": secrets.token_hex(16),
            "X-Argus": secrets.token_hex(32),
            "X-Ladon": secrets.token_hex(32),
            "sdk_name": "aweme",
            "sdk_version": "2",
        }
        
        return url, data, cookies, headers
    
    async def send_view_request(self, video_id: str, semaphore: asyncio.Semaphore) -> bool:
        """Send view request với device và user như thật"""
        async with semaphore:
            try:
                device = AdvancedDeviceGenerator.get_device_from_pool()
                user = self._get_user_profile()
                
                # Kiểm tra xem đã xem video này chưa (long-term viewing)
                watch_count = self.video_watch_count.get(video_id, 0)
                is_repeat_view = watch_count > 0
                
                url, data, cookies, headers = self.generate_advanced_view_data(
                    video_id, device, user, is_repeat_view
                )
                
                # Generate signature
                params_str = url.split('?')[1] if '?' in url else ''
                data_str = (
                    f"item_id={data['item_id']}&play_delta={data['play_delta']}&action_time={data['action_time']}"
                    f"&play_time={data['play_time']}&video_play_duration={data['video_play_duration']}"
                    f"&is_play={data['is_play']}"
                )
                cookies_str = f"sessionid={cookies.get('sessionid', '')}"
                
                sig = Signature(params_str, data_str, cookies_str).generate()
                headers = {**headers, **sig}
                
                form_data = urlencode(data)
                
                async with self.session.post(
                    url,
                    data=form_data,
                    headers=headers,
                    cookies=cookies,
                    ssl=False,
                    allow_redirects=True
                ) as response:
                    status = response.status
                    
                    if 200 <= status < 300:
                        self.count += 1
                        self.successful_requests += 1
                        self.video_watch_count[video_id] = watch_count + 1
                        self.last_minute_views.append(time.time())
                        return True
                    
                    # Try parse JSON
                    try:
                        response_text = await response.text()
                        if response_text:
                            try:
                                response_json = json.loads(response_text)
                                if response_json.get('status_code', -1) == 0:
                                    self.count += 1
                                    self.successful_requests += 1
                                    self.video_watch_count[video_id] = watch_count + 1
                                    self.last_minute_views.append(time.time())
                                    return True
                            except:
                                pass
                    except:
                        pass
                    
                    self.failed_requests += 1
                    return False
                    
            except Exception as e:
                self.failed_requests += 1
                error_name = type(e).__name__
                is_dns_error = (
                    isinstance(e, (aiohttp.ClientConnectorError, aiohttp.ClientConnectorDNSError, 
                                 asyncio.TimeoutError)) or
                    'gaierror' in error_name.lower() or
                    isinstance(e, socket.gaierror)
                )
                if not is_dns_error and self.failed_requests % 100 == 0:
                    logger.warning(f"Request error: {type(e).__name__}")
                return False
    
    async def view_sender(self, video_id: str, task_id: int, semaphore: asyncio.Semaphore):
        """Send views continuously với delay phù hợp"""
        # Stagger initial delay để tránh đơ
        initial_delay = (task_id % 100) * 0.01
        if initial_delay > 0:
            await asyncio.sleep(initial_delay)
        
        while self.is_running:
            try:
                await self.send_view_request(video_id, semaphore)
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log lỗi nhưng không dừng
                if self.failed_requests % 1000 == 0:
                    logger.debug(f"View sender error: {type(e).__name__}")
                await asyncio.sleep(0.1)  # Delay nhỏ khi lỗi
            
            # Delay tối ưu dựa trên views_per_minute
            delay = max(0.1, self.delay_between_views / self.max_workers)
            try:
                await asyncio.sleep(delay)
            except asyncio.CancelledError:
                break
    
    def calculate_stats(self) -> Dict:
        """Calculate statistics"""
        elapsed = time.time() - self.start_time
        if elapsed <= 0:
            return {
                "total_views": self.count,
                "elapsed_time": 0,
                "views_per_minute": 0,
                "success_rate": 0,
                "current_speed": 0,
            }
        
        views_per_minute = (self.count / elapsed) * 60
        current_speed = len(self.last_minute_views) * 60  # Views trong phút gần nhất
        
        if views_per_minute > self.peak_speed:
            self.peak_speed = views_per_minute
        
        total_requests = self.successful_requests + self.failed_requests
        success_rate = (self.successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_views": self.count,
            "elapsed_time": elapsed,
            "views_per_minute": views_per_minute,
            "current_speed": current_speed,
            "peak_speed": self.peak_speed,
            "success_rate": success_rate,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "repeat_views": sum(1 for v in self.video_watch_count.values() if v > 1),
        }
    
    def display_stats(self):
        """Display statistics"""
        stats = self.calculate_stats()
        
        print(f"\n{'='*70}")
        print(f"📊 THỐNG KÊ CHI TIẾT")
        print(f"{'='*70}")
        print(f"👀 Tổng view: {stats['total_views']:,}")
        print(f"⏰ Thời gian: {stats['elapsed_time']:.1f}s ({stats['elapsed_time']/60:.1f} phút)")
        print(f"📈 Tốc độ trung bình: {stats['views_per_minute']:.1f} view/phút")
        print(f"⚡ Tốc độ hiện tại: {stats['current_speed']:.1f} view/phút")
        print(f"🏆 Tốc độ cao nhất: {stats['peak_speed']:.1f} view/phút")
        print(f"✅ Thành công: {stats['successful_requests']:,} | ❌ Thất bại: {stats['failed_requests']:,}")
        print(f"🎯 Tỷ lệ thành công: {stats['success_rate']:.1f}%")
        print(f"🔄 Xem lại: {stats['repeat_views']:,} views")
        print(f"📱 Devices trong pool: {AdvancedDeviceGenerator.get_pool_size():,}")
        print(f"{'='*70}\n")
    
    async def run(self, video_url: str):
        """Main run method - giữ nguyên logic gốc"""
        print("\n" + "="*70)
        print("🚀 TIKTOK VIEWER V2 - PREMIUM EDITION")
        print("="*70)
        print("⚠️  EDUCATIONAL & RESEARCH PURPOSE ONLY")
        print(f"🐍 Python Version: {PYTHON_VERSION}")
        print(f"⚙️  Tốc độ mục tiêu: {self.views_per_minute} view/phút")
        print(f"👥 Số workers: {self.max_workers:,}")
        print("="*70 + "\n")
        
        print("🔄 Đang lấy Video ID...")
        video_id = self.get_video_id(video_url)
        
        if not video_id:
            print("❌ Không thể lấy Video ID. Kiểm tra lại URL!")
            return
        
        print(f"✅ Video ID: {video_id}\n")
        
        # Pre-generate devices - giảm số lượng để tránh đơ
        device_count = min(200000, self.max_workers * 100)  # Giảm để tránh đơ
        AdvancedDeviceGenerator.generate_batch_devices(device_count)
        
        print("\n💡 ĐẶC ĐIỂM V2:")
        print("   ✅ 1 TỶ devices có thể tạo (1,000,000,000)")
        print("   ✅ Mỗi lần chạy tạo devices khác nhau (Session ID unique)")
        print("   ✅ Device info đầy đủ (screen, RAM, DPI, variants)")
        print("   ✅ User profile realistic (age, gender, region, interests)")
        print("   ✅ Long-term viewing (có thể xem lại video)")
        print("   ✅ Behavior như thật (pause, scroll, watch time)")
        print("   ✅ Nhiều workers đồng thời (nhanh)")
        print("   ✅ Tối ưu để thành công cao")
        print("\n⚡ Đang khởi chạy... (Nhấn Ctrl+C để dừng)\n")
        
        await asyncio.sleep(0.5)
        
        await self.init_session()
        self.is_running = True
        self.start_time = time.time()
        
        # Semaphore để control số lượng requests đồng thời
        semaphore = asyncio.Semaphore(self.max_workers)
        
        tasks = []
        try:
            print(f"🔄 Đang khởi tạo {self.max_workers:,} workers...")
            
            # Tạo tasks theo batch để tránh quá tải - tăng delay để tránh đơ
            batch_size = min(200, self.max_workers // 10)  # Giảm batch size
            if batch_size < 50:
                batch_size = 50
            
            for i in range(0, self.max_workers, batch_size):
                batch_end = min(i + batch_size, self.max_workers)
                for j in range(i, batch_end):
                    try:
                        task = asyncio.create_task(self.view_sender(video_id, j, semaphore))
                        tasks.append(task)
                    except Exception as e:
                        logger.warning(f"Error creating task {j}: {e}")
                        continue
                
                if batch_end < self.max_workers:
                    await asyncio.sleep(0.2)  # Tăng delay để tránh đơ
            
            print(f"✅ Đã khởi tạo {len(tasks):,} workers thành công!\n")
            
            last_display = 0
            while self.is_running:
                await asyncio.sleep(1.0)
                
                current_time = time.time()
                if current_time - last_display >= 2.0:  # Update mỗi 2 giây
                    stats = self.calculate_stats()
                    pool_size = AdvancedDeviceGenerator.get_pool_size()
                    
                    print(
                        f"\r✅ Views: {stats['total_views']:,} | "
                        f"Tốc độ: {stats['current_speed']:.0f}/phút | "
                        f"Thành công: {stats['success_rate']:.1f}% | "
                        f"Xem lại: {stats['repeat_views']:,} | "
                        f"Devices: {pool_size:,}",
                        end="", flush=True
                    )
                    last_display = current_time
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Đang dừng...")
        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            self.is_running = False
            
            # Cancel tasks - cải thiện để tránh đơ
            if tasks:
                for task in tasks:
                    if not task.done():
                        task.cancel()
                
                await asyncio.sleep(0.5)
                try:
                    # Chia nhỏ gather để tránh đơ
                    batch_size = 100
                    for i in range(0, len(tasks), batch_size):
                        batch = tasks[i:i+batch_size]
                        try:
                            await asyncio.wait_for(
                                asyncio.gather(*batch, return_exceptions=True),
                                timeout=2.0
                            )
                        except:
                            pass
                except:
                    pass
            
            await self.close_session()
            self.display_stats()

def signal_handler(sig, frame):
    print("\n\n🛑 Nhận tín hiệu dừng...")
    sys.exit(0)

def main():
    """Main entry point - đơn giản: chỉ nhập link và Enter là chạy"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n" + "="*70)
    print("🎯 TIKTOK VIEWER V2 - PREMIUM EDITION")
    print("="*70)
    print("⚠️  EDUCATIONAL & RESEARCH PURPOSE ONLY")
    print(f"🐍 Python {PYTHON_VERSION}")
    print("="*70)
    
    # Đơn giản: chỉ nhập link và Enter là chạy luôn với mặc định 50 view/phút
    video_url_input = input("\n📥 Nhập URL video TikTok (Enter để chạy mặc định 50 view/phút): ").strip()
    
    if not video_url_input:
        print("❌ URL không được để trống!")
        return
    
    # Parse URL
    url_pattern = r'https?://[^\s]+'
    if video_url_input.startswith(('http://', 'https://')):
        video_url = video_url_input
    else:
        match = re.search(url_pattern, video_url_input)
        if match:
            video_url = match.group(0)
        else:
            print("❌ URL không hợp lệ!")
            return
    
    # Mặc định: 50 view/phút, 1000 workers
    views_per_minute = 50
    max_workers = 1000
    
    print(f"\n✅ URL: {video_url[:70]}..." if len(video_url) > 70 else f"\n✅ URL: {video_url}")
    print(f"⚙️  Mặc định: {views_per_minute} view/phút với {max_workers:,} workers")
    
    # Test internet
    print("\n🔍 Đang kiểm tra kết nối...", end="", flush=True)
    try:
        requests.get("https://www.google.com", timeout=5)
        print(" ✅")
    except:
        print(" ❌ Không có kết nối internet!")
        return
    
    # Chạy video
    viewer = TikTokViewerV2(views_per_minute=views_per_minute, max_workers=max_workers)
    try:
        asyncio.run(viewer.run(video_url))
    except KeyboardInterrupt:
        print("\n\n👋 Đã dừng chương trình. Tạm biệt!")
    except Exception as e:
        print(f"\n💥 Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

