from flask import Flask, request, jsonify
import requests
import boto3
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://capestone-lb-767169422.ap-south-1.elb.amazonaws.com"])

# ✅ Backend internal load balancer URL
BACKEND_URL = "http://internal-instance-ll-rr-1942256296.ap-south-1.elb.amazonaws.com:8080"

# ✅ SQS Setup (replace with your actual values)
sqs_client = boto3.client("sqs", region_name="ap-south-1")
SQS_QUEUE_URL = "https://sqs.ap-south-1.amazonaws.com/YOUR_ACCOUNT_ID/YOUR_QUEUE_NAME"


@app.route("/", methods=["GET"])
def show_form():
    try:
        with open("food_order_form.html", "r") as f:
            html_content = f.read()
        return html_content
    except Exception as e:
        return f"<h2>Error loading form:</h2><p>{str(e)}</p>", 500


# ✅ Proxy /submit to backend + push message to SQS
@app.route("/submit", methods=["POST"])
def proxy_submit():
    form_data = request.form.to_dict()
    try:
        # Forward to backend
        response = requests.post(f"{BACKEND_URL}/submit", data=form_data)

        # Push to SQS if backend call is successful
        if response.status_code == 200:
            email = form_data.get("email")
            if email:
                message = {
                    "email": email,
                    "form_data": form_data
                }
                sqs_client.send_message(
                    QueueUrl=SQS_QUEUE_URL,
                    MessageBody=json.dumps(message)
                )

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
