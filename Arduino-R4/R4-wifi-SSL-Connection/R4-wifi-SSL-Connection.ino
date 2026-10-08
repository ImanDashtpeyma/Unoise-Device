#include <WiFiS3.h>
#include <WiFiSSLClient.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// Server details
const char* server = "unoise-device.onrender.com";
const int port = 443;

const int analogPin = A0;  // Pin connected to the sound sensor
const int sampleWindow = 50;  // Time window for sound sampling

WiFiSSLClient client;

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  int retryCount = 0;
  while (WiFi.status() != WL_CONNECTED && retryCount < 30) {
    delay(1000);
    Serial.print(".");
    retryCount++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected to WiFi!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to connect to WiFi!");
    while (true);  // Halt the program
  }
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
  char jsonPayload[128];
  snprintf(jsonPayload, sizeof(jsonPayload), "{\"sound\":%d,\"decibels\":%.2f}", peakToPeak, decibels);

  // Send data as HTTPS POST
  if (client.connect(server, port)) {
    Serial.println("Connected to server");

    client.print(String("POST /receive_data HTTP/1.1\r\n") +
                 "Host: " + server + "\r\n" +
                 "Content-Type: application/json\r\n" +
                 "Content-Length: " + String(strlen(jsonPayload)) + "\r\n" +
                 "Connection: close\r\n\r\n" +
                 jsonPayload);

    Serial.println("Data sent (JSON): " + String(jsonPayload));

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
