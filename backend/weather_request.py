from datetime import datetime, timedelta
from utils import add_weather, add_one_day_weather
import redis

'''
View weather forecast for 4 days, including today
'''
def weather_request(user_date: datetime, r: redis) -> None:
    '''
    Add weather data into redis
    '''
    dates_needed_ahead = [user_date + timedelta(days=i) for i in range(0, 4)]
    missing_dates = []
    for i in range(len(dates_needed_ahead)):
        date_str = dates_needed_ahead[i].strftime("%Y-%m-%d") # Convert datetime back to string
        if not r.exists(date_str): # this date is not in redis
            missing_dates.append((i, date_str))

    if missing_dates:
        add_weather(user_date - timedelta(days=1), missing_dates, r, historical=False) # Add missing dates into redis

def aggregation_request(from_date: datetime, to_date: datetime, r: redis) -> None:
    '''
    Add weather data into redis
    '''
    date_range = [from_date + timedelta(days=i) for i in range((to_date-from_date).days + 1)]
    for i in range(len(date_range)):
        if not r.exists(date_range[i].strftime("%Y-%m-%d")): # weather data for this date doesn't exist
            add_one_day_weather(date_range[i] - timedelta(days=1), r)
