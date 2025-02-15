from datetime import datetime, timedelta
from utils import add_weather
import redis

'''
View weather forecast for 4 days, including today
'''
def weather_request(user_date: datetime, r: redis):
    dates_needed_ahead = [user_date + timedelta(days=i) for i in range(0, 4)]
    missing_dates = []
    for i in range(len(dates_needed_ahead)):
        date_str = dates_needed_ahead[i].strftime("%Y-%m-%d") # Convert datetime back to string
        if not r.exists(date_str): # this date is not in redis
            missing_dates.append((i, date_str))

    if missing_dates:
        add_weather(user_date - timedelta(days=1), missing_dates, r, historical=False) # Add missing dates into redis

