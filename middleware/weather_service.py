# middleware/services/weather_service.py
import requests
import os
from datetime import datetime
from typing import Dict, List, Any

class WeatherService:
    def __init__(self):
        self.api_key = os.environ.get('OPENWEATHER_API_KEY')
        self.base_url = 'https://api.openweathermap.org/data/2.5'
        
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY environment variable not set")
    
    def get_current_weather(self, location: str = 'Geneva,CH') -> Dict[str, Any]:
        """Get current weather data for a location"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant information
            return {
                'location': location,
                'timestamp': datetime.now().isoformat(),
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'weather': data['weather'][0]['main'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'wind_speed': data['wind']['speed'],
                'clouds': data['clouds']['all'],
                'coordinates': {
                    'lat': data['coord']['lat'],
                    'lon': data['coord']['lon']
                }
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch weather data: {str(e)}")
    
    def get_forecast(self, location: str = 'Geneva,CH') -> Dict[str, Any]:
        """Get 5-day weather forecast"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process forecast data
            forecast_list = []
            for item in data['list'][:40]:  # 5 days * 8 times per day
                forecast_list.append({
                    'timestamp': item['dt_txt'],
                    'temperature': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'humidity': item['main']['humidity'],
                    'weather': item['weather'][0]['main'],
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon'],
                    'wind_speed': item['wind']['speed'],
                    'rain_probability': item.get('pop', 0) * 100,
                    'rain_volume': item.get('rain', {}).get('3h', 0) if 'rain' in item else 0
                })
            
            return {
                'location': location,
                'timestamp': datetime.now().isoformat(),
                'forecast': forecast_list
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch forecast data: {str(e)}")
    
    def get_weather_icon_url(self, icon_code: str) -> str:
        """Get URL for weather icon"""
        return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
    
 
