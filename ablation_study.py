# ablation_study.py

import pandas as pd
import numpy as np
from sklearn.model_selection import KFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression

# ==============================
# LOAD DATA
# ==============================
df = pd.read_excel("TBP_readings.xlsx")

# Drop useless column
df = df.drop(columns=['Sample No'])

# Target
y = df['Surface Roughness Value Ra(µm)']

# ==============================
# MODEL PIPELINE
# ==============================
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LinearRegression())
])

kf = KFold(n_splits=5, shuffle=True, random_state=42)

# ==============================
# CASE 1: WITHOUT VIBRATION
# ==============================
X_no_vib = df.drop(columns=[
    'Surface Roughness Value Ra(µm)',
    'Vibration Frequency(Hz)'
])

rmse_no_vib = cross_val_score(
    pipeline, X_no_vib, y,
    scoring='neg_root_mean_squared_error',
    cv=kf
)

# ==============================
# CASE 2: WITH VIBRATION
# ==============================
X_with_vib = df.drop(columns=['Surface Roughness Value Ra(µm)'])

rmse_with_vib = cross_val_score(
    pipeline, X_with_vib, y,
    scoring='neg_root_mean_squared_error',
    cv=kf
)

# ==============================
# RESULTS
# ==============================
rmse_no_vib = -rmse_no_vib
rmse_with_vib = -rmse_with_vib

print("\nWITHOUT Vibration:")
print("RMSE:", rmse_no_vib)
print("Mean RMSE:", rmse_no_vib.mean())

print("\nWITH Vibration:")
print("RMSE:", rmse_with_vib)
print("Mean RMSE:", rmse_with_vib.mean())

# Improvement
improvement = ((rmse_no_vib.mean() - rmse_with_vib.mean()) / rmse_no_vib.mean()) * 100

print(f"\nImprovement with Vibration: {improvement:.2f}%")