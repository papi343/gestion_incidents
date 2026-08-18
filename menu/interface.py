"""
Interface console interactive proposant les menus adaptés à chaque rôle (UTILISATEUR, TECHNICIEN, ADMIN).
"""

from dao.utilisateur_dao import UtilisateurDAO
from dao.incident_dao import IncidentDAO
from dao.intervention_dao import InterventionDAO
from models.utilisateur import Utilisateur
from models.incident import Incident
from models.intervention import Intervention


class InterfaceConsole:
    """Interface graphique en ligne de commande (CLI)."""

    def __init__(self, auth_service):
        self.auth = auth_service
        self.user_dao = UtilisateurDAO()
        self.incident_dao = IncidentDAO()
        self.intervention_dao = InterventionDAO()

    def demarrer(self):
        """Boucle principale de l'application."""
        while True:
            if not self.auth.est_connecte():
                succes = self.auth.se_connecter()
                if not succes:
                    reessayer = input("Voulez-vous réessayer ? (o/n) : ").strip().lower()
                    if reessayer != 'o':
                        print("Au revoir !")
                        break
                    continue

            user = self.auth.utilisateur_connecte
            if user.role == "ADMIN":
                self.afficher_menu_admin()
            elif user.role == "TECHNICIEN":
                self.afficher_menu_technicien()
            else:
                self.afficher_menu_utilisateur()

    # =========================================================================
    # MENU UTILISATEUR
    # =========================================================================

    def afficher_menu_utilisateur(self):
        """Menu réservé aux utilisateurs simples."""
        user = self.auth.utilisateur_connecte
        print("\n" + "=" * 45)
        print(f"   ESPACE UTILISATEUR - [{user.prenom} {user.nom}]")
        print("=" * 45)
        print("1. Signaler un nouvel incident")
        print("2. Consulter la liste de mes incidents")
        print("3. Consulter le détail d'un de mes incidents")
        print("4. Filtrer mes incidents par statut")
        print("5. Filtrer mes incidents par priorité")
        print("6. Annuler un de mes incidents (si OUVERT)")
        print("0. Se déconnecter")

        choix = input("\nVotre choix : ").strip()
        if choix == "1":
            self.creer_incident()
        elif choix == "2":
            self.lister_mes_incidents()
        elif choix == "3":
            self.detail_incident()
        elif choix == "4":
            self.filtrer_mes_incidents_par_statut()
        elif choix == "5":
            self.filtrer_mes_incidents_par_priorite()
        elif choix == "6":
            self.annuler_mon_incident()
        elif choix == "0":
            self.auth.se_deconnecter()
        else:
            print("[!] Choix invalide.")

    def creer_incident(self):
        """Formulaire de création d'un incident."""
        print("\n--- NOUVEL INCIDENT ---")
        titre = input("Titre de l'incident : ").strip()
        description = input("Description détaillée : ").strip()

        print("\nNiveau de priorité :")
        print("1. BASSE | 2. MOYENNE | 3. HAUTE | 4. CRITIQUE")
        choix_prio = input("Choix (1-4) [défaut: 2] : ").strip()
        map_prio = {"1": "BASSE", "2": "MOYENNE", "3": "HAUTE", "4": "CRITIQUE"}
        priorite = map_prio.get(choix_prio, "MOYENNE")

        if not titre or not description:
            print("[!] Le titre et la description sont obligatoires.")
            return

        incident = Incident(
            titre=titre,
            description=description,
            priorite=priorite,
            utilisateur_id=self.auth.utilisateur_connecte.id
        )
        if self.incident_dao.ajouter(incident):
            print(f"[SUCCESS] Incident #{incident.id} créé avec succès !")

    def lister_mes_incidents(self):
        """Affiche la liste des incidents créés par l'utilisateur connecté."""
        user_id = self.auth.utilisateur_connecte.id
        incidents = self.incident_dao.get_par_utilisateur(user_id)
        self._afficher_table_incidents(incidents)

    def detail_incident(self):
        """Affiche les détails d'un incident et la liste de ses interventions."""
        user = self.auth.utilisateur_connecte
        try:
            inc_id = int(input("ID de l'incident à consulter : "))
        except ValueError:
            print("[!] ID invalide.")
            return

        incident = self.incident_dao.get_by_id(inc_id)
        if not incident:
            print("[!] Incident introuvable.")
            return

        # Contrainte fonctionnelle : Seul l'auteur de l'incident ou un tech/admin peut voir le détail
        if user.role == "UTILISATEUR" and incident["utilisateur_id"] != user.id:
            print("[!] Accès refusé: Vous n'avez pas le droit de consulter cet incident.")
            return

        print("\n" + "-" * 50)
        print(f"DÉTAILS DE L'INCIDENT #{incident['id']}")
        print(f"Titre        : {incident['titre']}")
        print(f"Description  : {incident['description']}")
        print(f"Priorité     : {incident['priorite']}")
        print(f"Statut       : {incident['statut']}")
        print(f"Date Création: {incident['date_creation']}")
        print("-" * 50)

        interventions = self.intervention_dao.get_par_incident(inc_id)
        print(f"INTERVENTIONS ({len(interventions)}) :")
        if not interventions:
            print("  Aucune intervention enregistrée pour le moment.")
        else:
            for inv in interventions:
                print(f"  - [{inv['date_intervention']}] Tech: {inv['tech_prenom']} {inv['tech_nom']} ({inv['duree_minutes']} min) : {inv['commentaire']}")

    def filtrer_mes_incidents_par_statut(self):
        """Filtre les incidents par statut."""
        print("Statuts : OUVERT, EN_COURS, RESOLU, FERME, ANNULE")
        statut = input("Statut recherché : ").strip().upper()
        incidents = self.incident_dao.get_par_utilisateur(self.auth.utilisateur_connecte.id, statut=statut)
        self._afficher_table_incidents(incidents)

    def filtrer_mes_incidents_par_priorite(self):
        """Filtre les incidents par priorité."""
        print("Priorités : BASSE, MOYENNE, HAUTE, CRITIQUE")
        priorite = input("Priorité recherchée : ").strip().upper()
        incidents = self.incident_dao.get_par_utilisateur(self.auth.utilisateur_connecte.id, priorite=priorite)
        self._afficher_table_incidents(incidents)

    def annuler_mon_incident(self):
        """Permet d'annuler un incident uniquement s'il est au statut OUVERT."""
        try:
            inc_id = int(input("ID de l'incident à annuler : "))
        except ValueError:
            print("[!] ID invalide.")
            return

        incident = self.incident_dao.get_by_id(inc_id)
        if not incident or incident["utilisateur_id"] != self.auth.utilisateur_connecte.id:
            print("[!] Incident introuvable ou non autorisé.")
            return

        if self.incident_dao.changer_statut(inc_id, "ANNULE"):
            print("[SUCCESS] Incident annulé avec succès.")

    # =========================================================================
    # MENU TECHNICIEN
    # =========================================================================

    def afficher_menu_technicien(self):
        """Menu réservé aux techniciens."""
        user = self.auth.utilisateur_connecte
        print("\n" + "=" * 45)
        print(f"   ESPACE TECHNICIEN - [{user.prenom} {user.nom}]")
        print("=" * 45)
        print("1. Consulter les incidents actifs (OUVERT / EN_COURS)")
        print("2. Prendre en charge un incident (OUVERT -> EN_COURS)")
        print("3. Ajouter une intervention sur un incident")
        print("4. Résoudre un incident (EN_COURS -> RESOLU)")
        print("5. Fermer un incident résolu (RESOLU -> FERME)")
        print("6. Consulter mon historique d'incidents traités")
        print("7. Consulter le détail d'un incident")
        print("0. Se déconnecter")

        choix = input("\nVotre choix : ").strip()
        if choix == "1":
            self.lister_incidents_actifs()
        elif choix == "2":
            self.prendre_en_charge_incident()
        elif choix == "3":
            self.ajouter_intervention()
        elif choix == "4":
            self.resoudre_incident()
        elif choix == "5":
            self.fermer_incident()
        elif choix == "6":
            self.historique_technicien()
        elif choix == "7":
            self.detail_incident()
        elif choix == "0":
            self.auth.se_deconnecter()
        else:
            print("[!] Choix invalide.")

    def lister_incidents_actifs(self):
        """Affiche les incidents ouverts et en cours."""
        incidents = self.incident_dao.get_incidents_actifs()
        self._afficher_table_incidents(incidents)

    def prendre_en_charge_incident(self):
        """Passe le statut d'un incident de OUVERT à EN_COURS."""
        try:
            inc_id = int(input("ID de l'incident à prendre en charge : "))
        except ValueError:
            print("[!] ID invalide.")
            return

        if self.incident_dao.changer_statut(inc_id, "EN_COURS"):
            print(f"[SUCCESS] Incident #{inc_id} pris en charge (statut EN_COURS).")

    def ajouter_intervention(self):
        """Formulaire pour enregistrer une intervention."""
        try:
            inc_id = int(input("ID de l'incident : "))
            duree = int(input("Durée de l'intervention (en minutes) : "))
        except ValueError:
            print("[!] Durée ou ID invalide.")
            return

        commentaire = input("Commentaire d'intervention : ").strip()
        if not commentaire:
            print("[!] Le commentaire est obligatoire.")
            return

        user = self.auth.utilisateur_connecte
        inv = Intervention(
            incident_id=inc_id,
            technicien_id=user.id,
            commentaire=commentaire,
            duree_minutes=duree
        )
        if self.intervention_dao.ajouter(inv, role_technicien=user.role):
            print("[SUCCESS] Intervention enregistrée avec succès.")

    def resoudre_incident(self):
        """Passe le statut d'un incident de EN_COURS à RESOLU."""
        try:
            inc_id = int(input("ID de l'incident résolu : "))
        except ValueError:
            print("[!] ID invalide.")
            return

        if self.incident_dao.changer_statut(inc_id, "RESOLU"):
            print(f"[SUCCESS] Incident #{inc_id} marqué comme RESOLU.")

    def fermer_incident(self):
        """Passe le statut d'un incident de RESOLU à FERME."""
        try:
            inc_id = int(input("ID de l'incident à fermer : "))
        except ValueError:
            print("[!] ID invalide.")
            return

        if self.incident_dao.changer_statut(inc_id, "FERME"):
            print(f"[SUCCESS] Incident #{inc_id} FERME.")

    def historique_technicien(self):
        """Affiche les incidents traités par le technicien connecté."""
        incidents = self.incident_dao.get_historique_technicien(self.auth.utilisateur_connecte.id)
        self._afficher_table_incidents(incidents)

    # =========================================================================
    # MENU ADMIN
    # =========================================================================

    def afficher_menu_admin(self):
        """Menu complet réservé à l'administrateur."""
        user = self.auth.utilisateur_connecte
        print("\n" + "=" * 50)
        print(f"   PANNEAU D'ADMINISTRATION - [{user.prenom} {user.nom}]")
        print("=" * 50)
        print("1. Gestion des Utilisateurs (CRUD)")
        print("2. Consulter tous les incidents (Globaux)")
        print("3. Prise en charge / Interventions / Résolution Incident")
        print("4. Consulter les Statistiques & Rapports")
        print("0. Se déconnecter")

        choix = input("\nVotre choix : ").strip()
        if choix == "1":
            self.menu_crud_utilisateurs()
        elif choix == "2":
            incidents = self.incident_dao.get_all()
            self._afficher_table_incidents(incidents)
        elif choix == "3":
            self.afficher_menu_technicien()
        elif choix == "4":
            self.afficher_statistiques_admin()
        elif choix == "0":
            self.auth.se_deconnecter()
        else:
            print("[!] Choix invalide.")

    def menu_crud_utilisateurs(self):
        """Sous-menu pour le CRUD complet sur les utilisateurs."""
        print("\n--- GESTION DES UTILISATEURS ---")
        print("1. Ajouter un utilisateur")
        print("2. Afficher tous les utilisateurs")
        print("3. Afficher les détails d'un utilisateur (par ID ou Login)")
        print("4. Modifier un utilisateur")
        print("5. Supprimer un utilisateur")
        print("6. Rechercher un utilisateur")
        print("0. Retour")

        choix = input("\nVotre choix : ").strip()
        if choix == "1":
            self.admin_ajouter_utilisateur()
        elif choix == "2":
            self.admin_lister_utilisateurs()
        elif choix == "3":
            self.admin_detail_utilisateur()
        elif choix == "4":
            self.admin_modifier_utilisateur()
        elif choix == "5":
            self.admin_supprimer_utilisateur()
        elif choix == "6":
            self.admin_rechercher_utilisateur()

    def admin_ajouter_utilisateur(self):
        """Formulaire administrateur pour ajouter un utilisateur."""
        print("\n--- AJOUT UTILISATEUR ---")
        login = input("Login : ").strip()
        password = input("Mot de passe : ").strip()
        nom = input("Nom : ").strip()
        prenom = input("Prénom : ").strip()
        email = input("Email : ").strip()
        service = input("Service (ex: RH, Comptabilité, IT) : ").strip()

        print("Rôle : 1. UTILISATEUR | 2. TECHNICIEN | 3. ADMIN")
        c_role = input("Choix (1-3) : ").strip()
        map_role = {"1": "UTILISATEUR", "2": "TECHNICIEN", "3": "ADMIN"}
        role = map_role.get(c_role, "UTILISATEUR")

        u = Utilisateur(login=login, password=password, nom=nom, prenom=prenom, email=email, role=role, service=service)
        if self.user_dao.ajouter(u):
            print(f"[SUCCESS] Utilisateur {u.login} créé avec succès !")

    def admin_lister_utilisateurs(self):
        """Affiche la liste complète des utilisateurs."""
        users = self.user_dao.get_all()
        print("\n" + "-" * 75)
        print(f"{'ID':<4} | {'LOGIN':<12} | {'NOM COMPLET':<20} | {'RÔLE':<12} | {'SERVICE':<15}")
        print("-" * 75)
        for u in users:
            print(f"{u['id']:<4} | {u['login']:<12} | {u['prenom'] + ' ' + u['nom']:<20} | {u['role']:<12} | {u['service']:<15}")
        print("-" * 75)

    def admin_detail_utilisateur(self):
        """Affiche les détails d'un utilisateur par ID ou login."""
        recherche = input("Entrez l'ID ou le Login de l'utilisateur : ").strip()
        user = None
        if recherche.isdigit():
            u_row = self.user_dao.get_by_id(int(recherche))
            if u_row:
                user = Utilisateur(
                    id=u_row["id"], login=u_row["login"], password=u_row["password"],
                    nom=u_row["nom"], prenom=u_row["prenom"], email=u_row["email"],
                    role=u_row["role"], service=u_row["service"], date_creation=u_row["date_creation"]
                )
        else:
            user = self.user_dao.get_by_login(recherche)

        if user:
            print("\n" + "-" * 40)
            print(f"ID           : {user.id}")
            print(f"Login        : {user.login}")
            print(f"Nom Complet  : {user.prenom} {user.nom}")
            print(f"Email        : {user.email}")
            print(f"Rôle         : {user.role}")
            print(f"Service      : {user.service}")
            print(f"Date Création: {user.date_creation}")
            print("-" * 40)
        else:
            print("[!] Utilisateur non trouvé.")

    def admin_modifier_utilisateur(self):
        """Modifie les informations d'un utilisateur."""
        try:
            u_id = int(input("ID de l'utilisateur à modifier : "))
        except ValueError:
            print("[!] ID invalide.")
            return

        u_row = self.user_dao.get_by_id(u_id)
        if not u_row:
            print("[!] Utilisateur introuvable.")
            return

        print(f"Modification de l'utilisateur #{u_id} (Laissez vide pour conserver la valeur actuelle)")
        password = input(f"Mot de passe [{u_row['password']}] : ").strip() or u_row['password']
        nom = input(f"Nom [{u_row['nom']}] : ").strip() or u_row['nom']
        prenom = input(f"Prénom [{u_row['prenom']}] : ").strip() or u_row['prenom']
        email = input(f"Email [{u_row['email']}] : ").strip() or u_row['email']
        service = input(f"Service [{u_row['service']}] : ").strip() or u_row['service']
        role = input(f"Rôle (UTILISATEUR, TECHNICIEN, ADMIN) [{u_row['role']}] : ").strip().upper() or u_row['role']

        u = Utilisateur(id=u_id, login=u_row['login'], password=password, nom=nom, prenom=prenom, email=email, role=role, service=service)
        if self.user_dao.modifier(u):
            print("[SUCCESS] Utilisateur mis à jour.")

    def admin_supprimer_utilisateur(self):
        """Supprime un utilisateur s'il respecte les contraintes d'intégrité."""
        try:
            u_id = int(input("ID de l'utilisateur à supprimer : "))
        except ValueError:
            print("[!] ID invalide.")
            return

        if self.user_dao.supprimer_utilisateur(u_id):
            print("[SUCCESS] Utilisateur supprimé avec succès.")

    def admin_rechercher_utilisateur(self):
        """Recherche des utilisateurs par terme (nom, login ou service)."""
        terme = input("Terme de recherche : ").strip()
        users = self.user_dao.rechercher(terme)
        print(f"\nRÉSULTATS ({len(users)}) :")
        for u in users:
            print(f"  - #{u['id']} {u['login']} ({u['prenom']} {u['nom']}) | Rôle: {u['role']} | Service: {u['service']}")

    def afficher_statistiques_admin(self):
        """Affiche le rapport statistique complet réservé à l'administrateur."""
        print("\n" + "=" * 60)
        print("       RAPPORT STATISTIQUE ET DASHBOARD ADMIN")
        print("=" * 60)

        stats = self.incident_dao.get_stats_globales()

        print("\n1. INCIDENTS PAR STATUT :")
        for statut, count in stats.get("par_statut", {}).items():
            print(f"   - {statut:<10} : {count}")

        print("\n2. INCIDENTS PAR PRIORITÉ :")
        for prio, count in stats.get("par_priorite", {}).items():
            print(f"   - {prio:<10} : {count}")

        print(f"\n3. TEMPS MOYEN DE RÉSOLUTION : {stats.get('temps_moyen_resolution_heures', 0.0)} heures")
        print(f"4. TAUX DE RÉSOLUTION EN MOINS DE 48H : {stats.get('taux_resolution_48h', 0.0)} %")

        print("\n5. TOP 3 DES TECHNICIENS LES PLUS ACTIFS :")
        top = stats.get("top_techniciens", [])
        if not top:
            print("   Aucune donnée.")
        else:
            for i, tech in enumerate(top, 1):
                print(f"   {i}. {tech['prenom']} {tech['nom']} -> {tech['nb_interventions']} intervention(s)")

        print("\n6. DÉTAILS PERFORMANCES PAR TECHNICIEN :")
        details = stats.get("details_techniciens", [])
        if not details:
            print("   Aucune donnée.")
        else:
            for tech in details:
                tm = round(tech['temps_moyen'], 2) if tech['temps_moyen'] else 0.0
                print(f"   - {tech['prenom']} {tech['nom']} : {tech['nb_incidents_traites']} incident(s) traité(s) | Temps moyen: {tm} h")

        print("=" * 60)

    # =========================================================================
    # FONCTIONS UTILITAIRES D'AFFICHAGE
    # =========================================================================

    def _afficher_table_incidents(self, incidents):
        """Affiche joliment une liste d'incidents."""
        if not incidents:
            print("\nAucun incident trouvé.")
            return

        print("\n" + "-" * 75)
        print(f"{'ID':<4} | {'PRIORITÉ':<9} | {'STATUT':<10} | {'TITRE':<25} | {'DATE':<16}")
        print("-" * 75)
        for inc in incidents:
            titre_court = inc['titre'][:23] + ".." if len(inc['titre']) > 25 else inc['titre']
            print(f"{inc['id']:<4} | {inc['priorite']:<9} | {inc['statut']:<10} | {titre_court:<25} | {str(inc['date_creation'])[:16]}")
        print("-" * 75)
