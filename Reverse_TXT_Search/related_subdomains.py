import duckdb
import argparse


def main(folder, domain):
    con = duckdb.connect()
    query = f"""
    WITH shared_txt AS (
        SELECT txt_text
        FROM read_parquet('{folder}/*')
        GROUP BY txt_text
        HAVING COUNT(DISTINCT query_name) > 1
    ),
    domain_related AS (
        SELECT DISTINCT s.txt_text
        FROM shared_txt s
        JOIN read_parquet('{folder}/*') t
          ON s.txt_text = t.txt_text
        WHERE t.query_name LIKE '%{domain}%'
    )
    SELECT DISTINCT t.txt_text, t.query_name
    FROM read_parquet('{folder}/*') t
    WHERE t.txt_text IN (SELECT txt_text FROM domain_related)
      AND t.txt_text NOT LIKE '%v=DMARC1%'
      AND t.txt_text NOT LIKE '%v=spf1%'
      AND t.txt_text NOT LIKE '%include:%'
      AND t.txt_text NOT LIKE '%dmarc%'
      AND t.txt_text NOT LIKE '%yandex%'
      AND t.txt_text NOT LIKE '%v=DKIM1%'
      AND t.txt_text NOT LIKE '%proxy-ssl.webflow.com%'
      AND t.txt_text NOT LIKE '%mailru-verification%'
      AND t.query_name NOT LIKE '%{domain}%'
    ORDER BY t.txt_text, t.query_name
    """
    result = con.execute(query).fetchall()
    for row in result:
        print(row)
    print(f"{len(result)} domains found")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Znajdź powiązania domen przez TXT w plikach Parquet.")
    parser.add_argument("folder", type=str, help="Ścieżka do folderu z plikami Parquet")
    parser.add_argument("domain", type=str, help="Fragment domeny do wyszukania (np. verizon)")
    args = parser.parse_args()
    main(args.folder, args.domain)