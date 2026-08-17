from Database.connexion import DatabaseConnection
from dao.base_dao import BaseDAO
from models.intervention import Intervention
from datetime import datetime


class InterventionDAO(BaseDAO):
    """Gestion des interventions - CRUD + Statistiques"""

    # ========== MÉTHODES OBLIGATOIRES ==========

    def get_all(self):
        """Liste toutes les interventions"""
        if not self.db.connect():
            return []

        sql = "SELECT * FROM intervention ORDER BY date_intervention DESC"
        self.db.execute(sql)
        resultats = self.db.fetchall()
        self.db.disconnect()

        interventions = []
        for ligne in resultats:
            intervention = Intervention(
                id=ligne[0],
                commentaire=ligne[1],
                duree_minutes=ligne[2],
                date_intervention=ligne[3],
                incident_id=ligne[4],
                technicien_id=ligne[5]
            )
            interventions.append(intervention)
        return interventions

    def get_by_id(self, id_intervention):
        """Récupère une intervention par son ID"""
        if not self.db.connect():
            return None

        sql = "SELECT * FROM intervention WHERE id = %s"
        self.db.execute(sql, (id_intervention,))
        ligne = self.db.fetchone()
        self.db.disconnect()

        if ligne:
            return Intervention(
                id=ligne[0],
                commentaire=ligne[1],
                duree_minutes=ligne[2],
                date_intervention=ligne[3],
                incident_id=ligne[4],
                technicien_id=ligne[5]
            )
        return None

    def delete_by_id(self, id_intervention):
        """Supprime une intervention"""
        if not self.db.connect():
            return False

        sql = "DELETE FROM intervention WHERE id = %s"
        ok = self.db.execute(sql, (id_intervention,))
        if ok:
            self.db.commit()
        self.db.disconnect()
        return ok

    # ========== MÉTHODES SPÉCIFIQUES ==========

    def ajouter(self, intervention):
        """Ajoute une intervention (vérifie l'état de l'incident)"""
        if not self._incident_est_modifiable(intervention.incident_id):
            print("L'incident doit être OUVERT ou EN_COURS")
            return False

        if not self.db.connect():
            return False

        sql = """INSERT INTO intervention 
                 (commentaire, duree_minutes, date_intervention, incident_id, technicien_id)
                 VALUES (%s, %s, %s, %s, %s)"""

        params = (
            intervention.commentaire,
            intervention.duree_minutes,
            datetime.now(),
            intervention.incident_id,
            intervention.technicien_id
        )

        ok = self.db.execute(sql, params)
        if ok:
            self.db.commit()
        self.db.disconnect()
        return ok

    def get_par_incident(self, incident_id):
        """Récupère toutes les interventions d'un incident"""
        if not self.db.connect():
            return []

        sql = "SELECT * FROM intervention WHERE incident_id = %s ORDER BY date_intervention"
        self.db.execute(sql, (incident_id,))
        resultats = self.db.fetchall()
        self.db.disconnect()

        interventions = []
        for ligne in resultats:
            intervention = Intervention(
                id=ligne[0],
                commentaire=ligne[1],
                duree_minutes=ligne[2],
                date_intervention=ligne[3],
                incident_id=ligne[4],
                technicien_id=ligne[5]
            )
            interventions.append(intervention)
        return interventions

    def get_par_technicien(self, technicien_id):
        """Récupère toutes les interventions d'un technicien"""
        if not self.db.connect():
            return []

        sql = "SELECT * FROM intervention WHERE technicien_id = %s ORDER BY date_intervention"
        self.db.execute(sql, (technicien_id,))
        resultats = self.db.fetchall()
        self.db.disconnect()

        interventions = []
        for ligne in resultats:
            intervention = Intervention(
                id=ligne[0],
                commentaire=ligne[1],
                duree_minutes=ligne[2],
                date_intervention=ligne[3],
                incident_id=ligne[4],
                technicien_id=ligne[5]
            )
            interventions.append(intervention)
        return interventions

    def get_temps_total_technicien(self, technicien_id):
        """Calcule le temps total travaillé par un technicien"""
        if not self.db.connect():
            return 0

        sql = "SELECT COALESCE(SUM(duree_minutes), 0) FROM intervention WHERE technicien_id = %s"
        self.db.execute(sql, (technicien_id,))
        total = self.db.fetchone()[0]
        self.db.disconnect()
        return total

    def get_top_techniciens(self, limite=3):
        """Récupère le top N des techniciens les plus actifs"""
        if not self.db.connect():
            return []

        sql = """SELECT technicien_id, COUNT(*) as nb_interventions, SUM(duree_minutes) as temps_total
                 FROM intervention
                 GROUP BY technicien_id
                 ORDER BY nb_interventions DESC
                 LIMIT %s"""

        self.db.execute(sql, (limite,))
        resultats = self.db.fetchall()
        self.db.disconnect()

        top = []
        for ligne in resultats:
            top.append({
                'technicien_id': ligne[0],
                'nb_interventions': ligne[1],
                'temps_total': ligne[2]
            })
        return top

    # ========== MÉTHODES PRIVÉES ==========

    def _incident_est_modifiable(self, incident_id):
        """Vérifie si l'incident est OUVERT ou EN_COURS"""
        if not self.db.connect():
            return False

        sql = "SELECT statut FROM incident WHERE id = %s"
        self.db.execute(sql, (incident_id,))
        ligne = self.db.fetchone()
        self.db.disconnect()

        if ligne:
            return ligne[0] in ('OUVERT', 'EN_COURS')
        return False