/*
 * ========================================
 * CODE PRODUCTION - WiFi + HTTP POST
 * Envoie données en temps réel au serveur Flask
 * ========================================
 * 
 * CONNEXIONS:
 * DHT11 (D4) - Température/Humidité
 * MQ135 (D32) - Qualité Air
 * MQ9 (D33) - Gaz Inflammables
 * TDS Meter (D35) - Qualité Eau
 * 
 * ========================================
 */

#include <Arduino.h>
#include <DHT.h>
#include <WiFi.h>
#include <HTTPClient.h>

// ============ CONFIGURATION WIFI ============
const char* ssid = "VOTRE_WIFI";           // Change avec ton WiFi
const char* password = "VOTRE_MOT_DE_PASSE";       // Change avec ton mot de passe
const char* server_url = "http://192.168.1.11:5000/api/update"; // Change avec l'IP de ton PC (voir Windows: ipconfig)

// ============ CONFIGURATION CAPTEURS ============
#define DHTPIN 4          // GPIO 4 (D4)
#define DHTTYPE DHT11
#define MQ135_PIN 32      // GPIO 32 (D32) - ADC1
#define MQ9_PIN 33        // GPIO 33 (D33) - ADC1
#define TDS_PIN 35        // GPIO 35 (D35) - ADC1

DHT dht(DHTPIN, DHTTYPE);

// ============ VARIABLES GLOBALES ============
float tempAir = 0.0;
float humidity = 0.0;
float mq135Volt = 0.0;
float mq9Volt = 0.0;
float tdsPPM = 0.0;

// ============ SETUP ============
void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n========================================");
    Serial.println("DÉMARRAGE - WiFi Monitoring");
    Serial.println("========================================");
    Serial.println("[D4] DHT11 - Température/Humidité");
    Serial.println("[D33] MQ9 - Gaz Inflammables");
    Serial.println("[D32] MQ135 - Qualité Air");
    Serial.println("[D35] TDS Meter - Qualité Eau");
    Serial.println("[WiFi] Envoi des données");
    
    dht.begin();
    delay(1000);
    
    // Connecter WiFi
    connectToWiFi();
    
    Serial.println("Prêt! Envoi des données...");
    Serial.println("========================================\n");
}

// ============ LOOP ============
void loop() {
    // ===== LECTURE DHT11 =====
    float h = NAN;
    float t = NAN;
    
    for (int i = 0; i < 5; i++) {
        h = dht.readHumidity();
        t = dht.readTemperature();
        if (!isnan(h) && !isnan(t)) {
            break;
        }
        delay(500);
    }
    
    if (isnan(h)) h = 0.0;
    if (isnan(t)) t = 0.0;
    
    tempAir = t;
    humidity = h;
    
    // ===== LECTURE MQ135 =====
    int raw135 = analogRead(MQ135_PIN);
    mq135Volt = (raw135 / 4095.0) * 3.3;
    
    // ===== LECTURE MQ9 =====
    int raw9 = analogRead(MQ9_PIN);
    mq9Volt = (raw9 / 4095.0) * 3.3;
    
    // ===== LECTURE TDS METER =====
    int rawTDS = analogRead(TDS_PIN);
    float voltTDS = (rawTDS / 4095.0) * 3.3;
    tdsPPM = voltTDS * 820.0;
    
    // ===== ENVOYER DONNÉES =====
    sendDataToServer();
    
    delay(2000);  // Envoyer toutes les 2 secondes
}

// ============ CONNECTER WIFI ============
void connectToWiFi() {
    Serial.print("🔗 Connexion WiFi: ");
    Serial.println(ssid);
    
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✓ WiFi Connecté!");
        Serial.print("📡 IP: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\n❌ Erreur WiFi!");
    }
}

// ============ ENVOYER DONNÉES HTTP ============
void sendDataToServer() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        
        // Valider les données (éviter NaN, inf)
        float temp = isnan(tempAir) ? 0.0 : tempAir;
        float hum = isnan(humidity) ? 0.0 : humidity;
        float mq135 = isnan(mq135Volt) ? 0.0 : mq135Volt;
        float mq9 = isnan(mq9Volt) ? 0.0 : mq9Volt;
        float water = isnan(tdsPPM) ? 0.0 : tdsPPM;
        
        // URL du serveur
        http.begin(server_url);
        
        // Header JSON
        http.addHeader("Content-Type", "application/json");
        
        // Créer JSON avec valeurs sûres
        String jsonData = "";
        jsonData += "{";
        jsonData += "\"temp\":" + String(temp, 2) + ",";
        jsonData += "\"humidity\":" + String(hum, 2) + ",";
        jsonData += "\"air_quality\":" + String(mq135, 2) + ",";
        jsonData += "\"flammable\":" + String(mq9, 2) + ",";
        jsonData += "\"water_quality\":" + String(water, 2);
        jsonData += "}";
        
        // DEBUG: Afficher le JSON envoyé
        Serial.print("📤 Envoi: ");
        Serial.println(jsonData);
        
        // Envoyer POST
        int httpResponseCode = http.POST(jsonData);
        
        if (httpResponseCode == 200) {
            Serial.println("✓ Données envoyées!");
        } else {
            Serial.print("❌ Erreur HTTP: ");
            Serial.println(httpResponseCode);
            
            // Afficher plus de détails sur l'erreur
            if (httpResponseCode == 400) {
                String response = http.getString();
                Serial.print("   Réponse: ");
                Serial.println(response);
            }
        }
        
        http.end();
    } else {
        Serial.println("❌ WiFi déconnecté!");
        connectToWiFi();
    }
}
