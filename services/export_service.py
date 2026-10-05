import csv
import json
from database.db_manager import obtenir_toutes_les_donnees

def exporter_vers_csv(chemin_fichier):
    """Exporte les données relationnelles de la base au format CSV."""
    lignes = obtenir_toutes_les_donnees()
    if not lignes:
        raise ValueError("Aucune donnée enregistrée en base à exporter.")

    en_tetes = [
        "ID_Recherche", "Depart", "Arrivee", "Date_Vol", "Date_Recherche",
        "Prix_EUR", "Compagnie", "Duree_Minutes", "Heure_Depart", "Heure_Arrivee", "Type_Trajet"
    ]

    with open(chemin_fichier, mode="w", newline="", encoding="utf-8") as f:
        redacteur = csv.writer(f, delimiter=";")
        redacteur.writerow(en_tetes)
        for ligne in lignes:
            redacteur.writerow(ligne)

    return len(lignes)

def exporter_vers_json(chemin_fichier):
    """Exporte les données au format JSON structuré par session de recherche."""
    lignes = obtenir_toutes_les_donnees()
    if not lignes:
        raise ValueError("Aucune donnée enregistrée en base à exporter.")

    # Regroupement hiérarchique : chaque recherche contient sa liste d'offres
    sessions = {}
    for r in lignes:
        r_id, dep, arr, d_vol, d_rech, prix, comp, duree, h_dep, h_arr, trajet = r

        if r_id not in sessions:
            sessions[r_id] = {
                "recherche_id": r_id,
                "trajet": f"{dep} -> {arr}",
                "date_vol": d_vol,
                "date_recherche": d_rech,
                "offres": []
            }

        sessions[r_id]["offres"].append({
            "prix_eur": prix,
            "compagnie": comp,
            "duree_minutes": duree,
            "heure_depart": h_dep,
            "heure_arrivee": h_arr,
            "type": trajet
        })

    donnees_json = list(sessions.values())

    with open(chemin_fichier, mode="w", encoding="utf-8") as f:
        json.dump(donnees_json, f, indent=4, ensure_ascii=False)

    return len(lignes)