import os
import requests
from bs4 import BeautifulSoup
import re
import uuid
from app import app, db
from models import Product

# Base URL to scrape
# Baseus Colombo has various categories. We'll scrape a few to populate the store.
CATEGORIES = [
    "https://baseuscolombo.lk/product-category/new-arrival/",
    "https://baseuscolombo.lk/product-category/power-banks/",
    "https://baseuscolombo.lk/product-category/earbuds-and-headset/wireless-earbuds/",
    "https://baseuscolombo.lk/product-category/charging-adapters/"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

def clean_price(price_str):
    # e.g., "Rs. 2,500.00" -> 2500.0
    price_str = re.sub(r'[^\d.]', '', price_str)
    try:
        # Sometimes there's a trailing dot or multiple dots. 
        # We will split by dot. If there's more than one, the last one is decimal.
        if price_str.count('.') > 1:
            parts = price_str.rsplit('.', 1)
            price_str = parts[0].replace('.', '') + '.' + parts[1]
        return float(price_str)
    except:
        return 0.0

def scrape_category(url):
    print(f"Scraping category: {url}")
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('li', class_='product')
    print(f"Found {len(products)} products on this page.")
    
    scraped_data = []
    
    for item in products:
        # Extract title
        title_elem = item.find('h2', class_='woocommerce-loop-product__title')
        if not title_elem:
            title_elem = item.find('h3') # Sometimes H3 is used
            
        title = title_elem.text.strip() if title_elem else "Unknown Product"
        
        # Extract price
        price_elem = item.find('span', class_='price')
        price_val = 0.0
        if price_elem:
            # If there's an ins tag, it's the sale price
            ins = price_elem.find('ins')
            if ins:
                amount = ins.find('bdi') or ins.find('span', class_='woocommerce-Price-amount')
            else:
                amount = price_elem.find('bdi') or price_elem.find('span', class_='woocommerce-Price-amount')
            if amount:
                price_val = clean_price(amount.text)
        
        # Extract image URL
        img_elem = item.find('img', class_='attachment-woocommerce_thumbnail')
        img_url = None
        if img_elem:
            img_url = img_elem.get('src')
            if not img_url or img_url.startswith('data:'):
                img_url = img_elem.get('data-src') or img_elem.get('data-lazy-src')
                
        if title and price_val > 0 and img_url:
            scraped_data.append({
                'title': title,
                'price': price_val,
                'image_url': img_url
            })
            
    return scraped_data

def download_image(img_url, filename):
    try:
        response = requests.get(img_url, headers=HEADERS, stream=True)
        if response.status_code == 200:
            filepath = os.path.join('static', 'images', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"Error downloading {img_url}: {e}")
    return False

def main():
    print("Starting Baseus Colombo Scraper...")
    all_products = []
    for cat_url in CATEGORIES:
        all_products.extend(scrape_category(cat_url))
        
    print(f"Total products scraped: {len(all_products)}")
    
    with app.app_context():
        # Clear existing demo products optionally or just add new ones
        # For a clean slate, let's delete existing products:
        Product.query.delete()
        db.session.commit()
        
        for item in all_products:
            # Download image
            ext = item['image_url'].split('.')[-1].split('?')[0]
            if not ext or len(ext) > 4:
                ext = 'jpg'
            filename = f"p_{uuid.uuid4().hex[:8]}.{ext}"
            
            if download_image(item['image_url'], filename):
                safe_title = item['title'].encode('ascii', 'ignore').decode('ascii')
                print(f"Saved: {safe_title} - LKR {item['price']}")
                new_product = Product(
                    name=item['title'],
                    price=item['price'],
                    image=f"images/{filename}"
                )
                db.session.add(new_product)
        
        db.session.commit()
        print("Database updated successfully.")

if __name__ == "__main__":
    main()
