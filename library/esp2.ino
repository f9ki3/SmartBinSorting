#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// WiFi credentials
const char* ssid = "Lleva";
const char* password = "HappyLittleAccident";

// Flask server endpoint
const char* serverURL = "http://192.168.1.170:5000/send_data2";

// Sensor 3 pins
#define TRIG_PIN_3 D5
#define ECHO_PIN_3 D6

// Sensor 4 pins
#define TRIG_PIN_4 D7
#define ECHO_PIN_4 D8

void setup() {
  Serial.begin(9600);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");

  pinMode(TRIG_PIN_3, OUTPUT);
  pinMode(ECHO_PIN_3, INPUT);
  pinMode(TRIG_PIN_4, OUTPUT);
  pinMode(ECHO_PIN_4, INPUT);
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
  float distance3 = measureDistance(TRIG_PIN_3, ECHO_PIN_3);
  float distance4 = measureDistance(TRIG_PIN_4, ECHO_PIN_4);

  Serial.print("Distance3: ");
  Serial.print(distance3);
  Serial.print(" cm, Distance4: ");
  Serial.println(distance4);

  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;

    http.begin(client, serverURL);
    http.addHeader("Content-Type", "application/json");

    // JSON with sensor3 and sensor4
    String payload = "{\"sensor3\":" + String(distance3, 2) + ",\"sensor4\":" + String(distance4, 2) + "}";

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
