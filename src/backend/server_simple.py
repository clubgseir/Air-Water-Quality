"""
Moniteur Air & Eau PRO v3.0 - Backend Simple
Serveur Flask sans dépendance COM7
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
from collections import deque

# Déterminer les chemins
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_FILE = os.path.join(WORKSPACE, 'frontend', 'advanced_dashboard.html')

print(f"📁 Workspace: {WORKSPACE}")
print(f"📄 Interface HTML: {TEMPLATE_FILE}")

# Initialiser Flask
app = Flask(__name__)
CORS(app)

# Historique des données
sensor_history = {
    'timestamps': deque(maxlen=300),
    'temp': deque(maxlen=300),
    'humidity': deque(maxlen=300),
    'air_quality': deque(maxlen=300),
    'flammable': deque(maxlen=300),
    'water_quality': deque(maxlen=300),
}

# Dernières données
latest_data = {
    'temp': 20.0,
    'humidity': 60.0,
    'air_quality': 0.0,
    'flammable': 0.0,
    'water_quality': 500.0,
    'timestamp': datetime.now().isoformat(),
}

# ============ ROUTES HTTP ============

@app.route('/', methods=['GET'])
def index():
    """Servir l'interface HTML"""
    try:
        if os.path.exists(TEMPLATE_FILE):
            with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return f"❌ Fichier non trouvé: {TEMPLATE_FILE}", 404
    except Exception as e:
        return f"Erreur: {str(e)}", 500

@app.route('/api/data', methods=['GET'])
def get_data():
    """API: Retourner les dernières données"""
    return jsonify(latest_data)

@app.route('/api/update', methods=['POST'])
def update_data():
    """API: Recevoir les données depuis ESP32"""
    global latest_data
    try:
        data = request.get_json()
        
        # Mettre à jour les données
        latest_data.update({
            'temp': float(data.get('temp', 0)),
            'humidity': float(data.get('humidity', 0)),
            'air_quality': float(data.get('air_quality', 0)),
            'flammable': float(data.get('flammable', 0)),
            'water_quality': float(data.get('water_quality', 0)),
            'timestamp': datetime.now().isoformat(),
        })
        
        # Ajouter à l'historique
        sensor_history['timestamps'].append(latest_data['timestamp'])
        sensor_history['temp'].append(latest_data['temp'])
        sensor_history['humidity'].append(latest_data['humidity'])
        sensor_history['air_quality'].append(latest_data['air_quality'])
        sensor_history['flammable'].append(latest_data['flammable'])
        sensor_history['water_quality'].append(latest_data['water_quality'])
        
        print(f"✓ Données reçues: {latest_data}")
        return jsonify({'status': 'ok', 'data': latest_data})
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/history', methods=['GET'])
def get_history():
    """API: Retourner l'historique"""
    return jsonify({
        'timestamps': list(sensor_history['timestamps']),
        'temp': list(sensor_history['temp']),
        'humidity': list(sensor_history['humidity']),
        'air_quality': list(sensor_history['air_quality']),
        'flammable': list(sensor_history['flammable']),
        'water_quality': list(sensor_history['water_quality']),
    })

@app.route('/api/health', methods=['GET'])
def health():
    """API: Santé du serveur"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'last_update': latest_data['timestamp'],
    })

# ============ MAIN ============

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🌍 Moniteur Air & Eau PRO v3.0")
    print("="*50)
    print("🔗 Interface: http://localhost:5000")
    print("📡 API Update: POST /api/update")
    print("="*50 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )
