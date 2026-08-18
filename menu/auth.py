"""
Gestion de l'authentification et de la session utilisateur.
"""

from dao.utilisateur_dao import UtilisateurDAO


class ServiceAuthentification:
    """Gère la connexion et l'utilisateur actuellement authentifié."""

    def __init__(self):
        self.utilisateur_dao = UtilisateurDAO()
        self.utilisateur_connecte = None

    def se_connecter(self):
        """Demande les identifiants à l'utilisateur et effectue la connexion."""
        print("\n" + "=" * 45)
        print("    AUTHENTIFICATION - GESTION DES INCIDENTS")
        print("=" * 45)

        login = input("Identifiant (login) : ").strip()
        password = input("Mot de passe         : ").strip()

        user = self.utilisateur_dao.authentifier(login, password)
        if user:
            self.utilisateur_connecte = user
            print(f"\n[SUCCESS] Connexion réussie ! Bienvenue {user.prenom} {user.nom} ({user.role})")
            return True
        else:
            print("\n[ERREUR] Login ou mot de passe incorrect.")
            return False

    def se_deconnecter(self):
        """Déconnecte l'utilisateur actuel."""
        if self.utilisateur_connecte:
            print(f"\nDéconnexion de {self.utilisateur_connecte.login} effectuée.")
            self.utilisateur_connecte = None

    def est_connecte(self):
        """Vérifie si un utilisateur est actuellement connecté."""
        return self.utilisateur_connecte is not None
