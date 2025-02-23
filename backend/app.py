from datetime import datetime, timedelta
from dateutil.relativedelta import *

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
    date_today = datetime.now().date()
    start_date = None
    method = request.args.get("method")
    if method == "daily": # Allow users to view the past 2 weeks trend
        start_date = date_today - relativedelta(weeks=2)
    elif method == "monthly": # Allow users to view past 6 months trend
        start_date = date_today - relativedelta(months=6)
    else: # Allow users to view past 3 years trend
        start_date = date_today - relativedelta(years=3)

    aggregation_request(start_date, date_today, r) # add weather data into redis

    # Put everything into a dataframe for plotting
    date_range = [start_date + timedelta(days=i) for i in range((date_today - start_date).days + 1)]
    aggregate_count = pd.DataFrame(columns=["date", "type", "values"])
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

        aggregate_count = pd.concat([aggregate_count, curr_weather])

        '''
        Return as a list of values for each type, so we can use js graphing libraries e.g. Plotly.js in our html file
        Do not use matplotlib / seaborn in the backend, as we can only save an image and display that on our website,
        resulting in non-interactive graphs.
        '''
    filter_low = aggregate_count["type"] == "low"
    filter_high = aggregate_count["type"] == "high"
    filter_humidityLow = aggregate_count["type"] == "humidityLow"
    filter_humidityHigh = aggregate_count["type"] == "humidityHigh"
    filter_windLow = aggregate_count["type"] == "windLow"
    filter_windHigh = aggregate_count["type"] == "windHigh"
    if method == "daily":
        return {"date": aggregate_count["date"].apply(lambda x: x.strftime("%Y-%m-%d")).tolist(),
                "low": aggregate_count[filter_low]["values"].tolist(),
                "high": aggregate_count[filter_high]["values"].tolist(),
                "humidityLow": aggregate_count[filter_humidityLow]["values"].tolist(),
                "humidityHigh": aggregate_count[filter_humidityHigh]["values"].tolist(),
                "windLow": aggregate_count[filter_windLow]["values"].tolist(),
                "windHigh": aggregate_count[filter_windHigh]["values"].tolist()
                }

    elif method == "monthly":
        aggregate_count["year_month"] = aggregate_count["date"].apply(lambda x: x.strftime("%Y-%m"))
        grouped = aggregate_count.groupby(["year_month", "type"]).mean().reset_index()

        return {"date": grouped["year_month"], # year_month already converted to string, so no need to convert anymore
                "low": grouped[filter_low]["values"].tolist(),
                "high": grouped[filter_high]["values"].tolist(),
                "humidityLow": grouped[filter_humidityLow]["values"].tolist(),
                "humidityHigh": grouped[filter_humidityHigh]["values"].tolist(),
                "windLow": grouped[filter_windLow]["values"].tolist(),
                "windHigh": grouped[filter_windHigh]["values"].tolist()
                }
    else: # yearly
        aggregate_count["year"] = aggregate_count["date"].dt.year
        grouped = aggregate_count.groupby(["year", "type"]).mean().reset_index()

        return {"date": grouped["year"],
                "low": grouped[filter_low]["values"].tolist(),
                "high": grouped[filter_high]["values"].tolist(),
                "humidityLow": grouped[filter_humidityLow]["values"].tolist(),
                "humidityHigh": grouped[filter_humidityHigh]["values"].tolist(),
                "windLow": grouped[filter_windLow]["values"].tolist(),
                "windHigh": grouped[filter_windHigh]["values"].tolist()
                }


@app.route("/")
def home():
    return render_template("weather_ui.html")


