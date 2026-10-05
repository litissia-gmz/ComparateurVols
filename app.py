import customtkinter as ctk
from serpapi import GoogleSearch

# Configuration du thème graphique
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Fenêtre principale
app = ctk.CTk()
app.title("✈️ Comparateur de Vols - Temps Réel")
app.geometry("540x680")

# 1. Titre
label_titre = ctk.CTkLabel(
    app,
    text="✈️ Comparateur de Vols (Temps Réel)",
    font=("Arial", 20, "bold")
)
label_titre.pack(pady=20)

# 2. Champs de saisie
entry_depart = ctk.CTkEntry(
    app,
    placeholder_text="Aéroport départ (ex: PKX, CDG)",
    width=340
)
entry_depart.pack(pady=8)

entry_arrivee = ctk.CTkEntry(
    app,
    placeholder_text="Aéroport arrivée (ex: ALG, JFK)",
    width=340
)
entry_arrivee.pack(pady=8)

entry_date = ctk.CTkEntry(
    app,
    placeholder_text="Date de vol (AAAA-MM-JJ, ex: 2027-04-01)",
    width=340
)
entry_date.pack(pady=8)

# 3. Zone d'affichage des résultats
label_resultat = ctk.CTkLabel(
    app,
    text="Renseigne l'itinéraire et la date, puis lance la recherche.",
    font=("Arial", 13),
    text_color="gray",
    justify="left"
)
label_resultat.pack(pady=20)

# 4. Fonction pour formater un vol en texte clair
def formater_vol(vol, medaille):
    prix = vol.get("price", "N/C")
    segments = vol.get("flights", [])
    compagnie = segments[0].get("airline", "Inconnue") if segments else "Inconnue"
    
    # Durée totale
    duree_min = vol.get("total_duration", 0)
    h = duree_min // 60
    m = duree_min % 60
    texte_duree = f"{h}h{m:02d}" if h > 0 else f"{m}min"

    # Horaires
    h_dep = segments[0].get("departure_airport", {}).get("time", "--:--") if segments else "--:--"
    h_arr = segments[-1].get("arrival_airport", {}).get("time", "--:--") if segments else "--:--"

    # Type de vol (direct ou escales)
    escales = len(segments) - 1
    type_trajet = "Direct" if escales == 0 else f"{escales} escale(s)"

    return f"{medaille} {prix} € | {compagnie} ({type_trajet})\n    🕒 {h_dep} ➔ {h_arr} (Durée : {texte_duree})"

# 5. Logique de recherche complète
def lancer_recherche():
    depart = entry_depart.get().upper().strip()
    arrivee = entry_arrivee.get().upper().strip()
    date_vol = entry_date.get().strip()

    if not (depart and arrivee and date_vol):
        label_resultat.configure(
            text="⚠️ Merci de remplir tous les champs !",
            text_color="#E74C3C"
        )
        return

    label_resultat.configure(
        text="⏳ Récupération de l'ensemble des offres (y compris cachées)...",
        text_color="yellow"
    )
    app.update()

    try:
        # Paramètres optimisés : show_hidden=true débloque tous les vols cachés
        params = {
            "engine": "google_flights",
            "departure_id": depart,
            "arrival_id": arrivee,
            "outbound_date": date_vol,
            "type": "2",           # Aller simple
            "show_hidden": "true", # Débloque "Afficher plus de vols"
            "sort_by": "2",        # Force le tri par prix le plus bas
            "currency": "EUR",
            "hl": "fr",
            "api_key": "5b4ac4941fd479189aa6eded7d78155b229d3ad684632a6a9634bb46a2631444"
        }

        search = GoogleSearch(params)
        resultats = search.get_dict()

        # On rassemble absolument TOUTES les listes de vols renvoyées
        tous_les_vols = resultats.get("best_flights", []) + resultats.get("other_flights", [])

        # On garde uniquement ceux qui ont un prix chiffré
        vols_avec_prix = [v for v in tous_les_vols if v.get("price") is not None]

        if vols_avec_prix:
            # Tri strict du plus petit au plus grand prix
            vols_avec_prix.sort(key=lambda x: x.get("price"))

            medailles = ["🥇", "🥈", "🥉"]
            lignes = [f"✈️ Trajet réel : {depart} ➔ {arrivee} au {date_vol}\n"]
            
            # On prend les 3 premiers
            top_3 = vols_avec_prix[:3]
            for i, vol in enumerate(top_3):
                lignes.append(formater_vol(vol, medailles[i]))

            texte_final = "\n\n".join(lignes)
            label_resultat.configure(
                text=texte_final,
                text_color="#2ECC71"
            )
        else:
            label_resultat.configure(
                text="❌ Aucun vol trouvé pour cet itinéraire à cette date.",
                text_color="#E74C3C"
            )

    except Exception as e:
        label_resultat.configure(
            text=f"⚠️ Erreur : {str(e)}",
            text_color="#E74C3C"
        )

# 6. Bouton de recherche
bouton_rechercher = ctk.CTkButton(
    app,
    text="🔍 Trouver les vols les moins chers",
    command=lancer_recherche,
    width=240,
    height=42
)
bouton_rechercher.pack(pady=10)

# Lancement
app.mainloop()