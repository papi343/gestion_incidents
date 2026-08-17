from abc import ABC, abstractmethod
#from Database.connexion import DatabaseConnection


class BaseDAO(ABC):
    """
    Classe abstraite - Tous les DAO doivent hériter d'elle
    Elle définit les méthodes obligatoires
    """

    def __init__(self):
        """Récupère l'instance unique de connexion (Singleton)"""
    #    self.db = DatabaseConnection()

    @abstractmethod
    def get_all(self):
        """Récupère tous les enregistrements"""
        pass

    @abstractmethod
    def get_by_id(self, id_objet):
        """Récupère un enregistrement par son ID"""
        pass

    @abstractmethod
    def delete_by_id(self, id_objet):
        """Supprime un enregistrement par son ID"""
        pass