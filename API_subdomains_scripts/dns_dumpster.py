import requests
import json
import os
from dotenv import load_dotenv

"""
DNSdumpster Subdomain Finder

This script fetches subdomains and their corresponding A records (IP addresses)
for a specific domain using the DNSdumpster API. The results are saved to a file.

Prerequisites:
- A .env file containing API_KEY_DNSDUMPSTER.
"""

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
API_KEY = os.getenv("API_KEY_DNSDUMPSTER")
DOMAIN = ""  # Target domain
# ---------------------

# Construct the API request
url = f"https://api.dnsdumpster.com/domain/{DOMAIN}"
HEADERS = {"X-API-Key" : API_KEY}

try:
    # Make the API request
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status() # Check for HTTP errors

    # Parse the JSON response
    api_data = response.json()
    
    # The API returns different record types; we focus on 'a' records for hosts.
    hosts = api_data.get('a', [])
    output_filename = f"dnsdumpster_subdomains_{DOMAIN}.txt"

    # Write the subdomain and IP address to a file
    with open(output_filename, 'w') as f:
        for item in hosts:
            subdomain = item.get('host')
            # Ensure the 'ips' list exists and is not empty
            if item.get('ips'):
                ip_address = item['ips'][0].get('ip')
                f.write(f"{subdomain} : {ip_address}\n")
    
    print(f"Results saved successfully to {output_filename}")

except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Response content: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Connection Error: {e}")
except json.JSONDecodeError:
    print("Error: Failed to parse JSON response.")