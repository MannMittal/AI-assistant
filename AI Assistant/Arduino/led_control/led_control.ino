// LED connected to Pin 10
int led = 10;

void setup() {
    pinMode(led, OUTPUT);
    Serial.begin(9600);   // Start serial communication
}

void loop() {
    if (Serial.available()) {
        char cmd = Serial.read();  // Read command from Python

        // Turn LED ON
        if (cmd == '1') {
            digitalWrite(led, HIGH);
        }

        // Turn LED OFF
        if (cmd == '0') {
            digitalWrite(led, LOW);
        }
    }   
}
