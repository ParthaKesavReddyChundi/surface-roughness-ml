# optimizer.py
# --------------------------------------------------
# Nudges each printer parameter ±5 / ±10 % and returns
# the top-3 adjustments that would most reduce predicted Ra.
# --------------------------------------------------

from predict import predict_ra

# Valid physical ranges to clamp nudged values within
PARAM_META = {
    "print_speed":    ("Print Speed",    "mm/s",  20.0,  150.0),
    "layer_height":   ("Layer Height",   "mm",     0.05,   0.50),
    "nozzle_temp":    ("Nozzle Temp",    "°C",   180.0,  250.0),
    "vibration_freq": ("Vibration Freq", "Hz",    30.0,  400.0),
}

NUDGE_PCTS = [-0.10, -0.05, 0.05, 0.10]


def get_optimization_tips(
    print_speed: float,
    layer_height: float,
    nozzle_temp: float,
    vibration_freq: float,
) -> list:
    """
    Return up to 3 parameter-change suggestions that would lower Ra.

    Each tip dict contains:
        param        : human-readable parameter name
        unit         : unit string
        direction    : 'increase' | 'decrease'
        pct          : nudge percentage (5 or 10)
        current_val  : original value
        new_val      : suggested value (clamped to valid range)
        new_ra       : predicted Ra after the change
        improvement  : Ra delta (positive = improvement)
    """
    baseline = predict_ra(print_speed, layer_height, nozzle_temp, vibration_freq)
    base_ra  = baseline["predicted_ra"]

    inputs = {
        "print_speed":    print_speed,
        "layer_height":   layer_height,
        "nozzle_temp":    nozzle_temp,
        "vibration_freq": vibration_freq,
    }

    best_per_param: dict = {}

    for param, (label, unit, lo, hi) in PARAM_META.items():
        for pct in NUDGE_PCTS:
            new_val = inputs[param] * (1 + pct)
            new_val = round(max(lo, min(hi, new_val)), 4)

            trial = {**inputs, param: new_val}
            try:
                res   = predict_ra(**trial)
                delta = round(base_ra - res["predicted_ra"], 4)
            except Exception:
                continue

            if delta <= 0.005:          # ignore negligible improvement
                continue

            tip = {
                "param":       label,
                "unit":        unit,
                "direction":   "increase" if pct > 0 else "decrease",
                "pct":         round(abs(pct) * 100),
                "current_val": round(inputs[param], 3),
                "new_val":     new_val,
                "new_ra":      res["predicted_ra"],
                "improvement": delta,
            }

            # Keep only the best-performing nudge per parameter
            if param not in best_per_param or delta > best_per_param[param]["improvement"]:
                best_per_param[param] = tip

    tips = sorted(best_per_param.values(), key=lambda t: -t["improvement"])
    return tips[:3]
