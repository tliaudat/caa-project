
from dotenv import load_dotenv
load_dotenv()  # charge dashboard/.env# dashboard/utils/data_fetcher.py
import requests
import os
from typing import Dict, List, Any, Optional
import streamlit as st
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account
from google.cloud import secretmanager
import json

class DataFetcher:
    def __init__(self):
        self.api_base_url = os.getenv('API_BASE_URL', 'https://caa-project-middleware-972566364424.europe-west6.run.app')
        self.headers = {'Content-Type': 'application/json'}

    @st.cache_resource
    def get_bq_client(_self):
        """Initialize BigQuery client using credentials from Secret Manager"""
        try:
                # Initialize Secret Manager client
                secret_client = secretmanager.SecretManagerServiceClient()
                
                # Define the secret details
                project_id = "data-science-443020"
                secret_id = "credentials"
                version_id = "latest"
                
                # Build the resource name of the secret version
                name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
                
                # Access the secret version
                response = secret_client.access_secret_version(request={"name": name})
                
                # Parse the secret payload as JSON
                secret_data = response.payload.data.decode("UTF-8")
                credentials_info = json.loads(secret_data)
                
                # Create credentials from the JSON data
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                
                # Create and return BigQuery client
                client = bigquery.Client(project=project_id, credentials=credentials)
                
                # Test the connection
                list(client.list_datasets(max_results=1))
                
                return client
                
        except Exception as e:
                # Fallback to default credentials for local development
            try:
                client = bigquery.Client(project="data-science-443020")
                list(client.list_datasets(max_results=1))
                return client
            except Exception as fallback_error:
                    st.error(f"Failed to initialize BigQuery client: {str(e)}")
                    st.error(f"Fallback also failed: {str(fallback_error)}")
                    st.info("""
                    **Authentication Setup Required:**
                    
                    1. For local development:
                    ```bash
                    gcloud auth login
                    gcloud auth application-default login
                    ```
                    
                    2. Ensure your account has:
                    - Secret Manager Secret Accessor role
                    - BigQuery User role
                    """)
                    return None
    
    def get_current_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """Fetch current weather data"""
        return self._get_current_weather_cached(self.api_base_url, location, self.headers)
    
    @staticmethod
    
    def _get_current_weather_cached(api_base_url: str, location: str, headers: Dict) -> Optional[Dict[str, Any]]:
        """Cached version of get_current_weather"""
        try:
            response = requests.get(
                f"{api_base_url}/weather",
                params={'location': location},
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to fetch current weather: {str(e)}")
            return None
    
    def get_forecast(self, location: str) -> Optional[Dict[str, Any]]:
        """Fetch weather forecast"""
        return self._get_forecast_cached(self.api_base_url, location, self.headers)
    
    @staticmethod
    
    def _get_forecast_cached(api_base_url: str, location: str, headers: Dict) -> Optional[Dict[str, Any]]:
        """Cached version of get_forecast"""
        try:
            response = requests.get(
                f"{api_base_url}/forecast",
                params={'location': location},
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to fetch forecast: {str(e)}")
            return None
    
    def get_last_sensor_data(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Fetch last sensor reading"""
        return self._get_last_sensor_data_cached(self.api_base_url, device_id, self.headers)
    
    @staticmethod
    def _get_last_sensor_data_cached(api_base_url: str, device_id: str, headers: Dict) -> Optional[Dict[str, Any]]:
        """Cached version of get_last_sensor_data"""
        try:
            response = requests.get(
                f"{api_base_url}/sensors/last",
                params={'device_id': device_id},
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to fetch sensor data: {str(e)}")
            return None
        
    def _fetch_last_from_bigquery(self, device_id: str) -> Optional[Dict[str, Any]]:
        query = f"""
            SELECT timestamp, temperature, humidity
            FROM `data-science-443020.weather_monitor.sensor_readings`
            WHERE device_id = @device_id
            ORDER BY timestamp DESC
            LIMIT 1
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("device_id", "STRING", device_id)]
        )
        query_job = self.bq_client.query(query, job_config=job_config)
        rows = list(query_job.result())
        if not rows:
            return None
        row = rows[0]
        return {
            "timestamp": row.timestamp.isoformat(),
            "temperature": row.temperature,
            "humidity": row.humidity
        }
    
    def get_sensor_history(self, device_id: str, hours: int) -> Optional[List[Dict[str, Any]]]:
        """Fetch sensor history"""
        return self._get_sensor_history_cached(self.api_base_url, device_id, hours, self.headers)
    
    @staticmethod
    def _get_sensor_history_cached(api_base_url: str, device_id: str, hours: int, headers: Dict) -> Optional[List[Dict[str, Any]]]:
        """Cached version of get_sensor_history"""
        try:
            response = requests.get(
                f"{api_base_url}/history/sensors",
                params={'device_id': device_id, 'hours': hours},
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to fetch sensor history: {str(e)}")
            return None
    
    def get_weather_history(self, location: str, hours: int) -> Optional[List[Dict[str, Any]]]:
        """Fetch weather history"""
        return self._get_weather_history_cached(self.api_base_url, location, hours, self.headers)
    
    @staticmethod
    def _get_weather_history_cached(api_base_url: str, location: str, hours: int, headers: Dict) -> Optional[List[Dict[str, Any]]]:
        """Cached version of get_weather_history"""
        try:
            response = requests.get(
                f"{api_base_url}/history/weather",
                params={'location': location, 'hours': hours},
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to fetch weather history: {str(e)}")
            return None
    
    def get_alerts_history(self, device_id: str, days: int) -> Optional[List[Dict[str, Any]]]:
        """Fetch alerts history"""
        return self._get_alerts_history_cached(self.api_base_url, device_id, days, self.headers)
    
    @staticmethod
    def _get_alerts_history_cached(api_base_url: str, device_id: str, days: int, headers: Dict) -> Optional[List[Dict[str, Any]]]:
        """Cached version of get_alerts_history"""
        try:
            # This endpoint would need to be implemented in the Flask app
            # For now, we'll return mock data or empty list
            return []
        except Exception as e:
            st.error(f"Failed to fetch alerts history: {str(e)}")
            return None
    
    def check_alerts(self, sensor_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check sensor data for alert conditions (client-side)"""
        alerts = []
        
        # Define thresholds
        thresholds = {
            'humidity_low': 40,
            'humidity_high': 70,
            'temperature_low': 16,
            'temperature_high': 28,
            'air_quality_poor': 150,
            'air_quality_very_poor': 300
        }
        
        # Check humidity
        humidity = sensor_data.get('humidity')
        if humidity is not None:
            if humidity < thresholds['humidity_low']:
                alerts.append({
                    'type': 'LOW_HUMIDITY',
                    'severity': 'warning',
                    'message': f"Low humidity: {humidity}% (below {thresholds['humidity_low']}%)"
                })
            elif humidity > thresholds['humidity_high']:
                alerts.append({
                    'type': 'HIGH_HUMIDITY',
                    'severity': 'warning',
                    'message': f"High humidity: {humidity}% (above {thresholds['humidity_high']}%)"
                })
        
        # Check temperature
        temperature = sensor_data.get('temperature')
        if temperature is not None:
            if temperature < thresholds['temperature_low']:
                alerts.append({
                    'type': 'LOW_TEMPERATURE',
                    'severity': 'warning',
                    'message': f"Low temperature: {temperature}°C (below {thresholds['temperature_low']}°C)"
                })
            elif temperature > thresholds['temperature_high']:
                alerts.append({
                    'type': 'HIGH_TEMPERATURE',
                    'severity': 'warning',
                    'message': f"High temperature: {temperature}°C (above {thresholds['temperature_high']}°C)"
                })
        
        # Check air quality
        air_quality = sensor_data.get('air_quality')
        if air_quality is not None:
            if air_quality > thresholds['air_quality_very_poor']:
                alerts.append({
                    'type': 'VERY_POOR_AIR_QUALITY',
                    'severity': 'critical',
                    'message': f"Very poor air quality: {air_quality} (above {thresholds['air_quality_very_poor']})"
                })
            elif air_quality > thresholds['air_quality_poor']:
                alerts.append({
                    'type': 'POOR_AIR_QUALITY',
                    'severity': 'warning',
                    'message': f"Poor air quality: {air_quality} (above {thresholds['air_quality_poor']})"
                })
        
        return alerts
