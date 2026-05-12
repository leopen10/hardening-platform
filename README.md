# Hardening Platform

Plateforme d'automatisation du durcissement de sécurité (hardening)
conforme aux CIS Benchmarks sur des parcs Linux et Windows Server.

## Ce que fait ce projet

- Audite l'état de conformité CIS (~300 contrôles) sur Linux et Windows
- Remédie automatiquement aux écarts détectés
- Génère un rapport de conformité HTML/JSON
- Trace chaque changement dans une CMDB

## Technologies

- Ansible 2.16+
- Python 3.12+
- Ubuntu 22.04 / RedHat 9 / Windows Server 2022
- CIS Benchmark Niveau 1 & 2

## Lancement rapide

```bash
# Audit uniquement
ansible-playbook -i ansible/inventory/hosts.ini ansible/playbooks/audit.yml

# Vérifier la connectivité
ansible -i ansible/inventory/hosts.ini linux_cibles -m ping
```

## Structure du projet

hardening-platform/
├── ansible/
│   ├── ansible.cfg
│   ├── inventory/
│   ├── group_vars/
│   ├── roles/
│   │   ├── audit_linux/
│   │   └── remediate_linux/
│   └── playbooks/
└── README.md

## Auteur

Leonel Pengou — Cloud & DevOps junior

