import requests
import json
from datetime import datetime
import redis

def add_future_weather(user_date: datetime, missing_dates: list[(int, str)], r: redis) -> None:
    '''
    API provided by data.gov.sg
    Calls API and adds forecast for dates that are not in redis into redis.
    '''
    url = "https://api-open.data.gov.sg/v2/real-time/api/four-day-outlook?date=" + user_date.strftime("%Y-%m-%d") # Get the 4-day forecast
    response = requests.get(url)
    forecast = json.loads(json.dumps(response.json()["data"]["records"][0])) # index 0 is the most recent forecast
    forecast = forecast["forecasts"]

    try:
        for i, date_str in missing_dates:
            forecast_i = forecast[i]

            weather = forecast_i["forecast"]["text"]
            temp = [forecast_i["temperature"]["low"], forecast_i["temperature"]["high"]]
            humidity = [forecast_i["relativeHumidity"]["low"], forecast_i["relativeHumidity"]["high"]]
            windSpeed = [forecast_i["wind"]["speed"]["low"], forecast_i["wind"]["speed"]["high"]]
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

        print("missing forecast dates:", [date for i, date in missing_dates])
        print("Added into redis successfully")
    except Exception as e:
        print(e)


def add_historical_weather(missing_dates: list[str], r: redis) -> None:
    url = "https://api-open.data.gov.sg/v2/real-time/api/twenty-four-hr-forecast"

    try:
        for date_str in missing_dates:
            response = requests.get(url + date_str)
            forecast = json.loads(json.dumps(response.json()["data"]["records"][0])) # index 0 is the most recent forecast
            forecast = forecast["general"]

            weather = forecast["forecast"]["text"]
            temp = [forecast["temperature"]["low"], forecast["temperature"]["high"]]
            humidity = [forecast["relativeHumidity"]["low"], forecast["relativeHumidity"]["high"]]
            windSpeed = [forecast["wind"]["speed"]["low"], forecast["wind"]["speed"]["high"]]
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

        print("missing historical dates:", missing_dates)
        print("Added into redis successfully")
    except Exception as e:
        print(e)

