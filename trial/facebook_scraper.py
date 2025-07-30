from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import json
import re

# Setup
options = Options()
options.add_argument("--disable-notifications")
# options.add_argument("--headless")  # Don't use headless for tooltip hovering
driver = webdriver.Chrome(options=options)

# Open Facebook group
driver.get("https://www.facebook.com/groups/bphcshoutbox/?sorting_setting=CHRONOLOGICAL")
input("➡️ Login manually and press Enter to start scraping...")

def is_timestamp(text):
    return bool(re.match(r"^(Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|[A-Za-z]+ \d+)", text))

results = []

# Scroll a few times to load posts
for _ in range(5):
    driver.execute_script("window.scrollBy(0, 2000);")
    time.sleep(2)

# Get posts
posts = driver.find_elements(By.XPATH, '//div[@role="article"]')

for post in posts:
    try:
        # Expand full post text if there's a "See more" button
        try:
            see_more = post.find_element(By.XPATH, './/div[contains(@role,"button") and contains(text(),"See more")]')
            driver.execute_script("arguments[0].click();", see_more)
            time.sleep(0.5)
        except:
            pass

        # Get full visible text
        visible_text = post.text.strip()

        # Collect image URLs
        images = []
        img_elements = post.find_elements(By.XPATH, './/img')
        for img in img_elements:
            src = img.get_attribute("src")
            if src and "scontent" in src:
                images.append(src)

        # Timestamp extraction
        timestamp_text = None
        time_candidates = post.find_elements(By.XPATH, './/a | .//span')
        for el in time_candidates:
            try:
                tooltip = el.get_attribute("aria-label") or el.get_attribute("title")
                if tooltip and is_timestamp(tooltip):
                    timestamp_text = tooltip
                    break

                short = el.text.strip()
                if re.match(r"^\d+[hdwm]$", short.lower()) or short.lower() in ["just now", "1 m"]:
                    ActionChains(driver).move_to_element(el).perform()
                    time.sleep(1.2)
                    tooltips = driver.find_elements(By.XPATH, '//div[@role="tooltip"]')
                    for tip in tooltips:
                        ts = tip.text.strip()
                        if ts and is_timestamp(ts):
                            timestamp_text = ts
                            break
                    if timestamp_text:
                        break
            except:
                continue

        results.append({
            "visible_text": visible_text,
            "timestamp": timestamp_text,
            "images": images
        })

    except Exception as e:
        print("❌ Error on post:", e)
        continue

# Save to JSON
with open("fb_posts.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

driver.quit()
print("✅ Done. Posts saved to fb_posts.json.")
