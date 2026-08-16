"""
Configuration de la base de données MySQL.
Permet de définir les paramètres de connexion à MySQL.
"""

import os

# Paramètres de connexion MySQL (modifiables via variables d'environnement)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "gestion_incidents")