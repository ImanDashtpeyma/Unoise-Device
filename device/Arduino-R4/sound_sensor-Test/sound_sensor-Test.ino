const int analogPin = A0;  // Pin connected to AO (analog output) of the sound sensor
const int sampleWindow = 50;  // Time window for sound sample in milliseconds
int peakToPeak = 0;          // Peak-to-peak amplitude

void setup() {
  Serial.begin(9600);  // Initialize serial communication
}

void loop() {
  unsigned int signalMax = 0;
  unsigned int signalMin = 1023;

  unsigned long startMillis = millis();  // Start time for sampling
  while (millis() - startMillis < sampleWindow) {
    int sample = analogRead(analogPin);

    // Find max and min signal levels
    if (sample > signalMax) {
      signalMax = sample;
    }
    if (sample < signalMin) {
      signalMin = sample;
    }
  }

  peakToPeak = signalMax - signalMin;  // Calculate peak-to-peak amplitude

  // Map peak-to-peak amplitude to approximate decibel range
  float decibels = map(peakToPeak, 0, 1023, 0, 100);

  // Print the results to the Serial Monitor
  Serial.print("Raw Signal: ");
  Serial.print(peakToPeak);
  Serial.print(" | Approx. Decibels: ");
  Serial.print(decibels);
  Serial.println(" dB");

  delay(300);  // Small delay before the next loop
}
