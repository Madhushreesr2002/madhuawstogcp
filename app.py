from flask import Flask, render_template_string, request, jsonify
import requests
import boto3
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://capestone-lb-767169422.ap-south-1.elb.amazonaws.com"])

# ✅ Load HTML form template
with open("food_order_form.html", "r") as f:
    html_form = f.read()

# ✅ Backend internal load balancer URL
BACKEND_URL = "http://internal-instance-ll-rr-1942256296.ap-south-1.elb.amazonaws.com:8080"


@app.route("/", methods=["GET"])
def food_order_form():
    return render_template_string(html_form)


# ✅ Proxy /submit to backend + push message to SQS
@app.route("/submit", methods=["POST"])
def proxy_submit():
    form_data = request.form.to_dict()
    try:
        # Forward to backend
        response = requests.post(f"{BACKEND_URL}/submit", data=form_data)

        # Push to SQS if successful
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
