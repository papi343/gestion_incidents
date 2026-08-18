"""
Script DDL de création des tables MySQL (utilisateur, incident, intervention).
"""

import sys
import os

import mysql.connector
from database.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from database.connexion import Connexion


def creer_database():
    """Crée la base de données MySQL si elle n'existe pas encore."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            autocommit=True
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4;")
        conn.close()
        print(f"[SUCCESS] Base de données '{DB_NAME}' vérifiée/créée.")
    except mysql.connector.Error as e:
        print(f"[ERREUR MYSQL] Connexion impossible au serveur MySQL ({e}).")
        raise e


def creer_tables():
    """Exécute les requêtes DDL pour créer la base et les 3 tables MySQL requises."""
    creer_database()
    db = Connexion()
    with db.get_cursor(dictionary=False) as cursor:
        # Table Utilisateur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS utilisateur (
                id INT AUTO_INCREMENT PRIMARY KEY,
                login VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                nom VARCHAR(100) NOT NULL,
                prenom VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'UTILISATEUR',
                service VARCHAR(100) NOT NULL DEFAULT 'Général',
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Table Incident
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incident (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titre VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                priorite VARCHAR(50) NOT NULL DEFAULT 'MOYENNE',
                statut VARCHAR(50) NOT NULL DEFAULT 'OUVERT',
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                utilisateur_id INT NOT NULL,
                FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Table Intervention
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS intervention (
                id INT AUTO_INCREMENT PRIMARY KEY,
                commentaire TEXT NOT NULL,
                duree_minutes INT NOT NULL DEFAULT 0,
                date_intervention DATETIME DEFAULT CURRENT_TIMESTAMP,
                incident_id INT NOT NULL,
                technicien_id INT NOT NULL,
                FOREIGN KEY (incident_id) REFERENCES incident(id),
                FOREIGN KEY (technicien_id) REFERENCES utilisateur(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        db.commit()
    print("[SUCCESS] Tables créées avec succès dans la base de données MySQL.")


if __name__ == "__main__":
    creer_tables()


