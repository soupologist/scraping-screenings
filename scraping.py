import time
import json
import re
import hashlib
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# --- Database Setup ---
conn = sqlite3.connect('posts.db')
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    timestamp TEXT,
    images TEXT,
    hash TEXT UNIQUE
)
""")
conn.commit()

# --- Utility Functions ---
def post_exists(post_hash):
    cursor.execute("SELECT 1 FROM posts WHERE hash=?", (post_hash,))
    return cursor.fetchone() is not None

def save_post(text, timestamp, images):
    post_hash = hashlib.md5((text + (timestamp or "")).encode('utf-8')).hexdigest()
    if not post_exists(post_hash):
        cursor.execute("INSERT INTO posts (text, timestamp, images, hash) VALUES (?, ?, ?, ?)",
                       (text, timestamp, ','.join(images), post_hash))
        conn.commit()
        return True
    return False

def is_timestamp(text):
    return bool(re.match(r'^\d+[hd]$', text)) or 'at' in text.lower() or re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', text)

# --- Driver Setup ---
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
driver.get("https://www.facebook.com/groups/bphcshoutbox/?sorting_setting=CHRONOLOGICAL")

input("🔐 Log in manually, then press Enter to continue...")

# --- Infinite Scroll ---
print("📜 Scrolling and scraping...")
last_height = driver.execute_script("return document.body.scrollHeight")
seen_posts = set()
scroll_attempts = 0

max_scraped = 25
scraped_count = 0

while scraped_count < max_scraped and scroll_attempts < 15:
    posts = driver.find_elements(By.XPATH, "//div[@role='feed']/div")

    new_posts = 0

    for post in posts:
        try:
            # Expand "See more"
            see_more = post.find_elements(By.XPATH, ".//div[contains(@role, 'button') and contains(text(), 'See more')]")
            for btn in see_more:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.3)

            # Get visible text
            text = post.text.strip()

            # Get images
            images = []
            for img in post.find_elements(By.TAG_NAME, "img"):
                src = img.get_attribute("src")
                if src and "scontent" in src:
                    images.append(src)

            # Timestamp logic
            timestamp = None
            hover_targets = post.find_elements(By.XPATH, './/a | .//span')
            for el in hover_targets:
                tooltip = el.get_attribute("aria-label") or el.get_attribute("title")
                if tooltip and is_timestamp(tooltip):
                    timestamp = tooltip
                    break

                short = el.text.strip()
                if re.match(r"^\d+[hd]$", short) or short.lower() in ["just now", "1 m"]:
                    ActionChains(driver).move_to_element(el).perform()
                    time.sleep(1.2)
                    tips = driver.find_elements(By.XPATH, '//div[@role="tooltip"]')
                    for tip in tips:
                        ts = tip.text.strip()
                        if ts:
                            timestamp = ts
                            break
                    if timestamp:
                        break

            if text:
                post_hash = hashlib.md5((text + (timestamp or "")).encode()).hexdigest()
                if post_hash not in seen_posts:
                    if save_post(text, timestamp, images):
                        new_posts += 1
                        seen_posts.add(post_hash)
                        scraped_count += 1
                        print(f"📥 Scraped post {scraped_count}")

        except Exception as e:
            continue

    # Scroll further
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        scroll_attempts += 1
    else:
        scroll_attempts = 0
    last_height = new_height

    print(f"📥 Scraped {new_posts} new posts this round.")

print("✅ Scraping complete.")
driver.quit()
conn.close()
