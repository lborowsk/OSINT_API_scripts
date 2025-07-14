import json

# Nazwa pliku wejściowego z danymi JSON
input_filename = 'subdomains_output.json'

# Nazwa pliku wyjściowego, który zostanie stworzony
output_filename = 'subdomains_list.txt'

try:
    # Otwórz i wczytaj istniejący plik JSON
    with open(input_filename, 'r', encoding='utf-8') as f_in:
        data = json.load(f_in)

    # Otwórz nowy plik tekstowy do zapisu
    with open(output_filename, 'w', encoding='utf-8') as f_out:
        print(f"Tworzę plik: {output_filename}")
        
        # Przejdź przez każdy element (słownik) na liście
        for item in data:
            subdomain = item['subdomain']
            ips = item['ips']
            
            # Sformatuj listę IP do postaci stringa, np. "[8.8.8.8, 1.1.1.1]"
            ips_as_string = str(ips)
            
            # Zapisz sformatowaną linię do pliku tekstowego
            f_out.write(f"{subdomain} : {ips_as_string}\n")
            
    print("Zakończono. Plik został pomyślnie utworzony.")

except FileNotFoundError:
    print(f"Błąd: Nie znaleziono pliku '{input_filename}'.")
except (KeyError, TypeError):
    print(f"Błąd: Dane w pliku '{input_filename}' mają nieoczekiwaną strukturę.")
except Exception as e:
    print(f"Wystąpił nieoczekiwany błąd: {e}")