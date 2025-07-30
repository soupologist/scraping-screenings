import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

# Setup
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.facebook.com/groups/bphcshoutbox/?sorting_setting=CHRONOLOGICAL")
input("👉 Log in manually and press Enter once you're on the group page...")

# Let content load
time.sleep(5)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(4)

# Find posts
posts = driver.find_elements(By.XPATH, '//div[@role="article"]')
print(f"🧾 Found {len(posts)} posts")

if not posts:
    print("❌ No posts found")
    driver.quit()
    exit()

post = posts[0]  # First post only for now

# === TRY TO CLICK "SEE MORE" ===
try:
    see_more = post.find_element(By.XPATH, './/div[contains(text(), "See more")]')
    driver.execute_script("arguments[0].click();", see_more)
    print("✅ Clicked 'See more'")
    time.sleep(1)
except (NoSuchElementException, ElementClickInterceptedException):
    print("ℹ️ No 'See more' found or clickable")

# === EXTRACT FULL TEXT ===
try:
    content_elem = post.find_element(By.XPATH, './/div[contains(@data-ad-preview, "message")]')
    post_text = content_elem.text.strip()
except:
    post_text = "Unknown"

# === EXTRACT AUTHOR ===
try:
    author_elem = post.find_element(By.XPATH, './/h2//span//strong')
    author = author_elem.text.strip()
except:
    try:
        author_elem = post.find_element(By.XPATH, './/span[contains(text(), "·")]/preceding-sibling::span')
        author = author_elem.text.strip()
    except:
        author = "Unknown"

# === EXTRACT TIMESTAMP ===
try:
    time_elem = post.find_element(By.XPATH, './/a[contains(@href, "/permalink") or contains(@href, "/posts")]/span')
    timestamp = time_elem.get_attribute("aria-label") or time_elem.text
except:
    timestamp = "Unknown"

# === EXTRACT VALID IMAGE URLs ===
image_urls = []
try:
    images = post.find_elements(By.TAG_NAME, "img")
    for img in images:
        src = img.get_attribute("src")
        if src and "emoji" not in src and not src.startswith("data:image/svg+xml"):
            image_urls.append(src)
except:
    pass

# === COMPILE JSON ===
post_data = {
    "author": author,
    "timestamp": timestamp,
    "text": post_text,
    "images": image_urls
}

with open("post_expanded_1.json", "w", encoding="utf-8") as f:
    json.dump(post_data, f, indent=2, ensure_ascii=False)

print("✅ Saved full post to post_expanded_1.json")
