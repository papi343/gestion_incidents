"""
DAO pour la gestion des interventions réalisées sur les incidents.
"""

from dao.base_dao import BaseDAO
from models.intervention import Intervention


class InterventionDAO(BaseDAO):
    """DAO pour la table intervention."""

    @property
    def table_name(self):
        return "intervention"

    def ajouter(self, intervention, role_technicien="TECHNICIEN"):
        """Ajoute une nouvelle intervention sur un incident."""
        if role_technicien.upper() not in ["TECHNICIEN", "ADMIN"]:
            print("Erreur: Seul un technicien ou un administrateur peut ajouter une intervention.")
            return False

        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                cursor.execute("SELECT statut FROM incident WHERE id = %s", (intervention.incident_id,))
                row = cursor.fetchone()

                if not row:
                    print("Erreur: Incident non trouvé.")
                    return False

                if row["statut"] not in ["OUVERT", "EN_COURS"]:
                    print(f"Erreur: Impossible d'ajouter une intervention sur un incident au statut '{row['statut']}'.")
                    return False

            with self.db.get_cursor(dictionary=False) as cursor_insert:
                query = """
                    INSERT INTO intervention (commentaire, duree_minutes, incident_id, technicien_id)
                    VALUES (%s, %s, %s, %s)
                """
                cursor_insert.execute(query, (
                    intervention.commentaire,
                    intervention.duree_minutes,
                    intervention.incident_id,
                    intervention.technicien_id
                ))
                self.db.commit()
                intervention.id = cursor_insert.lastrowid
                return True
        except Exception as e:
            self.db.rollback()
            print(f"Erreur lors de l'ajout de l'intervention: {e}")
            return False

    def get_par_incident(self, incident_id):
        """Récupère la liste de toutes les interventions réalisées sur un incident donné."""
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                query = """
                    SELECT inv.*, u.nom as tech_nom, u.prenom as tech_prenom
                    FROM intervention inv
                    JOIN utilisateur u ON inv.technicien_id = u.id
                    WHERE inv.incident_id = %s
                    ORDER BY inv.date_intervention ASC
                """
                cursor.execute(query, (incident_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Erreur lors de la récupération des interventions: {e}")
            return []


