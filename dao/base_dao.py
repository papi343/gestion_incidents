"""
Classe abstraite BaseDAO fournissant les méthodes génériques CRUD d'accès aux données.
"""

from abc import ABC, abstractmethod
from database.connexion import Connexion


class BaseDAO(ABC):
    """Classe de base abstraite pour tous les DAO du système."""

    def __init__(self):
        self.db = Connexion()

    @property
    @abstractmethod
    def table_name(self):
        """Nom de la table SQL associée au DAO."""
        pass

    def get_all(self):
        """Récupère l'ensemble des enregistrements de la table."""
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name}")
                return cursor.fetchall()
        except Exception as e:
            print(f"Erreur lors de la récupération de {self.table_name}: {e}")
            return []

    def get_by_id(self, item_id):
        """Récupère un enregistrement par son identifiant unique."""
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = %s", (item_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Erreur lors de la recherche de ID {item_id} dans {self.table_name}: {e}")
            return None

    def delete_by_id(self, item_id):
        """Supprime un enregistrement par son identifiant unique."""
        try:
            with self.db.get_cursor(dictionary=False) as cursor:
                cursor.execute(f"DELETE FROM {self.table_name} WHERE id = %s", (item_id,))
                self.db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.db.rollback()
            print(f"Erreur lors de la suppression de {item_id} dans {self.table_name}: {e}")
            return False


