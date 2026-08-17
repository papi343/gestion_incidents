"""Classe modèle Intervention représentant la table intervention"""

class Intervention:
    """Modèle représentant une intervention réalisée par un technicien sur un incident."""

    def __init__(self, incident_id, technicien_id, commentaire, duree_minutes, date_intervention=None, id=None):
        self.id = id
        self.incident_id = incident_id
        self.technicien_id = technicien_id
        self.commentaire = commentaire
        self.duree_minutes = int(duree_minutes) if duree_minutes else 0
        self.date_intervention = date_intervention

    def __str__(self):
        return f"Intervention #{self.id} | Incident #{self.incident_id} | Durée: {self.duree_minutes} min - Note: {self.commentaire}"