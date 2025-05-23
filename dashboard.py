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
        width: 100%;
        box-sizing: border-box;
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
                    
                    # Create the complete HTML block
                    weather_html = f"""
                    <div class="weather-card">
                        <div class="condition-header">🌤️ Outdoor Weather</div>
                        <div style="text-align: center; font-size: 10em; margin: 20px 0;">{weather_icon}</div>
                        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
                            <div style="text-align: center; min-width: 90px;">
                                <div style="font-size: 1.8em; font-weight: bold; color: black;">{weather_data['temperature']:.1f}°C</div>
                                <div style="font-size: 1em; color: black;">Temperature</div>
                            </div>
                            <div style="text-align: center; min-width: 90px;">
                                <div style="font-size: 1.8em; font-weight: bold; color: black;">{weather_data['humidity']}%</div>
                                <div style="font-size: 1em; color: black;">Humidity</div>
                            </div>
                            <div style="text-align: center; min-width: 90px;">
                                <div style="font-size: 1.8em; font-weight: bold; color: black;">{weather_data['pressure']} hPa</div>
                                <div style="font-size: 1em; color: black;">Pressure</div>
                            </div>
                        </div>
                        <br>
                        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
                            <div style="text-align: center; min-width: 90px;">
                                <div style="font-size: 1.8em; font-weight: bold; color: black;">{weather_data['wind_speed']} m/s</div>
                                <div style="font-size: 1em; color: black;">Wind Speed</div>
                            </div>
                            <div style="text-align: center; min-width: 90px;">
                                <div style="font-size: 1.8em; font-weight: bold; color: black;">{weather_data['clouds']}%</div>
                                <div style="font-size: 1em; color: black;">Cloud Cover</div>
                            </div>
                        </div>
                    </div>
                    """
                    
                    st.markdown(weather_html, unsafe_allow_html=True)
                    
                else:
                    st.markdown("""
                    <div class="weather-card">
                        <div class="condition-header">🌤️ Outdoor Weather</div>
                        <div style="color: #ff4b4b; margin-top: 20px;">❌ Unable to fetch weather data</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.markdown(f"""
                <div class="weather-card">
                    <div class="condition-header">🌤️ Outdoor Weather</div>
                    <div style="color: #ff4b4b; margin-top: 20px;">❌ Error fetching weather data: {str(e)}</div>
                </div>
                """, unsafe_allow_html=True)


        with col2:
            # Indoor conditions with data in same block as title
            sensor_data = fetch_last_reading()
            if sensor_data:
                # Create warning if needed
                warning_html = ""
                if sensor_data['humidity'] < 40:
                    warning_html = """
                    <div style="color: #ff6b35; font-size: 0.9em; padding: 8px; background-color: #fff3cd; border-radius: 5px; margin: 10px 0;">
                        ⚠️ Indoor humidity is below 40% – this might be too dry. Consider using a humidifier.
                    </div>
                    """
                
                # Get air quality description based on TVOC value
                tvoc_value = sensor_data['tvoc']
                if tvoc_value <= 50:
                    air_quality_desc = 'Excellent air quality'
                    air_quality_color = '#28a745'  # Green
                elif 51 < tvoc_value < 100:
                    air_quality_desc = 'Good air quality'
                    air_quality_color = '#6f9e04'  # Light green
                elif 101 < tvoc_value < 150:
                    air_quality_desc = 'Moderate air quality'
                    air_quality_color = '#ffc107'  # Yellow
                elif 151 < tvoc_value < 200:
                    air_quality_desc = 'Bad air quality'
                    air_quality_color = '#fd7e14'  # Orange
                elif 201 < tvoc_value < 250:
                    air_quality_desc = 'Very bad air quality'
                    air_quality_color = '#dc3545'  # Red
                else:
                    air_quality_desc = 'You are going to die'
                    air_quality_color = '#6f42c1'  # Purple
                
                indoor_html = f"""
                <div class="weather-card">
                    <div class="condition-header">Indoor Weather</div>
                    <div style="text-align: center; font-size: 10em;">🏠</div>
                    <div style="text-align: center; font-size: 1em; color: grey; margin: 20px 0;">It is nice to be at home</div>
                    <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
                        <div style="text-align: center; min-width: 90px;">
                            <div style="font-size: 1.8em; font-weight: bold; color: black;">{sensor_data['temperature']:.1f}°C</div>
                            <div style="font-size: 1em; color: black;">Temperature</div>
                        </div>
                        <div style="text-align: center; min-width: 90px;">
                            <div style="font-size: 1.8em; font-weight: bold; color: black;">{sensor_data['humidity']}%</div>
                            <div style="font-size: 1em; color: black;">Humidity</div>
                        </div>
                        <div style="text-align: center; min-width: 90px;">
                            <div style="font-size: 1.8em; font-weight: bold; color: black;">{sensor_data['tvoc']:.1f}</div>
                            <div style="font-size: 1em; color: black;">TVOC</div>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 15px; padding: 10px; border-radius: 5px;">
                        <div style="font-size: 1.2em; font-weight: bold; color: {air_quality_color};">{air_quality_desc}</div>
                    </div>
                </div>
                """
                
                st.markdown(indoor_html, unsafe_allow_html=True)
                    
            else:
                st.markdown("""
                <div class="weather-card">
                    <div class="condition-header">Indoor Conditions</div>
                    <div style="color: #ff6b35; margin-top: 20px; padding: 10px; background-color: #fff3cd; border-radius: 5px;">
                        ⚠️ No indoor sensor data available
                    </div>
                </div>
                """, unsafe_allow_html=True)

with tab2:
    st.header("Weather Forecast")

    try:
        forecast_data = data_fetcher.get_forecast(location)

        if forecast_data and 'forecast' in forecast_data:
            df_forecast = pd.DataFrame(forecast_data['forecast'])
            df_forecast['timestamp'] = pd.to_datetime(df_forecast['timestamp'])

            # Icon map
            icon_map = {
                "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️", "Snow": "❄️",
                "Thunderstorm": "⛈️", "Drizzle": "🌦️", "Mist": "🌫️", "Fog": "🌫️"
            }
            df_forecast['icon'] = df_forecast['weather'].map(icon_map).fillna("🌤️")
            df_forecast['tooltip_temp'] = (
                df_forecast['timestamp'].dt.strftime("%a %b %d, %H:%M") +
                "<br>" +
                df_forecast['icon'] + " " +
                df_forecast['temperature'].round(1).astype(str) + "°C"
            )
            df_forecast['tooltip_rain'] = (
                df_forecast['timestamp'].dt.strftime("%a %b %d, %H:%M") +
                "<br>☔ " +
                df_forecast['rain_probability'].round(0).astype(str) + "%"
            )

            # Temperature forecast: red gradient
            fig_forecast = px.line(
                df_forecast,
                x='timestamp',
                y='temperature',
                title='5-Day Temperature Forecast'
            )
            fig_forecast.update_traces(
                line=dict(color='#e74c3c', width=4),
                mode='lines',
                fill='tonexty',
                fillcolor='rgba(231, 76, 60, 0.2)',
                hovertemplate=df_forecast['tooltip_temp']
            )
            fig_forecast.update_layout(
                xaxis_title='Date',
                yaxis_title='Temperature (°C)',
                height=420,
                font=dict(family="Segoe UI, sans-serif", size=14),
                plot_bgcolor='rgba(255,255,255,1)',
                paper_bgcolor='rgba(255,255,255,1)',
                margin=dict(t=50, l=50, r=50, b=50),
                title_x=0.02,
            )

            # Rain probability chart with gradient
            fig_rain = px.bar(
                df_forecast,
                x='timestamp',
                y='rain_probability',
                title='5-Day Rain Probability',
                color='rain_probability',
                color_continuous_scale=['#AED6F1', '#2E86C1']
            )
            fig_rain.update_traces(
                hovertemplate=df_forecast['tooltip_rain'],
                marker_line_color='rgba(0,0,0,0)',
            )
            fig_rain.update_layout(
                xaxis_title='Date',
                yaxis_title='Probability (%)',
                height=420,
                font=dict(family="Segoe UI, sans-serif", size=14),
                plot_bgcolor='rgba(255,255,255,1)',
                paper_bgcolor='rgba(255,255,255,1)',
                coloraxis_showscale=False,
                margin=dict(t=50, l=50, r=50, b=50),
                title_x=0.02,
            )

            # Display plots side by side
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig_forecast, use_container_width=True)
            with col2:
                st.plotly_chart(fig_rain, use_container_width=True)

            # Optional: Enable animation across time (uncomment below if needed)
            # fig_forecast.update_layout(updatemenus=[dict(type='buttons', showactive=False)])
            # fig_forecast.update_traces(mode='lines+markers')

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
            FROM {TABLE}
            ORDER BY timestamp DESC
            LIMIT 30
        """
        rows = bq.query(sql).to_dataframe()
        rows['timestamp'] = pd.to_datetime(rows['timestamp'])
        return rows.sort_values("timestamp")

    try:
        df_history = fetch_sensor_history()

        if not df_history.empty:
            # Download button
            csv = df_history.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name='sensor_history.csv', mime='text/csv')

            # Temperature Plot
            st.subheader("Temperature Over Time")
            fig_temp = px.line(
                df_history,
                x='timestamp',
                y='temperature',
                labels={'timestamp': 'Date', 'temperature': 'Temperature (°C)'},
                title="Indoor Temperature History"
            )
            fig_temp.add_traces([
                px.area(
                    df_history,
                    x='timestamp',
                    y='temperature'
                ).data[0]
            ])
            fig_temp.update_traces(
                line=dict(color='#e74c3c', width=4),
                mode='lines',
                fill='tonexty',
                fillcolor='rgba(231, 76, 60, 0.2)',
                hovertemplate=df_forecast['tooltip_temp']
            )
            fig_forecast.update_layout(
                xaxis_title='Date',
                yaxis_title='Temperature (°C)',
                height=420,
                font=dict(family="Segoe UI, sans-serif", size=14),
                plot_bgcolor='rgba(255,255,255,1)',
                paper_bgcolor='rgba(255,255,255,1)',
                margin=dict(t=50, l=50, r=50, b=50),
                title_x=0.02,
            )
            st.plotly_chart(fig_temp, use_container_width=True)

            # Humidity Plot
            st.subheader("Humidity Over Time")
            fig_hum = px.line(
                df_history,
                x='timestamp',
                y='humidity',
                labels={'timestamp': 'Date', 'humidity': 'Humidity (%)'},
                title="Indoor Humidity History"
            )
            fig_hum.update_traces(line=dict(color='rgba(52, 152, 219, 1)', width=3))
            fig_hum.update_layout(
                height=400,
                plot_bgcolor='rgba(255,255,255,0)',
                paper_bgcolor='rgba(255,255,255,0)',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.2)')
            )
            st.plotly_chart(fig_hum, use_container_width=True)
        else:
            st.warning("No historical data available")

    except Exception as e:
        st.error(f"Error loading sensor history: {str(e)}")




# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #6c757d; padding: 1rem;">
    Stratos Dashboard - Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)
