# app.py — Flask backend for the Surface Roughness Predictor UI

from flask import Flask, request, jsonify, render_template
from predict    import predict_ra
from optimizer  import get_optimization_tips
from confidence import get_confidence_band
from explainer  import explain_prediction
import joblib, json, os

app = Flask(__name__)

PIPELINE_PATH = os.path.join(os.path.dirname(__file__), "saved_model", "pipeline.pkl")
FEATURE_PATH  = os.path.join(os.path.dirname(__file__), "saved_model", "feature_names.pkl")
META_PATH     = os.path.join(os.path.dirname(__file__), "saved_model", "model_meta.json")


def _parse_inputs(data):
    return (float(data["print_speed"]), float(data["layer_height"]),
            float(data["nozzle_temp"]), float(data["vibration_freq"]))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        ps, lh, nt, vf = _parse_inputs(request.get_json(force=True))
        result     = predict_ra(ps, lh, nt, vf)
        confidence = get_confidence_band(result["predicted_ra"])
        return jsonify({"success": True, **result, "confidence": confidence})
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 503
    except (KeyError, TypeError, ValueError) as e:
        return jsonify({"success": False, "error": f"Bad input: {e}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/optimize", methods=["POST"])
def optimize():
    try:
        ps, lh, nt, vf = _parse_inputs(request.get_json(force=True))
        tips = get_optimization_tips(ps, lh, nt, vf)
        return jsonify({"success": True, "tips": tips})
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 503
    except (KeyError, TypeError, ValueError) as e:
        return jsonify({"success": False, "error": f"Bad input: {e}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/explain", methods=["POST"])
def explain():
    try:
        ps, lh, nt, vf = _parse_inputs(request.get_json(force=True))
        result = explain_prediction(ps, lh, nt, vf)
        return jsonify({"success": True, **result})
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 503
    except (KeyError, TypeError, ValueError) as e:
        return jsonify({"success": False, "error": f"Bad input: {e}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/model_info", methods=["GET"])
def model_info():
    try:
        pipeline = joblib.load(PIPELINE_PATH)
        features = joblib.load(FEATURE_PATH)
        model    = pipeline.named_steps["model"]

        # Feature importances (works for XGBoost, RF; falls back to coef)
        importances = None
        if hasattr(model, "feature_importances_"):
            importances = dict(zip(features, [round(float(v), 4) for v in model.feature_importances_]))
        elif hasattr(model, "coef_"):
            importances = dict(zip(features, [round(abs(float(v)), 4) for v in model.coef_]))

        meta = {}
        if os.path.exists(META_PATH):
            with open(META_PATH) as f:
                meta = json.load(f)

        return jsonify({
            "success":      True,
            "model_name":   meta.get("best_model", type(model).__name__),
            "rmse":         meta.get("rmse"),
            "r2":           meta.get("r2"),
            "features":     features,
            "importances":  importances,
            "model_class":  type(model).__name__,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5050)
