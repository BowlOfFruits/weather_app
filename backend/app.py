from datetime import datetime
import redis
from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from weather_request import weather_request

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
default_date = datetime.now().date().strftime("%Y-%m-%d")

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://"
)

@app.route("/data", methods=["GET"])
#@limiter.limit("10 per day")
def get_data():
    user_date = datetime.strptime(request.args.get("date"), "%Y-%m-%d")
    weather_request(user_date, r) # Check if redis contains this date. If not, add it in

    payload = r.hgetall(user_date.strftime("%Y-%m-%d"))

    weather = payload.get("weather")
    low = eval(payload.get("temp"))[0] # values are stored as a string in redis -> "['20', '30']". So convert to a list using eval()
    high = eval(payload.get("temp"))[1]
    humidityLow = eval(payload.get("humidity"))[0]
    humidityHigh = eval(payload.get("humidity"))[1]
    windLow = eval(payload.get("windSpeed"))[0]
    windHigh = eval(payload.get("windSpeed"))[1]
    windDirection = payload.get("windDirection")

    return {"weather": weather, "low": low, "high": high, "humidityLow": humidityLow, "humidityHigh": humidityHigh, "windLow": windLow, "windHigh": windHigh, "windDirection": windDirection}


@app.route("/")
def home():
    return render_template("weather_ui.html")


