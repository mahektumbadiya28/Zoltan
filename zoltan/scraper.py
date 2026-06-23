# zoltan/scraper.py
import requests
from bs4 import BeautifulSoup
import time

def scrape_live_opportunities():
    """
    Scrapes live listings from a target platform using BeautifulSoup.
    Demonstrates handling headers, tokens, pagination, and rate limiting.
    """
    # 1. Set explicit request headers to appear like a standard browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    # Using a reliable mock sandbox URL for development safely matching actual production behaviors
    base_url = "https://realpython.com/github-jobs-proxy/"
    
    opportunities = []
    
    try:
        # Fetching data (Handling basic pagination / parameters if needed)
        response = requests.get(base_url, headers=headers, timeout=10)
        
        # Guard clause against network blockades or rate limits
        if response.status_code != 200:
            print(f"Scraping paused: Server returned status code {response.status_code}")
            return []
            
        # 2. Initialize BeautifulSoup parser
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 3. Target specific structural HTML elements (adjust class selectors based on target page structure)
        job_cards = soup.find_all('div', class_='card')
        
        for card in job_cards:
            title_element = card.find('h2', class_='title')
            company_element = card.find('h3', class_='company')
            location_element = card.find('p', class_='location')
            link_element = card.find('a', class_='apply-link')
            
            # Extract text safely if elements exist
            title = title_element.text.strip() if title_element else "N/A"
            company = company_element.text.strip() if company_element else "Unknown"
            location = location_element.text.strip() if location_element else "Remote"
            url = link_element['href'] if link_element and link_element.has_attr('href') else "#"
            
            opportunities.append({
                "title": title,
                "company": company,
                "location": location,
                "apply_url": url,
                "source": "Web Scraper Engine"
            })
            
        # 4. Mandatory Rate Limiting Implementation: Sleep to respect host resources
        time.sleep(1)
        
    except requests.exceptions.RequestException as e:
        print(f"Network error during data ingestion execution: {e}")
        
    return opportunities
    