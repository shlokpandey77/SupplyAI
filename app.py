from flask import Flask, render_template
import requests
import os
import csv

app = Flask(__name__)

# ✅ Use environment variable only
API_KEY = os.environ.get("API_KEY")


# 📂 Read CSV (no pandas)
def read_csv_data():
    data = []
    with open("data.csv", newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data


# 📡 Get real-time weather
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()
        return data["weather"][0]["main"]
    except:
        return "Unknown"


# 🚨 Detect disruption
def detect_disruption():
    df = read_csv_data()

    def risk_logic(delay, weather):
        if delay > 40 or weather in ["Rain", "Storm"]:
            return "HIGH"
        elif delay > 15:
            return "MEDIUM"
        else:
            return "LOW"

    results = []

    for row in df:
        delay = int(row["delay_minutes"])  # ✅ fix

        weather = get_weather(row["location"])
        risk = risk_logic(delay, weather)

        if risk != "LOW":
            results.append({
                "location": row["location"],
                "delay": delay,
                "weather": weather,
                "risk": risk,
                "solution": suggest_route(row["location"])
            })

    return results


# 🛣 Route suggestions
def suggest_route(location):
    routes = {
        "Delhi": "Use NH48 alternative",
        "Mumbai": "Divert via Pune route",
        "Chennai": "Use coastal bypass",
        "Lucknow": "Use outer ring road",
        "Kanpur": "Use highway bypass"
    }
    return routes.get(location, "No suggestion")


# 🌐 Main route
@app.route("/")
def home():
    alerts = detect_disruption()
    return render_template("index.html", alerts=alerts)


# 🚀 Run server (safe for local only)
if __name__ == "__main__":
    print("🚀 Starting SmartSupply AI...")
    app.run(host="0.0.0.0", port=10000)