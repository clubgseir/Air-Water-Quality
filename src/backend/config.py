"""
========================================
Configuration - Moniteur Air & Eau PRO
========================================

Fichier de configuration centralisé pour personnaliser
l'application sans modifier le code principal.

Usage:
    from backend.config import THRESHOLDS, PORTS, COLORS
"""

# ============ CONFIGURATION SÉRIELLE ============
SERIAL_CONFIG = {
    'default_port': 'COM3',          # Port par défaut
    'default_baudrate': 115200,      # Vitesse défaut
    'timeout': 1,                     # Timeout lecture (sec)
    'encoding': 'utf-8',              # Encodage texte
}

# ============ SEUILS D'ALERTE ============
THRESHOLDS = {
    'temperature': {
        'min_good': 15,               # Minimum bonne température
        'max_good': 30,               # Maximum bonne température
        'critical_high': 40,          # Critique haute
        'critical_low': 5,            # Critique basse
        'unit': '°C'
    },
    
    'humidity': {
        'min_good': 30,               # Minimum bonne humidité
        'max_good': 70,               # Maximum bonne humidité
        'critical_high': 90,          # Critique haute (moisi)
        'critical_low': 10,           # Critique basse (trop sec)
        'unit': '%'
    },
    
    'mq135_air_quality': {
        'excellent': 400,             # < 400 ppm
        'good': 800,                  # 400-800 ppm
        'fair': 1200,                 # 800-1200 ppm
        'poor': 2000,                 # 1200-2000 ppm
        'critical': 2000,             # > 2000 ppm
        'unit': 'ppm',
        'sensor_name': 'CO2/Qualité Air'
    },
    
    'mq9_flammable': {
        'excellent': 10,              # < 10 ppm
        'good': 20,                   # 10-20 ppm
        'fair': 50,                   # 20-50 ppm
        'poor': 100,                  # 50-100 ppm
        'critical': 100,              # > 100 ppm ⚠️ DANGER
        'unit': 'ppm',
        'sensor_name': 'Gaz Inflammables'
    },
    
    'water_quality': {
        'excellent': 300,             # < 300 µS/cm (très pur)
        'good': 600,                  # 300-600 µS/cm
        'fair': 1000,                 # 600-1000 µS/cm
        'poor': 2000,                 # 1000-2000 µS/cm
        'critical': 2000,             # > 2000 µS/cm
        'unit': 'µS/cm',
        'sensor_name': 'Conductivité Eau'
    },
    
    'water_temperature': {
        'min_good': 10,               # Minimum bonne température eau
        'max_good': 30,               # Maximum bonne température eau
        'critical_high': 40,          # Critique haute
        'critical_low': 0,            # Critique basse (gel)
        'unit': '°C'
    }
}

# ============ COULEURS & STYLES ============
COLORS = {
    'primary': '#667eea',             # Couleur principale (bleu/violet)
    'success': '#51cf66',             # Vert (bon)
    'warning': '#ffd43b',             # Jaune (attention)
    'danger': '#ff6b6b',              # Rouge (danger)
    'orange': '#f76707',              # Orange (mauvais)
    'info': '#4dabf7',                # Bleu (information)
}

# ============ ALERTES SONORES ============
AUDIO_CONFIG = {
    'enabled': True,                   # Activer/désactiver son
    'volume': 70,                      # Volume par défaut (0-100)
    'warning_frequency': 600,          # Hz (fréquence son alerte)
    'critical_frequency': 1000,        # Hz (fréquence son critique)
    'warning_duration': 300,           # ms (durée alerte)
    'critical_duration': 500,          # ms (durée critique)
}

# ============ NOTIFICATIONS HAPTIQUES ============
VIBRATION_CONFIG = {
    'enabled': True,                   # Activer/désactiver vibration
    'warning': [200, 100, 200],        # Pattern vibration alerte (ms)
    'critical': [100, 100, 100, 100, 100],  # Pattern vibration critique
}

# ============ INTERFACE ============
UI_CONFIG = {
    'app_name': 'Moniteur Air & Eau PRO',
    'version': '3.0',
    'max_history_points': 300,         # Garder 300 derniers points
    'update_interval_ms': 500,         # Mettre à jour tous les 500ms
    'chart_refresh_ms': 1000,          # Rafraîchir graphique tous les 1s
}

# ============ STICKERS & REWARDS ============
GAMIFICATION = {
    'stickers': ['🎉', '🌟', '✨', '🎊', '🏆', '💯', '👏', '🚀'],
    'confetti_count': 30,              # Nombres de confetti à générer
    'confetti_emojis': ['🎉', '✨', '🌟', '💫'],
    
    'achievements': {
        'detective': {
            'name': 'Détective',
            'description': '10 minutes sans alerte',
            'icon': '🔍',
            'reward_points': 100
        },
        'expert': {
            'name': 'Expert',
            'description': '1 heure sans alerte',
            'icon': '🏆',
            'reward_points': 500
        },
        'ecologist': {
            'name': 'Écologiste',
            'description': '0 alertes en 1 jour',
            'icon': '💚',
            'reward_points': 1000
        },
        'scientist': {
            'name': 'Scientist',
            'description': 'Utiliser le système 7 jours',
            'icon': '🚀',
            'reward_points': 2000
        }
    }
}

# ============ DONNÉES & LOGS ============
DATA_CONFIG = {
    'log_enabled': True,               # Enregistrer les données
    'log_file': 'data/sensor_log.csv',
    'log_interval_s': 60,              # Enregistrer chaque minute
    'database_enabled': False,         # SQLite (optionnel)
    'database_file': 'data/sensors.db'
}

# ============ PARAMÈTRES SERVEUR ============
SERVER_CONFIG = {
    'host': '0.0.0.0',                # Écouter sur toutes les interfaces
    'port': 5000,                     # Port Flask
    'debug': False,                    # Mode debug (True = developpement)
    'threaded': True,                  # Support multi-thread
}

# ============ LANGUE & LOCALISATION ============
LOCALE_CONFIG = {
    'default_language': 'fr',          # Français par défaut
    'supported_languages': ['fr', 'en', 'es', 'de'],
    'timezone': 'Europe/Paris',
}

# ============ CALIBRATION CAPTEURS ============
CALIBRATION = {
    'mq135': {
        'RL': 10,                      # Valeur résistance charge (kOhms)
        'Ro_clean_air': 3.7,           # Résistance air propre
        'a': 102.2,
        'b': -2.427
    },
    
    'mq9': {
        'RL': 10,
        'Ro_clean_air': 2.3,
        'a': 9.83,
        'b': -0.322
    }
}

# ============ API ENDPOINTS ============
API_ENDPOINTS = {
    'base_url': 'http://localhost:5000',
    'api_prefix': '/api',
    'websocket_url': 'ws://localhost:5000/socket.io'
}

# ============ EXPORTE DE CONFIG ============
CONFIG = {
    'SERIAL': SERIAL_CONFIG,
    'THRESHOLDS': THRESHOLDS,
    'COLORS': COLORS,
    'AUDIO': AUDIO_CONFIG,
    'VIBRATION': VIBRATION_CONFIG,
    'UI': UI_CONFIG,
    'GAMIFICATION': GAMIFICATION,
    'DATA': DATA_CONFIG,
    'SERVER': SERVER_CONFIG,
    'LOCALE': LOCALE_CONFIG,
    'CALIBRATION': CALIBRATION,
    'API': API_ENDPOINTS
}

if __name__ == '__main__':
    # Afficher la configuration
    import json
    print(json.dumps(CONFIG, indent=2, ensure_ascii=False))
