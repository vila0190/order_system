from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

COURIER_PRICING = [
    (200, 5), (500, 10), (1000, 15), (5000, 20)
]

def get_courier_cost(weight):
    for limit, price in COURIER_PRICING:
        if weight <= limit:
            return price
    return 25  # Default if weight is beyond 5000g

def split_packages(items):
    total_price = sum(item['price'] for item in items)
    packages = []
    
    if total_price <= 250:
        weight = sum(item['weight'] for item in items)
        packages.append({
            "items": [item["name"] for item in items],
            "total_price": total_price,
            "total_weight": weight,
            "courier_cost": get_courier_cost(weight)
        })
    else:
        items.sort(key=lambda x: x['price'], reverse=True)
        temp_pack = []
        temp_price = 0
        temp_weight = 0

        for item in items:
            if temp_price + item['price'] > 250:
                packages.append({
                    "items": [p["name"] for p in temp_pack],
                    "total_price": temp_price,
                    "total_weight": temp_weight,
                    "courier_cost": get_courier_cost(temp_weight)
                })
                temp_pack = []
                temp_price = 0
                temp_weight = 0
            
            temp_pack.append(item)
            temp_price += item['price']
            temp_weight += item['weight']

        if temp_pack:
            packages.append({
                "items": [p["name"] for p in temp_pack],
                "total_price": temp_price,
                "total_weight": temp_weight,
                "courier_cost": get_courier_cost(temp_weight)
            })

    return packages

@app.route("/process_order", methods=["POST"])
def process_order():
    items = request.json
    result = split_packages(items)

    html_response = "<h3>This order has the following packages:</h3>"
    for i, package in enumerate(result):
        html_response += f"<b>Package {i + 1}</b><br>"
        html_response += f"Items: {', '.join(package['items'])}<br>"
        html_response += f"Total Weight: {package['total_weight']}g<br>"
        html_response += f"Total Price: ${package['total_price']}<br>"
        html_response += f"Courier Price: ${package['courier_cost']}<br><br>"

    return html_response

if __name__ == "__main__":
    app.run(debug=True)
