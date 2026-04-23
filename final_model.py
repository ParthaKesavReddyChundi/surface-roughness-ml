# final_model.py

import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import KFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor

from sklearn.metrics import make_scorer, mean_squared_error

# XGBOOST
from xgboost import XGBRegressor

# ==============================
# LOAD DATA (AUGMENTED DATASET)
# ==============================
df = pd.read_excel("TBP_readings_1000samples.xlsx")

df = df.drop(columns=['Sample No'])

X = df.drop(columns=['Surface Roughness Value Ra(µm)'])
y = df['Surface Roughness Value Ra(µm)']

# ==============================
# CROSS VALIDATION SETUP
# ==============================
kf = KFold(n_splits=5, shuffle=True, random_state=42)

rmse_scorer = make_scorer(mean_squared_error, squared=False)

# ==============================
# MODELS
# ==============================
models = {
    "Linear Regression": LinearRegression(),
    "Ridge": Ridge(),
    "SVR": SVR(),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
    "KNN": KNeighborsRegressor(),
    "XGBoost": XGBRegressor(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=4,
        subsample=0.8,
        random_state=42
    )
}

# ==============================
# TRAIN + EVALUATE ALL MODELS
# ==============================
results = {}

print("\n=== MODEL PERFORMANCE ===\n")

for name, model in models.items():
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', model)
    ])

    rmse_scores = -cross_val_score(
        pipeline, X, y,
        scoring='neg_root_mean_squared_error',
        cv=kf
    )

    r2_scores = cross_val_score(
        pipeline, X, y,
        scoring='r2',
        cv=kf
    )

    results[name] = {
        "RMSE": rmse_scores.mean(),
        "R2": r2_scores.mean()
    }

    print(f"{name}:")
    print(f"  RMSE = {rmse_scores.mean():.4f}")
    print(f"  R2   = {r2_scores.mean():.4f}\n")

# ==============================
# BEST MODEL
# ==============================
best_model = min(results, key=lambda x: results[x]['RMSE'])

print("🏆 BEST MODEL:", best_model)

# ==============================
# SAVE BEST MODEL + SCALER
# ==============================
print("\n=== SAVING MODEL ===")

# Refit best model on full dataset with a fresh pipeline
best_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', models[best_model])
])
best_pipeline.fit(X, y)

os.makedirs("saved_model", exist_ok=True)
joblib.dump(best_pipeline, "saved_model/pipeline.pkl")
joblib.dump(list(X.columns), "saved_model/feature_names.pkl")

print(f"Pipeline (scaler + {best_model}) saved → saved_model/pipeline.pkl")
print(f"Feature names saved → saved_model/feature_names.pkl")

# ==============================
# FEATURE IMPORTANCE (XGBOOST)
# ==============================
print("\n=== FEATURE IMPORTANCE (XGBoost) ===")

xgb = XGBRegressor(n_estimators=200, random_state=42)
xgb.fit(X, y)

for feature, importance in zip(X.columns, xgb.feature_importances_):
    print(f"{feature}: {importance:.4f}")

# ==============================
# ABLATION STUDY
# ==============================
print("\n=== ABLATION STUDY ===")

# WITHOUT vibration
X_no_vib = X.drop(columns=['Vibration Frequency(Hz)'])

rmse_no_vib = -cross_val_score(
    Pipeline([('scaler', StandardScaler()), ('model', xgb)]),
    X_no_vib, y,
    scoring='neg_root_mean_squared_error',
    cv=kf
)

# WITH vibration
rmse_with_vib = -cross_val_score(
    Pipeline([('scaler', StandardScaler()), ('model', xgb)]),
    X, y,
    scoring='neg_root_mean_squared_error',
    cv=kf
)

print(f"Without Vibration RMSE: {rmse_no_vib.mean():.4f}")
print(f"With Vibration RMSE: {rmse_with_vib.mean():.4f}")

improvement = ((rmse_no_vib.mean() - rmse_with_vib.mean()) / rmse_no_vib.mean()) * 100

print(f"Improvement: {improvement:.2f}%")