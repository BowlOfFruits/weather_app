from datetime import datetime, timedelta
import redis

from utils import add_future_weather, add_historical_weather

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

user_date = "2025-02-04"
to_date = datetime.strptime(user_date, '%Y-%m-%d')

'''
We want to display the weather for today as well as 3 days before and ahead. So, check if they are in redis
'''
forecast_dates_ahead = [to_date + timedelta(days=i) for i in range(1, 4)]
missing_dates_ahead = []
for i in range(len(forecast_dates_ahead)):
    date_str = forecast_dates_ahead[i].strftime("%Y-%m-%d") # Convert datetime back to string
    if not r.get(date_str): # this date is not in redis
        missing_dates_ahead.append((i, date_str))

if missing_dates_ahead:
    add_future_weather(to_date, missing_dates_ahead, r)

forecast_dates_back = [to_date - timedelta(days=i) for i in range(4)] # Inclusive of user_date
missing_dates_back = []
for i in range(len(forecast_dates_back)):
    date_str = forecast_dates_back[i].strftime("%Y-%m-%d")
    if not r.get(date_str):
        missing_dates_back.append(date_str)

if missing_dates_back:
    add_historical_weather(missing_dates_back, r)

