"""
DAO pour la gestion des incidents et des statistiques.
"""

from dao.base_dao import BaseDAO
from models.incident import Incident


class IncidentDAO(BaseDAO):
    """DAO pour la table incident."""

    # Transitions de statut autorisées selon le workflow du sujet
    TRANSITIONS_VALIDES = {
        "OUVERT": ["EN_COURS", "ANNULE"],
        "EN_COURS": ["RESOLU"],
        "RESOLU": ["FERME"],
        "FERME": [],
        "ANNULE": []
    }

    @property
    def table_name(self):
        return "incident"

    def ajouter(self, incident):
        """Créer un nouvel incident."""
        try:
            with self.db.get_cursor(dictionary=False) as cursor:
                query = """
                    INSERT INTO incident (titre, description, priorite, statut, utilisateur_id)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    incident.titre, incident.description, incident.priorite,
                    incident.statut, incident.utilisateur_id
                ))
                self.db.commit()
                incident.id = cursor.lastrowid
                return True
        except Exception as e:
            self.db.rollback()
            print(f"Erreur création incident: {e}")
            return False

    def changer_statut(self, incident_id, nouveau_statut):
        """Change le statut d'un incident en respectant les règles du workflow."""
        nouveau_statut = nouveau_statut.upper()
        incident_row = self.get_by_id(incident_id)
        if not incident_row:
            print("Incident introuvable.")
            return False

        statut_actuel = incident_row["statut"]
        if nouveau_statut not in self.TRANSITIONS_VALIDES.get(statut_actuel, []):
            print(f"Transition de statut interdite: Impossible de passer de {statut_actuel} à {nouveau_statut}.")
            return False

        try:
            with self.db.get_cursor(dictionary=False) as cursor:
                cursor.execute("UPDATE incident SET statut = %s WHERE id = %s", (nouveau_statut, incident_id))
                self.db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.db.rollback()
            print(f"Erreur changement statut: {e}")
            return False

    def get_par_utilisateur(self, utilisateur_id, statut=None, priorite=None):
        """Récupère les incidents d'un utilisateur avec filtres optionnels."""
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                query = "SELECT * FROM incident WHERE utilisateur_id = %s"
                params = [utilisateur_id]

                if statut:
                    query += " AND statut = %s"
                    params.append(statut.upper())
                if priorite:
                    query += " AND priorite = %s"
                    params.append(priorite.upper())

                query += " ORDER BY date_creation DESC"
                cursor.execute(query, tuple(params))
                return cursor.fetchall()
        except Exception as e:
            print(f"Erreur incidents utilisateur: {e}")
            return []

    def get_incidents_actifs(self):
        """Récupère tous les incidents avec le statut OUVERT ou EN_COURS."""
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM incident WHERE statut IN ('OUVERT', 'EN_COURS') ORDER BY date_creation ASC")
                return cursor.fetchall()
        except Exception as e:
            print(f"Erreur incidents actifs: {e}")
            return []

    def peut_etre_supprime(self, incident_id):
        """Vérifie si un incident a des interventions avant suppression."""
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                cursor.execute("SELECT COUNT(*) as nb FROM intervention WHERE incident_id = %s", (incident_id,))
                row = cursor.fetchone()
                return (row["nb"] if row else 0) == 0
        except Exception as e:
            print(f"Erreur vérification incident: {e}")
            return False

    def supprimer_incident(self, incident_id):
        """Supprime un incident uniquement s'il n'a aucune intervention associée."""
        if not self.peut_etre_supprime(incident_id):
            print("Impossible de supprimer cet incident : des interventions sont déjà enregistrées.")
            return False
        return self.delete_by_id(incident_id)

    def get_historique_technicien(self, technicien_id):
        """Récupère les incidents sur lesquels le technicien est intervenu."""
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                query = """
                    SELECT DISTINCT i.* 
                    FROM incident i
                    JOIN intervention inv ON i.id = inv.incident_id
                    WHERE inv.technicien_id = %s
                    ORDER BY i.date_creation DESC
                """
                cursor.execute(query, (technicien_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Erreur historique technicien: {e}")
            return []

    # --- STATISTIQUES ET RAPPORTS POUR L'ADMINISTRATEUR ---

    def get_stats_globales(self):
        """Calcule l'ensemble des statistiques d'incidents pour l'administrateur."""
        stats = {}
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                # 1. Total d'incidents par statut
                cursor.execute("SELECT statut, COUNT(*) as nb FROM incident GROUP BY statut")
                stats["par_statut"] = {row["statut"]: row["nb"] for row in cursor.fetchall()}

                # 2. Total d'incidents par priorité
                cursor.execute("SELECT priorite, COUNT(*) as nb FROM incident GROUP BY priorite")
                stats["par_priorite"] = {row["priorite"]: row["nb"] for row in cursor.fetchall()}

                # 3. Temps moyen de résolution par incident (en heures)
                query_temps = """
                    SELECT AVG(TIMESTAMPDIFF(SECOND, inc.date_creation, inv.date_intervention) / 3600.0) as temps_moyen
                    FROM incident inc
                    JOIN intervention inv ON inc.id = inv.incident_id
                    WHERE inc.statut IN ('RESOLU', 'FERME')
                """
                cursor.execute(query_temps)
                row = cursor.fetchone()
                stats["temps_moyen_resolution_heures"] = round(float(row["temps_moyen"]), 2) if row and row["temps_moyen"] is not None else 0.0

                # 4. Top 3 des techniciens les plus actifs
                query_top_tech = """
                    SELECT u.id, u.nom, u.prenom, COUNT(inv.id) as nb_interventions
                    FROM utilisateur u
                    JOIN intervention inv ON u.id = inv.technicien_id
                    GROUP BY u.id, u.nom, u.prenom
                    ORDER BY nb_interventions DESC
                    LIMIT 3
                """
                cursor.execute(query_top_tech)
                stats["top_techniciens"] = cursor.fetchall()

                # 5. Statistiques par technicien
                query_stat_tech = """
                    SELECT u.id, u.nom, u.prenom, 
                           COUNT(DISTINCT inv.incident_id) as nb_incidents_traites,
                           AVG(TIMESTAMPDIFF(SECOND, inc.date_creation, inv.date_intervention) / 3600.0) as temps_moyen
                    FROM utilisateur u
                    JOIN intervention inv ON u.id = inv.technicien_id
                    JOIN incident inc ON inc.id = inv.incident_id
                    WHERE u.role IN ('TECHNICIEN', 'ADMIN')
                    GROUP BY u.id, u.nom, u.prenom
                """
                cursor.execute(query_stat_tech)
                stats["details_techniciens"] = cursor.fetchall()

                # 6. Taux de résolution dans les 48h
                query_48h = """
                    SELECT 
                        COUNT(CASE WHEN (TIMESTAMPDIFF(SECOND, inc.date_creation, inv.date_intervention) / 3600.0) <= 48 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as taux
                    FROM incident inc
                    JOIN intervention inv ON inc.id = inv.incident_id
                    WHERE inc.statut IN ('RESOLU', 'FERME')
                """
                cursor.execute(query_48h)
                row_48 = cursor.fetchone()
                stats["taux_resolution_48h"] = round(float(row_48["taux"]), 2) if row_48 and row_48["taux"] is not None else 0.0

        except Exception as e:
            print(f"Erreur lors du calcul des statistiques: {e}")

        return stats


