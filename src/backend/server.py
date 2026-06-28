"""
========================================
Moniteur Air & Eau PRO v3.0
Backend Python Flask + WebSocket
========================================

Installation des dépendances:
pip install flask flask-cors flask-socketio python-socketio python-engineio pyserial

Usage:
python backend/app.py
"""

from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
import json
import threading
import time
from datetime import datetime
from collections import deque
import os

try:
    from flask_socketio import SocketIO, emit
except:
    SocketIO = None
    emit = None

try:
    import serial
    import serial.tools.list_ports
except:
    serial = None

# ============ CONFIGURATION ============
# Obtenir le chemin absolu du projet
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_dir = os.path.join(project_root, 'frontend')

app = Flask(__name__,
            static_folder=frontend_dir,
            template_folder=frontend_dir)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Historique de données (max 300 points)
sensor_history = {
    'timestamps': deque(maxlen=300),
    'temp': deque(maxlen=300),
    'humidity': deque(maxlen=300),
    'mq135': deque(maxlen=300),
    'mq9': deque(maxlen=300),
    'water': deque(maxlen=300),
    'waterTemp': deque(maxlen=300),
}

latest_data = {
    'temp': 0,
    'humidity': 0,
    'mq135': 0,
    'mq9': 0,
    'water': 0,
    'waterTemp': 0,
    'timestamp': None,
    'connected': False,
}

# Configuration seuils
THRESHOLDS = {
    'temp': {'min': 15, 'max': 30, 'critical': 40},
    'humidity': {'min': 30, 'max': 70, 'critical': 90},
    'mq135': {'excellent': 400, 'good': 800, 'fair': 1200, 'poor': 2000},
    'mq9': {'excellent': 10, 'good': 20, 'fair': 50, 'poor': 100},
    'water': {'excellent': 300, 'good': 600, 'fair': 1000, 'poor': 2000},
    'waterTemp': {'min': 10, 'max': 30, 'critical': 40}
}

# ============ SERIAL COMMUNICATION ============
class SerialReader(threading.Thread):
    def __init__(self, port='COM3', baudrate=115200):
        super().__init__(daemon=True)
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.running = False
        self.buffer = ''
        
    def run(self):
        """Lire continuellement les données du port série"""
        global latest_data
        
        while True:
            try:
                if not self.running:
                    if self.ser:
                        self.ser.close()
                        self.ser = None
                    time.sleep(0.5)
                    continue
                
                # Connexion
                if self.ser is None:
                    try:
                        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
                        time.sleep(2)  # Attendre stabilisation
                        latest_data['connected'] = True
                        print(f"✓ Connecté à {self.port} @ {self.baudrate} baud")
                        socketio.emit('status', {'connected': True}, broadcast=True)
                    except Exception as e:
                        print(f"✗ Impossible de se connecter: {e}")
                        latest_data['connected'] = False
                        time.sleep(2)
                        continue
                
                # Lire données
                if self.ser and self.ser.in_waiting:
                    byte = self.ser.read(1).decode('utf-8', errors='ignore')
                    self.buffer += byte
                    
                    if byte == '\n':
                        line = self.buffer.strip()
                        self.buffer = ''
                        
                        if line.startswith('{'):
                            try:
                                data = json.loads(line)
                                self.process_data(data)
                            except json.JSONDecodeError as e:
                                print(f"Erreur JSON: {e} | Ligne: {line}")
            
            except Exception as e:
                print(f"Erreur série: {e}")
                if self.ser:
                    self.ser.close()
                    self.ser = None
                latest_data['connected'] = False
                time.sleep(1)
    
    def process_data(self, data):
        """Traiter et diffuser les données"""
        global latest_data, sensor_history
        
        # Mettre à jour données
        latest_data.update(data)
        latest_data['timestamp'] = datetime.now().isoformat()
        
        # Historique
        sensor_history['timestamps'].append(
            datetime.now().strftime('%H:%M:%S')
        )
        sensor_history['temp'].append(data.get('temp', 0))
        sensor_history['humidity'].append(data.get('humidity', 0))
        sensor_history['mq135'].append(data.get('mq135', 0))
        sensor_history['mq9'].append(data.get('mq9', 0))
        sensor_history['water'].append(data.get('water', 0))
        sensor_history['waterTemp'].append(data.get('waterTemp', 0))
        
        # Diffuser à tous les clients WebSocket
        socketio.emit('sensor_update', latest_data, broadcast=True)
        
        # Vérifier seuils et envoyer alertes si nécessaire
        alerts = check_thresholds(data)
        if alerts:
            socketio.emit('alert', {
                'alerts': alerts,
                'critical': any(a['level'] == 'critical' for a in alerts),
                'timestamp': latest_data['timestamp']
            }, broadcast=True)
        
        # DEBUG
        print(f"📊 Temp: {data.get('temp', 0):.1f}°C | "
              f"Hum: {data.get('humidity', 0):.1f}% | "
              f"MQ135: {data.get('mq135', 0):.0f} ppm")
    
    def start_reading(self, port):
        """Démarrer la lecture"""
        self.port = port
        self.running = True
        if not self.is_alive():
            self.start()
    
    def stop_reading(self):
        """Arrêter la lecture"""
        self.running = False
        if self.ser:
            self.ser.close()
            self.ser = None
        latest_data['connected'] = False

def check_thresholds(data):
    """Vérifier les seuils et retourner les alertes"""
    alerts = []
    
    temp = data.get('temp', 0)
    humidity = data.get('humidity', 0)
    mq135 = data.get('mq135', 0)
    mq9 = data.get('mq9', 0)
    water = data.get('water', 0)
    waterTemp = data.get('waterTemp', 0)
    
    # Température
    if temp > THRESHOLDS['temp']['critical']:
        alerts.append({
            'type': 'temperature',
            'message': f'🔥 TEMPÉRATURE CRITIQUE: {temp:.1f}°C!',
            'level': 'critical',
            'value': temp
        })
    elif temp > THRESHOLDS['temp']['max']:
        alerts.append({
            'type': 'temperature',
            'message': f'⚠️ Température élevée: {temp:.1f}°C',
            'level': 'warning',
            'value': temp
        })
    
    # Humidité
    if humidity > THRESHOLDS['humidity']['critical']:
        alerts.append({
            'type': 'humidity',
            'message': f'💧 HUMIDITÉ EXTRÊME: {humidity:.1f}%!',
            'level': 'critical',
            'value': humidity
        })
    elif humidity > THRESHOLDS['humidity']['max']:
        alerts.append({
            'type': 'humidity',
            'message': f'⚠️ Humidité élevée: {humidity:.1f}%',
            'level': 'warning',
            'value': humidity
        })
    
    # MQ135 (qualité air)
    if mq135 > THRESHOLDS['mq135']['poor']:
        alerts.append({
            'type': 'air_quality',
            'message': f'🌬️ AIR TRÈS POLLUÉ: {mq135:.0f} ppm!',
            'level': 'critical',
            'value': mq135
        })
    elif mq135 > THRESHOLDS['mq135']['fair']:
        alerts.append({
            'type': 'air_quality',
            'message': f'⚠️ Air pollué: {mq135:.0f} ppm',
            'level': 'warning',
            'value': mq135
        })
    
    # MQ9 (gaz inflammables)
    if mq9 > THRESHOLDS['mq9']['poor']:
        alerts.append({
            'type': 'gas',
            'message': f'⚠️ GAZ INFLAMMABLES DÉTECTÉS: {mq9:.2f} ppm!',
            'level': 'critical',
            'value': mq9
        })
    elif mq9 > THRESHOLDS['mq9']['fair']:
        alerts.append({
            'type': 'gas',
            'message': f'⚠️ Gaz détectés: {mq9:.2f} ppm',
            'level': 'warning',
            'value': mq9
        })
    
    # Eau
    if water > THRESHOLDS['water']['poor']:
        alerts.append({
            'type': 'water_quality',
            'message': f'🚰 EAU TRÈS POLLUÉE: {water:.0f} µS/cm!',
            'level': 'critical',
            'value': water
        })
    
    if waterTemp > THRESHOLDS['waterTemp']['critical']:
        alerts.append({
            'type': 'water_temp',
            'message': f'🌊 Eau trop chaude: {waterTemp:.1f}°C',
            'level': 'warning',
            'value': waterTemp
        })
    
    return alerts

# ============ API ROUTES ============
@app.route('/')
def index():
    """Servir l'interface HTML principale"""
    try:
        html_path = os.path.join(frontend_dir, 'monitoring_dashboard.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Erreur lors du chargement du fichier HTML: {e}")
        return f"<h1>Erreur: Impossible de charger l'interface</h1><p>Chemin attendu: {html_path}</p>", 500

@app.route('/api/ports')
def get_ports():
    """Lister les ports série disponibles"""
    try:
        ports = [p.device for p in serial.tools.list_ports.comports()]
        return jsonify({'ports': ports, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/data')
def get_data():
    """Retourner les dernières données"""
    return jsonify({
        'latest': latest_data,
        'history': {
            'timestamps': list(sensor_history['timestamps']),
            'temp': list(sensor_history['temp']),
            'humidity': list(sensor_history['humidity']),
            'mq135': list(sensor_history['mq135']),
            'mq9': list(sensor_history['mq9']),
            'water': list(sensor_history['water']),
            'waterTemp': list(sensor_history['waterTemp']),
        }
    })
@app.route('/api/update', methods=['POST'])
def update_data():
    """Recevoir les données du capteur WiFi ESP32"""
    global latest_data
    try:
        # Vérifier que c'est du JSON
        if not request.is_json:
            print(f"✗ Erreur: Content-Type n'est pas JSON")
            return jsonify({'error': 'Content-Type must be application/json', 'success': False}), 400
        
        data = request.json
        
        # Valider et convertir les données
        try:
            latest_data['temp'] = float(data.get('temp', 0))
            latest_data['humidity'] = float(data.get('humidity', 0))
            latest_data['mq135'] = float(data.get('air_quality', 0))
            latest_data['mq9'] = float(data.get('flammable', 0))
            latest_data['water'] = float(data.get('water_quality', 0))
        except (ValueError, TypeError) as e:
            print(f"✗ Erreur conversion données: {e}")
            return jsonify({'error': f'Invalid data format: {str(e)}', 'success': False}), 400
        
        latest_data['timestamp'] = datetime.now().isoformat()
        latest_data['connected'] = True
        
        # Ajouter à l'historique
        sensor_history['timestamps'].append(latest_data['timestamp'])
        sensor_history['temp'].append(latest_data['temp'])
        sensor_history['humidity'].append(latest_data['humidity'])
        sensor_history['mq135'].append(latest_data['mq135'])
        sensor_history['mq9'].append(latest_data['mq9'])
        sensor_history['water'].append(latest_data['water'])
        
        # Diffuser les données via WebSocket (si disponible)
        try:
            if socketio:
                socketio.emit('data_update', {
                    'latest': latest_data,
                    'timestamp': latest_data['timestamp']
                }, namespace='/', broadcast=True, skip_sid=None)
        except:
            pass  # Ignorer les erreurs WebSocket
        
        print(f"✓ Données reçues: T={latest_data['temp']}°C, H={latest_data['humidity']}%, Water={latest_data['water']} PPM")
        
        return jsonify({'success': True, 'message': 'Données reçues'}), 200
    except Exception as e:
        print(f"✗ Erreur API update: {e}")
        return jsonify({'error': str(e), 'success': False}), 400
@app.route('/api/thresholds')
def get_thresholds():
    """Retourner les seuils d'alerte"""
    return jsonify(THRESHOLDS)

@app.route('/api/thresholds', methods=['POST'])
def update_thresholds():
    """Mettre à jour les seuils d'alerte"""
    global THRESHOLDS
    try:
        new_thresholds = request.json
        THRESHOLDS.update(new_thresholds)
        return jsonify({'success': True, 'thresholds': THRESHOLDS})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 400

# ============ WEBSOCKET EVENTS ============
@socketio.on('connect')
def handle_connect():
    """Nouvel utilisateur connecté"""
    print(f"✓ Utilisateur connecté: {request.sid}")
    emit('connection_response', {
        'data': 'Connecté au serveur',
        'latest': latest_data,
        'history': {
            'timestamps': list(sensor_history['timestamps']),
            'temp': list(sensor_history['temp']),
            'humidity': list(sensor_history['humidity']),
            'mq135': list(sensor_history['mq135']),
            'mq9': list(sensor_history['mq9']),
            'water': list(sensor_history['water']),
            'waterTemp': list(sensor_history['waterTemp']),
        }
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Utilisateur déconnecté"""
    print(f"✗ Utilisateur déconnecté: {request.sid}")

@socketio.on('connect_serial')
def handle_serial_connect(data):
    """Connecter au port série"""
    try:
        port = data.get('port', 'COM3')
        baudrate = data.get('baudrate', 115200)
        
        reader.stop_reading()
        time.sleep(0.5)
        reader.start_reading(port)
        
        emit('serial_status', {
            'connected': True,
            'port': port,
            'message': f'Connecté à {port}'
        }, broadcast=True)
        
        print(f"✓ Connexion série initiée: {port}")
    except Exception as e:
        emit('serial_status', {
            'connected': False,
            'error': str(e)
        }, broadcast=True)
        print(f"✗ Erreur connexion: {e}")

@socketio.on('disconnect_serial')
def handle_serial_disconnect():
    """Déconnecter du port série"""
    try:
        reader.stop_reading()
        emit('serial_status', {
            'connected': False,
            'message': 'Déconnecté'
        }, broadcast=True)
        print("✓ Déconnexion série")
    except Exception as e:
        print(f"✗ Erreur déconnexion: {e}")

@socketio.on('request_history')
def handle_history_request():
    """Demander l'historique complet"""
    emit('history_update', {
        'timestamps': list(sensor_history['timestamps']),
        'temp': list(sensor_history['temp']),
        'humidity': list(sensor_history['humidity']),
        'mq135': list(sensor_history['mq135']),
        'mq9': list(sensor_history['mq9']),
        'water': list(sensor_history['water']),
        'waterTemp': list(sensor_history['waterTemp']),
    })

# ============ MAIN ============
if __name__ == '__main__':
    # Créer thread de lecture série
    reader = SerialReader()
    reader.daemon = True
    
    print("\n========================================")
    print("Moniteur Air & Eau PRO v3.0")
    print("Backend Flask + WebSocket")
    print("========================================")
    print(f"\n📡 Serveur démarré sur http://localhost:5000")
    print("\nCommandes disponibles:")
    print("  - http://localhost:5000/           : Interface web")
    print("  - http://localhost:5000/api/ports  : Lister ports série")
    print("  - http://localhost:5000/api/data   : Données en JSON")
    print("  - http://localhost:5000/api/update : Recevoir les données ESP32")
    print("\n========================================\n")
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n✓ Arrêt du serveur")
        reader.stop_reading()
