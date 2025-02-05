from datetime import datetime, timedelta
import redis

from utils import add_future_weather, add_historical_weather

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

user_date = "2025-02-04"
to_date = datetime.strptime(user_date, '%Y-%m-%d').date()

date_today = datetime.now().date()

'''
Different scenarios to user selected date (Assume date today is 2025-02-05)

1. If user selected date == date today, then we will get the forecast weather for 2 days in the future and historical weather 2 days in the past
2. If user selected date is yesterday (2025-02-04), we will get the forecast weather for 2025-02-06 and the historical weather for 2025-02-02, 2025-02-03 and 2025-02-05 (today's date)
3. If user selected date is more than 1 day from today (2025-02-03 and earlier), we will only get the historical weather.
'''
if to_date == date_today:
    '''
    Scenario 1
    '''
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
elif date_today - to_date == timedelta(days=1):
    '''
    Scenario 2
    '''
    forecast_date = to_date + timedelta(days=2)
    if not r.exists(forecast_date.strftime("%Y-%m-%d")):
        add_future_weather(date_today, [(0, forecast_date.strftime("%Y-%m-%d"))], r)

    historical_dates = [date_today.strftime("%Y-%m-%d")] + [to_date - timedelta(days=i) for i in range(3)]
    missing_dates_historical = []
    for i in range(len(historical_dates)):
        date_str = historical_dates[i].strftime("%Y-%m-%d")
        if not r.exists(date_str):
            missing_dates_historical.append(date_str)

    if missing_dates_historical:
        add_historical_weather(missing_dates_historical, r) # Add missing dates into redis
else:
    '''
    Scenario 3
    '''
    historical_dates = [to_date - timedelta(days=i) for i in range(3)] + [to_date + timedelta(days=i) for i in range(1, 3)]
    missing_dates_historical = []
    for i in range(len(historical_dates)):
        date_str = historical_dates[i].strftime("%Y-%m-%d")
        if not r.exists(date_str):
            missing_dates_historical.append(date_str)

    if missing_dates_historical:
        add_historical_weather(missing_dates_historical, r)  # Add missing dates into redis

