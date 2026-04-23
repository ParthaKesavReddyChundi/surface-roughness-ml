# cross_validation.py

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

# ==============================
# DROP USELESS COLUMN
# ==============================
df = df.drop(columns=['Sample No'])

# ==============================
# SPLIT
# ==============================
X = df.drop(columns=['Surface Roughness Value Ra(µm)'])
y = df['Surface Roughness Value Ra(µm)']

# ==============================
# PIPELINE (SCALING + MODEL)
# ==============================
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LinearRegression())
])

# ==============================
# K-FOLD CROSS VALIDATION
# ==============================
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# RMSE (negative because sklearn)
rmse_scores = cross_val_score(
    pipeline, X, y,
    scoring='neg_root_mean_squared_error',
    cv=kf
)

# R2 scores
r2_scores = cross_val_score(
    pipeline, X, y,
    scoring='r2',
    cv=kf
)

# ==============================
# RESULTS
# ==============================
print("\nCross-Validation Results:")

print("\nRMSE scores:", -rmse_scores)
print("Mean RMSE:", -rmse_scores.mean())

print("\nR2 scores:", r2_scores)
print("Mean R2:", r2_scores.mean())