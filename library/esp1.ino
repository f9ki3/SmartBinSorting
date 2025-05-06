#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// WiFi credentials
const char* ssid = "Lleva";
const char* password = "HappyLittleAccident";

// Flask server endpoint
const char* serverURL = "http://192.168.1.170:5000/send_data";

// Sensor 1 pins
#define TRIG_PIN_1 D5
#define ECHO_PIN_1 D6

// Sensor 2 pins
#define TRIG_PIN_2 D7
#define ECHO_PIN_2 D8

void setup() {
  Serial.begin(9600);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");

  pinMode(TRIG_PIN_1, OUTPUT);
  pinMode(ECHO_PIN_1, INPUT);
  pinMode(TRIG_PIN_2, OUTPUT);
  pinMode(ECHO_PIN_2, INPUT);
}

float measureDistance(uint8_t trigPin, uint8_t echoPin) {
  long duration;
  float distance;

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH, 30000);  // 30ms timeout
  distance = duration * 0.034 / 2;

  return distance;
}

void loop() {
  float distance1 = measureDistance(TRIG_PIN_1, ECHO_PIN_1);
  float distance2 = measureDistance(TRIG_PIN_2, ECHO_PIN_2);

  Serial.print("Distance1: ");
  Serial.print(distance1);
  Serial.print(" cm, Distance2: ");
  Serial.println(distance2);

  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;

    http.begin(client, serverURL);
    http.addHeader("Content-Type", "application/json");

    // Send both distances in a JSON object
    String payload = "{\"sensor1\":" + String(distance1, 2) + ",\"sensor2\":" + String(distance2, 2) + "}";

    Serial.println("Sending payload: " + payload);

    int httpResponseCode = http.POST(payload);

    Serial.print("Response Code: ");
    Serial.println(httpResponseCode);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server Response: " + response);
    } else {
      Serial.println("Error sending POST");
    }

    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }

  delay(2000);  // every 2 seconds
}
