# eda.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.ion()
sns.set(style="whitegrid")

# ==============================
# LOAD DATA
# ==============================
df = pd.read_excel("TBP_readings.xlsx")

# ==============================
# DROP USELESS COLUMN
# ==============================
df = df.drop(columns=['Sample No'])

# ==============================
# BASIC INFO
# ==============================
print("\nDataset Info:")
df.info()

print("\nStatistical Summary:")
print(df.describe())

# ==============================
# BOXPLOTS (OUTLIER DETECTION)
# ==============================
for col in df.columns:
    plt.figure()
    sns.boxplot(x=df[col])
    plt.title(f"Boxplot of {col}")
    plt.tight_layout()
    plt.show()

# ==============================
# KEEP WINDOW OPEN
# ==============================
plt.ioff()
plt.show()

input("\nPress Enter to exit...")