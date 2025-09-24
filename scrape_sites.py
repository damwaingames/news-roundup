import json
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def fetch_url(url: str, timeout: int = 30) -> Optional[str]:
    """
    Fetch HTML content from a URL with error handling.
    """
    if not url:
        return None
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {str(e)}")
        return None

def process_client(client: Dict) -> Dict:
    """
    Process a single client's URLs and add HTML content.
    """
    urls_to_fetch = {
        'homepage_html': client['homepage'],
        'news_html': client['news'],
        'blog_html': client['blog']
    }
    
    # Add HTML content for each URL
    for key, url in urls_to_fetch.items():
        if url:
            logging.info(f"Fetching {key} for {client['name']}")
            html_content = fetch_url(url)
            client[key] = html_content
            # Be nice to servers
            time.sleep(1)
    
    return client

def main():
    # Load the JSON file
    try:
        with open('data/torchbox-clients.json', 'r') as f:
            clients = json.load(f)
    except Exception as e:
        logging.error(f"Error reading JSON file: {str(e)}")
        return

    # Process each client
    updated_clients = []
    for client in tqdm(clients, desc="Processing clients"):
        updated_client = process_client(client)
        updated_clients.append(updated_client)

    # Save the updated JSON file
    try:
        output_file = 'data/torchbox-clients-with-html.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated_clients, f, indent=2, ensure_ascii=False)
        logging.info(f"Successfully saved updated data to {output_file}")
    except Exception as e:
        logging.error(f"Error saving JSON file: {str(e)}")

if __name__ == "__main__":
    main() 