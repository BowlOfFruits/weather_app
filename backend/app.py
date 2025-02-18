from datetime import datetime, timedelta
import pandas as pd
import redis
from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from weather_request import weather_request, aggregation_request

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

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
    if user_date <= datetime.now().date():
        return Exception("Error: Please choose a valid date. Date must be before or on today.")

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

@app.route("/aggregate", methods=["GET"])
def get_aggregate_data():
    from_date = datetime.strptime(request.args.get("from_date"), "%Y-%m-%d")
    to_date = datetime.strptime(request.args.get("to_date"), "%Y-%m-%d")
    method = request.args.get("method")
    if from_date >= to_date:
        return Exception("Error: Dates must be at least one day apart and to_date must come after from_date")

    aggregation_request(from_date, to_date, r) # add weather data into redis

    # Put everything into a dataframe for plotting
    date_range = [from_date + timedelta(days=i) for i in range((to_date - from_date).days + 1)]
    aggregate_count = pd.DataFrame(columns=["date", "type", "measurement"])
    for date in date_range:
        payload = r.hgetall(date.strftime("%Y-%m-%d"))
        low = eval(payload.get("temp"))[0]  # values are stored as a string in redis -> "['20', '30']". So convert to a list using eval()
        high = eval(payload.get("temp"))[1]
        humidityLow = eval(payload.get("humidity"))[0]
        humidityHigh = eval(payload.get("humidity"))[1]
        windLow = eval(payload.get("windSpeed"))[0]
        windHigh = eval(payload.get("windSpeed"))[1]

        curr_weather = pd.DataFrame([
            [date, "low", low],
            [date, "high", high],
            [date, "humidityLow", humidityLow],
            [date, "humidityHigh", humidityHigh],
            [date, "windLow", windLow],
            [date, "windHigh", windHigh]
        ], columns=["date", "type", "measurement"])

        pd.concat([aggregate_count, curr_weather])

    if method == "daily":
        # plot graph
        pass
    elif method == "monthly":
        # groupby date and type then aggregate using avg and plot
        pass
    else: # yearly
        # groupby date and type then aggregate using avg and plot
        pass


@app.route("/")
def home():
    return render_template("weather_ui.html")


