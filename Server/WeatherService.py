from flask import Flask, request, send_file, jsonify
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime, timedelta
import openmeteo_requests
import requests_cache
from retry_requests import retry
from weasyprint import HTML
import base64
from flask_cors import CORS
import pytz

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# -------------------- DATABASE SETUP --------------------
def init_db():
    """
    Initialize the SQLite database and create the weather table if it doesn't exist.
    """
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            timestamp TEXT PRIMARY KEY,
            temperature REAL,
            humidity REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -------------------- FETCH & STORE WEATHER DATA --------------------
def fetch_weather(lat, lon):
    """
    Fetch weather data from Open-Meteo API, filter for last 48 hours in IST,
    and store the result in the database.
    """
    # Setup caching and retry for API requests
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Prepare API request parameters
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "relative_humidity_2m"],
        "past_days": 2
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Extract hourly temperature and humidity data
    hourly = response.Hourly()
    temp = hourly.Variables(0).ValuesAsNumpy()
    humid = hourly.Variables(1).ValuesAsNumpy()

    # Create UTC timestamp index
    timestamps = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )

    # Convert timestamps to IST
    local_tz = pytz.timezone("Asia/Kolkata")
    timestamps_local = timestamps.tz_convert(local_tz)

    # Build DataFrame
    df = pd.DataFrame({
        "timestamp": timestamps_local,
        "temperature": temp,
        "humidity": humid
    })

    # Filter data for the last 48 hours (rounded to full hour)
    now = datetime.now(local_tz)
    end_time = now.replace(minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(hours=48)
    df_filtered = df[(df["timestamp"] >= start_time) & (df["timestamp"] <= end_time)]

    # Save filtered data to database
    conn = sqlite3.connect("weather.db")
    df_filtered.to_sql("weather", conn, if_exists="replace", index=False)
    conn.close()

    return df_filtered

# -------------------- WEATHER REPORT ENDPOINT --------------------
@app.get("/weather-report")
def weather_report():
    """
    API endpoint to fetch and return weather data as JSON.
    """
    lat = request.args.get("lat", type=float, default=47.37)
    lon = request.args.get("lon", type=float, default=8.55)
    df_filtered = fetch_weather(lat, lon)
    return jsonify(df_filtered.to_dict(orient="records"))

# -------------------- EXPORT TO EXCEL ENDPOINT --------------------
@app.get("/export/excel")
def export_excel():
    """
    API endpoint to export the last 48 hours of weather data as an Excel file.
    """
    conn = sqlite3.connect("weather.db")
    df = pd.read_sql("SELECT * FROM weather ORDER BY timestamp DESC LIMIT 48", conn)
    conn.close()
    # Rename columns for clarity
    df = df.rename(columns={"temperature": "temperature_2m", "humidity": "humidity_2m"})
    output = BytesIO()
    df.to_excel(output, index=False, sheet_name="Weather")
    output.seek(0)
    return send_file(output, download_name="weather.xlsx", as_attachment=True)

# -------------------- EXPORT TO PDF ENDPOINT --------------------
@app.get("/export/pdf")
def export_pdf():
    """
    API endpoint to export weather data and chart as a PDF report.
    """
    lat = request.args.get("lat", type=float, default=47.37)
    lon = request.args.get("lon", type=float, default=8.55)
    df = fetch_weather(lat, lon)

    # Plot temperature and humidity chart
    plt.figure(figsize=(10, 5))
    plt.plot(df["timestamp"], df["temperature"], label="Temperature (°C)", color="red")
    plt.plot(df["timestamp"], df["humidity"], label="Humidity (%)", color="blue")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    # Save chart as image and encode to base64
    img_buf = BytesIO()
    plt.savefig(img_buf, format="png")
    img_buf.seek(0)
    plt.close()
    img_base64 = base64.b64encode(img_buf.getvalue()).decode("utf-8")

    # Build HTML content for PDF
    html_content = f"""
    <html>
    <head>
        <style>
            @page {{
                size: A4;
                margin: 1cm;
            }}
            body {{ font-family: Arial, sans-serif; }}
            h1 {{ color: #333; }}
            .meta {{ margin-bottom: 20px; }}
            img.chart {{
                display: block;
                margin: 0 auto;
                width: 100%;
                max-width: 700px;
                height: auto;
            }}
        </style>
    </head>
    <body>
        <h1>Weather Report</h1>
        <div class="meta">
            <p><b>Location:</b> Lat: {lat}, Lon: {lon}</p>
            <p><b>Date Range:</b> Last 48 Hours</p>
        </div>
        <img class="chart" src="data:image/png;base64,{img_base64}"/>
    </body>
    </html>
    """
    pdf_file = BytesIO()
    HTML(string=html_content).write_pdf(pdf_file)
    pdf_file.seek(0)
    return send_file(pdf_file, download_name="weather_report.pdf", as_attachment=True)

# -------------------- MAIN ENTRY POINT --------------------
if __name__ == "__main__":
    # Start the Flask development server
    app.run(host="0.0.0.0", port=5000)
