/*
 * NetShield-IoT: ESP32 Hardware RF Radar & Latency Probe
 * Project: IoT Network Management & Optimization System
 */

#include <WiFi.h>

// Enter your hostel Wi-Fi credentials for Ping/Latency testing
// If you leave them as default, it will only do passive RF spectrum analysis
const char* TARGET_SSID = "YOUR_HOSTEL_WIFI_NAME";
const char* TARGET_PASS = "YOUR_HOSTEL_WIFI_PASSWORD";

// Target host for TCP latency probe (Google DNS port 53)
const char* PING_HOST = "8.8.8.8";
const int PING_PORT = 53;

unsigned long lastScanTime = 0;
const unsigned long SCAN_INTERVAL = 8000; // Scan every 8 seconds

void setup() {
  Serial.begin(115200);
  delay(1000);

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  
  if (String(TARGET_SSID) != "YOUR_HOSTEL_WIFI_NAME") {
    WiFi.begin(TARGET_SSID, TARGET_PASS);
  }
}

// Measure TCP Handshake Latency in milliseconds
long measureLatency() {
  if (WiFi.status() != WL_CONNECTED) return -1;
  
  WiFiClient client;
  unsigned long start = millis();
  if (client.connect(PING_HOST, PING_PORT, 1500)) {
    long latency = millis() - start;
    client.stop();
    return latency;
  }
  return -1; // Packet loss / timeout
}

void loop() {
  if (millis() - lastScanTime > SCAN_INTERVAL) {
    lastScanTime = millis();

    int n = WiFi.scanNetworks(false, false); // Active scan
    int channelCounts[14] = {0};
    int bestRSSI = -120;
    String bestBSSID = "";
    String bestSSID = "";
    int bestChannel = 1;

    for (int i = 0; i < n; ++i) {
      int ch = WiFi.channel(i);
      if (ch >= 1 && ch <= 13) {
        channelCounts[ch]++;
      }
      
      // Find strongest AP
      if (WiFi.RSSI(i) > bestRSSI) {
        bestRSSI = WiFi.RSSI(i);
        bestBSSID = WiFi.BSSIDstr(i);
        bestSSID = WiFi.SSID(i);
        bestChannel = ch;
      }
    }

    // Find least congested 2.4GHz channel among non-overlapping channels (1, 6, 11)
    int leastCongestedChannel = 1;
    int minCrowd = channelCounts[1];
    if (channelCounts[6] < minCrowd) { minCrowd = channelCounts[6]; leastCongestedChannel = 6; }
    if (channelCounts[11] < minCrowd) { minCrowd = channelCounts[11]; leastCongestedChannel = 11; }

    long latency = measureLatency();

    // Calculate overall congestion score (0 - 100%)
    int congestionScore = min(100, n * 5);

    // Stream structured JSON to Laptop over Serial USB
    Serial.print("{\"type\":\"telemetry\",");
    Serial.print("\"total_aps\":"); Serial.print(n); Serial.print(",");
    Serial.print("\"best_ssid\":\""); Serial.print(bestSSID); Serial.print("\",");
    Serial.print("\"best_bssid\":\""); Serial.print(bestBSSID); Serial.print("\",");
    Serial.print("\"best_rssi\":"); Serial.print(bestRSSI); Serial.print(",");
    Serial.print("\"recommended_channel\":"); Serial.print(leastCongestedChannel); Serial.print(",");
    Serial.print("\"congestion_score\":"); Serial.print(congestionScore); Serial.print(",");
    Serial.print("\"ch1_count\":"); Serial.print(channelCounts[1]); Serial.print(",");
    Serial.print("\"ch6_count\":"); Serial.print(channelCounts[6]); Serial.print(",");
    Serial.print("\"ch11_count\":"); Serial.print(channelCounts[11]); Serial.print(",");
    Serial.print("\"latency_ms\":"); Serial.print(latency);
    Serial.println("}");

    WiFi.scanDelete(); // Free memory
  }
}
