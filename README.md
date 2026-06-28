<div align="center">

# Moniteur de Qualité de l'Air & de l'Eau

### Système de monitoring environnemental en temps réel basé sur ESP32

*Mesurez, visualisez et analysez la qualité de l'air et de l'eau depuis une interface web professionnelle — sans équipement spécialisé.*

---

</div>

## Aperçu

Ce projet est un système complet de surveillance environnementale. Une carte ESP32 collecte en continu des données depuis plusieurs capteurs, les envoie via Wi-Fi à un serveur local, et les affiche sur un tableau de bord web accessible depuis n'importe quel navigateur.

**Ce que le système mesure :**

- 🌡️ Température et humidité ambiante
- 💨 Qualité de l'air et détection de gaz inflammables
- 💧 Qualité de l'eau

**Ce que le système offre :**

- Affichage en temps réel sur tableau de bord web
- Historique des mesures
- Interface web interactive (desktop et mobile)
- Support de simulation de données pour les tests

**Durée d'installation estimée :** 20 à 30 minutes

---

## Prérequis

Avant de commencer, assurez-vous de disposer des éléments suivants :

| Élément | Détails |
|---|---|
| Ordinateur | Windows 10 ou version ultérieure |
| Python | Version 3.8 ou supérieure |
| Carte ESP32 | N'importe quel ESP32 Dev Module |
| Câble USB | Compatible avec votre carte (micro-USB ou USB-C) |
| Réseau Wi-Fi | Pour la communication entre l'ESP32 et le serveur |
| Arduino IDE | Uniquement si vous souhaitez reprogrammer l'ESP32 |

---

## Structure du projet

```text
air-water-quality/
├── src/
│   ├── backend/                      # Serveur Flask et API de données
│   ├── frontend/                     # Interfaces web (tableaux de bord)
│   ├── scripts/                      # Scripts de lancement rapide
│   ├── desktop_monitor.py            # Application desktop autonome
│   ├── esp32_monitor_firmware.ino    # Code à téléverser sur l'ESP32
│   └── requirements.txt             # Dépendances Python
└── README.md                         # Documentation principale
```

---

## Installation et démarrage

### Étape 1 — Cloner ou télécharger le projet

Téléchargez le projet sur votre ordinateur et placez-le dans un dossier de votre choix.

---

### Étape 2 — Installer les dépendances Python

Ouvrez un terminal PowerShell dans le dossier du projet et exécutez les commandes suivantes :

```powershell
cd src
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> **Qu'est-ce que cela fait ?** Ces commandes créent un environnement Python isolé pour ce projet, puis installent toutes les bibliothèques nécessaires automatiquement.

> **Python n'est pas reconnu ?** Réinstallez Python depuis **https://www.python.org/downloads/** en cochant l'option **"Add Python to PATH"** lors de l'installation.

---

### Étape 3 — Lancer le serveur backend

```powershell
python src/backend/server.py
```

Laissez ce terminal ouvert — le serveur doit rester actif pour recevoir les données de l'ESP32.

---

### Étape 4 — Lancer l'interface web

Dans un second terminal, exécutez :

```powershell
python -m http.server 8000
```

Puis ouvrez l'un des tableaux de bord dans votre navigateur :

| Interface | URL |
|---|---|
| Tableau de bord principal | http://localhost:8000/monitoring_dashboard.html |
| Tableau de bord avancé | http://localhost:8000/advanced_dashboard.html |

> **Le port 8000 est déjà utilisé ?** Remplacez `8000` par un autre numéro, par exemple `8080`.

---

### Étape 5 — Scripts de lancement rapide *(optionnel)*

Pour éviter de relancer les commandes à chaque fois, des scripts sont fournis :

| Script | Usage |
|---|---|
| `src/scripts/start_server.bat` | Lancement rapide sous Windows (double-clic) |
| `src/scripts/start_server.ps1` | Lancement rapide sous PowerShell |

---

## Configuration de l'ESP32

> Suivez cette section uniquement si vous souhaitez modifier ou retéléverser le firmware sur la carte ESP32.

### Installer Arduino IDE

1. Téléchargez Arduino IDE depuis : **https://www.arduino.cc/en/software/**

2. Ouvrez Arduino IDE, allez dans **Fichier → Préférences** et ajoutez l'URL suivante dans le champ **"URL de gestionnaire de cartes supplémentaires"** :

   ```
   https://dl.espressif.com/dl/package_esp32_index.json
   ```

3. Allez dans **Outils → Type de carte → Gestionnaire de cartes**, recherchez `esp32` et installez **"esp32 by Espressif Systems"**

4. Installez les bibliothèques suivantes via le **Gestionnaire de bibliothèques** :
   - `DHT sensor library`
   - `Adafruit Unified Sensor`

### Téléverser le firmware

1. Ouvrez le fichier `src/esp32_monitor_firmware.ino` dans Arduino IDE

2. Modifiez les lignes suivantes avec vos propres informations :

   ```cpp
   const char* ssid     = "VotreNomWiFi";
   const char* password = "VotreMotDePasse";
   const char* serverURL = "http://192.168.X.X:5000/data"; // Adresse IP de votre PC
   ```

3. Branchez l'ESP32, sélectionnez le bon port dans **Outils → Port**, puis cliquez sur **Téléverser**

> ⚠️ **Important :** Ne publiez jamais vos identifiants Wi-Fi dans un dépôt public. Utilisez des variables d'environnement ou un fichier de configuration exclu du dépôt (`.gitignore`).

---

## Format des données

L'ESP32 envoie les mesures au serveur au format JSON :

```json
{
  "temp": 25.5,
  "humidity": 65.3,
  "air_quality": 1.25,
  "flammable": 0.85,
  "water_quality": 450.75
}
```

---

## Architecture du système

Le fonctionnement suit ce flux :

```
Capteurs ESP32  →  Wi-Fi  →  Serveur Flask  →  Interface Web
```

1. L'ESP32 lit les capteurs en continu
2. Il envoie les données au serveur via Wi-Fi
3. Le serveur Flask traite et stocke les mesures
4. Le tableau de bord web affiche les résultats en temps réel

---

## Résolution des problèmes

| Problème | Solution |
|---|---|
| Python non reconnu dans le terminal | Réinstallez Python en cochant **"Add Python to PATH"** |
| Erreur de dépendance manquante | Exécutez `pip install -r src/requirements.txt` |
| Le port 8000 est déjà utilisé | Changez le port : `python -m http.server 8080` |
| L'interface web ne s'affiche pas | Vérifiez que le serveur backend tourne toujours dans son terminal |
| L'ESP32 n'envoie pas de données | Vérifiez le SSID, le mot de passe Wi-Fi et l'adresse IP du serveur dans le firmware |
| Carte ESP32 non détectée | Installez le pilote CP210x ou CH340 selon votre modèle de carte |

---

## Liens utiles

| Ressource | URL |
|---|---|
| Arduino IDE | https://www.arduino.cc/en/software/ |
| Python | https://www.python.org/downloads/ |
| Pilote CP210x | https://www.silabs.com/software-and-tools/usb-to-uart-bridge-vcp-drivers |
| Pilote CH340 | https://www.wch-ic.com/downloads/CH341SER_EXE.html |
| Index du paquet ESP32 | https://dl.espressif.com/dl/package_esp32_index.json |

---

<h3 align="center">🧑🏻‍💻 | Responsable actuel : <a href="https://github.com/mohamedtalhaouii" target="_blank">----</a></h3>
