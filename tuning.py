# tuning.py
# Hyperparameter tuning using GridSearchCV on XGBoost, RandomForest, and SVR

import pandas as pd
import numpy as np
import joblib, os, time

from sklearn.model_selection import GridSearchCV, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from xgboost import XGBRegressor

# ==============================
# LOAD DATA (augmented dataset)
# ==============================
df = pd.read_excel("TBP_readings_1000samples.xlsx")
df = df.drop(columns=['Sample No'])

X = df.drop(columns=['Surface Roughness Value Ra(µm)'])
y = df['Surface Roughness Value Ra(µm)']

kf = KFold(n_splits=5, shuffle=True, random_state=42)

# ==============================
# PARAMETER GRIDS
# ==============================
search_configs = {

    "XGBoost": {
        "estimator": XGBRegressor(random_state=42, verbosity=0),
        "param_grid": {
            "model__n_estimators":  [100, 200, 300],
            "model__learning_rate": [0.05, 0.1, 0.2],
            "model__max_depth":     [3, 4, 6],
            "model__subsample":     [0.7, 0.8, 1.0],
        }
    },

    "Random Forest": {
        "estimator": RandomForestRegressor(random_state=42),
        "param_grid": {
            "model__n_estimators":  [100, 200, 300],
            "model__max_depth":     [None, 5, 10],
            "model__min_samples_split": [2, 5, 10],
        }
    },

    "SVR": {
        "estimator": SVR(),
        "param_grid": {
            "model__C":       [0.1, 1, 10, 100],
            "model__epsilon": [0.01, 0.1, 0.5],
            "model__kernel":  ["rbf", "poly"],
        }
    },
}

# ==============================
# RUN GRID SEARCH
# ==============================
best_overall_rmse  = np.inf
best_overall_name  = None
best_overall_pipeline = None
tuning_results = {}

print("\n" + "=" * 60)
print("  HYPERPARAMETER TUNING (GridSearchCV, 5-Fold CV)")
print("=" * 60)

for name, config in search_configs.items():
    print(f"\n⚙  Tuning {name} ...")
    t0 = time.time()

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', config["estimator"])
    ])

    gs = GridSearchCV(
        pipeline,
        param_grid=config["param_grid"],
        scoring='neg_root_mean_squared_error',
        cv=kf,
        n_jobs=-1,
        refit=True,
        verbose=0
    )
    gs.fit(X, y)

    best_rmse = -gs.best_score_
    elapsed   = time.time() - t0

    tuning_results[name] = {
        "best_params": gs.best_params_,
        "best_rmse":   best_rmse,
    }

    print(f"  Best RMSE   : {best_rmse:.4f}")
    print(f"  Best Params : {gs.best_params_}")
    print(f"  Time        : {elapsed:.1f}s")

    if best_rmse < best_overall_rmse:
        best_overall_rmse     = best_rmse
        best_overall_name     = name
        best_overall_pipeline = gs.best_estimator_

# ==============================
# SUMMARY
# ==============================
print("\n" + "=" * 60)
print("  TUNING SUMMARY")
print("=" * 60)
for name, res in tuning_results.items():
    marker = " ← BEST" if name == best_overall_name else ""
    print(f"  {name:15s}  RMSE = {res['best_rmse']:.4f}{marker}")

print(f"\n🏆 Overall Best: {best_overall_name}  (RMSE = {best_overall_rmse:.4f})")
print(f"   Best Params : {tuning_results[best_overall_name]['best_params']}")

# ==============================
# SAVE TUNED MODEL (overwrite saved_model)
# ==============================
os.makedirs("saved_model", exist_ok=True)
joblib.dump(best_overall_pipeline, "saved_model/pipeline.pkl")
joblib.dump(list(X.columns), "saved_model/feature_names.pkl")

print(f"\n✅ Tuned pipeline saved → saved_model/pipeline.pkl")
print("   (This will be used by predict.py and the web UI)")
