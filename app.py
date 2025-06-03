from flask import Flask, request, jsonify
import requests
import boto3
import json
from flask_cors import CORS

app = Flask(__name__)

# ✅ Backend internal load balancer URL
BACKEND_URL = "http://internal-capestone-internal-559327774.ap-south-1.elb.amazonaws.com:5000"

@app.route("/")
def index():
    return send_file('food_order_form.html')


# ✅ Proxy /submit to backend + push message to SQS
@app.route("/submit", methods=["POST"])
def proxy_submit():
    form_data = request.form.to_dict()
    try:
        # Forward to backend
        response = requests.post(f"{BACKEND_URL}/submit", data=form_data)

        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Proxy /get-data/<id> to backend (optional)
@app.route("/get-data/<int:user_id>", methods=["GET"])
def get_data(user_id):
    try:
        response = requests.get(f"{BACKEND_URL}/get-data/{user_id}")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
