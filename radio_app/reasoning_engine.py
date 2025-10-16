# reasoning_engine.py - FIXED VERSION
def analyze_patient_combined(fused, proba, pred_label):
    analysis = {
        "probability": round(proba, 3),
        "risk_level": "",
        "diagnoses": [],
        "anomalies": [],
        "recommendations": [],
        "confidence": "high" if proba > 0.8 or proba < 0.2 else "medium"
    }
    
    # Extract features with safe defaults
    tumor_size = float(fused.get('tumor_size_cm', 0))
    growth_rate = float(fused.get('growth_rate', 0))
    lymph_positive = fused.get('lymph_node_positive', 0)
    has_brca1 = fused.get('has_brca1', 0)
    has_brca2 = fused.get('has_brca2', 0)
    
    # Risk level classification
    if proba >= 0.8:
        analysis["risk_level"] = "HIGH RISK"
    elif proba >= 0.6:
        analysis["risk_level"] = "MODERATE RISK"
    elif proba >= 0.4:
        analysis["risk_level"] = "LOW RISK"
    else:
        analysis["risk_level"] = "VERY LOW RISK"
    
    # Generate diagnoses
    diagnoses = []
    
    # Size-based
    if tumor_size > 5:
        diagnoses.append({
            "condition": "Large Tumor Mass",
            "confidence": min(0.9, proba + 0.2),
            "evidence": f"Tumor size {tumor_size}cm exceeds 5cm threshold"
        })
    elif tumor_size > 2:
        diagnoses.append({
            "condition": "Medium Tumor Mass",
            "confidence": proba,
            "evidence": f"Tumor size {tumor_size}cm requires monitoring"
        })
    
    # Growth-based
    if growth_rate > 0.7:
        diagnoses.append({
            "condition": "Rapid Growth Pattern",
            "confidence": min(0.95, proba + 0.25),
            "evidence": f"Growth rate {growth_rate} indicates aggressive behavior"
        })
    
    # Genetic risk
    if has_brca1 or has_brca2:
        gene = "BRCA1" if has_brca1 else "BRCA2"
        diagnoses.append({
            "condition": f"Genetic Predisposition ({gene})",
            "confidence": 0.8,
            "evidence": f"{gene} mutation detected"
        })
    
    # Lymph node
    if lymph_positive:
        diagnoses.append({
            "condition": "Lymph Node Metastasis",
            "confidence": 0.9,
            "evidence": "Lymph node involvement detected"
        })
    
    # Model assessment
    diagnoses.append({
        "condition": "AI Model Assessment",
        "confidence": proba,
        "evidence": f"Model prediction: {'MALIGNANT' if pred_label == 1 else 'BENIGN'}"
    })
    
    analysis["diagnoses"] = sorted(diagnoses, key=lambda x: x['confidence'], reverse=True)[:5]
    
    # Anomaly detection
    anomalies = []
    
    if tumor_size > 3 and growth_rate < 0.1:
        anomalies.append("Large tumor with low growth rate - verify measurements")
    
    if tumor_size < 1 and growth_rate > 0.8:
        anomalies.append("Small tumor with high growth rate - confirm measurements")
    
    if (has_brca1 or has_brca2) and proba < 0.3:
        anomalies.append("Genetic markers present but low probability - review case")
    
    analysis["anomalies"] = anomalies
    
    # Recommendations
    recommendations = []
    
    if proba > 0.7:
        recommendations.extend([
            "Urgent specialist consultation",
            "Consider immediate biopsy",
            "Schedule follow-up imaging within 2 weeks"
        ])
    elif proba > 0.4:
        recommendations.extend([
            "Schedule specialist consultation",
            "Repeat imaging in 1-3 months"
        ])
    else:
        recommendations.extend([
            "Routine monitoring recommended",
            "Re-evaluate in 6-12 months"
        ])
    
    if anomalies:
        recommendations.append("Data inconsistencies detected - manual review recommended")
    
    analysis["recommendations"] = recommendations
    
    return analysis