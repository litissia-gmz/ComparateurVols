import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
from database.db_manager import chercher_en_cache, sauvegarder_recherche

# Charge les variables écrites dans le fichier .env
load_dotenv()
API_KEY = os.getenv("SERPAPI_KEY")

def extraire_et_nettoyer_vol(vol_brut):
    """Transforme un objet vol brut renvoyé par Google en un dictionnaire standardisé."""
    prix = vol_brut.get("price")
    segments = vol_brut.get("flights", [])
    
    compagnie = segments[0].get("airline", "Inconnue") if segments else "Inconnue"
    duree = vol_brut.get("total_duration", 0)
    
    heure_dep = segments[0].get("departure_airport", {}).get("time", "--:--") if segments else "--:--"
    heure_arr = segments[-1].get("arrival_airport", {}).get("time", "--:--") if segments else "--:--"
    
    escales = len(segments) - 1
    type_trajet = "Direct" if escales == 0 else f"{escales} escale(s)"

    return {
        "prix": prix,
        "compagnie": compagnie,
        "duree_minutes": duree,
        "heure_depart": heure_dep,
        "heure_arrivee": heure_arr,
        "type_trajet": type_trajet
    }

def recuperer_vols(depart, arrivee, date_vol):
    """
    Logique métier :
    1. Regarde d'abord si les données sont déjà en base locale (cache).
    2. Si oui -> renvoie les données locales sans consommer de crédit.
    3. Si non -> appelle l'API SerpApi, enregistre en base, et renvoie le résultat.
    """
    if not API_KEY:
        raise ValueError("Clé SERPAPI_KEY introuvable. Vérifie ton fichier .env !")

    # 1. Vérification du cache local
    vols_en_cache = chercher_en_cache(depart, arrivee, date_vol)
    if vols_en_cache:
        print("[CACHE] Données trouvées en base SQLite locale (aucun crédit consommé).")
        return vols_en_cache, True  # True = provient du cache

    # 2. Appel réseau vers l'API
    print("[API] Interrogation de Google Flights en direct...")
    params = {
        "engine": "google_flights",
        "departure_id": depart,
        "arrival_id": arrivee,
        "outbound_date": date_vol,
        "type": "2",
        "show_hidden": "true",
        "sort_by": "2",
        "currency": "EUR",
        "hl": "fr",
        "api_key": API_KEY
    }

    recherche = GoogleSearch(params)
    donnees = recherche.get_dict()

    tous_les_vols = donnees.get("best_flights", []) + donnees.get("other_flights", [])
    
    # Nettoyage et tri par prix croissant
    vols_propres = []
    for vol in tous_les_vols:
        if vol.get("price") is not None:
            vols_propres.append(extraire_et_nettoyer_vol(vol))

    vols_propres.sort(key=lambda x: x["prix"])

    # 3. Sauvegarde immédiate en base de données pour les prochaines requêtes
    if vols_propres:
        sauvegarder_recherche(depart, arrivee, date_vol, vols_propres)

    return vols_propres, False  # False = provient d'un appel réseau direct