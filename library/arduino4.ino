#include <Servo.h>

Servo servo1;     // For plastic and paper
Servo servo2;     // For metal and general
Servo conveyor;   // Conveyor motor (continuous servo on pin 10)

const int pinServo1 = 9;
const int pinServo2 = 8;
const int pinConveyor = 10;

// Define angles
const int PLASTIC_ANGLE = 120;
const int PAPER_ANGLE   = 60;
const int METAL_ANGLE   = 120;
const int GENERAL_ANGLE = 60;

void setup() {
  Serial.begin(9600);

  servo1.attach(pinServo1);
  servo2.attach(pinServo2);
  conveyor.attach(pinConveyor);

  // Start all at default
  servo1.write(0);
  servo2.write(0);
  conveyor.write(90); // Stop conveyor
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    input.toLowerCase();  // Make input case-insensitive
    Serial.println("Received: " + input);

    bool usedServo1 = false;
    bool usedServo2 = false;
    int delayTime = 0;

    // Trigger correct servo
    if (input == "plastic") {
      Serial.println("Plastic detected: Moving servo1 to PLASTIC_ANGLE");
      servo1.write(PLASTIC_ANGLE);
      usedServo1 = true;
      delayTime = 10000; // 10 seconds
    } 
    else if (input == "paper") {
      Serial.println("Paper detected: Moving servo1 to PAPER_ANGLE");
      servo1.write(PAPER_ANGLE);
      usedServo1 = true;
      delayTime = 10000; // 10 seconds
    } 
    else if (input == "metal") {
      Serial.println("Metal detected: Moving servo2 to METAL_ANGLE");
      servo2.write(METAL_ANGLE);
      usedServo2 = true;
      delayTime = 15000; // 15 seconds
    } 
    else if (input == "general") {
      Serial.println("General waste detected: Moving servo2 to GENERAL_ANGLE");
      servo2.write(GENERAL_ANGLE);
      usedServo2 = true;
      delayTime = 15000; // 15 seconds
    } 
    else {
      Serial.println("Unknown waste type. Send: plastic, paper, metal, or general.");
      return;
    }

    // Start conveyor while waiting
    Serial.println("Starting conveyor during servo operation...");
    conveyor.write(10); // Fast speed
    delay(delayTime);   // 10s or 15s depending on waste
    conveyor.write(90); // Stop conveyor
    Serial.println("Conveyor stopped.");

    // Reset servos
    if (usedServo1) {
      Serial.println("Resetting servo1 to 0...");
      servo1.write(0);
    }
    if (usedServo2) {
      Serial.println("Resetting servo2 to 0...");
      servo2.write(0);
    }
  }
}
