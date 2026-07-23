import os
import requests
from bs4 import BeautifulSoup
import re
import uuid
from app import app, db
from models import Product

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
    price_str = re.sub(r'[^\d.]', '', price_str)
    try:
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
    print(f"Found {len(products)} products on this page. Fetching details...")
    
    scraped_data = []
    
    for item in products:
        # Try to find the link to the detail page
        link_elem = item.find('a', class_='woocommerce-LoopProduct-link')
        if not link_elem:
            link_elem = item.find('a')
        
        if not link_elem or not link_elem.get('href'):
            continue
            
        product_url = link_elem['href']
        
        # Extract title from the grid first (it might be cleaner)
        title_elem = item.find('h2', class_='woocommerce-loop-product__title')
        raw_title = title_elem.text.strip() if title_elem else ""
        
        # Price extraction from grid
        price_elem = item.find('span', class_='price')
        price_val = 0.0
        if price_elem:
            ins = price_elem.find('ins')
            if ins:
                amount = ins.find('bdi') or ins.find('span', class_='woocommerce-Price-amount')
            else:
                amount = price_elem.find('bdi') or price_elem.find('span', class_='woocommerce-Price-amount')
            if amount:
                price_val = clean_price(amount.text)
                
        # Image extraction from grid
        img_elem = item.find('img', class_='attachment-woocommerce_thumbnail')
        img_url = None
        if img_elem:
            img_url = img_elem.get('src')
            if not img_url or img_url.startswith('data:'):
                img_url = img_elem.get('data-src') or img_elem.get('data-lazy-src')
                
        if not raw_title or price_val == 0 or not img_url:
            continue
            
        # Parse warranty from title
        warranty = "Not Specified"
        warranty_match = re.search(r'(-\s*)?(\d+\s*[yY]ear\s*[wW]arranty|6\s*[mM]onths\s*[wW]arranty)', raw_title)
        if warranty_match:
            warranty = warranty_match.group(2)
            # Remove warranty from title
            raw_title = raw_title.replace(warranty_match.group(0), '').strip()
            
        # Fetch Detail Page for description
        desc_text = "Premium Baseus electronics accessory."
        try:
            res_detail = requests.get(product_url, headers=HEADERS, timeout=10)
            if res_detail.status_code == 200:
                soup_detail = BeautifulSoup(res_detail.text, 'html.parser')
                desc_elem = soup_detail.find('div', class_='woocommerce-product-details__short-description')
                if desc_elem:
                    desc_text = desc_elem.text.strip()
        except Exception as e:
            pass # ignore timeouts and keep default desc
            
        scraped_data.append({
            'title': raw_title,
            'price': price_val,
            'image_url': img_url,
            'description': desc_text,
            'warranty': warranty
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
    print("Starting Baseus Colombo Scraper with Details...")
    all_products = []
    for cat_url in CATEGORIES:
        all_products.extend(scrape_category(cat_url))
        
    print(f"Total products scraped: {len(all_products)}")
    
    with app.app_context():
        # Drop and recreate tables to apply schema changes
        db.drop_all()
        db.create_all()
        
        for item in all_products:
            ext = item['image_url'].split('.')[-1].split('?')[0]
            if not ext or len(ext) > 4:
                ext = 'jpg'
            filename = f"p_{uuid.uuid4().hex[:8]}.{ext}"
            
            if download_image(item['image_url'], filename):
                safe_title = item['title'].encode('ascii', 'ignore').decode('ascii')
                print(f"Saved: {safe_title} - {item['warranty']}")
                new_product = Product(
                    name=item['title'],
                    price=item['price'],
                    image=f"images/{filename}",
                    description=item['description'],
                    warranty=item['warranty']
                )
                db.session.add(new_product)
        
        db.session.commit()
        print("Database updated successfully with details and warranty.")

if __name__ == "__main__":
    main()
