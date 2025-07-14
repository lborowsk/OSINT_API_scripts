import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY_SECURITYTRAILS")
DOMAIN = "pwr.edu.pl"
url = f"https://api.securitytrails.com/v1/domain/{DOMAIN}/subdomains"
HEADERS = {"apikey" : API_KEY}

try:
    response = requests.get(url, headers=HEADERS)
    api_data = response.json()
    subdomain_count = api_data.get('subdomain_count')
    subdomains = api_data.get('subdomains')
    with open(f"securitytrails_subdomains_{DOMAIN}.txt", 'w') as f:
        for subdomain in subdomains:
            f.write(f"{subdomain}.{DOMAIN}\n")
    print(f"Znaleziono {subdomain_count} subdomen, zapisano pomyslnie w pliku securitytrails_subdomains_{DOMAIN}.txt")

except requests.exceptions.HTTPError as e:
    print(f"Błąd HTTP: {e}")
    print(f"Treść odpowiedzi: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"Błąd połączenia: {e}")
    
except json.JSONDecodeError:
    print("Błąd: Nie udało się sparsować odpowiedzi JSON.")