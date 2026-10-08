#include <WiFi.h>
#include <WiFiClient.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_NAME";
//For Open Network
//WPA Need 8 char passworg
const char* password="YOUR_WIFI_PASSWORD" ;

// Server details
const char* server = "https://im-unoise-1.onrender.com/";
const int port=443;

const int analogPin = A0;  // Pin connected to the sound sensor
const int sampleWindow = 50;  // Time window for sound sampling

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  unsigned int signalMax = 0;
  unsigned int signalMin = 1023;
  unsigned long startMillis = millis();

  // Capture sound signal
  while (millis() - startMillis < sampleWindow) {
    int sample = analogRead(analogPin);
    if (sample > signalMax) signalMax = sample;
    if (sample < signalMin) signalMin = sample;
  }

  int peakToPeak = signalMax - signalMin;
  float decibels = map(peakToPeak, 0, 1023, 0, 100);  // Approximation of decibels

  // Create JSON payload
  String jsonPayload = "{";
  jsonPayload += "\"sound\":" + String(peakToPeak) + ",";
  jsonPayload += "\"decibels\":" + String(decibels);
  jsonPayload += "}";

  // Send data as HTTP POST
  WiFiClient client;
  if (client.connect(server, port)) {
    Serial.println("Connected to server");

    client.print(String("POST /receive_data HTTP/1.1\r\n") +
                 "Host: " + server + "\r\n" +
                 "Content-Type: application/json\r\n" +
                 "Content-Length: " + jsonPayload.length() + "\r\n" +
                 "Connection: close\r\n\r\n" +
                 jsonPayload);

    Serial.println("Data sent (JSON): " + jsonPayload);

    // Read server response
    while (client.connected() || client.available()) {
      if (client.available()) {
        String line = client.readStringUntil('\n');
        Serial.println(line);
      }
    }
    client.stop();
    Serial.println("Disconnected from server");
  } else {
    Serial.println("Connection to server failed!");
  }

  delay(1000);  // Delay before sending the next request
}
