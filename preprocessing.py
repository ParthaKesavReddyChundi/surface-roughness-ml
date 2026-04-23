# preprocessing.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

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

print("\nTrain size:", X_train.shape)
print("Test size:", X_test.shape)

# ==============================
# SCALING
# ==============================
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==============================
# VERIFY SCALING
# ==============================
print("\nBefore Scaling (first row):")
print(X_train.iloc[0])

print("\nAfter Scaling (first row):")
print(X_train_scaled[0])