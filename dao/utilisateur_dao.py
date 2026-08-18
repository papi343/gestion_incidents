"""
DAO spécifique pour la gestion des utilisateurs et l'authentification.
"""

import re
from dao.base_dao import BaseDAO
from models.utilisateur import Utilisateur


class UtilisateurDAO(BaseDAO):
    """DAO pour la table utilisateur."""

    @property
    def table_name(self):
        return "utilisateur"

    @staticmethod
    def valider_email(email):
        """Vérifie le format d'une adresse email avec une expression régulière simple."""
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return bool(re.match(pattern, email))

    def _mapper_utilisateur(self, row):
        """Méthode utilitaire pour convertir une ligne de BD en objet Utilisateur."""
        if not row:
            return None
        return Utilisateur(
            id=row["id"], login=row["login"], password=row["password"],
            nom=row["nom"], prenom=row["prenom"], email=row["email"],
            role=row["role"], service=row["service"], date_creation=row["date_creation"]
        )

    def authentifier(self, login, password):
        """Vérifie le login et mot de passe d'un utilisateur."""
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM utilisateur WHERE login = %s AND password = %s", (login, password))
                return self._mapper_utilisateur(cursor.fetchone())
        except Exception as e:
            print(f"Erreur d'authentification: {e}")
            return None

    def get_by_login(self, login):
        """Recherche un utilisateur par son login."""
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM utilisateur WHERE login = %s", (login,))
                return self._mapper_utilisateur(cursor.fetchone())
        except Exception as e:
            print(f"Erreur recherche login: {e}")
            return None

    def ajouter(self, utilisateur):
        """Ajoute un nouvel utilisateur dans la base de données."""
        if not self.valider_email(utilisateur.email):
            print("Erreur: Format d'adresse email invalide.")
            return False

        try:
            with self.db.get_cursor(dictionary=False) as cursor:
                query = """
                    INSERT INTO utilisateur (login, password, nom, prenom, email, role, service)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    utilisateur.login, utilisateur.password, utilisateur.nom,
                    utilisateur.prenom, utilisateur.email, utilisateur.role, utilisateur.service
                ))
                self.db.commit()
                utilisateur.id = cursor.lastrowid
                return True
        except Exception as e:
            self.db.rollback()
            print(f"Erreur lors de l'ajout de l'utilisateur: {e}")
            return False

    def modifier(self, utilisateur):
        """Met à jour les informations d'un utilisateur existant."""
        if not self.valider_email(utilisateur.email):
            print("Erreur: Format d'adresse email invalide.")
            return False

        try:
            with self.db.get_cursor(dictionary=False) as cursor:
                query = """
                    UPDATE utilisateur
                    SET password = %s, nom = %s, prenom = %s, email = %s, role = %s, service = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    utilisateur.password, utilisateur.nom, utilisateur.prenom,
                    utilisateur.email, utilisateur.role, utilisateur.service, utilisateur.id
                ))
                self.db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.db.rollback()
            print(f"Erreur modification utilisateur: {e}")
            return False

    def peut_etre_supprime(self, user_id):
        """Vérifie si l'utilisateur peut être supprimé (aucun incident ni intervention)."""
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                cursor.execute("SELECT COUNT(*) as nb FROM incident WHERE utilisateur_id = %s", (user_id,))
                nb_incidents = cursor.fetchone()["nb"]

                cursor.execute("SELECT COUNT(*) as nb FROM intervention WHERE technicien_id = %s", (user_id,))
                nb_interventions = cursor.fetchone()["nb"]

                return (nb_incidents == 0) and (nb_interventions == 0)
        except Exception as e:
            print(f"Erreur vérification suppression: {e}")
            return False

    def supprimer_utilisateur(self, user_id):
        """Supprime l'utilisateur s'il respecte les contraintes d'intégrité."""
        if not self.peut_etre_supprime(user_id):
            print("Impossible de supprimer cet utilisateur : il possède des incidents ou des interventions associées.")
            return False
        return self.delete_by_id(user_id)

    def rechercher(self, terme):
        """Recherche des utilisateurs par nom, login ou service."""
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                query = "SELECT * FROM utilisateur WHERE nom LIKE %s OR login LIKE %s OR service LIKE %s"
                filtre = f"%{terme}%"
                cursor.execute(query, (filtre, filtre, filtre))
                return cursor.fetchall()
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return []


