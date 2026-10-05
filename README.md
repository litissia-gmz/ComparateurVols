# ✈️ Système de Veille Tarifaire Aérienne

Application desktop d'analyse et de comparaison des tarifs de vols en temps réel, conçue selon l'architecture logicielle MVC et intégrant une persistance relationnelle avec cache local.

## 🏗️ Architecture & Fonctionnalités

- **Pattern MVC :** Découplage strict entre la vue graphique, la logique métier et la couche de persistance.
- **Cache Local & Optimisation :** Système de mise en cache SQLite avec politique d'invalidation temporelle (6 heures) pour optimiser les temps de réponse et réduire l'usage de l'API externe.
- **Base de Données Relationnelle :** Schéma SQLite normalisé (`recherches`, `vols_trouves`) avec intégrité référentielle (`FOREIGN KEY` et `ON DELETE CASCADE`).
- **Exports Métier :** Extraction et transformation des relevés tarifaires vers les formats CSV et JSON structuré.

## 🛠️ Stack Technique

- **Langage :** Python 3
- **Interface graphique :** CustomTkinter
- **Base de données :** SQLite3
- **Source de données :** API SerpApi (Google Flights Engine)

## 🚀 Installation & Lancement

1. Cloner le projet :
   ```bash
   git clone [https://github.com/VOTRE_PSEUDO/ComparateurVols.git](https://github.com/litissia-gmz/ComparateurVols.git)
   cd ComparateurVols