import sqlite3
from datetime import datetime, timedelta

NOM_BDD = "vols_historique.db"

def ouvrir_connexion():
    """Crée ou ouvre le fichier SQLite et active les contraintes FK."""
    connexion = sqlite3.connect(NOM_BDD)
    connexion.execute("PRAGMA foreign_keys = ON;")
    return connexion

def initialiser_base_de_donnees():
    """Crée les deux tables relationnelles si elles n'existent pas."""
    connexion = ouvrir_connexion()
    curseur = connexion.cursor()

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS recherches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            depart TEXT NOT NULL,
            arrivee TEXT NOT NULL,
            date_vol TEXT NOT NULL,
            date_recherche TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS vols_trouves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recherche_id INTEGER NOT NULL,
            prix REAL NOT NULL,
            compagnie TEXT NOT NULL,
            duree_minutes INTEGER,
            heure_depart TEXT,
            heure_arrivee TEXT,
            type_trajet TEXT,
            FOREIGN KEY (recherche_id) REFERENCES recherches(id) ON DELETE CASCADE
        );
    """)

    connexion.commit()
    connexion.close()

def chercher_en_cache(depart, arrivee, date_vol, validite_heures=6):
    """Vérifie si une recherche identique existe depuis moins de 6 heures."""
    connexion = ouvrir_connexion()
    curseur = connexion.cursor()

    date_limite = datetime.now() - timedelta(hours=validite_heures)
    date_limite_texte = date_limite.strftime("%Y-%m-%d %H:%M:%S")

    curseur.execute("""
        SELECT id FROM recherches
        WHERE depart = ? AND arrivee = ? AND date_vol = ? AND date_recherche >= ?
        ORDER BY date_recherche DESC
        LIMIT 1;
    """, (depart, arrivee, date_vol, date_limite_texte))

    ligne = curseur.fetchone()
    if not ligne:
        connexion.close()
        return None

    recherche_id = ligne[0]

    curseur.execute("""
        SELECT prix, compagnie, duree_minutes, heure_depart, heure_arrivee, type_trajet
        FROM vols_trouves
        WHERE recherche_id = ?
        ORDER BY prix ASC;
    """, (recherche_id,))

    vols_recuperes = []
    for r in curseur.fetchall():
        vols_recuperes.append({
            "prix": r[0],
            "compagnie": r[1],
            "duree_minutes": r[2],
            "heure_depart": r[3],
            "heure_arrivee": r[4],
            "type_trajet": r[5]
        })

    connexion.close()
    return vols_recuperes

def sauvegarder_recherche(depart, arrivee, date_vol, liste_vols):
    """Enregistre une recherche et ses vols associés."""
    connexion = ouvrir_connexion()
    curseur = connexion.cursor()

    curseur.execute("""
        INSERT INTO recherches (depart, arrivee, date_vol)
        VALUES (?, ?, ?);
    """, (depart, arrivee, date_vol))

    recherche_id = curseur.lastrowid

    for vol in liste_vols:
        curseur.execute("""
            INSERT INTO vols_trouves (
                recherche_id, prix, compagnie, duree_minutes,
                heure_depart, heure_arrivee, type_trajet
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            recherche_id,
            vol["prix"],
            vol["compagnie"],
            vol["duree_minutes"],
            vol["heure_depart"],
            vol["heure_arrivee"],
            vol["type_trajet"]
        ))

    connexion.commit()
    connexion.close()

def obtenir_historique():
    """Récupère les 10 dernières recherches avec leur meilleur tarif."""
    connexion = ouvrir_connexion()
    curseur = connexion.cursor()

    curseur.execute("""
        SELECT r.depart, r.arrivee, r.date_vol, MIN(v.prix), r.date_recherche
        FROM recherches r
        JOIN vols_trouves v ON r.id = v.recherche_id
        GROUP BY r.id
        ORDER BY r.date_recherche DESC
        LIMIT 10;
    """)

    lignes = curseur.fetchall()
    connexion.close()
    return lignes

def obtenir_toutes_les_donnees():
    """Récupère l'intégralité des recherches et des offres associées via une jointure SQL."""
    connexion = ouvrir_connexion()
    curseur = connexion.cursor()

    curseur.execute("""
        SELECT 
            r.id,
            r.depart,
            r.arrivee,
            r.date_vol,
            r.date_recherche,
            v.prix,
            v.compagnie,
            v.duree_minutes,
            v.heure_depart,
            v.heure_arrivee,
            v.type_trajet
        FROM recherches r
        JOIN vols_trouves v ON r.id = v.recherche_id
        ORDER BY r.date_recherche DESC, v.prix ASC;
    """)

    lignes = curseur.fetchall()
    connexion.close()
    return lignes