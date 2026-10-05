import customtkinter as ctk
from tkinter import filedialog

class FlightTrackerView(ctk.CTk):
    def __init__(self, callback_recherche, callback_historique, callback_export):
        super().__init__()

        self.callback_recherche = callback_recherche
        self.callback_historique = callback_historique
        self.callback_export = callback_export

        self.title("✈️ Système de Veille Tarifaire - Architecture MVC")
        self.geometry("580x760")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.creer_composants()

    def creer_composants(self):
        # Titre
        self.label_titre = ctk.CTkLabel(
            self,
            text="✈️ Observatoire des Tarifs Aériens",
            font=("Arial", 20, "bold")
        )
        self.label_titre.pack(pady=10)

        self.label_sous_titre = ctk.CTkLabel(
            self,
            text="Architecture MVC | Cache SQLite | Export CSV / JSON",
            font=("Arial", 11),
            text_color="gray"
        )
        self.label_sous_titre.pack(pady=2)

        # Formulaire
        self.entry_depart = ctk.CTkEntry(self, placeholder_text="Aéroport départ (ex: CDG)", width=360)
        self.entry_depart.pack(pady=5)

        self.entry_arrivee = ctk.CTkEntry(self, placeholder_text="Aéroport arrivée (ex: ALG, JFK)", width=360)
        self.entry_arrivee.pack(pady=5)

        self.entry_date = ctk.CTkEntry(self, placeholder_text="Date (AAAA-MM-JJ, ex: 2026-11-15)", width=360)
        self.entry_date.pack(pady=5)

        # Ligne 1 d'actions : Recherche et Historique
        cadre_actions = ctk.CTkFrame(self, fg_color="transparent")
        cadre_actions.pack(pady=8)

        self.btn_chercher = ctk.CTkButton(
            cadre_actions,
            text="🔍 Rechercher",
            command=self.declencher_recherche,
            width=160,
            height=36
        )
        self.btn_chercher.pack(side="left", padx=5)

        self.btn_historique = ctk.CTkButton(
            cadre_actions,
            text="📜 Historique BDD",
            command=self.declencher_historique,
            width=160,
            height=36,
            fg_color="#34495E",
            hover_color="#2C3E50"
        )
        self.btn_historique.pack(side="left", padx=5)

        # Ligne 2 d'actions : Exports de données
        cadre_exports = ctk.CTkFrame(self, fg_color="transparent")
        cadre_exports.pack(pady=4)

        self.btn_export_csv = ctk.CTkButton(
            cadre_exports,
            text="📊 Export CSV",
            command=lambda: self.declencher_export("csv"),
            width=160,
            height=32,
            fg_color="#1E8449",
            hover_color="#145A32"
        )
        self.btn_export_csv.pack(side="left", padx=5)

        self.btn_export_json = ctk.CTkButton(
            cadre_exports,
            text="📄 Export JSON",
            command=lambda: self.declencher_export("json"),
            width=160,
            height=32,
            fg_color="#7D6608",
            hover_color="#5B4605"
        )
        self.btn_export_json.pack(side="left", padx=5)

        # Badge source
        self.label_badge = ctk.CTkLabel(self, text="", font=("Arial", 11, "bold"))
        self.label_badge.pack(pady=2)

        # Zone d'affichage
        self.label_resultats = ctk.CTkLabel(
            self,
            text="Renseigne un itinéraire, consulte l'historique ou exporte les données.",
            font=("Arial", 13),
            text_color="gray",
            justify="left"
        )
        self.label_resultats.pack(pady=10)

    def declencher_recherche(self):
        dep = self.entry_depart.get().upper().strip()
        arr = self.entry_arrivee.get().upper().strip()
        date = self.entry_date.get().strip()

        if not (dep and arr and date):
            self.afficher_erreur("Merci de remplir l'ensemble des champs.")
            return

        self.btn_chercher.configure(state="disabled")
        self.btn_historique.configure(state="disabled")
        self.label_badge.configure(text="")
        self.label_resultats.configure(
            text="⏳ Traitement en cours (analyse du cache ou requête API)...",
            text_color="yellow"
        )
        self.update()
        self.callback_recherche(dep, arr, date)

    def declencher_historique(self):
        self.label_badge.configure(text="🗄️ Données extraites de la base SQLite locale", text_color="#9B59B6")
        self.callback_historique()

    def declencher_export(self, format_fichier):
        if format_fichier == "csv":
            chemin = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Fichiers CSV", "*.csv")],
                title="Enregistrer l'export CSV"
            )
        else:
            chemin = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Fichiers JSON", "*.json")],
                title="Enregistrer l'export JSON"
            )

        if chemin:
            self.callback_export(format_fichier, chemin)

    def afficher_resultats(self, vols, provient_du_cache, dep, arr, date):
        self.btn_chercher.configure(state="normal")
        self.btn_historique.configure(state="normal")

        if provient_du_cache:
            self.label_badge.configure(
                text="⚡ Données issues du Cache Local (0 crédit consommé)",
                text_color="#3498DB"
            )
        else:
            self.label_badge.configure(
                text="🌐 Données en direct de Google Flights (Synchronisé en BDD)",
                text_color="#E67E22"
            )

        if not vols:
            self.label_resultats.configure(
                text="❌ Aucun vol trouvé pour cet itinéraire.",
                text_color="#E74C3C"
            )
            return

        medailles = ["🥇", "🥈", "🥉"]
        lignes = [f"Itinéraire : {dep} ➔ {arr} le {date}\n"]

        top_3 = vols[:3]
        for i, vol in enumerate(top_3):
            duree_min = vol["duree_minutes"]
            h = duree_min // 60
            m = duree_min % 60
            texte_duree = f"{h}h{m:02d}" if h > 0 else f"{m}min"

            lignes.append(
                f"{medailles[i]} {vol['prix']} € | {vol['compagnie']} ({vol['type_trajet']})\n"
                f"    🕒 {vol['heure_depart']} ➔ {vol['heure_arrivee']} (Durée : {texte_duree})"
            )

        self.label_resultats.configure(
            text="\n\n".join(lignes),
            text_color="#2ECC71"
        )

    def afficher_historique(self, lignes_historique):
        self.btn_chercher.configure(state="normal")
        self.btn_historique.configure(state="normal")

        if not lignes_historique:
            self.label_resultats.configure(
                text="ℹ️ Aucune recherche enregistrée dans la base pour le moment.",
                text_color="gray"
            )
            return

        lignes = ["📋 DERNIÈRES RECHERCHES EN BASE SQL :\n"]
        for r in lignes_historique:
            dep, arr, date_vol, min_prix, date_rech = r
            date_courte = date_rech[:16] if date_rech else ""
            lignes.append(
                f"• {dep} ➔ {arr} ({date_vol})\n"
                f"  Meilleur tarif relevé : {min_prix} €  [le {date_courte}]"
            )

        self.label_resultats.configure(
            text="\n\n".join(lignes),
            text_color="#ECF0F1"
        )

    def afficher_succes_export(self, format_fichier, total_lignes, chemin):
        self.label_badge.configure(
            text=f"✅ Export {format_fichier.upper()} réussi ({total_lignes} offres sauvegardées)",
            text_color="#2ECC71"
        )

    def afficher_erreur(self, message):
        self.btn_chercher.configure(state="normal")
        self.btn_historique.configure(state="normal")
        self.label_badge.configure(text="")
        self.label_resultats.configure(
            text=f"⚠️ {message}",
            text_color="#E74C3C"
        )