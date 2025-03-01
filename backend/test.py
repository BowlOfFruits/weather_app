from datetime import datetime, timedelta
from dateutil.relativedelta import *
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

now = datetime.now().date()
print(now - relativedelta(weeks=2))


