import time
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# --- Utility: hover and extract tooltip ---
def hover_and_get_tooltip(element):
    try:
        ActionChains(driver).move_to_element(element).perform()
        time.sleep(0.5)
        return element.get_attribute("aria-label") or element.get_attribute("title") or element.text
    except:
        return None

# --- Utility: is this string a timestamp? ---
def is_timestamp(text):
    return bool(re.match(r'^\d+[hd]$', text)) or 'at' in text.lower() or re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', text)

# --- Setup driver ---
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
driver.get("https://www.facebook.com/groups/bphcshoutbox/?sorting_setting=CHRONOLOGICAL")

print("🔐 Log in manually. Press Enter after login.")
input()

# --- Scroll to load posts ---
print("📜 Scrolling to load more posts...")
for _ in range(3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

posts = driver.find_elements(By.XPATH, "//div[@role='feed']/div")
print(f"🧾 Found {len(posts)} posts. Starting scraping...")

results = []

for i, post in enumerate(posts[:20]):
    try:
        # --- Expand "See more" if it exists ---
        try:
            see_more_btns = post.find_elements(By.XPATH, ".//div[contains(@role, 'button') and contains(text(), 'See more')]")
            for btn in see_more_btns:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.5)
        except Exception as e:
            pass

        # --- Get full visible text ---
        visible_text = post.text.strip()

        # --- Get all images ---
        images = []
        image_tags = post.find_elements(By.TAG_NAME, "img")
        for img in image_tags:
            src = img.get_attribute("src")
            if src and "scontent" in src:
                images.append(src)

        # --- Extract timestamp ---
        timestamp_text = None
        hover_targets = post.find_elements(By.XPATH, './/a | .//span')

        for el in hover_targets:
            try:
                tooltip_before = el.get_attribute("aria-label") or el.get_attribute("title")
                if tooltip_before and is_timestamp(tooltip_before):
                    timestamp_text = tooltip_before
                    break

                short_text = el.text.strip()
                if re.match(r"^\d+[hd]$", short_text) or short_text.lower() in ["just now", "1 m"]:
                    ActionChains(driver).move_to_element(el).perform()
                    time.sleep(1.2)

                    tooltip_divs = driver.find_elements(By.XPATH, '//div[@role="tooltip"]')
                    for tip in tooltip_divs:
                        ts = tip.text.strip()
                        if ts:
                            timestamp_text = ts
                            break

                    if timestamp_text:
                        break

            except Exception as e:
                continue

        results.append({
            "visible_text": visible_text,
            "timestamp": timestamp_text,
            "images": images
        })
        print(f"✅ Post {i+1} scraped successfully.")

    except Exception as e:
        print(f"❌ Error scraping post {i+1}: {e}")
        continue

# --- Save output ---
with open("facebook_posts.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("✅ Scraping complete. Results saved to 'facebook_posts.json'.")
driver.quit()
