import requests
import json
import socket
import os
import time
from dotenv import load_dotenv

load_dotenv()

def dnsdumpster_subdomains(domain_cache: dict, domain: str):
    API_KEY = os.getenv("API_KEY_DNSDUMPSTER")
    url = f"https://api.dnsdumpster.com/domain/{domain}"
    HEADERS = {"X-API-Key" : API_KEY}
    print("Pobieranie subdomen z DNSdumpster...")
    try:
        response = requests.get(url, headers= HEADERS)
        api_data = response.json()
        hosts = api_data.get('a', [])
        for item in hosts:
            subdomain = item.get('host')
            if item.get('ips'):
                ip_address = item['ips'][0].get('ip')
                add_to_cache(domain_cache, subdomain, [ip_address])

    except requests.exceptions.HTTPError as e:
        print(f"Błąd HTTP: {e}")
        print(f"Treść odpowiedzi: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Błąd połączenia: {e}")
        
    except json.JSONDecodeError:
        print("Błąd: Nie udało się sparsować odpowiedzi JSON.")

def securitytrails_subdomains(domain_cache: dict, domain: str):
    API_KEY = os.getenv("API_KEY_SECURITYTRAILS")
    url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
    HEADERS = {"apikey" : API_KEY}
    print("Pobieranie subdomen z SecurityTrails...")
    try:
        response = requests.get(url, headers=HEADERS)
        api_data = response.json()
        subdomains = api_data.get('subdomains')
        print(f'Znaleziono {len(subdomains)} domen przez SecurityTrails, trwa rezolucja DNS...')
        for subdomain in subdomains:
            hostname = f'{subdomain}.{domain}'
            if hostname in domain_cache:
                continue
            else:
                try:
                    ip = socket.gethostbyname(hostname)
                    add_to_cache(domain_cache, hostname, [ip])
                except socket.gaierror:
                    print(f"Nie znaleziono IP dla {hostname}")
        
    except requests.exceptions.HTTPError as e:
        print(f"Błąd HTTP: {e}")
        print(f"Treść odpowiedzi: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Błąd połączenia: {e}")
        
    except json.JSONDecodeError:
        print("Błąd: Nie udało się sparsować odpowiedzi JSON.")

def virustotal_subdomains(domain_cache: dict, domain: str):
    API_KEY = os.getenv("API_KEY_VIRUSTOTAL")
    current_url = f"https://www.virustotal.com/api/v3/domains/{domain}/subdomains?limit=40"
    HEADERS = {"x-apikey": API_KEY}
    all_results = []
    page_count = 1

    session = requests.Session()
    session.headers.update(HEADERS)

    print("Pobieranie subdomen z VirusTotal...")

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
                
                if subdomain_name and len(ip_addresses) > 0:
                    add_to_cache(domain_cache, subdomain_name, ip_addresses)

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

def add_to_cache(domain_cache: dict, subdomain: str, ips: list):
    if subdomain in domain_cache:
        for ip in ips:
            if ip not in domain_cache[subdomain]:
                domain_cache[subdomain].append(ip)
    else:
        domain_cache[subdomain] = ips

def find_subdomains(domain: str, filename: str):
    domain_cache = {}
    dnsdumpster_subdomains(domain_cache, domain)
    virustotal_subdomains(domain_cache, domain)
    securitytrails_subdomains(domain_cache, domain)
    print(f"Znaleziono łącznie {len(domain_cache)} domen")
    with open(filename, 'w') as f:
        for subdomain in domain_cache:
            f.write(f'{subdomain}; {domain_cache[subdomain]}\n')

    print(f"Wynik działania programu zapisany do pliku {filename}")


    
