"""
Classe modèle Utilisateur représentant la table utilisateur.
"""
class Utilisateur:
    """Modèle représentant un utilisateur du système."""

    ROLES_VALIDES = ["UTILISATEUR", "TECHNICIEN", "ADMIN"]

    def __init__(self, login, password, nom, prenom, email, role="UTILISATEUR", service="Général", date_creation=None, id=None):
        self.id = id
        self.login = login
        self.password = password
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.role = role.upper() if role else "UTILISATEUR"
        self.service = service
        self.date_creation = date_creation

    def __str__(self):
        return f"Utilisateur #{self.id} | {self.login} ({self.prenom} {self.nom}) - Rôle: {self.role} | Service: {self.service}"