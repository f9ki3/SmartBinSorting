#include <ESP8266WiFi.h>
#include <WiFiManager.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecureBearSSL.h>

// Pins for Bin1 & Bin2
const int trigPin1 = D1;
const int echoPin1 = D2;
const int trigPin2 = D5;
const int echoPin2 = D6;

// Built-in LED (usually D4 / GPIO2)
#define wifiLed LED_BUILTIN

// Firebase setup
const char* firebaseHost = "smart-bin-1b802-default-rtdb.asia-southeast1.firebasedatabase.app";
const String binsPath = "/bins.json";          // Bin distances
const String statusPath = "/devices/esp8266_1.json"; // Status info

BearSSL::WiFiClientSecure client;

// Measure distance
long measureDistance(int trigPin, int echoPin){
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH);
  return duration * 0.034 / 2;
}

// Update online status
void updateStatus(String status){
  if(WiFi.status() == WL_CONNECTED){
    digitalWrite(wifiLed, LOW); // LED ON (active low)
    HTTPClient https;
    String url = String("https://") + firebaseHost + statusPath;
    https.begin(client, url);
    https.addHeader("Content-Type", "application/json");

    unsigned long now = millis(); // simple timestamp
    String payload = "{\"status\":\"" + status + "\",\"last_update\":" + String(now) + "}";
    int httpCode = https.sendRequest("PATCH", payload);

    Serial.print("Status update: "); Serial.println(status);
    https.end();
  } else {
    digitalWrite(wifiLed, HIGH); // LED OFF if disconnected
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(trigPin1, OUTPUT); pinMode(echoPin1, INPUT);
  pinMode(trigPin2, OUTPUT); pinMode(echoPin2, INPUT);
  pinMode(wifiLed, OUTPUT);
  digitalWrite(wifiLed, HIGH); // LED off initially

  WiFiManager wifiManager;
  if(!wifiManager.autoConnect("SmartBin 1&2 Config")){
    ESP.restart();
  }

  Serial.println("Wi-Fi connected. IP: " + WiFi.localIP().toString());
  client.setInsecure(); // for HTTPS testing
  updateStatus("online"); // set initial status
}

void loop() {
  long d1 = measureDistance(trigPin1, echoPin1);
  long d2 = measureDistance(trigPin2, echoPin2);

  Serial.printf("Bin1: %ld cm | Bin2: %ld cm\n", d1, d2);

  if(WiFi.status() == WL_CONNECTED){
    digitalWrite(wifiLed, LOW); // LED ON (connected)
    HTTPClient https;
    String url = String("https://") + firebaseHost + binsPath;
    https.begin(client, url);
    https.addHeader("Content-Type", "application/json");

    String payload = "{\"bin1\":" + String(d1) + ",\"bin2\":" + String(d2) + "}";
    int httpCode = https.sendRequest("PATCH", payload);

    if(httpCode > 0) Serial.printf("Bins updated: %d\n", httpCode);
    else Serial.printf("Error sending bins: %s\n", https.errorToString(httpCode).c_str());
    https.end();
  } else {
    digitalWrite(wifiLed, HIGH); // LED OFF if disconnected
  }

  // Update online status every 30 sec
  static unsigned long lastStatus = 0;
  if(millis() - lastStatus > 30000){
    updateStatus("online");
    lastStatus = millis();
  }

  delay(2000);
}
