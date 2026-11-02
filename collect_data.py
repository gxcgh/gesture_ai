import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import emlearn

# --- CONFIGURATION ---
CSV_FILE = "gesture_dataset.csv"
OUTPUT_HEADER = "gesture_model.h"

def main():
    # 1. Load the dataset
    print(f"Loading dataset from {CSV_FILE}...")
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print(f"Error: {CSV_FILE} not found. Run your data collection script first.")
        return

    print(f"Total samples loaded: {len(df)}")
    print("Class distribution:")
    print(df['label'].value_counts())
    print("-" * 40)

    # 2. Separate features (X) and target labels (y)
    X = df[['ax', 'ay', 'az', 'gx', 'gy', 'gz']]
    y = df['label']

    # 3. Split data for validation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. Train a compact Random Forest Classifier
    # Keeping n_estimators and max_depth low ensures low memory footprint on the ESP32
    print("Training RandomForest model...")
    clf = RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42)
    clf.fit(X_train, y_train)

    # 5. Evaluate model performance
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nModel Validation Accuracy: {acc * 100:.2f}%\n")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    # 6. Convert model to C using emlearn and save as header file
    print(f"Converting model and exporting to {OUTPUT_HEADER}...")
    cmodel = emlearn.convert(clf, method='inline')
    cmodel.save(file=OUTPUT_HEADER)
    
    print(f"Success! '{OUTPUT_HEADER}' generated and ready for your Arduino sketch.")

if __name__ == "__main__":
    main()