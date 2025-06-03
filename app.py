from flask import Flask, render_template_string, request, jsonify
import requests
import boto3
import json

app = Flask(__name__)

# ✅ Load HTML form template
with open("food_order_form.html", "r") as f:
    html_form = f.read()

# ✅ Backend internal load balancer URL
BACKEND_URL = "http://internal-instance-ll-rr-1942256296.ap-south-1.elb.amazonaws.com:8080"



@app.route("/", methods=["GET", "POST"])
def food_order():
    if request.method == "POST":
        form_data = request.form.to_dict()

        try:
            # Forward the form data to the backend service
            response = requests.post(f"{BACKEND_URL}/submit", data=form_data)


            return f"""
            <h2>Order Confirmed!</h2>
            <p>Thank you, {email}. Your order for {form_data.get("quantity")} {form_data.get("food_item")}(s) from {form_data.get("restaurant")} has been placed.</p>
            <p>Delivery Address: {form_data.get("address")}</p>
            <p>Payment Method: {form_data.get("payment_method")}</p>
            <p><a href="/">Place another order</a></p>
            """, response.status_code

        except Exception as e:
            return f"<h2>Error</h2><p>{str(e)}</p>", 500

    return render_template_string(html_form)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
