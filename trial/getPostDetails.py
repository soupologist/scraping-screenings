import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

# --- Setup Selenium
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.facebook.com/groups/bphcshoutbox/?sorting_setting=CHRONOLOGICAL")

input("👉 Log in to Facebook and press Enter once you're on the group feed...")

time.sleep(5)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(4)

# --- Find all posts
posts = driver.find_elements(By.XPATH, '//div[@role="article"]')
print(f"🧾 Found {len(posts)} post(s)")

post = posts[0]  # Start with the first post only

# === Click "See more" ===
try:
    see_more = post.find_element(By.XPATH, './/*[contains(text(), "See more")]')
    driver.execute_script("arguments[0].click();", see_more)
    time.sleep(1)
except:
    pass

# === Extract full post text ===
try:
    content_elem = post.find_element(By.XPATH, './/div[@data-ad-preview="message"]')
    post_text = content_elem.text.strip()
except:
    post_text = "Unknown"

# === Extract author name ===
try:
    # Common structure is span inside header
    author_elem = post.find_element(By.XPATH, './/h2//span//span//a | .//h3//span//span//a')
    author = author_elem.text.strip()
except:
    author = "Unknown"

# === Extract timestamp (hover/aria-label) ===
try:
    time_elem = post.find_element(By.XPATH, './/a[contains(@href, "/permalink") or contains(@href, "/posts")]/span')
    timestamp = time_elem.get_attribute("aria-label") or time_elem.get_attribute("title") or time_elem.text
except:
    timestamp = "Unknown"

# === Extract image URLs ===
image_urls = []
try:
    images = post.find_elements(By.TAG_NAME, "img")
    for img in images:
        src = img.get_attribute("src")
        if src and "emoji" not in src and not src.startswith("data:image/svg+xml"):
            image_urls.append(src)
except:
    pass

# === Save as JSON ===
post_data = {
    "author": author,
    "timestamp": timestamp,
    "text": post_text,
    "images": image_urls
}

with open("post_final.json", "w", encoding="utf-8") as f:
    json.dump(post_data, f, indent=2, ensure_ascii=False)

print("✅ Saved clean post to post_final.json")
