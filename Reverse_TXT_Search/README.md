# Reverse TXT Domain Relationship Finder

This script analyzes DNS data sets in Parquet format to uncover hidden relationships between domains. It identifies domains that share the same unique TXT records, which can indicate that they are managed by the same entity or use the same infrastructure. This is a useful tool for security analysis and internet asset mapping.

***

## Data Source

The script is designed to work with Parquet files containing Forward DNS data. The recommended data source is the archives provided by **OpenINTEL.nl**.

You can download the files from:
[https://openintel.nl/data/forward-dns/top-lists/](https://openintel.nl/data/forward-dns/top-lists/)

You should download the archives of interest (e.g., from popular domain lists) and then extract all `.parquet` files into a single, common folder.

***

## Requirements

* Python 3.x
* DuckDB library

You can install the required library using `pip`:
```bash
pip install duckdb

## Usage

The script is run from the command line and takes two mandatory arguments:

* **folder**: The path to the folder containing the `.parquet` files.
* **domain**: A fragment of the domain name for which you want to find relationships (e.g., `google`, `cloudflare`, `verizon`).

### Example
Let's assume your Parquet files are located in the `/data/dns/` directory. To find domains related to `verizon`, use the command:

```bash
python reverse_txt.py /data/dns/ verizon

## How It Works 🤔

The script's logic is based on an SQL query executed by **DuckDB**, which efficiently processes the Parquet files directly in memory. The process occurs in several steps:

1.  **Find Shared Records**: The script first finds all TXT records that are used by more than one unique domain.
2.  **Identify Target Domain's Records**: It then filters these shared records to isolate only those associated with the domain provided as the `domain` argument.
3.  **Find Related Domains**: In the final step, the script searches for all *other* domains that also use the previously identified TXT records.
4.  **Filter Noise**: The results are cleaned of common, generic records (such as SPF, DMARC, DKIM, and verification keys for popular services) that do not indicate a unique relationship but rather the use of the same popular technologies.

---

## Output Format

The script prints a list of found relationships to the standard output (your console). Each line represents one relationship and has the format `('shared_txt_record', 'related_domain')`.

At the end, a summary with the total number of found domains is displayed.

### Example Output
('google-site-verification=ABC...xyz', 'related-domain-one.com')
('facebook-domain-verification=123...789', 'another-related-domain.org')
('adobe-idp-site-verification=...', 'company-site.co.uk')
Found 3 related domains.