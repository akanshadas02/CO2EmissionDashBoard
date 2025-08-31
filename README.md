# 🌍 CO₂ Emissions Monitoring Dashboard

A full-stack real-time **CO₂ Emissions Monitoring Dashboard** built with **Flask (backend)** and **React + Plotly.js (frontend)**.  
The system simulates monitoring stations across Rwanda, processes pollutant gas levels (SO₂, NO₂, CO), and visualizes real-time CO₂ emissions trends on an interactive dashboard.

Please Find the dataset and the model - .pkl file in the drive link: https://drive.google.com/drive/folders/1muz-pkp0DzX1aFgQ3Elkg2UkJUYKlcwP?usp=sharing

---

## 📌 Project Structure

```
co2-emissions-dashboard/
│
├── backend/                 # Flask API Server
│   ├── app.py               # Main Flask application
│   ├── requirements.txt     # Python dependencies  
│   └── emission_model_complete.pkl  # Pre-trained model (or mock model if unavailable)
│
├── frontend/                # React Dashboard  
│   ├── public/
│   │   └── index.html       # HTML template
│   ├── src/
│   │   ├── App.js           # Main React component
│   │   ├── CO2EmissionsDashboard.js  # Dashboard component
│   │   ├── index.js         # React entry point
│   │   ├── App.css          # Application styles
│   │   └── index.css        # Global styles + Tailwind
│   └── package.json         # Node.js dependencies
```

---

## ⚙️ How It Is Built

1. **Backend (Flask API)**
   - Runs a **Flask server** (`app.py`) that handles real-time emissions monitoring.
   - Loads a trained machine learning model (`emission_model_complete.pkl`) to predict CO₂ emissions.  
     If the model is missing, a **mock simulation** is used instead.
   - Provides REST API endpoints such as:
     - `/api/realtime-data` → Streams simulated sensor data in real time.
     - `/api/locations` → Returns metadata of all monitoring stations.
     - `/api/locations-geojson` → Provides data in GeoJSON format for map visualization.
     - `/api/predict` → Predicts CO₂ emissions given pollutants and location.

2. **Frontend (React + Plotly.js + TailwindCSS)**
   - Built with **React** and styled with **TailwindCSS**.
   - Uses **Plotly.js** for live charts and geospatial mapping.
   - Fetches live emissions data from the Flask backend (`localhost:5000`).
   - Displays:
     - 🌍 Interactive map of Rwanda with markers for monitoring stations.
     - 📊 Real-time charts for CO₂ trends and pollutant levels (SO₂, NO₂, CO).
     - 📡 Location cards summarizing current emission statistics.

3. **Data Flow**
   - The backend continuously simulates or predicts emission data.
   - Frontend fetches updates every **3 seconds**.
   - Users can **click map markers or cards** to view detailed analytics per station.

---

## 🚀 How to Run

### 1️⃣ Start the Backend (Flask)
```bash
cd backend
pip install -r requirements.txt
python app.py
```
- The backend runs on: `http://localhost:5000`

### 2️⃣ Start the Frontend (React)
```bash
cd frontend
npm install
npm start
```
- The frontend runs on: `http://localhost:3000`  
- It is **proxied** to the Flask API (`localhost:5000`) via `package.json`.

---

## 🖼️ Features

- 🌍 **Interactive Rwanda Map** – Visualizes stations & emission intensity with color-coded markers.  
- 📊 **Live Time-Series Charts** – Displays CO₂ trends and pollutant gas levels.  
- ⚡ **Real-Time Data Updates** – Refreshes every 3 seconds.  
- 🎨 **Dark Themed UI** – Styled with TailwindCSS & enhanced custom effects.  
- 🧪 **Pollutant Analysis** – Breaks down SO₂, NO₂, and CO concentrations.  
- 🔍 **Drill-Down Mode** – Click on a station to view detailed analytics.  

---

## 📜 License
This project is licensed under the **MIT License**.

---

👨‍💻 Developed by **CO₂ Monitoring Team**
