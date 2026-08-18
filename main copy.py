"""
Point d'entrée principal du projet Gestion des Tickets d'Incidents.
"""

import sys
import os

# Configuration des chemins d'importation
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from create_tables import creer_tables
from insert_test_data import insérer_donnees_test
from menu.auth import ServiceAuthentification
from menu.interface import InterfaceConsole


def main():
    """Initialise l'application et démarre la boucle principale."""
    print("=" * 60)
    print("  SYSTÈME DE GESTION DES INCIDENTS INFORMATIQUES (HELP DESK)")
    print("  Groupe ISI - Licence 2 Génie Logiciel (GL)")
    print("=" * 60)

    # Initialisation automatique de la base et des tables
    creer_tables()
    
    # Insertion des données de test si nécessaire
    insérer_donnees_test()

    # Démarrage des services et de l'interface console
    auth_service = ServiceAuthentification()
    interface = InterfaceConsole(auth_service)
    
    # Lancement de l'application
    interface.demarrer()


if __name__ == "__main__":
    main()
