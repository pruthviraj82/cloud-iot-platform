// arduino/arduino_test.ino - Updated for better JSON parsing
void setup() {
  Serial.begin(9600);
  Serial.println("Arduino connected successfully!");
  Serial.println("Send commands: 'LED_ON', 'LED_OFF', 'READ_TEMP', 'STATUS'");
  delay(1000);
}

void loop() {
  // Send fake sensor data every 3 seconds
  float temperature = 25.0 + random(-100, 100) / 100.0;  // More variation
  float humidity = 50.0 + random(-200, 200) / 100.0;
  int heartRate = 70 + random(-50, 50) / 10;
  
  // Send clean JSON formatted data
  Serial.print("{");
  Serial.print("\"sensor\":\"multi\",");
  Serial.print("\"temp\":");
  Serial.print(temperature, 2);
  Serial.print(",\"humidity\":");
  Serial.print(humidity, 2);
  Serial.print(",\"heart_rate\":");
  Serial.print(heartRate);
  Serial.print(",\"timestamp\":");
  Serial.print(millis());
  Serial.println("}");
  
  // Check for incoming commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "LED_ON") {
      Serial.println("COMMAND_RESPONSE: LED turned ON");
    } else if (command == "LED_OFF") {
      Serial.println("COMMAND_RESPONSE: LED turned OFF");
    } else if (command == "READ_TEMP") {
      Serial.print("COMMAND_RESPONSE: Temperature: ");
      Serial.print(temperature, 2);
      Serial.println("°C");
    } else if (command == "STATUS") {
      Serial.println("COMMAND_RESPONSE: All systems operational");
    } else if (command == "HELP") {
      Serial.println("COMMAND_RESPONSE: Available commands: LED_ON, LED_OFF, READ_TEMP, STATUS, HELP");
    } else {
      Serial.print("COMMAND_RESPONSE: Unknown command: ");
      Serial.println(command);
    }
  }
  
  delay(3000); // Wait 3 seconds
}