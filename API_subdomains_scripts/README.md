# Subdomain Finder from Multiple API Sources

This project contains a collection of Python scripts designed to gather subdomain information from various public APIs. The main script aggregates the results from all sources, removes duplicates, and saves the final list to a single text file.

---

## Project Contents

The folder contains the following files:

* `find_all_subdomains.py` - **The main aggregator script**. It runs modules for each source, collects the results, removes duplicates, and saves them to a single file. **This is the script you should use for a comprehensive scan.**
* `dns_dumpster.py` - A standalone script for fetching subdomains from the DNSdumpster API.
* `securitytrails_subdomains.py` - A standalone script for fetching subdomains from the SecurityTrails API.
* `virustotal.py` - A standalone script for fetching subdomains from the VirusTotal API.

---

## Installation and Configuration

Follow the steps below to correctly run the scripts.

### 1. Install Dependencies

The scripts require the `requests` library (for API queries) and `python-dotenv` (for managing API keys). Install them using `pip`:

```bash
pip install requests python-dotenv
```
### 2. Configure API Keys
The scripts require access to API keys, which should be stored securely.

In the main API_subdomains_scripts folder, create a file named .env. Then, paste the following content into it and fill in your API keys for each service:

```
# .env file for storing API keys

API_KEY_DNSDUMPSTER="Your_API_key_from_dnsdumpster.com_here"
API_KEY_SECURITYTRAILS="Your_API_key_from_securitytrails.com_here"
API_KEY_VIRUSTOTAL="Your_API_key_from_virustotal.com_here"
Important: The .env file should never be shared publicly or added to public Git repositories.
```

## Usage

### Using the Aggregator Script (Recommended)
The primary way to use this project is by running the find_all_subdomains.py script.

Open the find_all_subdomains.py file in a code editor.

Find the if __name__ == '__main__': block at the end of the file.

Change the value of the target_domain variable to the domain you want to scan.

```Python
if __name__ == '__main__':
    target_domain = "orange.pl"  # <--- CHANGE THIS VALUE
    output_filename = f"{target_domain}_subdomains.txt"
    find_subdomains(target_domain, output_filename)
```

Run the script from your terminal:

```Bash
python find_all_subdomains.py
The script will begin collecting data from all configured sources and will save the results to a file named your_domain_subdomains.txt.
```
### Using Individual Scripts
Each of the scripts (dns_dumpster.py, securitytrails_subdomains.py, and virustotal.py) can also be run separately. They require a similar modification—you need to manually set the DOMAIN variable at the beginning of each file. They are mainly intended for testing individual data sources.

### Output Format
The resulting .txt file contains a list of unique subdomains along with their assigned IP addresses. Each line has the following format:

subdomain; ['list of IP addresses']
Example:
```
store.orange.com; ['192.168.1.1', '192.168.1.2']
mail.orange.com; ['10.0.0.1']
dev.orange.com; []
```
