# confidence.py
# --------------------------------------------------
# Builds a ±1-RMSE confidence interval around a predicted Ra value.
# Reads model metadata written by final_model.py.
# Falls back to a hard-coded RMSE when the file is absent.
# --------------------------------------------------

import json
import os

META_PATH     = os.path.join(os.path.dirname(__file__), "saved_model", "model_meta.json")
FALLBACK_RMSE = 0.28   # conservative fallback in µm


def get_confidence_band(predicted_ra: float) -> dict:
    """
    Return a ±1-RMSE confidence interval around predicted_ra.

    Returns
    -------
    dict with keys:
        lower      : float  — lower bound (clamped ≥ 0)
        upper      : float  — upper bound
        rmse       : float  — RMSE used
        model_name : str    — name of the best model
        r2         : float | None
    """
    rmse       = FALLBACK_RMSE
    model_name = "Best model"
    r2         = None

    if os.path.exists(META_PATH):
        try:
            with open(META_PATH, "r") as fh:
                meta = json.load(fh)
            rmse       = float(meta.get("rmse",       FALLBACK_RMSE))
            model_name = str(meta.get("best_model",   model_name))
            r2         = meta.get("r2")
        except Exception:
            pass   # silently fall back

    return {
        "lower":      max(0.0, round(predicted_ra - rmse, 4)),
        "upper":      round(predicted_ra + rmse, 4),
        "rmse":       round(rmse, 4),
        "model_name": model_name,
        "r2":         round(r2, 4) if r2 is not None else None,
    }
