#include <ESP8266WiFi.h>
#include <WiFiManager.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecureBearSSL.h>

// HC-SR04 pins
const int trigPin1 = D1; // Bin 1 Trig
const int echoPin1 = D2; // Bin 1 Echo

const int trigPin2 = D5; // Bin 2 Trig
const int echoPin2 = D6; // Bin 2 Echo

// Firebase Realtime Database
const char* firebaseHost = "smart-bin-1b802-default-rtdb.asia-southeast1.firebasedatabase.app";
const String firebasePath = "/bins.json"; // path in DB

// Use WiFiClientSecure for HTTPS
BearSSL::WiFiClientSecure client;

void setup() {
  Serial.begin(115200);
  Serial.println("\n--- Smart Bin 2 Sensors + Firebase (Secure) ---");

  // Initialize pins
  pinMode(trigPin1, OUTPUT);
  pinMode(echoPin1, INPUT);
  pinMode(trigPin2, OUTPUT);
  pinMode(echoPin2, INPUT);

  // Connect to Wi-Fi
  WiFiManager wifiManager;
  if (!wifiManager.autoConnect("Smart Bin Config")) {
    Serial.println("Failed to connect and hit timeout");
    delay(3000);
    ESP.restart();
  }

  Serial.println("Connected to Wi-Fi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Allow insecure SSL for testing (optional)
  client.setInsecure(); // Only for testing; for production, use fingerprint or certificate
}

// Function to measure distance from a sensor
long measureDistance(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  long distanceCm = duration * 0.034 / 2;
  return distanceCm;
}

void loop() {
  // Measure distances
  long distanceBin1 = measureDistance(trigPin1, echoPin1);
  long distanceBin2 = measureDistance(trigPin2, echoPin2);

  Serial.print("Bin 1 Distance: ");
  Serial.print(distanceBin1);
  Serial.print(" cm | Bin 2 Distance: ");
  Serial.print(distanceBin2);
  Serial.println(" cm");

  // Send to Firebase securely
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient https;

    String url = String("https://") + firebaseHost + firebasePath;
    https.begin(client, url); // <-- Secure HTTPS

    https.addHeader("Content-Type", "application/json");

    String payload = "{\"bin1\":" + String(distanceBin1) + ",\"bin2\":" + String(distanceBin2) + "}";
    int httpResponseCode = https.PUT(payload); // PUT overwrites data

    if (httpResponseCode > 0) {
      Serial.print("Firebase Response code: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Error sending to Firebase: ");
      Serial.println(https.errorToString(httpResponseCode));
    }

    https.end();
  } else {
    Serial.println("Wi-Fi disconnected!");
  }

  delay(2000); // send every 2 seconds
}
