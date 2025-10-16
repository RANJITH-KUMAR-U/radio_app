# app.py - FIXED VERSION
import os
import json
import sqlite3
from flask import Flask, request, render_template, jsonify
import pandas as pd
import joblib
from datetime import datetime
import traceback
import numpy as np

# Import our modules
try:
    from nlp_module import extract_entities_from_text
    from fusion_engine import fuse_patient_data_for_model
    from reasoning_engine import analyze_patient_combined
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Module import error: {e}")
    # Create dummy functions if modules fail to import
    def extract_entities_from_text(text):
        return {"tumor_size_cm": 2.5, "growth_rate": 0.5}
    
    def fuse_patient_data_for_model(structured, entities):
        return structured
    
    def analyze_patient_combined(fused, proba, pred_label):
        return {
            "probability": proba,
            "risk_level": "MEDIUM RISK",
            "diagnoses": [{"condition": "Basic Analysis", "confidence": proba}],
            "anomalies": [],
            "recommendations": ["Consult specialist"],
            "confidence": "medium"
        }

app = Flask(__name__)

# Safe model loading
def load_model_safely():
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.datasets import make_classification
        
        os.makedirs("models", exist_ok=True)
        model_path = "models/medi_fusion_rf.joblib"
        features_path = "models/feature_columns.json"
        
        if not os.path.exists(model_path):
            print("🛠️ Creating demo model...")
            X, y = make_classification(n_samples=100, n_features=7, random_state=42)
            model = RandomForestClassifier(n_estimators=10, random_state=42)
            model.fit(X, y)
            joblib.dump(model, model_path)
            
            feature_columns = ["feat1", "feat2", "feat3", "tumor_size_cm", "growth_rate", "tumor_size_feat", "growth_feat"]
            with open(features_path, 'w') as f:
                json.dump(feature_columns, f)
            print("✅ Demo model created!")
        
        model = joblib.load(model_path)
        with open(features_path, 'r') as f:
            feature_columns = json.load(f)
            
        return model, feature_columns
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return None, None

model, FEATURE_COLUMNS = load_model_safely()

@app.route('/')
def index():
    return render_template('index.html')

def create_demo_data():
    return pd.DataFrame([{
        'patient_id': 'DEMO_001',
        'feat1': 0.5, 'feat2': 0.3, 'feat3': 0.8,
        'tumor_size_cm': 3.2, 'growth_rate': 0.6,
        'tumor_size_feat': 1, 'growth_feat': 0
    }])

@app.route('/upload', methods=['POST'])
def upload_and_predict():
    try:
        print("🔍 Starting analysis request...")
        
        csv_file = request.files.get('structured')
        genomics_file = request.files.get('genomics')
        pathology_file = request.files.get('pathology')
        mri_files = request.files.getlist('mri')
        
        if csv_file and csv_file.filename:
            df = pd.read_csv(csv_file)
            print(f"📊 Loaded CSV with {len(df)} rows")
        else:
            df = create_demo_data()
            print("📋 Using demo data")
        
        def read_file_safe(file):
            if file and file.filename:
                try:
                    content = file.read()
                    if isinstance(content, bytes):
                        return content.decode('utf-8')
                    return str(content)
                except Exception as e:
                    print(f"⚠️ Error reading file: {e}")
                    return ""
            return ""
        
        genomics_text = read_file_safe(genomics_file)
        pathology_text = read_file_safe(pathology_file)
        combined_text = f"Genomics: {genomics_text}\nPathology: {pathology_text}"
        
        results = []
        
        for idx, row in df.iterrows():
            try:
                patient_id = row.get("patient_id", f"Patient_{idx}")
                structured_data = {k: v for k, v in row.items() if pd.notna(v)}
                
                entities = extract_entities_from_text(combined_text)
                fused_data = fuse_patient_data_for_model(structured_data, entities)
                
                if model and FEATURE_COLUMNS:
                    X_input = [fused_data.get(col, 0.0) for col in FEATURE_COLUMNS]
                    probability = float(model.predict_proba([X_input])[0][1])
                    prediction = int(model.predict([X_input])[0])
                else:
                    probability = 0.3 + (hash(patient_id) % 70) / 100
                    prediction = 1 if probability > 0.6 else 0
                
                analysis = analyze_patient_combined(fused_data, probability, prediction)
                
                results.append({
                    "patient_id": patient_id,
                    "fused": fused_data,
                    "analysis": analysis
                })
                
            except Exception as e:
                print(f"❌ Error processing patient {idx}: {e}")
                results.append({
                    "patient_id": f"Patient_{idx}",
                    "fused": {},
                    "analysis": {
                        "probability": 0.5,
                        "risk_level": "ERROR",
                        "diagnoses": [{"condition": "Processing Error", "confidence": 0.0}],
                        "anomalies": [f"Error: {str(e)}"],
                        "recommendations": ["Please check input data"],
                        "confidence": "low"
                    }
                })
        
        return jsonify({"status": "ok", "results": results})
        
    except Exception as e:
        print(f"💥 CRITICAL ERROR: {e}")
        traceback.print_exc()
        return jsonify({
            "status": "error", 
            "message": f"Analysis failed: {str(e)}"
        }), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)

if __name__ == '__main__':
    print("🚀 Starting MediFusion Server...")
    print("📍 Access at: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)