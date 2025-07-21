import duckdb
import argparse

"""
Domain Relationship Finder via Shared TXT Records.

This script analyzes a collection of Parquet files containing DNS TXT record data
to uncover relationships between domains. It identifies domains that share the same
TXT records with a specified target domain, potentially indicating they are
managed by the same entity.

The script is designed to be run from the command line and uses DuckDB for
efficient, in-memory processing of the Parquet files.

Example Usage:
    python related_subdomains.py /path/to/parquet_files/ verizon
"""

def main(folder, domain):
    """
    Executes the main logic to find and print related domains based on shared TXT records.

    The function connects to an in-memory DuckDB database, runs a complex SQL query
    to find connections, and prints the results to the console.

    Args:
        folder (str): The path to the directory containing Parquet files.
                      These files are expected to have at least 'txt_text' and 'query_name' columns.
        domain (str): A string fragment of the domain to use as the starting
                      point for finding relationships (e.g., 'google').
    """
    con = duckdb.connect()

    # The SQL query is structured with Common Table Expressions (CTEs) for clarity.
    query = f"""
    -- CTE 1: 'shared_txt'
    -- First, find all TXT record values ('txt_text') that appear in more than
    -- one unique domain ('query_name'). These are potential "fingerprints"
    -- that can link different domains together.
    WITH shared_txt AS (
        SELECT txt_text
        FROM read_parquet('{folder}/*')
        GROUP BY txt_text
        HAVING COUNT(DISTINCT query_name) > 1
    ),

    -- CTE 2: 'domain_related'
    -- Next, filter the list of shared TXT records to find only those that are
    -- associated with the specific 'domain' provided by the user.
    domain_related AS (
        SELECT DISTINCT s.txt_text
        FROM shared_txt s
        JOIN read_parquet('{folder}/*') t
          ON s.txt_text = t.txt_text
        WHERE t.query_name LIKE '%{domain}%'
    )

    -- Final SELECT Statement:
    -- Now, find all domains that use the TXT records we identified in 'domain_related'.
    SELECT DISTINCT t.txt_text, t.query_name
    FROM read_parquet('{folder}/*') t
    WHERE
        -- The TXT record must be one of the records associated with the target domain.
        t.txt_text IN (SELECT txt_text FROM domain_related)

        -- Exclude common and non-identifying TXT records to reduce noise.
        -- These records (DMARC, SPF, DKIM, etc.) are often identical across
        -- many unrelated domains and don't indicate a unique relationship.
        AND t.txt_text NOT LIKE '%v=DMARC1%'
        AND t.txt_text NOT LIKE '%v=spf1%'
        AND t.txt_text NOT LIKE '%include:%'
        AND t.txt_text NOT LIKE '%dmarc%'
        AND t.txt_text NOT LIKE '%yandex%'
        AND t.txt_text NOT LIKE '%v=DKIM1%'
        AND t.txt_text NOT LIKE '%proxy-ssl.webflow.com%'
        AND t.txt_text NOT LIKE '%mailru-verification%'

        -- Crucially, exclude the original input domain from the final results.
        -- We want to see *other* domains related to it, not the domain itself.
        AND t.query_name NOT LIKE '%{domain}%'

    -- Order the results for readability.
    ORDER BY t.txt_text, t.query_name
    """

    result = con.execute(query).fetchall()

    for row in result:
        print(row)

    print(f"Found {len(result)} related domains.")


if __name__ == "__main__":
    # Setup command-line argument parsing.
    parser = argparse.ArgumentParser(
        description="Find domain relationships via shared TXT records in Parquet files."
    )
    parser.add_argument(
        "folder",
        type=str,
        help="Path to the folder containing the Parquet files."
    )
    parser.add_argument(
        "domain",
        type=str,
        help="A part of the domain name to search for (e.g., 'verizon')."
    )
    args = parser.parse_args()

    # Run the main function with the provided arguments.
    main(args.folder, args.domain)