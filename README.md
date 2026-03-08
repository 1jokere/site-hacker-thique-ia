# site-hacker-thique-ia
site web sur le hack ia éthique

## Agent de gestion PC (local)

Un script Python est fourni pour démarrer un agent local basique qui peut:
- afficher les infos système,
- donner le statut CPU/RAM/disque,
- lister les processus,
- lancer quelques applications autorisées,
- arrêter un processus via PID (avec confirmation).

### Lancer l'agent

```bash
python3 pc_manager_agent.py
```

### Dépendance optionnelle

Pour les métriques système et la gestion des processus:

```bash
pip install psutil
```

