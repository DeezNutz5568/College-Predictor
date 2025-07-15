import os
import json
import requests
import pymysql
from time import sleep
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import random

# === CONFIGS ===
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '5568',
    'database': 'college_predictor',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}
SAVE_DIR = 'images'
os.makedirs(SAVE_DIR, exist_ok=True)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/605.1.15 Safari/605.1.15"
]

QUERY_VARIANTS = [
    "{} main building",
    "{} campus front view",
    "{} aerial view",
    "{} logo"
]

# === UTILS ===
def sanitize(name):
    return name.lower().replace(' ', '_').replace('.', '').replace(',', '')

def is_valid_image_type(content_type):
    return any(t in content_type for t in ['image/jpeg', 'image/png', 'image/jpg'])

def download_and_save_image(url, filename):
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200 and is_valid_image_type(response.headers.get('Content-Type', '')):
            img = Image.open(BytesIO(response.content))
            img.save(filename)
            print(f"✅ Saved: {filename}")
            return True
    except Exception as e:
        print(f"❌ Download fail: {e}")
    return False

def get_unique_institutes():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT institute_name FROM college_data")
    names = [row['institute_name'] for row in cursor.fetchall()]
    conn.close()
    return names

# === BING SCRAPER ===
def search_bing_image(query):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    url = f"https://www.bing.com/images/search?q={quote_plus(query)}&form=HDRSC2"

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        tags = soup.find_all('a', class_='iusc')
        for tag in tags:
            m = tag.get('m')
            if m:
                m_data = json.loads(m)
                return m_data.get('murl')
    except Exception as e:
        print(f"❌ Bing error: {e}")
    return None

# === DUCKDUCKGO SCRAPER ===
def search_duckduckgo_image(query):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    url = f"https://duckduckgo.com/?q={quote_plus(query)}&iar=images&iax=images&ia=images"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        imgs = soup.find_all('img')
        for img in imgs:
            src = img.get('src')
            if src and src.startswith("http"):
                return src
    except Exception as e:
        print(f"❌ DuckDuckGo error: {e}")
    return None

# === GOOGLE SELENIUM SCRAPER ===
def search_google_image_selenium(query):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(f"https://www.google.com/search?tbm=isch&q={quote_plus(query)}")
        sleep(2)
        img = driver.find_element(By.XPATH, '//img[contains(@class, "rg_i")]')
        src = img.get_attribute("src") or img.get_attribute("data-src")
        driver.quit()
        return src if src and src.startswith("http") else None
    except Exception as e:
        print(f"❌ Google Selenium error: {e}")
        return None

# === FINAL PUSH ===
if __name__ == "__main__":
    all_names = get_unique_institutes()
    existing_files = {f[:-4] for f in os.listdir(SAVE_DIR) if f.endswith('.jpg')}
    missing_names = [name for name in all_names if sanitize(name) not in existing_files]

    print(f"🚀 Starting FINAL PUSH. {len(missing_names)} missing.\n")

    for idx, inst in enumerate(missing_names, 1):
        filename = os.path.join(SAVE_DIR, sanitize(inst) + ".jpg")
        print(f"[{idx}/{len(missing_names)}] 🔍 {inst}")

        img_url = None

        # Try Bing
        for variant in QUERY_VARIANTS:
            img_url = search_bing_image(variant.format(inst))
            if img_url:
                break
            sleep(0.5)

        # Try DuckDuckGo if Bing failed
        if not img_url:
            img_url = search_duckduckgo_image(f"{inst} campus")

        # Try Google Images (headless) if still failed
        if not img_url:
            img_url = search_google_image_selenium(f"{inst} campus")

        # Download or fallback
        if img_url:
            success = download_and_save_image(img_url, filename)
            if not success and os.path.exists(filename):
                os.remove(filename)
        else:
            print(f"🛑 All methods failed for: {inst}")
        
        sleep(1.2)
