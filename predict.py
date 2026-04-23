# predict.py
# --------------------------------------------------
# Load the saved pipeline and predict surface roughness
# Usage:
#   python predict.py
#   OR import predict_ra() from another script / Flask app
# --------------------------------------------------

import joblib
import numpy as np
import os

# ==============================
# LOAD SAVED PIPELINE
# ==============================
PIPELINE_PATH = os.path.join(os.path.dirname(__file__), "saved_model", "pipeline.pkl")
FEATURE_PATH  = os.path.join(os.path.dirname(__file__), "saved_model", "feature_names.pkl")

_pipeline      = None
_feature_names = None

def _load_model():
    global _pipeline, _feature_names
    if _pipeline is None:
        if not os.path.exists(PIPELINE_PATH):
            raise FileNotFoundError(
                "Model not found. Run final_model.py first to train and save the model."
            )
        _pipeline      = joblib.load(PIPELINE_PATH)
        _feature_names = joblib.load(FEATURE_PATH)


# ==============================
# PREDICTION FUNCTION
# ==============================
def predict_ra(print_speed: float,
               layer_height: float,
               nozzle_temp: float,
               vibration_freq: float) -> dict:
    """
    Predict surface roughness Ra (µm) from printer parameters.

    Parameters
    ----------
    print_speed    : float  — Print speed in mm/s
    layer_height   : float  — Layer height in mm
    nozzle_temp    : float  — Nozzle temperature in °C
    vibration_freq : float  — Vibration frequency in Hz (accelerometer reading)

    Returns
    -------
    dict with keys:
        'predicted_ra'  : float  — Predicted Ra in µm
        'quality_label' : str    — 'Smooth', 'Acceptable', or 'Rough'
        'quality_level' : int    — 1 (best) → 3 (worst), for UI colour coding
    """
    _load_model()

    features = np.array([[print_speed, layer_height, nozzle_temp, vibration_freq]])
    ra = float(_pipeline.predict(features)[0])
    ra = max(0.0, round(ra, 4))   # clamp to non-negative

    # Quality classification thresholds (based on project Ra range 2.3–6.9 µm)
    if ra <= 3.5:
        label, level = "Smooth",     1
    elif ra <= 5.2:
        label, level = "Acceptable", 2
    else:
        label, level = "Rough",      3

    return {
        "predicted_ra":  ra,
        "quality_label": label,
        "quality_level": level
    }


# ==============================
# CLI DEMO
# ==============================
if __name__ == "__main__":
    print("\n=== Surface Roughness Predictor ===\n")

    try:
        print_speed    = float(input("Print Speed (mm/s)      : "))
        layer_height   = float(input("Layer Height (mm)       : "))
        nozzle_temp    = float(input("Nozzle Temperature (°C) : "))
        vibration_freq = float(input("Vibration Freq (Hz)     : "))
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        exit(1)

    result = predict_ra(print_speed, layer_height, nozzle_temp, vibration_freq)

    print(f"\n  Predicted Ra  : {result['predicted_ra']:.4f} µm")
    print(f"  Quality       : {result['quality_label']}")

    quality_icons = {1: "✅ Smooth", 2: "⚠️  Acceptable", 3: "❌ Rough"}
    print(f"  Status        : {quality_icons[result['quality_level']]}")
