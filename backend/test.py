from datetime import datetime, timedelta
import redis
import requests
import json
from utils import add_future_weather, add_historical_weather


r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

user_date = "2025-02-04"
to_date = datetime.strptime(user_date, '%Y-%m-%d').date()
date_today = datetime.now().date()


forecast_dates_ahead = [to_date + timedelta(days=i) for i in range(1, 3)]
missing_dates_ahead = []
for i in range(len(forecast_dates_ahead)):
    date_str = forecast_dates_ahead[i].strftime("%Y-%m-%d") # Convert datetime back to string
    if not r.exists(date_str): # this date is not in redis
        missing_dates_ahead.append((i, date_str))

if missing_dates_ahead:
    add_future_weather(to_date, missing_dates_ahead, r) # Add missing dates into redis


historical_dates = [to_date - timedelta(days=i) for i in range(3)] # Inclusive of user_date
missing_dates_historical = []
for i in range(len(historical_dates)):
    date_str = historical_dates[i].strftime("%Y-%m-%d")
    if not r.exists(date_str):
        missing_dates_historical.append(date_str)

if missing_dates_historical:
    add_historical_weather(missing_dates_historical, r) # Add missing dates into redis

