# explainer.py
# Local gradient-based feature attribution (no extra library needed).
# Uses central finite differences to estimate each feature's contribution.

from predict import predict_ra

DISPLAY = {
    0: ("Print Speed",    "mm/s"),
    1: ("Layer Height",   "mm"),
    2: ("Nozzle Temp",    "°C"),
    3: ("Vibration Freq", "Hz"),
}
DELTA_PCT = 0.02   # 2 % perturbation


def explain_prediction(print_speed, layer_height, nozzle_temp, vibration_freq):
    inputs = dict(print_speed=print_speed, layer_height=layer_height,
                  nozzle_temp=nozzle_temp, vibration_freq=vibration_freq)
    keys   = list(inputs.keys())
    base_ra = predict_ra(**inputs)["predicted_ra"]

    contributions = []
    for i, key in enumerate(keys):
        val   = inputs[key]
        delta = max(abs(val) * DELTA_PCT, 1e-4)
        ra_hi = predict_ra(**{**inputs, key: val + delta})["predicted_ra"]
        ra_lo = predict_ra(**{**inputs, key: val - delta})["predicted_ra"]
        grad  = (ra_hi - ra_lo) / (2 * delta)
        # attribution = gradient × current value (measures "weight" at this point)
        contributions.append(round(grad * val * 0.1, 5))

    total_abs = sum(abs(c) for c in contributions) or 1.0
    label, unit = zip(*[DISPLAY[i] for i in range(4)])

    features = sorted([
        {
            "name":        label[i],
            "unit":        unit[i],
            "value":       round(list(inputs.values())[i], 3),
            "contribution": contributions[i],
            "pct":         round(contributions[i] / total_abs * 100, 1),
            "direction":   "increases Ra" if contributions[i] > 0 else "decreases Ra",
        }
        for i in range(4)
    ], key=lambda x: abs(x["contribution"]), reverse=True)

    return {
        "features":     features,
        "predicted_ra": round(base_ra, 4),
        "method":       "Local Gradient Attribution",
    }
