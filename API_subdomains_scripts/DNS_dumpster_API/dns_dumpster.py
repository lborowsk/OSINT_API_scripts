import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY_DNSDUMPSTER")
DOMAIN = "orange.pl"
url = f"https://api.dnsdumpster.com/domain/{DOMAIN}"
HEADERS = {"X-API-Key" : API_KEY}

try:
    response = requests.get(url, headers= HEADERS)
    api_data = response.json()
    hosts = api_data.get('a', [])
    with open("dnsdumpster_subdomains.txt", 'w') as f:
        for item in hosts:
            subdomain = item.get('host')
            if item.get('ips'):
                ip_address = item['ips'][0].get('ip')
                f.write(f"{subdomain} : {ip_address}\n")

except requests.exceptions.HTTPError as e:
    print(f"Błąd HTTP: {e}")
    print(f"Treść odpowiedzi: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"Błąd połączenia: {e}")
    
except json.JSONDecodeError:
    print("Błąd: Nie udało się sparsować odpowiedzi JSON.")