from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os

# === CONFIG ===
GROUP_URL = "https://www.facebook.com/groups/YOUR_GROUP_ID_OR_NAME"
SCROLL_LIMIT = 30  # Number of times to scroll (adjust as needed)
KEYWORDS = ["film", "movie", "screening", "cinema", "short", "feature"]

# === SETUP ===
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

print("Opening Facebook... Please log in manually.")
driver.get(GROUP_URL)
input("Once logged in and sorted by 'Recent Posts', press Enter here...")

# === SCROLLING AND SCRAPING ===
matches = []

def extract_images(post_element):
    images = post_element.find_elements(By.TAG_NAME, "img")
    image_urls = []
    for img in images:
        src = img.get_attribute("src")
        if src and "scontent" in src:
            image_urls.append(src)
    return list(set(image_urls))

for scroll_num in range(SCROLL_LIMIT):
    print(f"\n🔄 Scrolling page {scroll_num + 1}/{SCROLL_LIMIT}...")
    time.sleep(2)
    posts = driver.find_elements(By.CSS_SELECTOR, '[role="feed"] [role="article"]')
    print(f"🔍 Found {len(posts)} posts on this page.")

    for idx, post in enumerate(posts):
        try:
            text = post.text.strip()
            print(f"\n📄 Reading post {idx + 1}:")
            print("-" * 40)
            print(text[:500])  # Print first 500 characters max
            print("-" * 40)

            if any(keyword in text.lower() for keyword in KEYWORDS):
                print("✅ MATCH FOUND!")
                images = extract_images(post)
                matches.append({
                    "text": text,
                    "images": images
                })

        except Exception as e:
            print(f"⚠️ Error reading post: {e}")

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

# === OUTPUT RESULTS ===
output_dir = "facebook_film_posts"
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "matches.txt"), "w", encoding="utf-8") as f:
    for idx, match in enumerate(matches):
        f.write(f"--- POST {idx + 1} ---\n")
        f.write(match['text'] + "\n")
        f.write("Images:\n")
        for img_url in match['images']:
            f.write(img_url + "\n")
        f.write("\n")

print(f"\n✅ Done! {len(matches)} matching posts saved to '{output_dir}/matches.txt'.")

driver.quit()
