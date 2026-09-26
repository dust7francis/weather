#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
#   "datetime",
# ]
# ///
#
# Canberra 7-day Weather Forecast
# ------------------------ 
# This script retrieves the 7-day Weather Forecast for Canberra
# using the Open-Meteo API. 
# 
# Requirements: 
# - Python 
# - uv (https://docs.astral.sh/uv/) 
# 
# 1. Make the script executable: 
# 
# chmod +x weather-7days.py 
# 
# 2. Run the script: 
# 
# ./weather-7days.py 
# 
# Sample output: 
# 
# ☀️ Canberra 7-day Weather Forecast☀️ 
#  
# Date          Day         Min     Max     Rain 
# 2026-09-26    Saturday    8.2°C   22.4°C  10%  
# 2026-09-27    Sunday      9.1°C   24.1°C  20% 
# 2026-09-28    Monday      7.5°C   19.8°C  30% 
# 2026-09-29    Tuesday     6.9°C   18.5°C  40% 
# 2026-09-30    Wednesday   10.2°C  21.7°C  20% 
# 2026-10-01    Thursday    11.4°C  25.3°C  10% 
# 2026-10-02    Friday      12.0°C  27.1°C  10%
# 

import requests
from datetime import datetime

def get_weather_now():
    # Coordinates for Canberra, Australia
    LAT = -35.2835
    LON = 149.1281

    url = ( 
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={LAT}&longitude={LON}"
        f"&daily=temperature_2m_max,"
        f"temperature_2m_min,"
        f"precipitation_probability_max"
        f"&timezone=Australia%2FSydney"
        f"&forecast_days=7"
    )
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        daily = data["daily"] 
        dates = daily["time"]
        max_temps = daily["temperature_2m_max"]
        min_temps = daily["temperature_2m_min"]
        rain_probs = daily["precipitation_probability_max"]
        
        print("☀️ Canberra 7-day Weather Forecast ☀️")
        print()
        
        print(
            f"{'Date':<12}"
            f"{'Day':<12}"
            f"{'Min':<8}"
            f"{'Max':<8}"
            f"{'Rain':<6}"
        )

        for date, min_temp, max_temp, rain in zip(
            dates, min_temps, max_temps, rain_probs
        ): 
            day = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
            
            print(
                f"{date:<12}"
                f"{day:<12}"
                f"{min_temp:>5.1f}°C "
                f"{max_temp:>5.1f}°C "
                f"{rain:>4}%"
            )
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")

if __name__ == "__main__":
    get_weather_now()
