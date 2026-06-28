import sys
import json
import serial
import threading
from datetime import datetime
from collections import deque
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                             QComboBox, QMessageBox, QTabWidget, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer
from PyQt5.QtGui import QFont, QColor, QPixmap
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import QPointF, QTimer as QTimerCore


# ========== SIGNAUX ==========
class SerialSignals(QObject):
    data_received = pyqtSignal(dict)
    connection_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)


# ========== WORKER SERIAL ==========
class SerialWorker(threading.Thread):
    def __init__(self, port, baudrate=115200):
        super().__init__(daemon=True)
        self.port = port
        self.baudrate = baudrate
        self.running = False
        self.signals = SerialSignals()
        self.serial_connection = None

    def run(self):
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            self.signals.connection_changed.emit(True)
            buffer = ""

            while self.running:
                if self.serial_connection.in_waiting:
                    chunk = self.serial_connection.read(self.serial_connection.in_waiting).decode('utf-8', errors='ignore')
                    buffer += chunk
                    lines = buffer.split('\n')
                    buffer = lines[-1]

                    for line in lines[:-1]:
                        line = line.strip()
                        if line.startswith('{'):
                            try:
                                data = json.loads(line)
                                self.signals.data_received.emit(data)
                            except json.JSONDecodeError:
                                pass

        except Exception as e:
            self.signals.error_occurred.emit(str(e))
            self.signals.connection_changed.emit(False)

    def stop(self):
        self.running = False
        if self.serial_connection:
            self.serial_connection.close()


# ========== WIDGET CAPTEUR ==========
class SensorWidget(QFrame):
    def __init__(self, title, icon, unit, color):
        super().__init__()
        self.title = title
        self.unit = unit
        self.color = color
        
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet(f"""
            QFrame {{
                border-radius: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {color}, stop:1 {self.darken_color(color)});
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # Titre
        title_label = QLabel(icon + " " + title)
        title_font = QFont("Arial", 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)
        
        # Valeur
        self.value_label = QLabel("--")
        value_font = QFont("Arial", 36, QFont.Bold)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet("color: white;")
        layout.addWidget(self.value_label)
        
        # Unité
        unit_label = QLabel(unit)
        unit_font = QFont("Arial", 12)
        unit_label.setFont(unit_font)
        unit_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        layout.addWidget(unit_label)

    def update_value(self, value):
        if value is None:
            self.value_label.setText("--")
        else:
            self.value_label.setText(f"{value:.1f}")

    @staticmethod
    def darken_color(color_hex):
        # Assombrir la couleur
        return color_hex.replace(')', ',0.7)').replace('rgb', 'rgba')


# ========== APPLICATION PRINCIPALE ==========
class AirWaterMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌍 Air & Water Quality Monitor - Professional")
        self.setGeometry(100, 100, 1400, 900)
        
        # Styles globaux
        self.setStyleSheet("""
            QMainWindow {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            QPushButton {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:disabled {
                opacity: 0.5;
            }
            QComboBox {
                background: white;
                color: #333;
                border: 2px solid #667eea;
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
            }
            QLabel {
                color: white;
            }
        """)
        
        # Données
        self.thresholds = {
            'air': {'excellent': 400, 'good': 800, 'fair': 1200, 'poor': 2000},
            'water': {'excellent': 300, 'good': 600, 'fair': 1000, 'poor': 2000}
        }
        
        self.history = deque(maxlen=60)
        self.serial_worker = None
        
        # GUI
        self.init_ui()
        self.detect_ports()

    def init_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Section connexion
        connection_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.connect_btn = QPushButton("🔌 Connecter")
        self.connect_btn.clicked.connect(self.connect_serial)
        self.disconnect_btn = QPushButton("🔌 Déconnecter")
        self.disconnect_btn.clicked.connect(self.disconnect_serial)
        self.disconnect_btn.setEnabled(False)
        
        self.status_label = QLabel("❌ Déconnecté")
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        connection_layout.addWidget(QLabel("Port COM:"))
        connection_layout.addWidget(self.port_combo)
        connection_layout.addWidget(self.connect_btn)
        connection_layout.addWidget(self.disconnect_btn)
        connection_layout.addStretch()
        connection_layout.addWidget(self.status_label)
        
        main_layout.addLayout(connection_layout)
        
        # Alertes
        self.alert_label = QLabel("✅ Système OK")
        self.alert_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.alert_label.setStyleSheet("background: #51cf66; padding: 15px; border-radius: 8px;")
        main_layout.addWidget(self.alert_label)
        
        # Grille capteurs
        sensors_layout = QGridLayout()
        
        self.temp_widget = SensorWidget("Température", "🌡️", "°C", "#f5576c")
        self.humidity_widget = SensorWidget("Humidité", "💧", "%", "#0099ff")
        self.air_widget = SensorWidget("Qualité Air", "🌬️", "ppm", "#667eea")
        self.water_widget = SensorWidget("Qualité Eau", "🚰", "ppm", "#764ba2")
        
        sensors_layout.addWidget(self.temp_widget, 0, 0)
        sensors_layout.addWidget(self.humidity_widget, 0, 1)
        sensors_layout.addWidget(self.air_widget, 1, 0)
        sensors_layout.addWidget(self.water_widget, 1, 1)
        
        main_layout.addLayout(sensors_layout)
        
        # Onglets pour graphiques
        tab_widget = QTabWidget()
        self.air_chart = self.create_chart("Qualité de l'Air")
        self.water_chart = self.create_chart("Qualité de l'Eau")
        self.temp_chart = self.create_chart("Température")
        
        tab_widget.addTab(self.air_chart, "📊 Air")
        tab_widget.addTab(self.water_chart, "📊 Eau")
        tab_widget.addTab(self.temp_chart, "📊 Température")
        
        main_layout.addWidget(tab_widget)

    def create_chart(self, title):
        chart = QChart()
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(QColor("#f8f9fa"))
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        return chart_view

    def detect_ports(self):
        import serial.tools.list_ports
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        
        if ports:
            for port in ports:
                self.port_combo.addItem(port.device)
        else:
            self.port_combo.addItem("Aucun port disponible")

    def connect_serial(self):
        port = self.port_combo.currentText()
        if not port or "Aucun" in port:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un port COM!")
            return
        
        self.serial_worker = SerialWorker(port)
        self.serial_worker.signals.data_received.connect(self.on_data_received)
        self.serial_worker.signals.connection_changed.connect(self.on_connection_changed)
        self.serial_worker.signals.error_occurred.connect(self.on_error)
        self.serial_worker.start()
        
        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)

    def disconnect_serial(self):
        if self.serial_worker:
            self.serial_worker.stop()
            self.serial_worker = None
        
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)

    def on_data_received(self, data):
        # Mise à jour widgets
        if 'temp' in data:
            self.temp_widget.update_value(data['temp'])
        if 'hum' in data:
            self.humidity_widget.update_value(data['hum'])
        if 'ppm' in data:
            self.air_widget.update_value(data['ppm'])
            self.update_card_status(self.air_widget, data['ppm'], 'air')
        if 'tds' in data:
            self.water_widget.update_value(data['tds'])
            self.update_card_status(self.water_widget, data['tds'], 'water')
        
        # Historique
        self.history.append(data)
        self.update_charts()
        
        # Alertes
        self.check_alerts(data)

    def update_card_status(self, widget, value, sensor_type):
        thresholds = self.thresholds[sensor_type]
        
        if value <= thresholds['excellent']:
            color = "#51cf66"  # Excellent
        elif value <= thresholds['good']:
            color = "#69db7c"  # Bon
        elif value <= thresholds['fair']:
            color = "#ffd43b"  # Moyen
        elif value <= thresholds['poor']:
            color = "#ff8787"  # Mauvais
        else:
            color = "#f76707"  # Critique
        
        widget.setStyleSheet(f"""
            QFrame {{
                border-radius: 15px;
                background: {color};
                padding: 20px;
            }}
        """)

    def update_charts(self):
        # Simple représentation - peut être améliorée avec matplotlib
        pass

    def check_alerts(self, data):
        alerts = []
        
        if data.get('ppm', 0) > self.thresholds['air']['poor']:
            alerts.append("🚨 AIR TRÈS POLLUÉ!")
        if data.get('tds', 0) > self.thresholds['water']['poor']:
            alerts.append("🚨 EAU TRÈS POLLUÉE!")
        
        if alerts:
            self.alert_label.setText(" | ".join(alerts))
            self.alert_label.setStyleSheet("background: #ff6b6b; padding: 15px; border-radius: 8px; color: white; font-weight: bold;")
        else:
            self.alert_label.setText("✅ Système OK")
            self.alert_label.setStyleSheet("background: #51cf66; padding: 15px; border-radius: 8px;")

    def on_connection_changed(self, connected):
        if connected:
            self.status_label.setText("✅ Connecté")
            self.status_label.setStyleSheet("color: #51cf66;")
        else:
            self.status_label.setText("❌ Déconnecté")
            self.status_label.setStyleSheet("color: #ff6b6b;")

    def on_error(self, error):
        QMessageBox.critical(self, "Erreur", f"Erreur série: {error}")
        self.disconnect_serial()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AirWaterMonitor()
    window.show()
    sys.exit(app.exec_())
