#include <Servo.h>

Servo servo1;  // Opening Servo
Servo servo2;  // Rotating Servo

const int pinServo1 = 9;  // Servo 1 (Opening)
const int pinServo2 = 8;  // Servo 2 (Rotating)

void setup() {
  Serial.begin(9600);

  // Attach servos to their respective pins
  servo1.attach(pinServo1);
  servo2.attach(pinServo2);

  // Set initial positions
  servo1.write(0);   // Opening servo starts closed
  servo2.write(0);   // Rotating servo starts at 0°
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();  // Remove spaces and newline characters
    Serial.println("Received: " + input);

    // Step 1: Rotate Servo 2 based on waste type
    if (input == "plastic") {
      Serial.println("Rotating to plastic position...");
      servo2.write(0);  // Move to 45° for plastic
    } 
    else if (input == "metal") {
      Serial.println("Rotating to metal position...");
      servo2.write(300);  // Move to 90° for metal
    } 
    else if (input == "paper") {
      Serial.println("Rotating to paper position...");
      servo2.write(135); // Move to 135° for paper
    } 
    else {
      Serial.println("Unknown waste type. Resetting.");
      servo2.write(0);  // Default reset position
      return;  // Exit loop if input is invalid
    }

    delay(3000);  // Wait 3 seconds before opening

    // Step 2: Open the bin (Servo 1)
    Serial.println("Opening the bin...");
    servo1.write(50);  // Fully open bin
    delay(1000);        // Keep bin open for 1 second

    // Step 3: Close the bin
    Serial.println("Closing the bin...");
    servo1.write(0);  // Close bin
    delay(500);

    // Step 4: Reset Servo 2
    Serial.println("Resetting rotation...");
    servo2.write(0);  // Reset rotating servo to 0°
  }
}
