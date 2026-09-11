import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

st.set_page_config(page_title="HF Readmission Predictor", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 2.5rem; }
    .big-font { font-size: 2rem; font-weight: bold; color: #1f77b4; }
    .medium-font { font-size: 1.3rem; color: #666; }
    .header-section { padding: 2rem 0; border-bottom: 2px solid #e0e0e0; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-section"><p style="font-size: 3.5rem; font-weight: bold; color: #1f77b4;">Heart Failure Readmission Risk Predictor</p></div>', unsafe_allow_html=True)
st.markdown('<p class="medium-font">ML-powered risk assessment at discharge</p>', unsafe_allow_html=True)

@st.cache_resource
def load_model():
    df = pd.read_csv('heart_failure_clinical_records_dataset.csv')
    X = df.drop('DEATH_EVENT', axis=1)
    y = df['DEATH_EVENT']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)
    
    return model, X.columns.tolist()

model, feature_names = load_model()

st.markdown("---")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("Patient Information")
    age = st.slider("Age", 18, 100, 60, help="Patient age in years")
    sex = st.radio("Sex", ["Male", "Female"], horizontal=True)
    diabetes = st.checkbox("Diabetes", value=False)
    high_blood_pressure = st.checkbox("High Blood Pressure", value=False)
    anaemia = st.checkbox("Anaemia", value=False)
    smoking = st.checkbox("Smoking", value=False)

with col2:
    st.subheader("Clinical Labs")
    ejection_fraction = st.slider("Ejection Fraction (%)", 10, 80, 40, help="% of blood heart pumps per beat")
    serum_creatinine = st.slider("Serum Creatinine (mg/dL)", 0.5, 4.0, 1.2, help="Kidney function marker")
    serum_sodium = st.slider("Serum Sodium (mEq/L)", 110, 150, 135)
    creatinine_phosphokinase = st.slider("Creatinine Phosphokinase (mcg/L)", 20, 10000, 500)
    platelets = st.slider("Platelets (thousands/mL)", 25, 850, 200)
    time = st.slider("Follow-up Period (days)", 1, 300, 100)

st.markdown("---")

sex_numeric = 1 if sex == "Female" else 0

patient_data = np.array([[
    age, int(anaemia), creatinine_phosphokinase, int(diabetes),
    ejection_fraction, int(high_blood_pressure), platelets, 
    serum_creatinine, serum_sodium, sex_numeric, int(smoking), time
]])

if st.button("Predict Risk", use_container_width=True, type="primary"):
    prediction_prob = model.predict_proba(patient_data)[0][1]
    risk_pct = prediction_prob * 100
    
    st.markdown("---")
    st.subheader("Risk Assessment Results")
    
    col_res1, col_res2, col_res3 = st.columns(3)
    
    with col_res1:
        st.metric("Readmission Risk", f"{risk_pct:.1f}%")
    
    with col_res2:
        if prediction_prob > 0.5:
            st.metric("Risk Level", "HIGH")
        elif prediction_prob > 0.3:
            st.metric("Risk Level", "MODERATE")
        else:
            st.metric("Risk Level", "LOW")
    
    with col_res3:
        st.metric("Follow-up Days", int(time))
    
    st.markdown("---")
    
    if prediction_prob > 0.5:
        st.error("HIGH RISK - Recommend intensive follow-up care, early clinic visit within 7 days")
    elif prediction_prob > 0.3:
        st.warning("MODERATE RISK - Schedule follow-up within 14 days, monitor for symptoms")
    else:
        st.success("LOW RISK - Standard discharge protocols, routine follow-up as usual")
    
    st.info(f"Key Factors: Serum Creatinine ({serum_creatinine}), Ejection Fraction ({ejection_fraction}%), Age ({age})")