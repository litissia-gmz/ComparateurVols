from database.db_manager import initialiser_base_de_donnees, obtenir_historique
from services.flight_service import recuperer_vols
from services.export_service import exporter_vers_csv, exporter_vers_json
from views.app_view import FlightTrackerView

def controlleur_recherche(depart, arrivee, date_vol):
    """Gère la recherche de vols."""
    try:
        vols, provient_du_cache = recuperer_vols(depart, arrivee, date_vol)
        vue.afficher_resultats(vols, provient_du_cache, depart, arrivee, date_vol)
    except Exception as e:
        vue.afficher_erreur(str(e))

def controlleur_historique():
    """Gère l'affichage de l'historique."""
    try:
        lignes = obtenir_historique()
        vue.afficher_historique(lignes)
    except Exception as e:
        vue.afficher_erreur(str(e))

def controlleur_export(format_fichier, chemin_fichier):
    """Gère l'export des données vers un fichier CSV ou JSON."""
    try:
        if format_fichier == "csv":
            total = exporter_vers_csv(chemin_fichier)
        else:
            total = exporter_vers_json(chemin_fichier)
        vue.afficher_succes_export(format_fichier, total, chemin_fichier)
    except Exception as e:
        vue.afficher_erreur(str(e))

if __name__ == "__main__":
    # 1. Initialise les tables SQLite
    initialiser_base_de_donnees()

    # 2. Instancie la vue avec ses trois contrôleurs
    vue = FlightTrackerView(
        callback_recherche=controlleur_recherche,
        callback_historique=controlleur_historique,
        callback_export=controlleur_export
    )

    # 3. Lance l'application
    vue.mainloop()