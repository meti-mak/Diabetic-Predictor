import pandas as pd
import joblib
from flask import Flask, request, jsonify
import numpy as np
import bcrypt

# Initialize Flask App
app = Flask(__name__)

# Load ML Model and Scaler
MODEL_PATH = "trained-model.sav"

def load_models():
    try:
        data = joblib.load(MODEL_PATH)
        models = data["models"]
        scaler = data["scaler"]
        print("✅ Models and Scaler loaded successfully.")
        return models, scaler
    except Exception as e:
        print(f"❌ Failed to load models or scaler: {e}")
        exit()

models, scaler = load_models()

# In-memory users (for demo purposes only)
users = []

# Expected features for prediction
FEATURES = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']

def validate_input(data):
    for feature in FEATURES:
        if feature not in data or data[feature] is None or data[feature] == '':
            return f"Missing or invalid value for field: {feature}"
    if data['Pregnancies'] < 0 or data['Age'] < 0:
        return "Pregnancies and Age should not be negative."
    if data['Glucose'] <= 0 or data['BMI'] <= 0 or data['BloodPressure'] <= 0:
        return "Glucose, BMI, and BloodPressure should be positive values."
    return None

def determine_risk(probability):
    if probability >= 70:
        return "High", "Consult a doctor immediately and monitor your blood sugar levels."
    elif probability >= 40:
        return "Medium", "Consider lifestyle changes like a balanced diet and regular exercise."
    return "Low", "Maintain a healthy lifestyle."

# ====================================
# 👤 User Registration Endpoint
# ====================================
@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        email = data.get("email")
        name = data.get("name")
        password = data.get("password")

        if not email or not name or not password:
            return jsonify({"error": "All fields are required"}), 400

        if any(user["email"] == email for user in users):
            return jsonify({"error": "User already exists"}), 409

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        users.append({
            "email": email,
            "name": name,
            "password": hashed_password.decode('utf-8')
        })

        print(f"✅ Registered user: {email}")
        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return jsonify({"error": "Registration failed"}), 500

# ====================================
# 🤖 Prediction Endpoint
# ====================================
@app.route('/predict', methods=['POST'])
def predict_diabetes():
    try:
        print("📨 Received a new prediction request...")
        data = request.get_json()
        print("📥 Raw input data:", data)

        validation_error = validate_input(data)
        if validation_error:
            print(f"❌ {validation_error}")
            return jsonify({"error": validation_error}), 400

        user_data = pd.DataFrame([data])[FEATURES]
        user_data_scaled = scaler.transform(user_data)

        predictions = {}
        for name, model in models.items():
            if name in ["SVM", "KNN", "Logistic Regression"]:
                prediction = model.predict(user_data_scaled)
                precentage = round(model.predict_proba(user_data_scaled)[0][1] * 100, 2)
            else:
                prediction = model.predict(user_data)
                precentage = round(model.predict_proba(user_data)[0][1] * 100, 2)

            risk_level, recommendation = determine_risk(precentage)
            predictions[name] = {
                "prediction": bool(prediction[0]),
                "precentage": precentage,
                "riskLevel": risk_level,
                "recommendation": recommendation
            }

        print("📊 Predictions:", predictions)
        return jsonify(predictions)

    except Exception as e:
        print("❌ Error during prediction:", str(e))
        return jsonify({"error": str(e)}), 500

# ====================================
# 🚀 Start Flask Server
# ====================================
if __name__ == '__main__':
    print("🚀 Starting Flask server on port 3002...")
    app.run(host='0.0.0.0', port=3002, debug=True)
