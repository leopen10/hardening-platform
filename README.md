# Hardening Platform

![CI](https://github.com/leopen10/hardening-platform/actions/workflows/ci.yml/badge.svg)

Plateforme d'automatisation du durcissement de sécurité conforme aux **CIS Benchmarks**
sur des parcs Linux et Windows Server.

## Problème résolu

Les équipes ops gèrent des centaines de VMs avec des configurations de sécurité
hétérogènes. Vérifier et corriger manuellement ~300 contrôles CIS par machine est
impossible à l'échelle. Ce projet automatise l'audit, la remédiation et la traçabilité.

## Ce que fait ce projet

- **Audit** — détecte les écarts CIS sur Linux (RedHat, Ubuntu) et Windows Server 2022
- **Remédiation** — corrige automatiquement les failles, de façon idempotente
- **Reporting** — génère un rapport HTML/JSON exploitable par les équipes sécurité
- **CMDB** — trace chaque changement dans Postgres (ou ServiceNow)

## Stack technique

| Composant | Technologie |
|---|---|
| Orchestration | Ansible 2.16+ |
| Systèmes cibles | Ubuntu 22.04, RedHat 8/9, Windows Server 2022 |
| Benchmark | CIS Benchmark Niveau 1 & 2 |
| Reporting | Python 3.12 |
| CMDB | PostgreSQL 16 |
| CI/CD | GitHub Actions |

## Résultats

Avant remédiation    Après remédiation
─────────────────────────────────────
[FAIL] 5.2.1    →   [PASS] SSH root login désactivé
[FAIL] 4.1.1    →   [PASS] auditd installé et actif
[FAIL] 5.3.1    →   [PASS] Longueur mot de passe >= 14
[FAIL] 3.2.1    →   [PASS] ICMP redirects refusés

## Installation

```bash
git clone https://github.com/leopen10/hardening-platform.git
cd hardening-platform
pip install psycopg2-binary
ansible-galaxy install -r ansible/requirements.yml
```

## Usage

```bash
# Audit uniquement
cd ansible
ansible-playbook -i inventory/hosts.ini playbooks/audit.yml \
  --ask-pass --ask-become-pass \
  -e "results_dir=/tmp/hardening-results"

# Remédiation
ansible-playbook -i inventory/hosts.ini playbooks/remediate.yml \
  --ask-pass --ask-become-pass \
  -e "results_dir=/tmp/hardening-results"

# Générer le rapport HTML
python3 scripts/generate_report.py /tmp/hardening-results ./reports

# Mettre à jour la CMDB
python3 scripts/update_cmdb.py /tmp/hardening-results
```

## Structure

hardening-platform/
├── ansible/
│   ├── inventory/          # Machines cibles
│   ├── group_vars/         # Variables par groupe
│   ├── roles/
│   │   ├── audit_linux/    # 13 contrôles CIS
│   │   └── remediate_linux/# Corrections idempotentes
│   └── playbooks/          # Orchestration
├── scripts/
│   ├── generate_report.py  # Rapport HTML/JSON
│   └── update_cmdb.py      # Intégration CMDB
└── .github/workflows/      # CI GitHub Actions

## Auteur

**Leonel Pengou** — Cloud & DevOps junior
[GitHub](https://github.com/leopen10) •
[LinkedIn](https://linkedin.com/in/leonel-magloire-pengou-mba)



