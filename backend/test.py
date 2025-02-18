from datetime import datetime, timedelta
import redis
import requests
import json
from utils import add_weather
import pandas as pd

'''
url = "https://api-open.data.gov.sg/v2/real-time/api/four-day-outlook?date=" + "2025-02-07" # Get the 4-day forecast from the specified day
response = requests.get(url)
forecast = json.loads(json.dumps(response.json()["data"]["records"][0])) # index 0 is the most recent forecast
print(forecast["forecasts"])
'''

aggregate_count = pd.DataFrame(columns=["date", "type", "measurement"])
print(pd.concat(
    [aggregate_count, pd.DataFrame([["2024-07-10", "low", 30], ["2024-07-10", "high", 35]], columns=["date", "type", "measurement"])]
))




