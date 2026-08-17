from Database.connexion import DatabaseConnection
from dao.base_dao import BaseDAO
from models.incident import Incident
from datetime import datetime


class IncidentDAO(BaseDAO):
    """Gestion des incidents - CRUD + Workflow"""

    # ========== MÉTHODES OBLIGATOIRES ==========

    def get_all(self):
        """Liste tous les incidents"""
        if not self.db.connect():
            return []

        sql = "SELECT * FROM incident ORDER BY date_creation DESC"
        self.db.execute(sql)
        resultats = self.db.fetchall()
        self.db.disconnect()

        incidents = []
        for ligne in resultats:
            incident = Incident(
                id=ligne[0],
                titre=ligne[1],
                description=ligne[2],
                priorite=ligne[3],
                statut=ligne[4],
                date_creation=ligne[5],
                utilisateur_id=ligne[6]
            )
            incidents.append(incident)
        return incidents

    def get_by_id(self, id_incident):
        """Récupère un incident par son ID"""
        if not self.db.connect():
            return None

        sql = "SELECT * FROM incident WHERE id = %s"
        self.db.execute(sql, (id_incident,))
        ligne = self.db.fetchone()
        self.db.disconnect()

        if ligne:
            return Incident(
                id=ligne[0],
                titre=ligne[1],
                description=ligne[2],
                priorite=ligne[3],
                statut=ligne[4],
                date_creation=ligne[5],
                utilisateur_id=ligne[6]
            )
        return None

    def delete_by_id(self, id_incident):
        """Supprime un incident (vérifie les interventions)"""
        if self._a_des_interventions(id_incident):
            print("Impossible de supprimer : l'incident a des interventions")
            return False

        if not self.db.connect():
            return False

        sql = "DELETE FROM incident WHERE id = %s"
        ok = self.db.execute(sql, (id_incident,))
        if ok:
            self.db.commit()
        self.db.disconnect()
        return ok

    # ========== MÉTHODES SPÉCIFIQUES ==========

    def creer(self, incident):
        """Crée un nouvel incident (statut OUVERT par défaut)"""
        if not self.db.connect():
            return False

        sql = """INSERT INTO incident 
                 (titre, description, priorite, statut, date_creation, utilisateur_id)
                 VALUES (%s, %s, %s, %s, %s, %s)"""

        params = (
            incident.titre,
            incident.description,
            incident.priorite,
            "OUVERT",
            datetime.now(),
            incident.utilisateur_id
        )

        ok = self.db.execute(sql, params)
        if ok:
            self.db.commit()
        self.db.disconnect()
        return ok

    def changer_statut(self, id_incident, nouveau_statut):
        """Change le statut avec vérification des transitions"""
        ancien_statut = self._get_statut(id_incident)
        if ancien_statut is None:
            print("Incident non trouvé")
            return False

        if not self._transition_autorisee(ancien_statut, nouveau_statut):
            print(f"Transition {ancien_statut} → {nouveau_statut} non autorisée")
            return False

        if not self.db.connect():
            return False

        sql = "UPDATE incident SET statut = %s WHERE id = %s"
        ok = self.db.execute(sql, (nouveau_statut, id_incident))
        if ok:
            self.db.commit()
        self.db.disconnect()
        return ok

    def get_par_utilisateur(self, utilisateur_id):
        """Récupère les incidents d'un utilisateur"""
        if not self.db.connect():
            return []

        sql = "SELECT * FROM incident WHERE utilisateur_id = %s ORDER BY date_creation DESC"
        self.db.execute(sql, (utilisateur_id,))
        resultats = self.db.fetchall()
        self.db.disconnect()

        incidents = []
        for ligne in resultats:
            incident = Incident(
                id=ligne[0],
                titre=ligne[1],
                description=ligne[2],
                priorite=ligne[3],
                statut=ligne[4],
                date_creation=ligne[5],
                utilisateur_id=ligne[6]
            )
            incidents.append(incident)
        return incidents

    def get_par_statut(self, statut):
        """Filtre les incidents par statut"""
        if not self.db.connect():
            return []

        sql = "SELECT * FROM incident WHERE statut = %s ORDER BY date_creation DESC"
        self.db.execute(sql, (statut,))
        resultats = self.db.fetchall()
        self.db.disconnect()

        incidents = []
        for ligne in resultats:
            incident = Incident(
                id=ligne[0],
                titre=ligne[1],
                description=ligne[2],
                priorite=ligne[3],
                statut=ligne[4],
                date_creation=ligne[5],
                utilisateur_id=ligne[6]
            )
            incidents.append(incident)
        return incidents

    def get_par_priorite(self, priorite):
        """Filtre les incidents par priorité"""
        if not self.db.connect():
            return []

        sql = "SELECT * FROM incident WHERE priorite = %s ORDER BY date_creation DESC"
        self.db.execute(sql, (priorite,))
        resultats = self.db.fetchall()
        self.db.disconnect()

        incidents = []
        for ligne in resultats:
            incident = Incident(
                id=ligne[0],
                titre=ligne[1],
                description=ligne[2],
                priorite=ligne[3],
                statut=ligne[4],
                date_creation=ligne[5],
                utilisateur_id=ligne[6]
            )
            incidents.append(incident)
        return incidents

    def get_incidents_ouverts_ou_en_cours(self):
        """Récupère les incidents à traiter (pour techniciens)"""
        if not self.db.connect():
            return []

        sql = "SELECT * FROM incident WHERE statut IN ('OUVERT', 'EN_COURS')"
        self.db.execute(sql)
        resultats = self.db.fetchall()
        self.db.disconnect()

        incidents = []
        for ligne in resultats:
            incident = Incident(
                id=ligne[0],
                titre=ligne[1],
                description=ligne[2],
                priorite=ligne[3],
                statut=ligne[4],
                date_creation=ligne[5],
                utilisateur_id=ligne[6]
            )
            incidents.append(incident)
        return incidents

    def get_historique_technicien(self, technicien_id):
        """Récupère les incidents traités par un technicien"""
        if not self.db.connect():
            return []

        sql = """SELECT DISTINCT i.* FROM incident i
                 JOIN intervention inter ON i.id = inter.incident_id
                 WHERE inter.technicien_id = %s
                 ORDER BY i.date_creation DESC"""

        self.db.execute(sql, (technicien_id,))
        resultats = self.db.fetchall()
        self.db.disconnect()

        incidents = []
        for ligne in resultats:
            incident = Incident(
                id=ligne[0],
                titre=ligne[1],
                description=ligne[2],
                priorite=ligne[3],
                statut=ligne[4],
                date_creation=ligne[5],
                utilisateur_id=ligne[6]
            )
            incidents.append(incident)
        return incidents

    # ========== MÉTHODES PRIVÉES ==========

    def _a_des_interventions(self, id_incident):
        """Vérifie si l'incident a des interventions"""
        if not self.db.connect():
            return True

        sql = "SELECT COUNT(*) FROM intervention WHERE incident_id = %s"
        self.db.execute(sql, (id_incident,))
        count = self.db.fetchone()[0]
        self.db.disconnect()
        return count > 0

    def _get_statut(self, id_incident):
        """Récupère le statut actuel"""
        if not self.db.connect():
            return None

        sql = "SELECT statut FROM incident WHERE id = %s"
        self.db.execute(sql, (id_incident,))
        ligne = self.db.fetchone()
        self.db.disconnect()
        return ligne[0] if ligne else None

    def _transition_autorisee(self, ancien, nouveau):
        """Vérifie si la transition est autorisée"""
        transitions = {
            "OUVERT": ["EN_COURS", "ANNULE"],
            "EN_COURS": ["RESOLU"],
            "RESOLU": ["FERME"]
        }
        return nouveau in transitions.get(ancien, [])