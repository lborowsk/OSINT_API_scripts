import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY_VIRUSTOTAL")
DOMAIN = "orange.pl"
current_url = f"https://www.virustotal.com/api/v3/domains/{DOMAIN}/subdomains?limit=40"
HEADERS = {"x-apikey": API_KEY}

all_results = {}
page_count = 1

session = requests.Session()
session.headers.update(HEADERS)

print(f"Rozpoczynam pobieranie subdomen dla: {DOMAIN}")

while current_url:
    try:
        print(f"Pobieram stronę nr {page_count}...")
        response = session.get(current_url)
        response.raise_for_status()

        api_data = response.json()

        subdomain_list = api_data.get('data', [])
        for item in subdomain_list:
            subdomain_name = item.get('id')
            attributes = item.get('attributes', {})
            dns_records = attributes.get('last_dns_records', [])
            
            ip_addresses = [
                record.get('value')
                for record in dns_records
                if record.get('type') in ('A')
            ]
            
            if subdomain_name:
                all_results[subdomain_name] = ip_addresses

        current_url = api_data.get('links', {}).get('next')
        
        page_count += 1

        if current_url:
            time.sleep(1) 

    except requests.exceptions.HTTPError as e:
        print(f"Błąd HTTP: {e}")
        print(f"Treść odpowiedzi: {response.text}")
        break
    except requests.exceptions.RequestException as e:
        print(f"Błąd połączenia: {e}")
        break
    except json.JSONDecodeError:
        print("Błąd: Nie udało się sparsować odpowiedzi JSON.")
        break

print("\nZakończono pobieranie wszystkich subdomen.")
print(f"Łącznie znaleziono {len(all_results)} subdomen na {page_count - 1} stronach.")

with open('subdomains_output.json', 'w', encoding='utf-8') as f:
    for subdomain in all_results:
        f.write(f"{subdomain} : {ip_addresses}")

print("\nWyniki zostały zapisane do pliku 'subdomains_output.txt'")