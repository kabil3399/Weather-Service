
# 🌦 Weather Service  

A Flask-based backend application that fetches, stores, and exports **48-hour weather data** (temperature & humidity) using the [Open-Meteo API](https://open-meteo.com/).  
The service supports:  
- 📡 Fetching real-time & past 2 days weather data  
- 📊 Exporting reports to **Excel** & **PDF**  
- 🗄 Data storage in **SQLite**  
- 🌍 CORS-enabled API for frontend integration  

---

## 📋 Prerequisites  

Before running this project, ensure you have the following installed:  

- [Python 3.9+](https://www.python.org/downloads/)  
- [pip](https://pip.pypa.io/en/stable/installation/)  
- [Virtual Environment (venv)](https://docs.python.org/3/library/venv.html)  

---

## ⚙️ Installation  

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/weather-service.git
   cd weather-service


2. **Create virtual environment**

   ```
   python -m venv venv
   ```

3. **Activate virtual environment**

   * On **Windows**

     ```
     venv\Scripts\activate
     ```
   * On **Linux/Mac**

     ```
     source venv/bin/activate
     ```

4. **Install dependencies**

   ```
   pip install -r requirements.txt
   ```

---

## ▶️ Running the Service

Run the Flask app using:

```
python WeatherService.py
```

By default, it runs on:

```
http://0.0.0.0:5000
```

---

## 🌐 API Endpoints

### 1. Get Weather Report (JSON)

Fetch weather data for last 48 hours.

```
GET /weather-report?lat={latitude}&lon={longitude}
```

Example:

```
/weather-report?lat=13.0827&lon=80.2707
```

---

### 2. Export Weather Data (Excel)

```
GET /export/excel
```

📥 Downloads `weather.xlsx`

---

### 3. Export Weather Data (PDF with Graph)

```
GET /export/pdf?lat={latitude}&lon={longitude}
```

📥 Downloads `weather_report.pdf`

---

## 📌 Example Output

* **JSON Weather Report**

```
[
  {
    "timestamp": "2025-08-25 12:00:00+05:30",
    "temperature": 29.5,
    "humidity": 70
  }
]
```

* **Excel** → `weather.xlsx`
* **PDF** → Includes line chart of **Temperature & Humidity** over time

---
---

## 🖥️ Frontend Demo  

To demonstrate how the API endpoints can be consumed, a simple **HTML + CSS + JavaScript** frontend is included in this project.  
This demo shows how weather data is fetched from the backend and displayed in the browser.  

### 🚀 Run the Frontend  
1. Make sure the Flask backend is running.  
2. Open the `index.html` file in your browser.  
3. You will see live weather data fetched via API.  

---

### 📸 Demo Screenshot  

![Weather Demo Screenshot](./assets/ss.png)  

 

---



## ✅ Conclusion

This project demonstrates a **complete weather reporting service** using Flask, SQLite, and Open-Meteo API with export functionality.
It can be easily integrated with frontend apps for dashboards or extended to include additional weather parameters.


