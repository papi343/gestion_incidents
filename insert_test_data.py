"""
Script d'insertion de jeux de données de test pour la démonstration.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from create_tables import creer_tables
from dao.utilisateur_dao import UtilisateurDAO
from dao.incident_dao import IncidentDAO
from dao.intervention_dao import InterventionDAO
from models.utilisateur import Utilisateur
from models.incident import Incident
from models.intervention import Intervention


def insérer_donnees_test():
    """Remplit la base de données avec des comptes et incidents de démonstration."""
    creer_tables()

    u_dao = UtilisateurDAO()
    inc_dao = IncidentDAO()
    inv_dao = InterventionDAO()

    # Insertion des Utilisateurs
    utilisateurs = [
        Utilisateur("admin", "admin123", "DIOP", "Amadou", "admin@isi.sn", role="ADMIN", service="Informatique"),
        Utilisateur("tndoye", "tech123", "NDOYE", "Samba", "samba.ndoye@isi.sn", role="TECHNICIEN", service="Support IT"),
        Utilisateur("mfall", "tech123", "FALL", "Modou", "modou.fall@isi.sn", role="TECHNICIEN", service="Réseau"),
        Utilisateur("jdupont", "user123", "DUPONT", "Jean", "jean.dupont@isi.sn", role="UTILISATEUR", service="Comptabilité"),
        Utilisateur("mmbaye", "user123", "MBAYE", "Mariama", "mariama.mbaye@isi.sn", role="UTILISATEUR", service="RH")
    ]

    print("\n--- Insertion des Utilisateurs ---")
    for u in utilisateurs:
        if not u_dao.get_by_login(u.login):
            u_dao.ajouter(u)
            print(f" [+] Utilisateur ajouté: {u.login} ({u.role})")
        else:
            print(f" [=] Utilisateur {u.login} existe déjà.")

    # Récupération des IDs
    admin_user = u_dao.get_by_login("admin")
    tech1 = u_dao.get_by_login("tndoye")
    tech2 = u_dao.get_by_login("mfall")
    user1 = u_dao.get_by_login("jdupont")
    user2 = u_dao.get_by_login("mmbaye")

    # Insertion des Incidents (créés en statut OUVERT/EN_COURS pour permettre l'ajout d'interventions)
    incidents = [
        Incident("Panne d'imprimante RH", "L'imprimante de la RH ne répond plus aux requêtes d'impression.", "HAUTE", user2.id, statut="EN_COURS"),
        Incident("Mot de passe oublié Outlook", "Impossibilité de se connecter à la messagerie.", "BASSE", user1.id, statut="EN_COURS"),
        Incident("Écran bleu au démarrage", "L'ordinateur portable s'éteint brutalement au démarrage.", "CRITIQUE", user2.id, statut="OUVERT"),
        Incident("Coupure réseau 2ème étage", "Pas d'accès internet sur le secteur comptabilité.", "HAUTE", user1.id, statut="EN_COURS")
    ]

    print("\n--- Insertion des Incidents ---")
    inc_dao_all = inc_dao.get_all()
    if len(inc_dao_all) == 0:
        for inc in incidents:
            inc_dao.ajouter(inc)
            print(f" [+] Incident créé: {inc.titre} [{inc.statut}]")

        incidents_db = inc_dao.get_all()

        # Insertion des Interventions de test
        print("\n--- Insertion des Interventions ---")
        interventions = [
            Intervention(incidents_db[0]["id"], tech1.id, "Diagnostic réseau de l'imprimante et redémarrage du spouleur.", 30),
            Intervention(incidents_db[1]["id"], tech2.id, "Réinitialisation du mot de passe et ré-authentification.", 15),
            Intervention(incidents_db[3]["id"], tech1.id, "Remplacement du câble RJ45 défectueux au switch.", 45)
        ]

        for inv in interventions:
            inv_dao.ajouter(inv, role_technicien="TECHNICIEN")
            print(f" [+] Intervention ajoutée sur l'incident #{inv.incident_id} par Tech #{inv.technicien_id}")

        # Évolution des statuts d'incidents selon le workflow
        inc_dao.changer_statut(incidents_db[1]["id"], "RESOLU")
        inc_dao.changer_statut(incidents_db[3]["id"], "RESOLU")
        inc_dao.changer_statut(incidents_db[3]["id"], "FERME")
    else:
        print(" [=] Les incidents de test sont déjà présents.")
        # Rattrapage d'interventions si incomplètes
        incidents_db = inc_dao.get_all()
        interventions_existantes = inv_dao.get_all()
        if len(interventions_existantes) < 3 and len(incidents_db) >= 4:
            # Réinitialiser temporairement le statut pour insérer les interventions manquées
            db = inc_dao.db
            with db.get_cursor(dictionary=False) as cursor:
                cursor.execute("UPDATE incident SET statut = 'EN_COURS' WHERE id IN (%s, %s)", (incidents_db[1]["id"], incidents_db[3]["id"]))
                db.commit()

            inv_dao.ajouter(Intervention(incidents_db[1]["id"], tech2.id, "Réinitialisation du mot de passe et ré-authentification.", 15))
            inv_dao.ajouter(Intervention(incidents_db[3]["id"], tech1.id, "Remplacement du câble RJ45 défectueux au switch.", 45))

            inc_dao.changer_statut(incidents_db[1]["id"], "RESOLU")
            inc_dao.changer_statut(incidents_db[3]["id"], "RESOLU")
            inc_dao.changer_statut(incidents_db[3]["id"], "FERME")
            print(" [+] Rattrapage des interventions de test effectué.")

    print("\n[SUCCESS] Données de test insérées avec succès.")


if __name__ == "__main__":
    insérer_donnees_test()
