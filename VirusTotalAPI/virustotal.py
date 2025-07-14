import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY_VIRUSTOTAL")
DOMAIN = "orange.pl"
# Zaczynamy od pierwszego linku
current_url = f"https://www.virustotal.com/api/v3/domains/{DOMAIN}/subdomains?limit=40" # Zwiększamy limit dla mniejszej liczby zapytań
HEADERS = {"x-apikey": API_KEY}

# Lista do przechowywania wszystkich znalezionych subdomen ze wszystkich stron
all_results = []
page_count = 1

# Używamy obiektu sesji dla wydajniejszych zapytań
session = requests.Session()
session.headers.update(HEADERS)

print(f"Rozpoczynam pobieranie subdomen dla: {DOMAIN}")

# --- Pętla do obsługi paginacji ---
while current_url:
    try:
        print(f"Pobieram stronę nr {page_count}...")
        response = session.get(current_url)
        # Sprawdzenie, czy zapytanie się powiodło
        response.raise_for_status()

        api_data = response.json()

        # Przetwarzanie subdomen z bieżącej strony
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
                all_results.append({
                    "subdomain": subdomain_name,
                    "ips": ip_addresses
                })

        # --- Kluczowy element: pobranie linku do następnej strony ---
        # Bezpiecznie sprawdzamy, czy link 'next' istnieje
        current_url = api_data.get('links', {}).get('next')
        
        page_count += 1

        # Dobra praktyka: krótka przerwa, aby nie przekroczyć limitu zapytań API
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

# --- Wyświetlenie końcowych wyników ---
print("\nZakończono pobieranie wszystkich subdomen.")
print(f"Łącznie znaleziono {len(all_results)} subdomen na {page_count - 1} stronach.")

# Zapisz do pliku lub wyświetl na ekranie
# print(json.dumps(all_results, indent=2, ensure_ascii=False))

# Opcjonalnie: Zapis wyników do pliku JSON
with open('subdomains_output.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print("\nWyniki zostały zapisane do pliku 'subdomains_output.json'")