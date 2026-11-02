#include <Wire.h>

const uint8_t MPU6050_ADDR = 0x68;

// Filter smoothing factor (alpha between 0.0 and 1.0)
// Lower alpha = smoother data (more filtering), Higher alpha = faster response
float alpha = 0.2; 

// Variables to hold filtered values
float filtered_ax = 0, filtered_ay = 0, filtered_az = 0;
float filtered_gx = 0, filtered_gy = 0, filtered_gz = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(10);
  }

  // Initialize I2C on ESP32 DevKit V1 pins (SDA = 21, SCL = 22)
  Wire.begin(21, 22);

  // Wake up MPU6050
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission();

  delay(100);

  // Initial read to prime the filter variables
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x3B); 
  Wire.endTransmission(false);
  Wire.requestFrom(MPU6050_ADDR, (uint8_t)14);
  if (Wire.available() == 14) {
    filtered_ax = (int16_t)((Wire.read() << 8) | Wire.read());
    filtered_ay = (int16_t)((Wire.read() << 8) | Wire.read());
    filtered_az = (int16_t)((Wire.read() << 8) | Wire.read());
    Wire.read(); Wire.read(); // Skip temp
    filtered_gx = (int16_t)((Wire.read() << 8) | Wire.read());
    filtered_gy = (int16_t)((Wire.read() << 8) | Wire.read());
    filtered_gz = (int16_t)((Wire.read() << 8) | Wire.read());
  }
}

void loop() {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x3B); 
  Wire.endTransmission(false);

  Wire.requestFrom(MPU6050_ADDR, (uint8_t)14);

  if (Wire.available() == 14) {
    // Read raw values
    float raw_ax = (int16_t)((Wire.read() << 8) | Wire.read());
    float raw_ay = (int16_t)((Wire.read() << 8) | Wire.read());
    float raw_az = (int16_t)((Wire.read() << 8) | Wire.read());

    Wire.read(); Wire.read(); // Skip temperature bytes

    float raw_gx = (int16_t)((Wire.read() << 8) | Wire.read());
    float raw_gy = (int16_t)((Wire.read() << 8) | Wire.read());
    float raw_gz = (int16_t)((Wire.read() << 8) | Wire.read());

    // Apply Low-Pass / Kalman-style filtering equation:
    // filtered = (alpha * raw) + ((1 - alpha) * previous_filtered)
    filtered_ax = (alpha * raw_ax) + ((1.0 - alpha) * filtered_ax);
    filtered_ay = (alpha * raw_ay) + ((1.0 - alpha) * filtered_ay);
    filtered_az = (alpha * raw_az) + ((1.0 - alpha) * filtered_az);
    
    filtered_gx = (alpha * raw_gx) + ((1.0 - alpha) * filtered_gx);
    filtered_gy = (alpha * raw_gy) + ((1.0 - alpha) * filtered_gy);
    filtered_gz = (alpha * raw_gz) + ((1.0 - alpha) * filtered_gz);

    // Print clean, filtered comma-separated values for Python collection
    Serial.print(filtered_ax, 2); Serial.print(",");
    Serial.print(filtered_ay, 2); Serial.print(",");
    Serial.print(filtered_az, 2); Serial.print(",");
    Serial.print(filtered_gx, 2); Serial.print(",");
    Serial.print(filtered_gy, 2); Serial.print(",");
    Serial.println(filtered_gz, 2);
  }

  delay(50); // Consistent sampling rate interval (~20Hz)
}