import csv
import os
import time
import serial

# --- CONFIGURATION ---
# Replace 'COM3' with your ESP32's actual COM port (e.g., '/dev/ttyUSB0' on Linux/Mac)
PORT = "COM3"
BAUD = 115200
CSV_FILE = "gesture_dataset.csv"


def initialize_csv():
  """Creates the CSV file with headers if it doesn't already exist."""
  if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as f:
      writer = csv.writer(f)
      writer.writerow([
          "ax",
          "ay",
          "az",
          "gx",
          "gy",
          "gz",
          "label",
      ])
    print(f"Created new dataset file: {CSV_FILE}")


def main():
  initialize_csv()

  try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)  # Allow ESP32 to reset and establish serial connection
    print(f"Connected to ESP32 on {PORT} at {BAUD} baud.\n")
  except Exception as e:
    print(
        f"Error connecting to port {PORT}. Please check your connection and"
        f" port name.\nDetails: {e}"
    )
    return

  print("=" * 50)
  print(" GESTURE DATA COLLECTION TOOL")
  print("=" * 50)
  print("Instructions:")
  print("1. Type your target label (e.g., front, back, left, right)")
  print("2. Press ENTER to start recording samples for that orientation.")
  print("3. Hold the device steady in position while it records.")
  print("4. Type 'q' or 'quit' to exit the program.\n")

  try:
    while True:
      label = input("Enter label for next recording (or 'q' to quit): ").strip()

      if label.lower() in ["q", "quit"]:
        print("Exiting data collection. Dataset saved to", CSV_FILE)
        break

      if not label:
        print("Label cannot be empty. Try again.")
        continue

      try:
        sample_count = int(
            input(
                f"How many samples do you want to collect for '{label}'? (e.g.,"
                " 300): "
            )
        )
      except ValueError:
        print("Please enter a valid integer for sample count.")
        continue

      print(
          f"\nGet ready! Recording {sample_count} samples for '{label}' in 2"
          " seconds..."
      )
      time.sleep(2)
      print("Recording started... Keep the device in position.")

      collected = 0
      with open(CSV_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)

        # Clear any stale buffer data
        ser.reset_input_buffer()

        while collected < sample_count:
          if ser.in_waiting > 0:
            line = ser.readline().decode("utf-8", errors="ignore").strip()

            # Expecting CSV line from ESP32: ax,ay,az,gx,gy,gz
            parts = line.split(",")
            if len(parts) == 6:
              try:
                # Convert to float/int to validate data integrity
                row = [float(p) for p in parts]
                row.append(label)  # Append the text label
                writer.writerow(row)
                collected += 1

                # Print progress bar / indicator
                if collected % 50 == 0:
                  print(f"Collected {collected}/{sample_count} samples...")
              except ValueError:
                # Skip lines that fail float conversion (e.g., debug text)
                continue

      print(f"Successfully recorded {collected} samples for '{label}'!\n")

  except KeyboardInterrupt:
    print("\nCollection interrupted by user. Exiting safely.")
  finally:
    if ser.is_open:
      ser.close()
    print("Serial port closed.")


if __name__ == "__main__":
  main()