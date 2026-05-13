#!/usr/bin/env python3
"""
update_cmdb.py — Enregistre les changements de remédiation dans Postgres
"""

import json
import sys
from datetime import datetime
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("[!] psycopg2 non installé — pip install psycopg2-binary")
    sys.exit(1)


def connect():
    return psycopg2.connect(
        host="localhost",
        dbname="hardening_cmdb",
        user="hardening",
        password="hardening123"
    )


def load_changes(results_dir):
    """Charge les fichiers JSON d'audit."""
    results = []
    for f in Path(results_dir).glob("*_audit.json"):
        with open(f) as fp:
            data = json.load(fp)
            host = f.stem.replace("_audit", "")
            results.append({"host": host, "controls": data})
    return results


def insert_changes(results, executor="ansible"):
    conn = connect()
    cur = conn.cursor()
    inserted = 0

    for r in results:
        host = r["host"]
        for ctrl in r["controls"]:
            cur.execute("""
                INSERT INTO config_changes
                    (host, control_id, description, before_val,
                     after_val, changed, executor)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                host,
                ctrl["cis_id"],
                ctrl["description"],
                ctrl["valeur_actuelle"],
                ctrl["valeur_attendue"],
                ctrl["status"] == "FAIL",
                executor
            ))
            inserted += 1

    conn.commit()
    cur.close()
    conn.close()
    return inserted


def show_report():
    """Affiche un résumé de la CMDB."""
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT host, control_id, description, before_val, changed, timestamp
        FROM config_changes
        ORDER BY timestamp DESC
        LIMIT 20
    """)
    rows = cur.fetchall()

    print("\n════════════════════════════════════════════════")
    print(" CMDB — Derniers enregistrements")
    print("════════════════════════════════════════════════")
    for row in rows:
        status = "FAIL" if row[4] else "PASS"
        color = "\033[91m" if row[4] else "\033[92m"
        reset = "\033[0m"
        print(f" {color}[{status}]{reset} {row[0]} | {row[1]} | {row[2]}")
        print(f"        Valeur : {row[3]} | {row[5].strftime('%Y-%m-%d %H:%M')}")
    print("════════════════════════════════════════════════\n")

    cur.close()
    conn.close()


def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hardening-results"

    print(f"[*] Chargement depuis : {results_dir}")
    results = load_changes(results_dir)

    if not results:
        print("[!] Aucun résultat trouvé.")
        sys.exit(1)

    print(f"[*] {len(results)} hôte(s) trouvé(s)")
    inserted = insert_changes(results)
    print(f"[+] {inserted} enregistrement(s) insérés dans la CMDB")

    show_report()


if __name__ == "__main__":
    main()
