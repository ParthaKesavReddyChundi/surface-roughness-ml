# eda.py
# Full Exploratory Data Analysis: distributions, correlations, scatter plots, pairplot

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set(style="whitegrid", palette="muted")
plt.rcParams["figure.figsize"] = (8, 5)

os.makedirs("screenshots", exist_ok=True)

# ==============================
# LOAD DATA
# ==============================
df = pd.read_excel("TBP_readings.xlsx")
df = df.drop(columns=['Sample No'])

TARGET = 'Surface Roughness Value Ra(µm)'
features = [c for c in df.columns if c != TARGET]

# ==============================
# 1 — BASIC INFO
# ==============================
print("=" * 50)
print("DATASET INFO")
print("=" * 50)
df.info()
print("\nStatistical Summary:")
print(df.describe().round(3))

# ==============================
# 2 — BOXPLOTS (OUTLIER DETECTION)
# ==============================
print("\n[Generating boxplots...]")
fig, axes = plt.subplots(1, len(df.columns), figsize=(16, 4))
for ax, col in zip(axes, df.columns):
    sns.boxplot(y=df[col], ax=ax, color="#4f8ef7")
    ax.set_title(col, fontsize=8)
    ax.set_xlabel("")
plt.suptitle("Boxplots — Outlier Detection", fontsize=12, y=1.02)
plt.tight_layout()
plt.savefig("screenshots/boxplots.png", dpi=150, bbox_inches="tight")
plt.show()

# ==============================
# 3 — FEATURE DISTRIBUTIONS (histograms)
# ==============================
print("[Generating distributions...]")
fig, axes = plt.subplots(1, len(df.columns), figsize=(16, 4))
for ax, col in zip(axes, df.columns):
    sns.histplot(df[col], ax=ax, kde=True, color="#6c63ff")
    ax.set_title(col, fontsize=8)
plt.suptitle("Feature Distributions", fontsize=12, y=1.02)
plt.tight_layout()
plt.savefig("screenshots/distributions.png", dpi=150, bbox_inches="tight")
plt.show()

# ==============================
# 4 — CORRELATION HEATMAP
# ==============================
print("[Generating correlation heatmap...]")
corr = df.corr()
mask = np.triu(np.ones_like(corr, dtype=bool))

plt.figure(figsize=(7, 6))
sns.heatmap(
    corr, mask=mask, annot=True, fmt=".2f",
    cmap="coolwarm", center=0,
    linewidths=0.5, square=True
)
plt.title("Correlation Heatmap", fontsize=13, pad=14)
plt.tight_layout()
plt.savefig("screenshots/heatmap.png", dpi=150, bbox_inches="tight")
plt.show()

print("\nCorrelation with Ra:")
print(corr[TARGET].sort_values(ascending=False).round(3))

# ==============================
# 5 — SCATTER PLOTS (each feature vs Ra)
# ==============================
print("[Generating scatter plots...]")
fig, axes = plt.subplots(1, len(features), figsize=(16, 4))
for ax, feat in zip(axes, features):
    ax.scatter(df[feat], df[TARGET], alpha=0.7, color="#ff6b6b", edgecolors="white", linewidth=0.4)
    m, b = np.polyfit(df[feat], df[TARGET], 1)
    x_line = np.linspace(df[feat].min(), df[feat].max(), 100)
    ax.plot(x_line, m * x_line + b, "w--", linewidth=1.2)
    ax.set_xlabel(feat, fontsize=8)
    ax.set_ylabel("Ra (µm)", fontsize=8)
    ax.set_title(f"{feat}\nvs Ra", fontsize=8)
plt.suptitle("Scatter Plots — Features vs Surface Roughness (Ra)", fontsize=12, y=1.02)
plt.tight_layout()
plt.savefig("screenshots/feature_maps.png", dpi=150, bbox_inches="tight")
plt.show()

# ==============================
# 6 — PAIRPLOT
# ==============================
print("[Generating pairplot...]")
pair = sns.pairplot(df, corner=True, diag_kind="kde", plot_kws={"alpha": 0.6, "color": "#4f8ef7"})
pair.fig.suptitle("Pairplot — All Feature Relationships", y=1.01, fontsize=12)
plt.savefig("screenshots/pairplot.png", dpi=150, bbox_inches="tight")
plt.show()

print("\n✅ All EDA plots saved to screenshots/")
input("\nPress Enter to exit...")