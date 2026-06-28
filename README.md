# 🌍 Air & Water Quality Monitor

Système de monitoring environnemental basé sur ESP32 pour mesurer et visualiser en temps réel la température, l'humidité, la qualité de l'air et la qualité de l'eau via une interface web professionnelle.

## 📌 Vue d'ensemble

Ce projet combine :
- un microcontrôleur ESP32 avec capteurs,
- un backend Python Flask,
- une interface web interactive,
- un système d'alertes et d'historique des mesures.

Il permet de suivre l'environnement en temps réel et d'observer l'évolution des données sur un tableau de bord.

## ✅ Fonctionnalités principales

- Mesure de la température et de l'humidité
- Détection de la qualité de l'air
- Détection de gaz inflammables
- Mesure de la qualité de l'eau
- Affichage en temps réel dans une interface web
- Historique des données
- Support pour l'envoi depuis ESP32 via Wi-Fi

## 📁 Structure du projet

```text
air-water-quality/
├── src/
│   ├── backend/              # Backend Flask et API
│   ├── frontend/             # Interfaces web
│   ├── scripts/              # Scripts de lancement rapide
│   ├── desktop_monitor.py    # Application desktop autonome
│   ├── esp32_monitor_firmware.ino
│   └── requirements.txt
└── README.md                 # Documentation principale
```

## 🚀 Démarrage rapide

### 1. Prérequis

- Python 3.8+
- Arduino IDE (si vous voulez programmer l'ESP32)
- Pilotes ESP32 si nécessaire

### 2. Installer les dépendances

```powershell
cd src
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Lancer le serveur

Pour le backend :

```powershell
python src/backend/server.py
```

Pour l'interface web locale :

```powershell
python -m http.server 8000
```

Puis ouvrir :
- http://localhost:8000/monitoring_dashboard.html
- ou http://localhost:8000/advanced_dashboard.html

### 4. Utiliser l'application

- Ouvrir la page web dans le navigateur
- Vérifier les données en temps réel
- Tester avec des valeurs simulées si nécessaire

## 🔧 Configuration ESP32 / Arduino

### Installer Arduino IDE

1. Télécharger Arduino IDE depuis https://www.arduino.cc/en/software
2. Ajouter l'URL ESP32 dans les préférences :
   https://dl.espressif.com/dl/package_esp32_index.json
3. Installer le board ESP32 depuis le gestionnaire de cartes
4. Installer les bibliothèques nécessaires :
   - DHT sensor library
   - Adafruit Unified Sensor

### Programmer l'ESP32

1. Ouvrir [src/esp32_monitor_firmware.ino](src/esp32_monitor_firmware.ino)
2. Modifier le SSID, le mot de passe Wi-Fi et l'URL du serveur si nécessaire
3. Téléverser le code sur l'ESP32

## 🧠 Architecture du système

Le flux de fonctionnement est le suivant :

1. L'ESP32 lit les capteurs
2. Il envoie les données au backend via Wi-Fi
3. Le backend traite et stocke les mesures
4. L'interface web affiche les résultats en temps réel

## 📊 Format des données

L'ESP32 envoie généralement des données JSON contenant :

```json
{
  "temp": 25.5,
  "humidity": 65.3,
  "air_quality": 1.25,
  "flammable": 0.85,
  "water_quality": 450.75
}
```

## 🛠️ Scripts utiles

- [src/scripts/start_server.bat](src/scripts/start_server.bat) : lancement rapide sous Windows
- [src/scripts/start_server.ps1](src/scripts/start_server.ps1) : lancement rapide sous PowerShell

## ⚠️ Sécurité

Le fichier [src/esp32_monitor_firmware.ino](src/esp32_monitor_firmware.ino) contient des champs `ssid` et `password` à compléter avec vos propres identifiants Wi-Fi. Ne jamais publier ces informations dans un dépôt public.

## 🧩 Documentation

Toute la documentation du projet est maintenant regroupée ici dans ce fichier README pour un accès plus simple.

## 🧪 Dépannage rapide

- Si Python n'est pas reconnu, réinstaller Python en cochant "Add Python to PATH"
- Si la dépendance manque, exécuter : `pip install -r src/requirements.txt`
- Si le port 8000 est déjà utilisé, essayer un autre port
- Si l'interface ne s'affiche pas, vérifier que le serveur tourne bien