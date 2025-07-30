from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# --- Config ---
FACEBOOK_URL = "https://www.facebook.com/groups/bphcshoutbox/?sorting_setting=CHRONOLOGICAL"
NUM_POSTS_TO_SCRAPE = 10
SCROLL_COUNT = 10  # Scroll this many times to load posts

# --- Start browser ---
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# --- Open Facebook group ---
driver.get(FACEBOOK_URL)
input("Please log in manually and press Enter here once the feed has loaded...")

# --- Scroll to load more posts ---
for _ in range(SCROLL_COUNT):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

# --- Helper: Hover over an element and get tooltip text ---
def hover_and_get_tooltip(element, timeout=4):
    try:
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="tooltip"]'))
        )
        tooltip = driver.find_element(By.XPATH, '//div[@role="tooltip"]')
        return tooltip.text.strip()
    except:
        return None

# --- Scrape posts ---
posts_data = []
feed = driver.find_element(By.XPATH, '//div[@role="feed"]')
post_elements = feed.find_elements(By.XPATH, './div')[:NUM_POSTS_TO_SCRAPE]

print(f"Found {len(post_elements)} posts. Starting extraction...")

for idx, post in enumerate(post_elements):
    try:
        visible_text = post.text.strip()
        hover_texts = []

        # --- Find the header section: contains author(s) and timestamp ---
        header = None
        try:
            header = post.find_element(By.XPATH, './/div[contains(@style, "justify-content")]')
        except:
            pass

        if header:
            # Hover over only <a> and <span> in the header
            hover_targets = header.find_elements(By.XPATH, './/a | .//span')
            for el in hover_targets:
                tooltip = hover_and_get_tooltip(el)
                if tooltip and tooltip not in hover_texts:
                    hover_texts.append(tooltip)

        # --- Collect image URLs ---
        images = []
        image_elements = post.find_elements(By.TAG_NAME, 'img')
        for img in image_elements:
            src = img.get_attribute('src')
            if src and "https" in src:
                images.append(src)

        # --- Store data ---
        posts_data.append({
            "index": idx,
            "visible_text": visible_text,
            "hover_texts": hover_texts,
            "images": images
        })

        print(f"✅ Post {idx + 1} scraped.")
    except Exception as e:
        print(f"❌ Error scraping post {idx + 1}: {e}")

# --- Save to JSON file ---
with open("facebook_posts.json", "w", encoding="utf-8") as f:
    json.dump(posts_data, f, ensure_ascii=False, indent=2)

print("\n✅ Scraping complete. Data saved to 'facebook_posts.json'.")
driver.quit()
