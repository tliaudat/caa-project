# dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.data_fetcher import DataFetcher
from google.cloud import bigquery
from typing import Union


# Page configuration
st.set_page_config(
    page_title="Weather Monitor Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_bq_client():
    return bigquery.Client(project="data-science-443020")

bq = get_bq_client()
TABLE = "data-science-443020.weather_monitor.sensor_readings"

# Fonction pour récupérer la dernière mesure
@st.cache_data(ttl=0)
def fetch_last_reading() -> Union[dict, None]:
    """
    Récupère la dernière ligne de sensor_readings depuis BigQuery.
    """
    sql = f"""
        SELECT
          timestamp,
          temperature,
          humidity,
          tvoc
        FROM `{TABLE}`
        ORDER BY timestamp DESC
        LIMIT 1
    """
    rows = list(bq.query(sql).result())
    if not rows:
        return None
    row = rows[0]
    return {
        "timestamp": row.timestamp.isoformat(),
        "temperature": row.temperature,
        "humidity": row.humidity,
        "tvoc": row.tvoc
    }

# Initialize data fetcher
@st.cache_resource
def get_data_fetcher():
    return DataFetcher()

data_fetcher = get_data_fetcher()

# Add custom CSS for better styling
st.markdown("""
<style>
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f0f0f0;
        margin: 0.5rem 0;
    }
    
    .weather-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .weather-card .stMetric {
        background-color: #f8f9fa;
        border: none;
        margin: 0.3rem;
    }
    
    .condition-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    
    .weather-icon {
        font-size: 3rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .last-update {
        color: #6c757d;
        font-size: 0.9rem;
        font-style: italic;
    }
    
    .presence-indicator {
        padding: 0.5rem;
        border-radius: 20px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .presence-detected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .presence-not-detected {
        background-color: #f8f9fa;
        color: #6c757d;
        border: 1px solid #dee2e6;
    }
    
    /* Ensure all content stays within the weather card */
    .weather-card > div[data-testid="stVerticalBlock"] {
        width: 100%;
    }
    
    .weather-card > div[data-testid="metric-container"] {
        background-color: #f8f9fa !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Simplified
st.sidebar.title("🌡️ Weather Monitor")
st.sidebar.markdown("---")

# Location selection only
location = st.sidebar.text_input("📍 Location", value="Lausanne,CH", key="location_input")

st.sidebar.markdown("---")
st.sidebar.markdown("### Actions")
if st.sidebar.button("🔄 Refresh Data", key="refresh_button"):
    st.cache_data.clear()
    st.rerun()

# Main dashboard
st.image("utils/stratos.jpg")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Current Conditions", "Forecast", "History"])

with tab1:
    st.header("Current Weather Conditions")
    
    # Create container with padding
    with st.container():
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            # Outdoor weather card with data in same block as title
            try:
                weather_data = data_fetcher.get_current_weather(location)
                if weather_data:
                    # Weather icon based on condition
                    weather_icons = {
                        "Clear": "☀️",
                        "Clouds": "☁️",
                        "Rain": "🌧️",
                        "Snow": "❄️",
                        "Thunderstorm": "⛈️",
                        "Drizzle": "🌦️",
                        "Mist": "🌫️",
                        "Fog": "🌫️"
                    }
                    
                    weather_icon = weather_icons.get(weather_data['weather'], "🌤️")
                    temp = f"{weather_data['temperature']:.1f}"
                    humidity = str(weather_data['humidity'])
                    pressure = str(weather_data['pressure'])
                    wind_speed = str(weather_data['wind_speed'])
                    clouds = str(weather_data['clouds'])
                    
                    st.markdown(f"""
                    <div class="weather-card">
                        <div class="condition-header">Outdoor Weather</div>
                        <div class="weather-icon">{weather_icon}</div>
                        
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 20px;">
                            <div style="text-align: center;">
                                <div style="font-size: 1.5em; font-weight: bold; color: #1f77b4;">{temp}°C</div>
                                <div style="font-size: 0.9em; color: #666;">Temperature</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 1.5em; font-weight: bold; color: #1f77b4;">{humidity}%</div>
                                <div style="font-size: 0.9em; color: #666;">Humidity</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 1.5em; font-weight: bold; color: #1f77b4;">{pressure} hPa</div>
                                <div style="font-size: 0.9em; color: #666;">Pressure</div>
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px;">
                            <div style="text-align: center;">
                                <div style="font-size: 1.5em; font-weight: bold; color: #1f77b4;">{wind_speed} m/s</div>
                                <div style="font-size: 0.9em; color: #666;">Wind Speed</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 1.5em; font-weight: bold; color: #1f77b4;">{clouds}%</div>
                                <div style="font-size: 0.9em; color: #666;">Cloud Cover</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    st.markdown("""
                    <div class="weather-card">
                        <div class="condition-header">Outdoor Weather</div>
                        <div style="color: #ff4b4b; margin-top: 20px;">❌ Unable to fetch weather data</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                error_msg = str(e)
                st.markdown(f"""
                <div class="weather-card">
                    <div class="condition-header">Outdoor Weather</div>
                    <div style="color: #ff4b4b; margin-top: 20px;">❌ Error fetching weather data: {error_msg}</div>
                </div>
                """, unsafe_allow_html=True)


        
        with col2:
            # Indoor conditions with data in same block as title
            sensor_data = fetch_last_reading()
            if sensor_data:
                # Check humidity and prepare warning
                humidity_warning = ""
                if sensor_data['humidity'] < 40:
                    humidity_warning = '<div style="color: #ff6b35; font-size: 0.9em; margin-top: 10px; padding: 10px; background-color: #fff3cd; border-radius: 5px;">⚠️ Indoor humidity is below 40% – this might be too dry. Consider using a humidifier.</div>'
                
                # Prepare values
                indoor_temp = f"{sensor_data['temperature']:.1f}"
                indoor_humidity = str(sensor_data['humidity'])
                tvoc_value = f"{sensor_data['tvoc']:.1f}"
                
                st.markdown(f"""
                <div class="weather-card">
                    <div class="condition-header">Indoor Conditions</div>
                    <div class="weather-icon">🏠</div>
                    {humidity_warning}
                    
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 20px;">
                        <div style="text-align: center;">
                            <div style="font-size: 1.5em; font-weight: bold; color: #1f77b4;">{indoor_temp}°C</div>
                            <div style="font-size: 0.9em; color: #666;">Temperature</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.5em; font-weight: bold; color: #1f77b4;">{indoor_humidity}%</div>
                            <div style="font-size: 0.9em; color: #666;">Humidity</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.5em; font-weight: bold; color: #1f77b4;">{tvoc_value}</div>
                            <div style="font-size: 0.9em; color: #666;">TVOC</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                    
            else:
                st.markdown("""
                <div class="weather-card">
                    <div class="condition-header">Indoor Conditions</div>
                    <div class="weather-icon">🏠</div>
                    <div style="color: #ff6b35; margin-top: 20px; padding: 10px; background-color: #fff3cd; border-radius: 5px;">⚠️ No indoor sensor data available</div>
                </div>
                """, unsafe_allow_html=True)


with tab2:
    st.header("Weather Forecast")
    
    try:
        forecast_data = data_fetcher.get_forecast(location)
        
        if forecast_data and 'forecast' in forecast_data:
            df_forecast = pd.DataFrame(forecast_data['forecast'])
            df_forecast['timestamp'] = pd.to_datetime(df_forecast['timestamp'])
            
            # Temperature forecast
            st.subheader("Temperature Forecast")
            fig_forecast = px.line(
                df_forecast,
                x='timestamp',
                y='temperature',
                title='5-Day Temperature Forecast'
            )
            fig_forecast.update_layout(
                xaxis_title='Date',
                yaxis_title='Temperature (°C)',
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            fig_forecast.update_traces(
                line=dict(color='#3498db', width=3),
                hovertemplate='%{x|%b %d, %H:%M}<br>%{y:.1f}°C<extra></extra>'
            )
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            # Rain probability
            st.subheader("Rain Probability")
            fig_rain = px.bar(
                df_forecast,
                x='timestamp',
                y='rain_probability',
                title='5-Day Rain Probability'
            )
            fig_rain.update_layout(
                xaxis_title='Date',
                yaxis_title='Probability (%)',
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            fig_rain.update_traces(
                marker_color='#3498db',
                hovertemplate='%{x|%b %d, %H:%M}<br>%{y:.0f}%<extra></extra>'
            )
            st.plotly_chart(fig_rain, use_container_width=True)
            
            
        else:
            st.error("Unable to fetch forecast data")
            
    except Exception as e:
        st.error(f"Error fetching forecast: {str(e)}")
with tab3:
    st.header("Indoor Sensor History")

    @st.cache_data(ttl=600)
    def fetch_sensor_history():
        sql = f"""
            SELECT
            timestamp,
            temperature,
            humidity
            FROM `{TABLE}`
            ORDER BY timestamp DESC
            LIMIT 30
        """
        rows = bq.query(sql).to_dataframe()
        rows['timestamp'] = pd.to_datetime(rows['timestamp'])
        return rows.sort_values("timestamp")

    try:
        df_history = fetch_sensor_history()

        if not df_history.empty:
            # Température dans le temps
            st.subheader("Temperature Over Time")
            fig_temp = px.line(
                df_history,
                x='timestamp',
                y='temperature',
                labels={'timestamp': 'Date', 'temperature': 'Temperature (°C)'},
                title="Indoor Temperature History"
            )
            fig_temp.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_temp, use_container_width=True)

            # Humidité dans le temps
            st.subheader("Humidity Over Time")
            fig_hum = px.line(
                df_history,
                x='timestamp',
                y='humidity',
                labels={'timestamp': 'Date', 'humidity': 'Humidity (%)'},
                title="Indoor Humidity History"
            )
            fig_hum.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_hum, use_container_width=True)
        else:
            st.warning("⚠️ No historical data available")

    except Exception as e:
        st.error(f"❌ Error loading sensor history: {str(e)}")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #6c757d; padding: 1rem;">
    Stratos Dashboard - Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)
