import requests
import json
import socket
import os
import time
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

"""
Subdomain Aggregator Script

This script collects subdomains for a given domain from multiple public APIs:
- DNSdumpster
- SecurityTrails
- VirusTotal
- HackerTarget

It aggregates the results, resolves IP addresses, and saves the unique
subdomains and their corresponding IPs into a single output file.
The script uses a cache to avoid redundant processing.

Prerequisites:
- A .env file with API keys:
  - API_KEY_DNSDUMPSTER
  - API_KEY_SECURITYTRAILS
  - API_KEY_VIRUSTOTAL
"""

def dnsdumpster_subdomains(domain_cache: dict, domain: str):
    """
    Fetches subdomains from the DNSdumpster API.

    Args:
        domain_cache (dict): The shared cache to store found subdomains and IPs.
        domain (str): The target domain to query.
    """
    API_KEY = os.getenv("API_KEY_DNSDUMPSTER")
    url = f"https://api.dnsdumpster.com/domain/{domain}"
    HEADERS = {"X-API-Key" : API_KEY}
    print("Fetching subdomains from DNSdumpster...")
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        api_data = response.json()
        
        # Extract hosts from the 'a' records section
        hosts = api_data.get('a', [])
        for item in hosts:
            subdomain = item.get('host')
            if item.get('ips'):
                ip_address = item['ips'][0].get('ip')
                add_to_cache(domain_cache, subdomain, [ip_address])

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response content: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON response.")

def securitytrails_subdomains(domain_cache: dict, domain: str):
    """
    Fetches subdomains from the SecurityTrails API and resolves their IPs.

    Args:
        domain_cache (dict): The shared cache to store found subdomains and IPs.
        domain (str): The target domain to query.
    """
    API_KEY = os.getenv("API_KEY_SECURITYTRAILS")
    url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
    HEADERS = {"apikey" : API_KEY}
    print("Fetching subdomains from SecurityTrails...")
    
    unresolved_count = 0
    dns_query_count = 0
    already_found_count = 0

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        api_data = response.json()
        subdomains = api_data.get('subdomains', [])
        
        print(f'Found {len(subdomains)} subdomains via SecurityTrails, starting DNS resolution...')
        for subdomain in subdomains:
            hostname = f'{subdomain}.{domain}'
            
            # Skip if already processed
            if hostname in domain_cache:
                already_found_count += 1
                continue
            
            # Resolve IP address for the new subdomain
            try:
                ip = socket.gethostbyname(hostname)
                add_to_cache(domain_cache, hostname, [ip])
            except socket.gaierror:
                # This happens if the hostname cannot be resolved
                unresolved_count += 1
            
            dns_query_count += 1
            if dns_query_count % 100 == 0:
                print(f"DNS Resolution: {dns_query_count}/{len(subdomains)} subdomains checked...")
        
        print(f"Could not resolve IPs for {unresolved_count} subdomains. {already_found_count} were found previously.")
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response content: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON response.")

def virustotal_subdomains(domain_cache: dict, domain: str):
    """
    Fetches subdomains and their last known IPs from the VirusTotal API.
    Handles pagination to retrieve all available results.

    Args:
        domain_cache (dict): The shared cache to store found subdomains and IPs.
        domain (str): The target domain to query.
    """
    API_KEY = os.getenv("API_KEY_VIRUSTOTAL")
    current_url = f"https://www.virustotal.com/api/v3/domains/{domain}/subdomains?limit=40"
    HEADERS = {"x-apikey": API_KEY}
    page_count = 1

    session = requests.Session()
    session.headers.update(HEADERS)

    print("Fetching subdomains from VirusTotal...")

    while current_url:
        try:
            print(f"Fetching page number {page_count}...")
            response = session.get(current_url)
            response.raise_for_status()

            api_data = response.json()

            # Process the list of subdomains in the current page
            subdomain_list = api_data.get('data', [])
            for item in subdomain_list:
                subdomain_name = item.get('id')
                attributes = item.get('attributes', {})
                dns_records = attributes.get('last_dns_records', [])
                
                # Extract IP addresses from 'A' records
                ip_addresses = [
                    record.get('value')
                    for record in dns_records
                    if record.get('type') == 'A'
                ]
                
                if subdomain_name and ip_addresses:
                    add_to_cache(domain_cache, subdomain_name, ip_addresses)

            # Get the URL for the next page of results
            current_url = api_data.get('links', {}).get('next')
            page_count += 1

            # Be respectful to the API rate limits
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

def hackertarget_subdomains(domain_cache: dict, domain: str):
    """
    Fetches subdomains from the HackerTarget API.

    Args:
        domain_cache (dict): The shared cache to store found subdomains and IPs.
        domain (str): The target domain to query.
    """
    url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
    print("Fetching subdomains from HackerTarget...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        subdomain_list = response.text.splitlines()
        
        for line in subdomain_list:
            if line.strip():
                parts = line.split(',')
                if len(parts) == 2:
                    subdomain, ip_address = parts
                    add_to_cache(domain_cache, subdomain, [ip_address])

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response content: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")

def add_to_cache(domain_cache: dict, subdomain: str, ips: list):
    """
    Adds a subdomain and its IP addresses to the cache.
    Avoids duplicate IPs for existing subdomains.

    Args:
        domain_cache (dict): The cache to modify.
        subdomain (str): The subdomain to add or update.
        ips (list): A list of IP addresses for the subdomain.
    """
    if subdomain in domain_cache:
        # Add only unique IPs to the existing list
        for ip in ips:
            if ip not in domain_cache[subdomain]:
                domain_cache[subdomain].append(ip)
    else:
        # Add a new entry
        domain_cache[subdomain] = ips

def find_subdomains(domain: str, filename: str):
    """
    Orchestrates the process of finding subdomains from all sources
    and saving them to a file.

    Args:
        domain (str): The target domain.
        filename (str): The name of the file to save the results.
    """
    domain_cache = {}
    
    # Call each data source function
    dnsdumpster_subdomains(domain_cache, domain)
    virustotal_subdomains(domain_cache, domain)
    securitytrails_subdomains(domain_cache, domain)
    hackertarget_subdomains(domain_cache, domain)
    
    print(f"\nFound a total of {len(domain_cache)} unique subdomains.")
    
    # Write the results to the output file
    with open(filename, 'w') as f:
        for subdomain, ips in domain_cache.items():
            f.write(f'{subdomain}; {ips}\n')

    print(f"Results have been saved to the file: {filename}")

# Example of how to run the script
if __name__ == '__main__':
    target_domain = "example.com"  # Replace with the domain you want to scan
    output_filename = f"{target_domain}_subdomains.txt"
    find_subdomains(target_domain, output_filename)