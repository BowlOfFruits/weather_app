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

aggregate_count = pd.DataFrame(columns=["date", "type", "value"])
aggregate_count = pd.concat(
    [ aggregate_count, pd.DataFrame([[datetime.strptime("2024-07-10", "%Y-%m-%d"), "low", 30], [datetime.strptime("2024-07-10", "%Y-%m-%d"), "high", 35]], columns=["date", "type", "value"]) ]
)
aggregate_count = pd.concat(
    [ aggregate_count, pd.DataFrame([[datetime.strptime("2024-07-11", "%Y-%m-%d"), "low", 27], [datetime.strptime("2024-07-11", "%Y-%m-%d"), "high", 32]], columns=["date", "type", "value"]) ]
)
aggregate_count = pd.concat(
    [ aggregate_count, pd.DataFrame([[datetime.strptime("2024-08-10", "%Y-%m-%d"), "low", 10], [datetime.strptime("2024-08-10", "%Y-%m-%d"), "high", 20]], columns=["date", "type", "value"]) ]
)
aggregate_count = pd.concat(
    [ aggregate_count, pd.DataFrame([[datetime.strptime("2024-08-11", "%Y-%m-%d"), "low", 25], [datetime.strptime("2024-08-11", "%Y-%m-%d"), "high", 30]], columns=["date", "type", "value"]) ]
)

#aggregate_count["year_month"] = aggregate_count["date"].apply(lambda x: x.strftime("%Y-%m")).tolist()
#print(aggregate_count.groupby(["year_month", "type"]).mean().reset_index())
#print(aggregate_count["date"].dt.year.tolist())

time1 = datetime.strptime("2024-07", "%Y-%m")
print(time1)


