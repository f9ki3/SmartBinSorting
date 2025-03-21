#include <Servo.h>

Servo servo1;  // Opening Servo
Servo servo2;  // Rotating Servo (Continuous Rotation)

const int pinServo1 = 9;  // Servo 1 (Opening)
const int pinServo2 = 8;  // Servo 2 (Rotating)

const int NEUTRAL = 1500;  // Stop rotation
const int LEFT_ROTATE = 1400;  // Rotate left (paper)
const int RIGHT_ROTATE = 1600; // Rotate right (metal)

void setup() {
  Serial.begin(9600);

  // Attach servos to their respective pins
  servo1.attach(pinServo1);
  servo2.attach(pinServo2);

  // Set initial positions
  servo1.write(0);   // Ensure bin is closed
  servo2.writeMicroseconds(NEUTRAL);  // Stop continuous rotation servo
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();  // Remove spaces and newline characters
    Serial.println("Received: " + input);

    // Step 1: Rotate Servo 2 based on waste type
    if (input == "plastic") {
      Serial.println("Plastic detected. Keeping position steady.");
      servo2.writeMicroseconds(NEUTRAL);  // No movement
    } 
    else if (input == "metal") {
      Serial.println("Rotating right for metal...");
      servo2.writeMicroseconds(RIGHT_ROTATE); // Rotate right
    } 
    else if (input == "paper") {
      Serial.println("Rotating left for paper...");
      servo2.writeMicroseconds(LEFT_ROTATE); // Rotate left
    } 
    else {
      Serial.println("Unknown waste type. Resetting.");
      servo2.writeMicroseconds(NEUTRAL);  // Stop movement
      return;  // Exit loop if input is invalid
    }

    delay(1000);  // Allow servo to rotate
    servo2.writeMicroseconds(NEUTRAL);  // Stop rotation
    delay(3000);  // Wait 3 seconds before opening

    // Step 2: Open the bin (Servo 1)
    Serial.println("Opening the bin...");
    servo1.write(50);  // Fully open bin
    delay(1000);        // Keep bin open for 1 second

    // Step 3: Close the bin
    Serial.println("Closing the bin...");
    servo1.write(0);  // Close bin
    delay(500);

    // Step 4: Reset Servo 2 to neutral position
    Serial.println("Returning to original position...");
    servo2.writeMicroseconds(NEUTRAL);
    delay(1000);  // Ensure rotation stops
  }
}
