from datetime import datetime, timedelta
from dateutil.relativedelta import *

import pandas as pd
import redis
from flask import Flask, render_template, request

from weather_request import weather_request, aggregation_request

# host argument must be the same as the name given in compost.yaml
r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")

@app.route("/data", methods=["GET"])
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
    print(method)
    if method == "Daily": # Allow users to view the past 2 weeks trend
        start_date = date_today - relativedelta(weeks=2)
    elif method == "Monthly": # Allow users to view past 6 months trend
        start_date = date_today - relativedelta(months=6)
    else: # Allow users to view past 3 years trend
        start_date = date_today - relativedelta(years=3)

    aggregation_request(start_date, date_today, r) # add weather data into redis

    # Put everything into a dataframe for plotting
    date_range = [start_date + timedelta(days=i) for i in range((date_today - start_date).days + 1)]
    aggregate_count = pd.DataFrame(columns=["date", "type", "values"])
    for date in date_range:
        payload = r.hgetall(date.strftime("%Y-%m-%d"))
        low = eval(payload.get("temp"))[0] # values are stored as a string in redis -> "['20', '30']". So convert to a list using eval()
        high = eval(payload.get("temp"))[1]

        curr_weather = pd.DataFrame([
            [date, "low", low],
            [date, "high", high]
        ], columns=["date", "type", "values"])

        aggregate_count = pd.concat([aggregate_count, curr_weather])

    aggregate_count["date"] = pd.to_datetime(aggregate_count["date"], format="%Y-%m-%d") # pandas converts date to object, so convert it back to datetime.
    aggregate_count.reset_index(inplace=True, drop=True)

    '''
    Return as a list of values for each type, so we can use js graphing libraries e.g. Plotly.js in our html file
    Do not use matplotlib / seaborn in the backend, as we can only save an image and display that on our website,
    resulting in non-interactive graphs.
    '''
    filter_low = aggregate_count["type"] == "low"
    filter_high = aggregate_count["type"] == "high"
    if method == "Daily":
        # Have to make date unique, as we have 2 same dates, one for low one for high.
        # e.g. [ ["2024-05-10", "low", 25], ["2024-05-10", "high", 30] ]
        return {"date": aggregate_count["date"].apply(lambda x: x.strftime("%Y-%m-%d")).unique().tolist(),
                "low": aggregate_count[filter_low]["values"].tolist(),
                "high": aggregate_count[filter_high]["values"].tolist()
                }
    elif method == "Monthly":
        aggregate_count["year_month"] = aggregate_count["date"].apply(lambda x: x.strftime("%Y-%m"))
        grouped = aggregate_count.groupby(["year_month", "type"]).mean().reset_index()

        return {"date": grouped["year_month"].unique().tolist(), # year_month already converted to string, so no need to convert anymore
                "low": grouped[filter_low]["values"].tolist(),
                "high": grouped[filter_high]["values"].tolist()
                }
    else: # Yearly
        aggregate_count["year"] = aggregate_count["date"].dt.year
        grouped = aggregate_count.groupby(["year", "type"]).mean().reset_index()

        return {"date": grouped["year"].unique().tolist(),
                "low": grouped[filter_low]["values"].tolist(),
                "high": grouped[filter_high]["values"].tolist()
                }


@app.route("/")
def home():
    return render_template("weather_ui.html")


