#include <ESP8266WiFi.h>
#include <WiFiManager.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecureBearSSL.h>

// Pins for Bin3 & Bin4
const int trigPin1 = D5;
const int echoPin1 = D6;
const int trigPin2 = D7;
const int echoPin2 = D8;

// Built-in LED for Wi-Fi status
#define wifiLed LED_BUILTIN

// Firebase setup
const char* firebaseHost = "smart-bin-1b802-default-rtdb.asia-southeast1.firebasedatabase.app";
const String binsPath = "/bins.json";           // Bin distances
const String lastUpdatePath = "/devices/esp8266_2.json"; // Only last_update

BearSSL::WiFiClientSecure client;

// Measure distance in cm
long measureDistance(int trigPin, int echoPin){
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH);
  return duration * 0.034 / 2;
}

// Update last_update timestamp in Firebase
void updateLastUpdate(){
  if(WiFi.status() == WL_CONNECTED){
    digitalWrite(wifiLed, LOW); // LED ON (connected)

    HTTPClient https;
    String url = String("https://") + firebaseHost + lastUpdatePath;
    https.begin(client, url);
    https.addHeader("Content-Type", "application/json");

    unsigned long now = millis(); // simple timestamp
    String payload = "{\"last_update\":" + String(now) + "}";
    int httpCode = https.sendRequest("PATCH", payload);

    if(httpCode > 0) Serial.printf("Last update timestamp sent: %d\n", httpCode);
    else Serial.printf("Error sending last_update: %s\n", https.errorToString(httpCode).c_str());

    https.end();
  } else {
    digitalWrite(wifiLed, HIGH); // LED OFF if disconnected
  }
}

// Update bin distances immediately
void updateBins(long d1, long d2){
  if(WiFi.status() == WL_CONNECTED){
    digitalWrite(wifiLed, LOW); // LED ON

    HTTPClient https;
    String url = String("https://") + firebaseHost + binsPath;
    https.begin(client, url);
    https.addHeader("Content-Type", "application/json");

    String payload = "{\"bin3\":" + String(d1) + ",\"bin4\":" + String(d2) + "}";
    int httpCode = https.sendRequest("PATCH", payload);

    if(httpCode > 0) Serial.printf("Bins updated: %d\n", httpCode);
    else Serial.printf("Error sending bins: %s\n", https.errorToString(httpCode).c_str());

    https.end();
  } else {
    digitalWrite(wifiLed, HIGH); // LED OFF
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(trigPin1, OUTPUT); pinMode(echoPin1, INPUT);
  pinMode(trigPin2, OUTPUT); pinMode(echoPin2, INPUT);
  pinMode(wifiLed, OUTPUT);
  digitalWrite(wifiLed, HIGH); // LED off initially

  WiFiManager wifiManager;
  if(!wifiManager.autoConnect("SmartBin 3&4 Config")){
    ESP.restart();
  }

  Serial.println("Wi-Fi connected. IP: " + WiFi.localIP().toString());
  client.setInsecure(); // for HTTPS testing
}

void loop() {
  long d1 = measureDistance(trigPin1, echoPin1);
  long d2 = measureDistance(trigPin2, echoPin2);

  Serial.printf("Bin3: %ld cm | Bin4: %ld cm\n", d1, d2);

  updateBins(d1, d2);       // Update bins immediately
  updateLastUpdate();        // Update last_update immediately

  delay(2000);               // Small delay to avoid overwhelming Firebase
}
