from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import pandas as pd
from pathlib import Path
import os

app = Flask(__name__, static_folder='.')
CORS(app)  # Permitir peticiones desde el HTML

# Cargar modelo
MODEL_PATH = Path("best_model.pkl")
model = joblib.load(MODEL_PATH)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "API funcionando",
        "model": "Random Forest Credit Scoring",
        "endpoint": "/predict"
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Crear DataFrame con los nombres exactos de las características
        X = pd.DataFrame([{
            'RevolvingUtilizationOfUnsecuredLines': float(data['utilization']),
            'age': int(data['age']),
            'NumberOfTime30-59DaysPastDueNotWorse': int(data['late30']),
            'DebtRatio': float(data['debtRatio']),
            'MonthlyIncome': float(data['income']),
            'NumberOfOpenCreditLinesAndLoans': int(data['openLines']),
            'NumberOfTimes90DaysLate': int(data['late90']),
            'NumberRealEstateLoansOrLines': int(data['realEstate']),
            'NumberOfTime60-89DaysPastDueNotWorse': int(data['late60']),
            'NumberOfDependents': float(data['dependents'])
        }])
        
        # Predicción
        probability = float(model.predict_proba(X)[0, 1])
        
        return jsonify({
            'success': True,
            'probability': probability
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 API de Credit Scoring iniciando...")
    print("📊 Modelo cargado correctamente")
    print(f"🌐 Accede desde: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
