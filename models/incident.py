""" Classe modèle Incident représentant la table incident """

class Incident:
    """Modèle représentant un incident informatique (ticket)."""

    PRIORITES_VALIDES = ["BASSE", "MOYENNE", "HAUTE", "CRITIQUE"]
    STATUTS_VALIDES = ["OUVERT", "EN_COURS", "RESOLU", "FERME", "ANNULE"]

    def __init__(self, titre, description, priorite, utilisateur_id, statut="OUVERT", date_creation=None, id=None):
        self.id = id
        self.titre = titre
        self.description = description
        self.priorite = priorite.upper() if priorite else "MOYENNE"
        self.statut = statut.upper() if statut else "OUVERT"
        self.utilisateur_id = utilisateur_id
        self.date_creation = date_creation

    def __str__(self):
        return f"Incident #{self.id} | [{self.priorite}] {self.titre} - Statut: {self.statut}"