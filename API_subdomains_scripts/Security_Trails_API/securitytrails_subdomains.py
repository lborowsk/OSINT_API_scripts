import requests
import json
import os
from dotenv import load_dotenv

"""
SecurityTrails Subdomain Finder

This script fetches all known subdomains for a specific domain using the
SecurityTrails API and saves them to a text file.

Prerequisites:
- A .env file containing API_KEY_SECURITYTRAILS.
"""

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
API_KEY = os.getenv("API_KEY_SECURITYTRAILS")
DOMAIN = ""  # Target domain
# ---------------------

# Construct the API request URL and headers
url = f"https://api.securitytrails.com/v1/domain/{DOMAIN}/subdomains"
HEADERS = {"apikey" : API_KEY}

try:
    # Make the API request
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

    # Parse the JSON response
    api_data = response.json()
    subdomain_count = api_data.get('subdomain_count')
    subdomains = api_data.get('subdomains', [])
    
    output_filename = f"securitytrails_subdomains_{DOMAIN}.txt"

    # Write the found subdomains to a file
    with open(output_filename, 'w') as f:
        for subdomain in subdomains:
            f.write(f"{subdomain}.{DOMAIN}\n")
            
    print(f"Found {subdomain_count} subdomains. Results saved successfully to {output_filename}")

except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Response content: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Connection Error: {e}")
except json.JSONDecodeError:
    print("Error: Failed to parse JSON response.")