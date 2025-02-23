from datetime import timedelta, date
from utils import add_weather
import redis

'''
View weather forecast for 4 days, including today
'''
def weather_request(user_date: date, r: redis) -> None:
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
        add_weather(user_date - timedelta(days=1), missing_dates, r) # Add missing dates into redis

def aggregation_request(from_date: date, to_date: date, r: redis) -> None:
    '''
    Add weather data into redis
    '''
    date_range = [from_date + timedelta(days=i) for i in range((to_date-from_date).days + 1)]
    for i in range(0, len(date_range), 4): # API returns 4 day outlook so look at 4 dates at a time
        missing_dates = []
        for j in range(4):
            if not r.exists(date_range[i+j].strftime("%Y-%m-%d")): # weather data for this date doesn't exist
                missing_dates.append((i+j, date_range[i+j].strftime("%Y-%m")))

        add_weather(date_range[i] - timedelta(days=1), missing_dates, r)
