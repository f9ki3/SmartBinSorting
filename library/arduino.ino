#include <Servo.h>

Servo servoPlastic;  // Servo for plastic
Servo servoMetal;    // Servo for metal
Servo servoPaper;    // Servo for paper

const int servo1 = 8;  // Pin for plastic servo
const int servo2 = 9;   // Pin for metal servo

void setup() {
  // Initialize serial communication
  Serial.begin(9600);

  // Attach servos to their respective pins
  servoPlastic.attach(pinPlastic);
  servoMetal.attach(pinMetal);
  servoPaper.attach(pinPaper);

  // Set initial servo positions
  servoPlastic.write(0);
  servoMetal.write(0);
  servoPaper.write(0);
}

void loop() {
  // Check if there is incoming data
  if (Serial.available() > 0) {
    // Read the incoming data
    String input = Serial.readStringUntil('\n');
    Serial.println("Received: " + input);

    // Act based on the input
    if (input == "plastic") {
      Serial.println("Moving plastic servo");
      servoPlastic.write(180);  // Move plastic servo to 180 degrees
      delay(1000);              // Wait for 1 second
      servoPlastic.write(0);    // Reset to 0 degrees
    } 
    else if (input == "metal") {
      Serial.println("Moving metal servo");
      servoMetal.write(180);    // Move metal servo to 180 degrees
      delay(1000);              // Wait for 1 second
      servoMetal.write(0);      // Reset to 0 degrees
    } 
    else if (input == "paper") {
      Serial.println("Moving paper servo");
      servoPaper.write(180);    // Move paper servo to 180 degrees
      delay(1000);              // Wait for 1 second
      servoPaper.write(0);      // Reset to 0 degrees
    } 
    else {
      Serial.println("Unknown input");
    }
  }
}
