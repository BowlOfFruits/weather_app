from datetime import datetime
import redis
from flask import Flask, g, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

#r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
#user_date = datetime.now().date().strftime("%Y-%m-%d")

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://"
)

@app.route("/data", methods=["GET", "POST"])
#@limiter.limit("10 per day")
def get_data():
    g.user_date = {}
    if request.method == "POST":
        g.user_date["user_date"] = request.json.get("user_date")
        print(request.json.get("user_date"))


    return render_template("test.html") # Not showing user_date

@app.route("/")
def home():
    g.data = {"low": "27", "high": "31",
             "windLow": "10", "windHigh": "15", "windDirection": "NNE",
             "humidity": "75",
             "weatherDescription": "Fair"}

    return render_template("weather_ui.html")


