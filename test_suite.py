"""
Script de test automatique pour vérifier toutes les fonctionnalités du projet.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connexion import Connexion
from dao.utilisateur_dao import UtilisateurDAO
from dao.incident_dao import IncidentDAO
from dao.intervention_dao import InterventionDAO
from models.utilisateur import Utilisateur
from models.incident import Incident
from models.intervention import Intervention


from create_tables import creer_tables
from insert_test_data import insérer_donnees_test


def test_complet():
    print("=== DÉBUT DES TESTS AUTOMATISÉS ===")
    creer_tables()
    insérer_donnees_test()

    
    # 1. Test connexion Singleton
    c1 = Connexion()
    c2 = Connexion()
    assert c1 is c2, "Le Singleton connexion a échoué !"
    print("[OK] Test Singleton Connexion réussi.")

    # 2. Test DAO Utilisateur
    u_dao = UtilisateurDAO()
    admin = u_dao.get_by_login("admin")
    assert admin is not None, "Utilisateur admin introuvable !"
    assert admin.role == "ADMIN", "Rôle admin incorrect !"
    print(f"[OK] Test UtilisateurDAO d'authentification réussi: {admin}")

    # 3. Test validation d'email
    assert UtilisateurDAO.valider_email("test@example.com") == True
    assert UtilisateurDAO.valider_email("test-invalide") == False
    print("[OK] Test Validation Email réussi.")

    # 4. Test Incident DAO & Workflow
    inc_dao = IncidentDAO()
    incidents_actifs = inc_dao.get_incidents_actifs()
    print(f"[OK] Nombre d'incidents actifs récupérés : {len(incidents_actifs)}")

    # Test Workflow interdit (statut ne peut pas reculer)
    succes_invalide = inc_dao.changer_statut(1, "OUVERT") # Supposons que l'incident 1 est EN_COURS
    assert succes_invalide == False, "Le workflow n'a pas bloqué un retour de statut !"
    print("[OK] Test Contrainte de Workflow (retour de statut interdit) réussi.")

    # 5. Test Statistiques Admin
    stats = inc_dao.get_stats_globales()
    assert "par_statut" in stats
    assert "par_priorite" in stats
    print("[OK] Test Calcul Statistiques Admin réussi.")
    print("Statistiques calculées :", stats)

    print("\n=== TOUS LES TESTS SE SONT DÉROULÉS AVEC SUCCÈS ! ===")


if __name__ == "__main__":
    test_complet()
