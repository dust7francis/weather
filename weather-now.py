#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
# ]
# ///
#
# Canberra Current Weather 
# ------------------------ 
# This script retrieves the current weather for Canberra
# using the Open-Meteo API. 
# 
# Requirements: 
# - Python 
# - uv (https://docs.astral.sh/uv/) 
# 
# 1. Make the script executable: 
# 
# chmod +x weather-now.py 
# 
# 2. Run the script: 
# 
# ./weather-now.py 
# 
# Sample output: 
# 
# ☀️ Canberra Current Weather ☀️ 
# Time:    2026-09-26T17:30 
# Temperature: 22.4°C 
# Wind speed: 11.5km/h #

import requests

def get_weather_now():
    # Coordinates for Canberra, Australia
    LAT = -35.2835
    LON = 149.1281

    url = ( 
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={LAT}&longitude={LON}"
        f"&current=temperature_2m,wind_speed_10m"
        f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
        f"&timezone=Australia%2FSydney"
    )
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        current = data["current"]
        time = current["time"]
        temp = current["temperature_2m"]
        wind = current["wind_speed_10m"]
        
        print("☀️ Canberra Current Weather ☀️")
        print(f"Time:    {time}")
        print(f"Temperature: {temp}°C")
        print(f"Wind speed: {wind}km/h")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")

if __name__ == "__main__":
    get_weather_now()
