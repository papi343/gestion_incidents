from Database.connexion import DatabaseConnection
from dao.base_dao import BaseDAO
from models.utilisateur import Utilisateur


class UtilisateurDAO(BaseDAO):
    """Gestion des utilisateurs - CRUD complet + Authentification"""

    # ========== MÉTHODES OBLIGATOIRES (héritées) ==========

    def get_all(self):
        """Liste tous les utilisateurs"""
        if not self.db.connect():
            return []

        sql = "SELECT * FROM utilisateur ORDER BY id"
        self.db.execute(sql)
        resultats = self.db.fetchall()
        self.db.disconnect()

        utilisateurs = []
        for ligne in resultats:
            utilisateur = Utilisateur(
                id=ligne[0],
                login=ligne[1],
                password=ligne[2],
                nom=ligne[3],
                prenom=ligne[4],
                email=ligne[5],
                role=ligne[6],
                service=ligne[7],
                date_creation=ligne[8]
            )
            utilisateurs.append(utilisateur)
        return utilisateurs

    def get_by_id(self, id_utilisateur):
        """Récupère un utilisateur par son ID"""
        if not self.db.connect():
            return None

        sql = "SELECT * FROM utilisateur WHERE id = %s"
        self.db.execute(sql, (id_utilisateur,))
        ligne = self.db.fetchone()
        self.db.disconnect()

        if ligne:
            return Utilisateur(
                id=ligne[0],
                login=ligne[1],
                password=ligne[2],
                nom=ligne[3],
                prenom=ligne[4],
                email=ligne[5],
                role=ligne[6],
                service=ligne[7],
                date_creation=ligne[8]
            )
        return None

    def delete_by_id(self, id_utilisateur):
        """Supprime un utilisateur (vérifie les dépendances)"""
        if self._a_des_incidents(id_utilisateur) or self._a_des_interventions(id_utilisateur):
            print("Impossible de supprimer : utilisateur a des incidents ou interventions")
            return False

        if not self.db.connect():
            return False

        sql = "DELETE FROM utilisateur WHERE id = %s"
        ok = self.db.execute(sql, (id_utilisateur,))
        if ok:
            self.db.commit()
        self.db.disconnect()
        return ok

    # ========== MÉTHODES SPÉCIFIQUES ==========

    def ajouter(self, utilisateur):
        """Ajoute un nouvel utilisateur"""
        if not self.db.connect():
            return False

        sql = """INSERT INTO utilisateur 
                 (login, password, nom, prenom, email, role, service)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""

        params = (
            utilisateur.login,
            utilisateur.password,
            utilisateur.nom,
            utilisateur.prenom,
            utilisateur.email,
            utilisateur.role,
            utilisateur.service
        )

        ok = self.db.execute(sql, params)
        if ok:
            self.db.commit()
        self.db.disconnect()
        return ok

    def modifier(self, utilisateur):
        """Modifie un utilisateur existant"""
        if not self.db.connect():
            return False

        sql = """UPDATE utilisateur 
                 SET login=%s, password=%s, nom=%s, prenom=%s,
                     email=%s, role=%s, service=%s
                 WHERE id=%s"""

        params = (
            utilisateur.login,
            utilisateur.password,
            utilisateur.nom,
            utilisateur.prenom,
            utilisateur.email,
            utilisateur.role,
            utilisateur.service,
            utilisateur.id
        )

        ok = self.db.execute(sql, params)
        if ok:
            self.db.commit()
        self.db.disconnect()
        return ok

    def authentifier(self, login, password):
        """Authentifie un utilisateur"""
        if not self.db.connect():
            return None

        sql = "SELECT * FROM utilisateur WHERE login = %s AND password = %s"
        self.db.execute(sql, (login, password))
        ligne = self.db.fetchone()
        self.db.disconnect()

        if ligne:
            return Utilisateur(
                id=ligne[0],
                login=ligne[1],
                password=ligne[2],
                nom=ligne[3],
                prenom=ligne[4],
                email=ligne[5],
                role=ligne[6],
                service=ligne[7],
                date_creation=ligne[8]
            )
        return None

    def rechercher(self, mot_cle):
        """Recherche par nom, login ou service"""
        if not self.db.connect():
            return []

        sql = """SELECT * FROM utilisateur 
                 WHERE nom LIKE %s OR login LIKE %s OR service LIKE %s"""

        param = f"%{mot_cle}%"
        self.db.execute(sql, (param, param, param))
        resultats = self.db.fetchall()
        self.db.disconnect()

        utilisateurs = []
        for ligne in resultats:
            utilisateur = Utilisateur(
                id=ligne[0],
                login=ligne[1],
                password=ligne[2],
                nom=ligne[3],
                prenom=ligne[4],
                email=ligne[5],
                role=ligne[6],
                service=ligne[7],
                date_creation=ligne[8]
            )
            utilisateurs.append(utilisateur)
        return utilisateurs

    def get_by_login(self, login):
        """Récupère un utilisateur par son login"""
        if not self.db.connect():
            return None

        sql = "SELECT * FROM utilisateur WHERE login = %s"
        self.db.execute(sql, (login,))
        ligne = self.db.fetchone()
        self.db.disconnect()

        if ligne:
            return Utilisateur(
                id=ligne[0],
                login=ligne[1],
                password=ligne[2],
                nom=ligne[3],
                prenom=ligne[4],
                email=ligne[5],
                role=ligne[6],
                service=ligne[7],
                date_creation=ligne[8]
            )
        return None

    # ========== MÉTHODES PRIVÉES ==========

    def _a_des_incidents(self, id_utilisateur):
        """Vérifie si l'utilisateur a des incidents"""
        if not self.db.connect():
            return True

        sql = "SELECT COUNT(*) FROM incident WHERE utilisateur_id = %s"
        self.db.execute(sql, (id_utilisateur,))
        count = self.db.fetchone()[0]
        self.db.disconnect()
        return count > 0

    def _a_des_interventions(self, id_utilisateur):
        """Vérifie si l'utilisateur a fait des interventions"""
        if not self.db.connect():
            return True

        sql = "SELECT COUNT(*) FROM intervention WHERE technicien_id = %s"
        self.db.execute(sql, (id_utilisateur,))
        count = self.db.fetchone()[0]
        self.db.disconnect()
        return count > 0