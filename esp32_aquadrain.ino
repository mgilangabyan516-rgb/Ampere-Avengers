#include <WiFi.h>
#include <HTTPClient.h>

// Isi sesuai jaringan Wi-Fi dan alamat IP laptop/server.
const char* WIFI_SSID = "NAMA_WIFI";
const char* WIFI_PASSWORD = "PASSWORD_WIFI";
const char* SERVER_URL = "http://192.168.1.10:8000/sensor";

// Contoh pin. Sesuaikan dengan modul sensor dan rangkaian sebenarnya.
const int PRESSURE_1_PIN = 34;
const int PRESSURE_2_PIN = 35;
const int FLOW_1_PIN = 25;
const int FLOW_2_PIN = 26;
const int PUMP_STATUS_PIN = 27;

volatile unsigned long pulse1 = 0;
volatile unsigned long pulse2 = 0;

void IRAM_ATTR countPulse1() { pulse1++; }
void IRAM_ATTR countPulse2() { pulse2++; }

void setup() {
  Serial.begin(115200);
  pinMode(FLOW_1_PIN, INPUT_PULLUP);
  pinMode(FLOW_2_PIN, INPUT_PULLUP);
  pinMode(PUMP_STATUS_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(FLOW_1_PIN), countPulse1, RISING);
  attachInterrupt(digitalPinToInterrupt(FLOW_2_PIN), countPulse2, RISING);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi connected");
}

void loop() {
  // PENTING:
  // Rumus konversi analog pressure sensor dan pulse-to-flow harus dikalibrasi
  // berdasarkan datasheet sensor yang benar-benar dibeli.
  int rawP1 = analogRead(PRESSURE_1_PIN);
  int rawP2 = analogRead(PRESSURE_2_PIN);

  float pressure1_bar = rawP1 * (3.3f / 4095.0f); // placeholder, BUKAN kalibrasi bar
  float pressure2_bar = rawP2 * (3.3f / 4095.0f); // placeholder, BUKAN kalibrasi bar

  noInterrupts();
  unsigned long p1 = pulse1; pulse1 = 0;
  unsigned long p2 = pulse2; pulse2 = 0;
  interrupts();

  // Placeholder pulse conversion. Ganti sesuai spesifikasi flow sensor.
  float flow1_lpm = p1 * 60.0f / 7.5f;
  float flow2_lpm = p2 * 60.0f / 7.5f;
  int pumpStatus = digitalRead(PUMP_STATUS_PIN) ? 1 : 0;

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");
    String payload = "{\"pressure_1\":" + String(pressure1_bar, 3) +
      ",\"pressure_2\":" + String(pressure2_bar, 3) +
      ",\"flow_1\":" + String(flow1_lpm, 3) +
      ",\"flow_2\":" + String(flow2_lpm, 3) +
      ",\"pump_status\":" + String(pumpStatus) + "}";
    int code = http.POST(payload);
    Serial.printf("HTTP response: %d\n", code);
    http.end();
  }
  delay(2000);
}
