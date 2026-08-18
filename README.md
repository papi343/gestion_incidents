# Gestion des Tickets d'Incidents (Help Desk)

Projet de Programmation Python - POO & Base de données  
**Établissement :** Groupe ISI - Licence 2 Génie Logiciel (GL)  
**Enseignant :** M. DIALLO  

---

## 📌 Présentation du Projet

Application console (CLI) développée en Python (POO) pour la gestion automatisée des incidents informatiques au sein d'une Direction des Systèmes d'Information (DSI).

Elle propose une gestion multi-rôles avec contrôle d'accès :
- **UTILISATEUR** : Signalement d'incidents, suivi de l'avancement, consultation des détails et interventions.
- **TECHNICIEN** : Prise en charge des incidents, enregistrement des interventions avec durée, résolution et fermeture des tickets.
- **ADMINISTRATEUR** : Superviseur du système, gestion complète des utilisateurs (CRUD), suivi global et génération de tableaux de bord statistiques avancés.

---

## 📂 Structure du Projet

```text
gestion_incidents/
│
├── database/
│   ├── __init__.py
│   ├── config.py          # Configuration du chemin et paramètres de la BD
│   └── connexion.py       # Pattern Singleton pour l'accès unique à la BD
│
├── models/
│   ├── __init__.py
│   ├── utilisateur.py     # Modèle POO Utilisateur
│   ├── incident.py        # Modèle POO Incident
│   └── intervention.py    # Modèle POO Intervention
│
├── dao/
│   ├── __init__.py
│   ├── base_dao.py        # Classe abstraite avec méthodes génériques CRUD
│   ├── utilisateur_dao.py # DAO Utilisateur + Authentification + Contraintes
│   ├── incident_dao.py    # DAO Incident + Workflow Statuts + Statistiques
│   └── intervention_dao.py# DAO Intervention + Validation des règles
│
├── menu/
│   ├── __init__.py
│   ├── auth.py            # Gestionnaire d'authentification et session
│   └── interface.py       # Interface console dynamique selon le rôle
│
├── create_tables.py       # Script DDL de création des 3 tables SQL
├── insert_test_data.py    # Script d'insertion du jeu de données de test
├── main.py                # Point d'entrée principal de l'application
├── README.md              # Documentation du projet
└── requirements.txt       # Fichier de dépendances
```

---

## 🛠️ Exigences et Contraintes Techniques Respectées

1. **Pattern Singleton** : Implémenté dans `Connexion` ([connexion.py](file:///c:/Users/ydabo/OneDrive/Bureau/projet%20python/gestion_incidents/database/connexion.py)).
2. **Héritage POO** : Classe abstraite `BaseDAO` ([base_dao.py](file:///c:/Users/ydabo/OneDrive/Bureau/projet%20python/gestion_incidents/dao/base_dao.py)) héritée par tous les DAO.
3. **Sécurité SQL** : Utilisation exclusive de **requêtes SQL paramétrées** (prévention des injections SQL).
4. **Transactions & Intégrité** : Gestion explicite de `commit()` et `rollback()`.
5. **Gestion des Erreurs** : Captures `try/except` sur toutes les opérations sensibles.
6. **Respect des Conventions PEP 8** : Code lisible, épuré et entièrement commenté en français.

---

## 🔄 Workflow des Statuts d'Incidents

L'application garantit qu'un statut **ne peut jamais reculer** :
- `OUVERT` ➡️ `EN_COURS` (Prise en charge par un technicien)
- `EN_COURS` ➡️ `RESOLU` (Résolution de l'incident)
- `RESOLU` ➡️ `FERME` (Clôture définitive)
- `OUVERT` ➡️ `ANNULE` (Annulation possible par l'utilisateur)

---

## 🚀 Installation et Exécution

### 1. Prérequis
- Python 3.8+
- Serveur MySQL (MySQL Server, XAMPP, WampServer ou Docker)
- Installation du connecteur Python MySQL :
  ```bash
  pip install -r requirements.txt
  ```

### 2. Base de Données MySQL
1. Assurez-vous que votre serveur MySQL est démarré.
2. Créez la base de données `gestion_incidents` (par exemple via phpMyAdmin ou MySQL CLI) :
   ```sql
   CREATE DATABASE gestion_incidents;
   ```
3. *(Optionnel)* Si vos identifiants diffèrent des valeurs par défaut (`localhost:3306`, `root`, mot de passe vide), vous pouvez configurer les variables d'environnement `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` ou modifier le fichier [database/config.py](file:///c:/Users/ydabo/OneDrive/Bureau/projet%20python/gestion_incidents/database/config.py).

### 3. Lancement
Exécutez la commande suivante à la racine du projet :

```bash
python main.py
```

*Remarque : Les tables de la base de données MySQL et le jeu de données de test sont automatiquement initialisés au lancement.*


---

## 🔑 Comptes de Test pré-configurés

| Identifiant (Login) | Mot de passe | Rôle | Nom / Service |
| :--- | :--- | :--- | :--- |
| **`admin`** | `admin123` | **ADMIN** | Amadou DIOP (Informatique) |
| **`tndoye`** | `tech123` | **TECHNICIEN** | Samba NDOYE (Support IT) |
| **`mfall`** | `tech123` | **TECHNICIEN** | Modou FALL (Réseau) |
| **`jdupont`** | `user123` | **UTILISATEUR** | Jean DUPONT (Comptabilité) |
| **`mmbaye`** | `user123` | **UTILISATEUR** | Mariama MBAYE (RH) |

---

## 📊 Rapports et Statistiques (Admin)

L'administrateur a accès au dashboard incluant :
- Total d'incidents par statut et par priorité.
- Temps moyen de résolution par incident (en heures).
- Top 3 des techniciens les plus actifs (nombre d'interventions).
- Nombre d'incidents traités et temps moyen par technicien.
- Taux de résolution sous 48h (pourcentage).
