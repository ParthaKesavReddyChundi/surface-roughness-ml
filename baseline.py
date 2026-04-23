# baseline.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# ==============================
# LOAD DATA
# ==============================
df = pd.read_excel("TBP_readings.xlsx")

# ==============================
# DROP USELESS COLUMN
# ==============================
df = df.drop(columns=['Sample No'])

# ==============================
# FEATURE / TARGET SPLIT
# ==============================
X = df.drop(columns=['Surface Roughness Value Ra(µm)'])
y = df['Surface Roughness Value Ra(µm)']

# ==============================
# TRAIN-TEST SPLIT
# ==============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ==============================
# SCALING
# ==============================
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==============================
# BASELINE MODEL
# ==============================
dummy = DummyRegressor(strategy='mean')
dummy.fit(X_train_scaled, y_train)

# Predictions
y_pred = dummy.predict(X_test_scaled)

# ==============================
# EVALUATION
# ==============================
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\nBaseline Model Performance:")
print("RMSE:", rmse)
print("R2 Score:", r2)