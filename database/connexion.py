"""
Classe Connexion implémentant le pattern Singleton.
"""

import mysql.connector
from .config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


class Connexion:
    """Singleton pour gérer la connexion unique à la base de données MySQL."""

    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_connection(self):
        """Retourne la connexion MySQL active ou en ouvre une nouvelle."""
        if self._connection is None or not self._connection.is_connected():
            try:
                self._connection = mysql.connector.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME,
                    autocommit=False
                )
            except mysql.connector.Error as e:
                print(f"\n[ERREUR MYSQL] Connexion impossible à la base '{DB_NAME}' sur {DB_HOST}:{DB_PORT} ({e}).")
                raise e
        return self._connection

    def get_cursor(self, dictionary=True):
        """Retourne un curseur MySQL (dictionnaire par défaut)."""
        return self.get_connection().cursor(dictionary=dictionary)

    def commit(self):
        """Valide la transaction en cours."""
        if self._connection and self._connection.is_connected():
            self._connection.commit()

    def rollback(self):
        """Annule la transaction en cours en cas d'erreur."""
        if self._connection and self._connection.is_connected():
            self._connection.rollback()

    def close(self):
        """Ferme proprement la connexion à la base de données."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None
