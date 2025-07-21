import requests
import json
import time
import os
from dotenv import load_dotenv

"""
VirusTotal Subdomain Finder

This script fetches subdomains for a specific domain using the VirusTotal API v3.
It handles API pagination to retrieve all results and extracts associated IP addresses
from the last DNS records. The results are saved to a file.

Prerequisites:
- A .env file containing API_KEY_VIRUSTOTAL.
"""

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
API_KEY = os.getenv("API_KEY_VIRUSTOTAL")
DOMAIN = ""  # Target domain
# ---------------------

# Initial API URL for the first page of results
current_url = f"https://www.virustotal.com/api/v3/domains/{DOMAIN}/subdomains?limit=40"
HEADERS = {"x-apikey": API_KEY}

# Dictionary to store all results (subdomain: [ips])
all_results = {}
page_count = 1

# Use a session object to persist headers across requests
session = requests.Session()
session.headers.update(HEADERS)

print(f"Starting to fetch subdomains for: {DOMAIN}")

# Loop as long as there is a 'next' URL provided by the API (for pagination)
while current_url:
    try:
        print(f"Fetching page number {page_count}...")
        response = session.get(current_url)
        response.raise_for_status()  # Check for HTTP errors

        api_data = response.json()

        # Process the list of subdomains from the current page
        subdomain_list = api_data.get('data', [])
        for item in subdomain_list:
            subdomain_name = item.get('id')
            attributes = item.get('attributes', {})
            dns_records = attributes.get('last_dns_records', [])
            
            # Extract IP addresses only from 'A' type records
            ip_addresses = [
                record.get('value')
                for record in dns_records
                if record.get('type') == 'A'
            ]
            
            if subdomain_name:
                all_results[subdomain_name] = ip_addresses

        # Get the URL for the next page of results
        current_url = api_data.get('links', {}).get('next')
        page_count += 1

        # Pause between requests to respect API rate limits
        if current_url:
            time.sleep(1) 

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response content: {response.text}")
        break
    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")
        break
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON response.")
        break

print("\nFinished fetching all subdomains.")
print(f"Found a total of {len(all_results)} subdomains across {page_count - 1} pages.")

# Save the results to a file
output_filename = f'virustotal_subdomains_{DOMAIN}.txt'
with open(output_filename, 'w', encoding='utf-8') as f:
    for subdomain, ips in all_results.items():
        f.write(f"{subdomain}; {ips}\n")

print(f"\nResults have been saved to the file '{output_filename}'")