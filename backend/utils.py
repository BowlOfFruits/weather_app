import sys, os
import requests
import json
from datetime import timedelta, date
import redis

def add_weather(start_date: date, missing_dates: list[(int, str)], r: redis, historical: bool) -> None:
    '''
    API provided by data.gov.sg
    Calls API and adds forecast for dates that are not in redis into redis.
    Sets expiry to one day later
    '''

    url = "https://api-open.data.gov.sg/v2/real-time/api/four-day-outlook?date=" + start_date.strftime("%Y-%m-%d") # Get the 4-day forecast from the specified day
    response = requests.get(url)
    forecast = json.loads(json.dumps(response.json()["data"]["records"][0])) # index 0 is the most recent forecast
    forecast = forecast["forecasts"]

    try:
        for i, date_str in missing_dates:
            forecast_i = forecast[i]

            weather = forecast_i["forecast"]["text"]
            temp = str([forecast_i["temperature"]["low"], forecast_i["temperature"]["high"]]) # List has to be conveted into a string to store into redis, if not redis will raise error.
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
            if not historical:
                r.expire(date_str, timedelta(hours=6)) # remove forecast after a few hours as we want to get updated forecast

    except Exception as e:
        fname = os.path.split(sys.exc_info()[2].tb_frame.f_code.co_filename)[1]
        print("script name: ", fname, ", line number: ", sys.exc_info()[2].tb_lineno, sep="")
        print(e)

    else:
        if historical:
            print("missing historical dates:", missing_dates)
        else:
            print("missing forecast dates:", [date for i, date in missing_dates])

        print("Added into redis successfully")

