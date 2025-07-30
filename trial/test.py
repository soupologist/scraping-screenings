import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome driver
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open Facebook group page
driver.get("https://www.facebook.com/groups/bphcshoutbox/?sorting_setting=CHRONOLOGICAL")

input("👉 Log in and press Enter once on the group feed...")

# Give time for posts to load
time.sleep(5)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(3)

# Find the first post using its role
posts = driver.find_elements(By.XPATH, '//div[@role="article"]')
print(f"Found {len(posts)} posts")

if posts:
    post = posts[0]

    # Try to get the full text content excluding comments/reactions
    try:
        text_elem = post.find_element(By.XPATH, './/div[contains(@data-ad-preview, "message")]')
        text = text_elem.text
    except:
        text = "Unknown"

    # Author: look for strong/bold text
    try:
        author_elem = post.find_element(By.XPATH, './/h2//span//strong')
        author = author_elem.text
    except:
        author = "Unknown"

    # Timestamp: look for <a> with time tag
    try:
        time_elem = post.find_element(By.XPATH, './/a[contains(@href, "/permalink")]/span')
        timestamp = time_elem.get_attribute("aria-label") or time_elem.text
    except:
        timestamp = "Unknown"

    # Image URLs: filter valid images only (exclude emoji/svg)
    image_urls = []
    try:
        image_tags = post.find_elements(By.TAG_NAME, 'img')
        for img in image_tags:
            src = img.get_attribute("src")
            if src and not src.startswith("data:image/svg+xml") and "emoji" not in src:
                image_urls.append(src)
    except:
        pass

    # Save to JSON
    post_data = {
        "author": author,
        "timestamp": timestamp,
        "text": text,
        "images": image_urls
    }

    with open("post_clean_1.json", "w", encoding="utf-8") as f:
        json.dump(post_data, f, indent=2, ensure_ascii=False)

    print("✅ Saved cleaned post to post_clean_1.json")
else:
    print("❌ No posts found")
