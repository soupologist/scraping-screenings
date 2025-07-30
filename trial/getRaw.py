import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.facebook.com/groups/bphcshoutbox/?sorting_setting=CHRONOLOGICAL")

input("👉 Log in to Facebook and press Enter once you're on the group feed...")

time.sleep(5)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(4)

posts = driver.find_elements(By.XPATH, '//div[@role="article"]')
print(f"🧾 Found {len(posts)} post(s)")

post = posts[0]

# Try expanding text
try:
    see_more = post.find_element(By.XPATH, './/*[contains(text(), "See more")]')
    driver.execute_script("arguments[0].click();", see_more)
    time.sleep(1)
except:
    pass

# === Get all visible text from the post
visible_text = post.text

# === Get hoverable data (e.g. timestamps)
hover_texts = []
for elem in post.find_elements(By.XPATH, ".//*"):
    aria = elem.get_attribute("aria-label")
    title = elem.get_attribute("title")
    if aria or title:
        hover_texts.append(aria or title)

# === Get image URLs
image_urls = []
images = post.find_elements(By.TAG_NAME, "img")
for img in images:
    src = img.get_attribute("src")
    if src and "emoji" not in src and not src.startswith("data:image/svg+xml"):
        image_urls.append(src)

# === Store everything as raw
post_data = {
    "visible_text": visible_text,
    "hover_texts": hover_texts,
    "images": image_urls
}

with open("post_raw.json", "w", encoding="utf-8") as f:
    json.dump(post_data, f, indent=2, ensure_ascii=False)

print("✅ Saved raw post data to post_raw.json")
