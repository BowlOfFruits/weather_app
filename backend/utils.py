import sys, os
import requests
import json
from datetime import timedelta, date
import redis

def add_future_weather(from_date: date, missing_dates: list[(int, str)], r: redis) -> None:
    '''
    API provided by data.gov.sg
    Calls API and adds forecast for dates that are not in redis into redis.
    Sets expiry to one day later
    '''
    url = "https://api-open.data.gov.sg/v2/real-time/api/four-day-outlook?date=" + from_date.strftime("%Y-%m-%d") # Get the 4-day forecast from the specified day
    response = requests.get(url)
    forecast = json.loads(json.dumps(response.json()["data"]["records"][0])) # index 0 is the most recent forecast
    forecast = forecast["forecasts"]

    try:
        for i, date_str in missing_dates:
            forecast_i = forecast[i]

            weather = forecast_i["forecast"]["text"]
            temp = str([forecast_i["temperature"]["low"], forecast_i["temperature"]["high"]])
            humidity = str([forecast_i["relativeHumidity"]["low"], forecast_i["relativeHumidity"]["high"]])
            windSpeed = str([forecast_i["wind"]["speed"]["low"], forecast_i["wind"]["speed"]["high"]])
            windDirection = forecast_i["wind"]["direction"]

            '''
            Store data in redis as so:
            {2025-02-05: {weather: "Thundery Showers", temp: [25, 35], humidity: [50, 90], windSpeed: [10, 20], windDirection: NNW}}
            
            '''
            r.hset(
                date_str,
                mapping={
                    "weather": weather,
                    "temp": temp,
                    "humidity": humidity,
                    "windSpeed": windSpeed,
                    "windDirection": windDirection
                }
            )
            r.expire(date_str, timedelta(days=1)) # remove forecast after 1 day
    except Exception as e:
        fname = os.path.split(sys.exc_info()[2].tb_frame.f_code.co_filename)[1]
        print("script name: ", fname, ", line number: ", sys.exc_info()[2].tb_lineno, sep="")
        print(e)
    else:
        print("missing forecast dates:", [date for i, date in missing_dates])
        print("Added into redis successfully")

def add_historical_weather(missing_dates: list[str], r: redis) -> None:
    url = "https://api-open.data.gov.sg/v2/real-time/api/twenty-four-hr-forecast?date=" # Uses 24h forecast API to get historical data.

    try:
        for date_str in missing_dates:
            response = requests.get(url + date_str)
            forecast = json.loads(json.dumps(response.json()["data"]["records"][0])) # index 0 is the most recent forecast
            forecast = forecast["general"]

            weather = forecast["forecast"]["text"]
            temp = str([forecast["temperature"]["low"], forecast["temperature"]["high"]]) # Must be stored as string in redis hash
            humidity = str([forecast["relativeHumidity"]["low"], forecast["relativeHumidity"]["high"]])
            windSpeed = str([forecast["wind"]["speed"]["low"], forecast["wind"]["speed"]["high"]])
            windDirection = forecast["wind"]["direction"]

            '''
            Store data in redis as so:
            {2025-02-05: {weather: "Thundery Showers", temp: [25, 35], humidity: [50, 90], windSpeed: [10, 20], windDirection: NNW}}
        
            '''
            r.hset(
                date_str,
                mapping={
                    "weather": weather,
                    "temp": temp,
                    "humidity": humidity,
                    "windSpeed": windSpeed,
                    "windDirection": windDirection
                }
            )
    except Exception as e:
        fname = os.path.split(sys.exc_info()[2].tb_frame.f_code.co_filename)[1]
        print("script name: ", fname, ", line number: ", sys.exc_info()[2].tb_lineno, sep="")
        print(e)
    else:
        print("missing historical dates:", missing_dates)
        print("Added into redis successfully")

