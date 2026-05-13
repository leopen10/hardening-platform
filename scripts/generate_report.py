#!/usr/bin/env python3
"""
generate_report.py — Génère un rapport HTML de conformité CIS
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def load_results(results_dir):
    """Charge tous les fichiers JSON d'audit."""
    results = []
    for f in Path(results_dir).glob("*_audit.json"):
        with open(f) as fp:
            data = json.load(fp)
            results.append({"host": f.stem.replace("_audit", ""), "controls": data})
    return results


def generate_html(results, output_path):
    """Génère le rapport HTML."""
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Calcul des stats globales
    total = sum(len(r["controls"]) for r in results)
    passed = sum(
        len([c for c in r["controls"] if c["status"] == "PASS"])
        for r in results
    )
    failed = total - passed
    rate = round((passed / total * 100) if total > 0 else 0, 1)

    # Couleur du taux
    color = "#22c55e" if rate >= 80 else "#f59e0b" if rate >= 60 else "#ef4444"

    # Lignes du tableau
    rows = ""
    for r in results:
        for c in r["controls"]:
            status_color = "#22c55e" if c["status"] == "PASS" else "#ef4444"
            rows += f"""
            <tr>
                <td>{r['host']}</td>
                <td><code>{c['cis_id']}</code></td>
                <td>{c['description']}</td>
                <td style="color:{status_color}; font-weight:600;">{c['status']}</td>
                <td><code>{c['valeur_actuelle']}</code></td>
                <td><code>{c['valeur_attendue']}</code></td>
            </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Rapport CIS — {date}</title>
<style>
  body {{ font-family: -apple-system, sans-serif; background:#0f172a; color:#e2e8f0; margin:0; }}
  .header {{ background:#1e293b; padding:2rem; border-bottom:1px solid #334155; }}
  .header h1 {{ margin:0; font-size:1.5rem; color:#f8fafc; }}
  .header p {{ margin:0.5rem 0 0; color:#94a3b8; font-size:0.9rem; }}
  .container {{ max-width:1200px; margin:0 auto; padding:2rem; }}
  .stats {{ display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin-bottom:2rem; }}
  .stat {{ background:#1e293b; border-radius:8px; padding:1.5rem; text-align:center; }}
  .stat-number {{ font-size:2rem; font-weight:700; }}
  .stat-label {{ font-size:0.8rem; color:#94a3b8; margin-top:0.25rem; }}
  table {{ width:100%; border-collapse:collapse; background:#1e293b; border-radius:8px; overflow:hidden; }}
  th {{ background:#334155; padding:0.75rem 1rem; text-align:left; font-size:0.8rem;
        text-transform:uppercase; color:#94a3b8; }}
  td {{ padding:0.75rem 1rem; border-bottom:1px solid #334155; font-size:0.85rem; }}
  tr:last-child td {{ border-bottom:none; }}
  code {{ background:#334155; padding:2px 6px; border-radius:4px; font-size:0.8rem; }}
</style>
</head>
<body>
<div class="header">
  <h1>Rapport de Conformité CIS Benchmark</h1>
  <p>Généré le {date} — Hardening Platform v1.0</p>
</div>
<div class="container">
  <div class="stats">
    <div class="stat">
      <div class="stat-number" style="color:#3b82f6;">{len(results)}</div>
      <div class="stat-label">Hôtes audités</div>
    </div>
    <div class="stat">
      <div class="stat-number" style="color:#3b82f6;">{total}</div>
      <div class="stat-label">Contrôles total</div>
    </div>
    <div class="stat">
      <div class="stat-number" style="color:#22c55e;">{passed}</div>
      <div class="stat-label">Conformes</div>
    </div>
    <div class="stat">
      <div class="stat-number" style="color:#ef4444;">{failed}</div>
      <div class="stat-label">Non conformes</div>
    </div>
  </div>
  <div class="stat" style="margin-bottom:2rem; text-align:center;">
    <div class="stat-number" style="color:{color}; font-size:3rem;">{rate}%</div>
    <div class="stat-label">Conformité globale</div>
  </div>
  <table>
    <thead>
      <tr>
        <th>Hôte</th>
        <th>ID CIS</th>
        <th>Description</th>
        <th>Statut</th>
        <th>Valeur actuelle</th>
        <th>Valeur attendue</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[+] Rapport HTML : {output_path}")


def generate_json(results, stats, output_path):
    """Génère le rapport JSON."""
    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": stats,
        "hosts": results,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"[+] Rapport JSON : {output_path}")


def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hardening-results"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./reports"

    os.makedirs(output_dir, exist_ok=True)

    print(f"[*] Chargement depuis : {results_dir}")
    results = load_results(results_dir)

    if not results:
        print("[!] Aucun résultat trouvé.")
        sys.exit(1)

    total = sum(len(r["controls"]) for r in results)
    passed = sum(
        len([c for c in r["controls"] if c["status"] == "PASS"])
        for r in results
    )
    stats = {
        "total_hosts": len(results),
        "total_controls": total,
        "passed": passed,
        "failed": total - passed,
        "compliance_rate": round((passed / total * 100) if total > 0 else 0, 1),
    }

    print(f"[*] {len(results)} hôte(s) — {total} contrôles — {stats['compliance_rate']}% conformité")

    timestamp = datetime.now().strftime("%Y-%m-%d")
    generate_html(results, f"{output_dir}/rapport_{timestamp}.html")
    generate_json(results, stats, f"{output_dir}/rapport_{timestamp}.json")

    print("[✓] Rapports générés avec succès")


if __name__ == "__main__":
    main()
