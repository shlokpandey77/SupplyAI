from flask import Flask, render_template
import pandas as pd
import requests
import os

API_KEY = os.environ.get("API_KEY")

app = Flask(__name__)

# 🔑 Replace with your API key
API_KEY = "YOUR_API_KEY"


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
    df = pd.read_csv("data.csv")

    def risk_logic(delay, weather):
        if delay > 40 or weather in ["Rain", "Storm"]:
            return "HIGH"
        elif delay > 15:
            return "MEDIUM"
        else:
            return "LOW"

    results = []

    for _, row in df.iterrows():
        weather = get_weather(row["location"])
        risk = risk_logic(row["delay_minutes"], weather)

        if risk != "LOW":
            results.append({
                "location": row["location"],
                "delay": row["delay_minutes"],
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


# 🚀 Run server
if __name__ == "__main__":
    print("🚀 Starting SmartSupply AI...")
    app.run(debug=True)