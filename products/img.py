import os
import requests
import time
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -------------------------------
# CONFIGURATION
# -------------------------------
BASE_URL = "https://baseuscolombo.lk"
# The main shop page URL
START_URL = f"{BASE_URL}/shop/"
# The directory where images will be saved
DOWNLOAD_DIR = "baseus_product_images"
# How many seconds to wait between requests (be respectful)
REQUEST_DELAY = 1
# Timeout for downloading a single image (in seconds)
IMAGE_DOWNLOAD_TIMEOUT = 30

# -------------------------------
# SETUP
# -------------------------------
# Create download directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Set up Selenium WebDriver (you might need to adjust the path to chromedriver)
chrome_options = Options()
chrome_options.add_argument("--headless")   # Run in background
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Make sure chromedriver is in your PATH or provide the full path here
driver = webdriver.Chrome(options=chrome_options)

# -------------------------------
# STEP 1: GET ALL PRODUCT URLs
# -------------------------------
def get_product_links():
    """Extract all product page URLs from the main shop page."""
    print(f"Loading shop page: {START_URL}")
    driver.get(START_URL)
    
    # Give the page time to load all dynamic content
    # Adjust this value if needed (higher for slower connections)
    time.sleep(5)
    
    # Scroll to the bottom to trigger lazy loading of products
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)   # Wait for new content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    # Get all links that look like product pages
    # This selector might need adjustment based on the exact structure of the site
    link_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/product/']")
    
    product_urls = set()
    for elem in link_elements:
        href = elem.get_attribute("href")
        if href and "/product/" in href:
            product_urls.add(href)
    
    print(f"Found {len(product_urls)} product pages.")
    return list(product_urls)

# -------------------------------
# STEP 2: EXTRACT PRODUCT DETAILS
# -------------------------------
def extract_product_details(product_url):
    """Fetch a product page and extract the name and image URL(s)."""
    print(f"Processing: {product_url}")
    
    # Use requests for faster downloading (no need for JS engine)
    try:
        response = requests.get(product_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  Failed to fetch page: {e}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # --- Extract product name ---
    # Common WooCommerce title selectors
    title_elem = soup.find('h1', class_='product_title') or \
                 soup.find('h1', class_='entry-title') or \
                 soup.find('h1')
    product_name = title_elem.get_text(strip=True) if title_elem else "unknown"
    # Clean the name for use as a filename (remove invalid characters)
    safe_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    
    # --- Extract image URLs ---
    image_urls = []
    
    # Look for main product image in the gallery
    # This pattern is common in WooCommerce
    gallery = soup.find('div', class_='woocommerce-product-gallery')
    if gallery:
        img = gallery.find('img', class_='wp-post-image')
        if img and img.get('src'):
            image_urls.append(img['src'])
    
    # Also look for any other images within the product gallery (thumbnails)
    other_images = soup.select('div.woocommerce-product-gallery img')
    for img in other_images:
        src = img.get('src')
        if src and src not in image_urls:
            image_urls.append(src)
    
    # If no gallery found, fallback to any large image on the page
    if not image_urls:
        main_img = soup.find('img', class_='attachment-shop_single') or \
                   soup.find('img', class_='attachment-full')
        if main_img and main_img.get('src'):
            image_urls.append(main_img['src'])
    
    # If still empty, try any img with 'product' in its class or ID
    if not image_urls:
        for img in soup.find_all('img'):
            classes = img.get('class', [])
            if any('product' in c.lower() for c in classes) or img.get('id') and 'product' in img['id'].lower():
                if img.get('src') and not img['src'].startswith('data:'):
                    image_urls.append(img['src'])
    
    return {"name": safe_name, "image_urls": image_urls}

# -------------------------------
# STEP 3: DOWNLOAD IMAGES
# -------------------------------
def download_image(image_url, save_path):
    """Download a single image and save it to the given path."""
    try:
        response = requests.get(image_url, timeout=IMAGE_DOWNLOAD_TIMEOUT, stream=True)
        response.raise_for_status()
        
        # Determine file extension from URL or Content-Type
        ext = os.path.splitext(urllib.parse.urlparse(image_url).path)[1]
        if not ext or ext.lower() not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'webp' in content_type:
                ext = '.webp'
            else:
                ext = '.jpg'  # default
        
        final_path = save_path + ext
        
        with open(final_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  Downloaded: {final_path}")
        return True
    except Exception as e:
        print(f"  Failed to download {image_url}: {e}")
        return False

# -------------------------------
# MAIN EXECUTION
# -------------------------------
def main():
    product_links = get_product_links()
    
    if not product_links:
        print("No product links found. The site structure might have changed.")
        driver.quit()
        return
    
    for idx, url in enumerate(product_links, 1):
        print(f"\n--- Product {idx}/{len(product_links)} ---")
        details = extract_product_details(url)
        if not details:
            continue
        
        product_name = details["name"]
        image_urls = details["image_urls"]
        
        if not image_urls:
            print(f"  No images found for '{product_name}'")
            continue
        
        # Use the first image as the primary one (or you can modify to download all)
        primary_img = image_urls[0]
        # Build a safe base filename from the product name
        base_filename = os.path.join(DOWNLOAD_DIR, product_name)
        download_image(primary_img, base_filename)
        
        # Optional: download additional images (thumbnails) by incrementing a counter
        # for i, img_url in enumerate(image_urls[1:], start=2):
        #     download_image(img_url, f"{base_filename}_{i}")
        
        # Be nice to the server
        time.sleep(REQUEST_DELAY)
    
    driver.quit()
    print("\nAll done! Images are saved in the folder:", DOWNLOAD_DIR)

if __name__ == "__main__":
    main()