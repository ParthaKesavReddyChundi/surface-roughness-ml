# app.py — Flask backend for the Surface Roughness Predictor UI

from flask import Flask, request, jsonify, render_template
from predict import predict_ra

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data          = request.get_json(force=True)
        print_speed   = float(data["print_speed"])
        layer_height  = float(data["layer_height"])
        nozzle_temp   = float(data["nozzle_temp"])
        vibration_freq = float(data["vibration_freq"])

        result = predict_ra(print_speed, layer_height, nozzle_temp, vibration_freq)
        return jsonify({"success": True, **result})

    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 503
    except (KeyError, TypeError, ValueError) as e:
        return jsonify({"success": False, "error": f"Bad input: {e}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5050)
