import os
import gzip
import json
import time
import logging
import requests
import random
from googlesearch import search
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

def extract_domain(site_url):
    parsed_url = urlparse(site_url)
    domain = parsed_url.netloc or parsed_url.path
    return domain.replace("www.", "").rstrip("/")

def extract_links_from_wikipedia(media_website, wikipedia_link):
    site_domain = extract_domain(media_website)
    extracted_site_links = []
    try:
        logging.info(f"Fetching Wikipedia URL: {wikipedia_link}")
        response = requests.get(wikipedia_link, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            logging.error(f"\nFailed to fetch {wikipedia_link}, status code: {response.status_code}\n")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        extracted_links = set()
        for anchor in soup.find_all("a", href=True):
            link = anchor["href"]
            if link.startswith("/"):
                link = wikipedia_link.rstrip("/") + link 
            article_domain = extract_domain(link)
            if link and site_domain in article_domain:
                extracted_links.add(link)
        
        return extracted_links
    except Exception as e:
        logging.error(f"Error extracting links from {media_website}: {e}")

def fetch_google_results(site):
    domain = extract_domain(site)
    query = f"site:en.wikipedia.org {domain}"
    logging.info(f"Fetching Google Search results for the query: {query}")

    extracted_site_links = []
    for result in search(query, num_results=50, unique=True, advanced=True, sleep_interval=10, region="us"):
        try:
            link = result.url

            site_links = extract_links_from_wikipedia(site, link)
            extracted_site_links.append({link: list(site_links)})
            logging.info(f"Wikipedia link:{link} found for: {domain}")
            time.sleep(5)
        except Exception as e:
            logging.error(f"Error extracting search result: {e}")
    return extracted_site_links

def create_directory(directory_path):
    os.makedirs(directory_path, exist_ok=True)

def main():
    with open("output.json", "r") as file:
        data = json.load(file)
    overall_start_time = time.time()
    for state, media_types in data.items():
        for media_type, media_list in media_types.items():
            execution_times_file = f'{media_type}_execution_times.txt'
            create_directory(f'{media_type}/{state}')
            state_start_time = time.time()

            
            serp_data = []
            for media in media_list:
                media_website = media.get("website")
                if not media_website:
                    continue
                logging.info(f"Processing {media_website} for {state}")
                results = fetch_google_results(media_website)
                serp_data.append({
                    'website': media_website,
                    'date': datetime.today().isoformat(),
                    'results': results,
                    'media_metadata': media
                })

            if serp_data:
                json_file_path = f'{media_type}/{state}/{media_type}_articles_{state}.jsonl.gz'
                try:
                    with gzip.open(json_file_path, 'wt', encoding='utf-8') as jsonl_gzip_file:
                        for entry in serp_data:
                            jsonl_gzip_file.write(json.dumps(entry) + '\n')
                    logging.info(f"Saved SERP data for {state} to {json_file_path}")
                except OSError as e:
                    logging.error(f"Error saving data to {json_file_path}: {e}")
            
            state_end_time = time.time()
            with open(execution_times_file, 'a') as execution_times_file_handle:
                execution_times_file_handle.write(f'State {state}: {state_end_time - state_start_time:.2f} seconds\n')

    overall_end_time = time.time()
    with open(execution_times_file, 'a') as execution_times_file_handle:
        execution_times_file_handle.write(f'Overall: {overall_end_time - overall_start_time:.2f} seconds\n')

    logging.info(f"Total execution time: {overall_end_time - overall_start_time:.2f} seconds.")
if __name__ == "__main__":
    main()
