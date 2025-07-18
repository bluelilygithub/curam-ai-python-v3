# Enhanced scraper.py for demo data collection

import requests
from bs4 import BeautifulSoup
import sqlite3
import datetime
import re
import time
import random

class WebScraper:
    def __init__(self, db_path='scraper.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced table structure for demo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitored_sites (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                price_selector TEXT,
                category TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY,
                site_id INTEGER,
                price REAL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (site_id) REFERENCES monitored_sites (id)
            )
        ''')
        
        # Demo data for immediate visualization
        cursor.execute('SELECT COUNT(*) FROM monitored_sites')
        if cursor.fetchone()[0] == 0:
            self.add_demo_sites()
        
        conn.commit()
        conn.close()
    
    def add_demo_sites(self):
        """Add demo sites for immediate testing"""
        demo_sites = [
            ("A Light in the Attic", "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html", ".price_color", "books"),
            ("Tipping the Velvet", "http://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html", ".price_color", "books"),
            ("Soumission", "http://books.toscrape.com/catalogue/soumission_998/index.html", ".price_color", "books"),
            ("Sharp Objects", "http://books.toscrape.com/catalogue/sharp-objects_997/index.html", ".price_color", "books"),
            ("Sapiens", "http://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html", ".price_color", "books"),
            ("The Requiem Red", "http://books.toscrape.com/catalogue/the-requiem-red_995/index.html", ".price_color", "books"),
            ("The Dirty Little Secrets", "http://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html", ".price_color", "books"),
            ("The Coming Woman", "http://books.toscrape.com/catalogue/the-coming-woman-a-novel-based-on-the-life-of-the-infamous-feminist-victoria-woodhull_993/index.html", ".price_color", "books"),
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for name, url, selector, category in demo_sites:
            cursor.execute(
                'INSERT INTO monitored_sites (name, url, price_selector, category) VALUES (?, ?, ?, ?)',
                (name, url, selector, category)
            )
        
        conn.commit()
        conn.close()
        print("✅ Added demo sites for testing")
    
    def add_site(self, name, url, price_selector, category='general'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO monitored_sites (name, url, price_selector, category) VALUES (?, ?, ?, ?)',
            (name, url, price_selector, category)
        )
        site_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return site_id
    
    def scrape_price(self, url, price_selector):
        try:
            url = url.replace('URL: ', '')
            print(f"Scraping: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            price_element = soup.select_one(price_selector)
            
            if price_element:
                if price_element.name == 'meta' and price_element.get('content'):
                    price_text = price_element.get('content')
                else:
                    price_text = price_element.get_text()
                
                # Extract number from price text (handles £, $, €)
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    final_price = float(price_match.group())
                    print(f"Found price: {final_price}")
                    return final_price
            
            return None
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def scrape_all_sites(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, url, price_selector FROM monitored_sites')
        sites = cursor.fetchall()
        
        results = []
        for site_id, name, url, price_selector in sites:
            price = self.scrape_price(url, price_selector)
            
            if price:
                # Add some random variation for demo purposes (±5%)
                demo_price = price + random.uniform(-price*0.05, price*0.05)
                demo_price = round(demo_price, 2)
                
                cursor.execute(
                    'INSERT INTO price_history (site_id, price) VALUES (?, ?)',
                    (site_id, demo_price)
                )
                results.append({
                    'site_id': site_id,
                    'name': name,
                    'price': demo_price,
                    'status': 'success'
                })
            else:
                results.append({
                    'site_id': site_id,
                    'name': name,
                    'price': None,
                    'status': 'failed'
                })
            
            time.sleep(1)  # Be respectful
        
        conn.commit()
        conn.close()
        return results
    
    def get_price_history(self, site_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT price, scraped_at FROM price_history 
            WHERE site_id = ? 
            ORDER BY scraped_at DESC LIMIT 50
        ''', (site_id,))
        history = cursor.fetchall()
        conn.close()
        
        return [{'price': row[0], 'scraped_at': row[1]} for row in history]
    
    def get_monitored_sites(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, url, price_selector, category FROM monitored_sites')
        sites = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0], 
                'name': row[1], 
                'url': row[2], 
                'price_selector': row[3],
                'category': row[4]
            } for row in sites
        ]
    
    def get_price_analytics(self):
        """Get analytics data for graphing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Average prices by site
        cursor.execute('''
            SELECT ms.name, AVG(ph.price) as avg_price, COUNT(ph.price) as data_points
            FROM monitored_sites ms
            LEFT JOIN price_history ph ON ms.id = ph.site_id
            GROUP BY ms.id, ms.name
            HAVING COUNT(ph.price) > 0
            ORDER BY avg_price DESC
        ''')
        avg_prices = cursor.fetchall()
        
        # Price trends over time
        cursor.execute('''
            SELECT ms.name, ph.price, ph.scraped_at
            FROM monitored_sites ms
            JOIN price_history ph ON ms.id = ph.site_id
            ORDER BY ph.scraped_at DESC
            LIMIT 50
        ''')
        price_trends = cursor.fetchall()
        
        conn.close()
        
        return {
            'average_prices': [{'name': row[0], 'avg_price': row[1], 'data_points': row[2]} for row in avg_prices],
            'price_trends': [{'name': row[0], 'price': row[1], 'date': row[2]} for row in price_trends]
        }
    
    def simulate_historical_data(self, days=7):
        """Generate historical data for demonstration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name FROM monitored_sites')
        sites = cursor.fetchall()
        
        # Generate data for each day
        for day in range(days):
            scrape_date = datetime.datetime.now() - datetime.timedelta(days=day)
            
            for site_id, name in sites:
                # Generate realistic price variations
                base_price = 20 + (site_id * 5)  # Different base prices
                daily_variation = random.uniform(0.8, 1.2)  # ±20% variation
                price = round(base_price * daily_variation, 2)
                
                cursor.execute(
                    'INSERT INTO price_history (site_id, price, scraped_at) VALUES (?, ?, ?)',
                    (site_id, price, scrape_date)
                )
        
        conn.commit()
        conn.close()
        print(f"✅ Generated {days} days of historical data")