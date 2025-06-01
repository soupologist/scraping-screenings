# NOTES
# need to improve the scraping of author, timestamp
# need to find the 'Most Recent' button and press it. 
# need to test how well it can pick up images. 
# need to see if opening the post link and scraping is a much better idea on this scale.

from selenium import webdriver
from selenium.webdriver.common.by import By
import time

GROUP_URL = "https://www.facebook.com/groups/bphcshoutbox"

options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")  # Show only fatal errors

driver = webdriver.Chrome(options=options)

# Manual login
print("Login to Facebook manually, then press Enter...")
driver.get("https://www.facebook.com/")
input("After logging in and navigating to the group page, press Enter...")

# Go to group
driver.get(GROUP_URL)
time.sleep(5)

# Click "Most recent"
try:
    most_recent_btn = driver.find_element(By.XPATH, '//span[text()="Most recent"]')
    most_recent_btn.click()
    time.sleep(5)
except:
    print("Could not find or click 'Most Recent' — continuing anyway.")

# Extract first post
post = driver.find_element(By.CSS_SELECTOR, '[role="feed"] [role="article"]')

# Post URL and ID
try:
    permalink = post.find_element(By.XPATH, './/a[contains(@href, "/permalink/") or contains(@href, "/posts/")]')
    post_url = permalink.get_attribute("href")
    post_id = post_url.split("/")[-1].split("?")[0]
except:
    post_url = post_id = None

# Author
try:
    author_elem = post.find_element(By.XPATH, './/strong//a | .//h2//span//a')
    author = author_elem.text.strip()
except:
    author = None

# Timestamp (real)
try:
    time_anchor = post.find_element(By.XPATH, './/a[contains(@href, "/permalink/") or contains(@href, "/posts/")]')
    timestamp = time_anchor.get_attribute("aria-label") or time_anchor.text
except:
    timestamp = None

# Content
try:
    text_blocks = post.find_elements(By.XPATH, './/div[@dir="auto"]')
    content = "\n".join([t.text for t in text_blocks if t.text.strip()])
except:
    content = ""

# Images
try:
    images = post.find_elements(By.XPATH, './/img')
    image_urls = list({
        img.get_attribute("src")
        for img in images
        if "scontent" in img.get_attribute("src", "")
    })
except:
    image_urls = []

# Result
post_data = {
    "post_id": post_id,
    "authors": [author] if author else [],
    "timestamp": timestamp,
    "content": content,
    "image_urls": image_urls,
    "post_url": post_url,
}

print("\n--- Extracted First Post ---")
for key, value in post_data.items():
    print(f"{key}: {value}")

driver.quit()
