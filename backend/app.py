# Enhanced app.py with improved GeoJSON mapping support
from flask import Flask, jsonify, request
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import time
from datetime import datetime
import threading
import warnings
import os
import json
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

class RealTimeEmissionMonitor:
    def __init__(self, model_path='emission_model_complete.pkl', data_path='playground-series-s3e20'):
        """Initialize the real-time emission monitor"""
        self.data_path = data_path
        
        try:
            model_package = joblib.load(model_path)
            self.model = model_package['model']
            self.feature_names = model_package['feature_names']
            self.feature_defaults = model_package['feature_defaults']
            print("Model loaded successfully!")
            print(f"Total features: {len(self.feature_names)}")
        except FileNotFoundError:
            print("Model file not found. Creating mock model for demo.")
            self.model = None
            self.feature_names = []
            self.feature_defaults = {}
        
        # Load dataset locations
        self.locations = self._load_locations_from_json()
        print(f"Initialized monitor with {len(self.locations)} locations")
    
    def _load_locations_from_json(self):
        """Load locations from extracted_locations.json file"""
        try:
            # Try multiple possible paths
            possible_paths = [
                'extracted_locations.json',
                './extracted_locations.json',
                os.path.join(os.path.dirname(__file__), 'extracted_locations.json'),
                'playground-series-s3e20/extracted_locations.json'
            ]
            
            for json_path in possible_paths:
                if os.path.exists(json_path):
                    with open(json_path, 'r') as f:
                        locations = json.load(f)
                    print(f"✓ Loaded {len(locations)} locations from {json_path}")
                    
                    # Validate location data structure
                    for loc_key, loc_data in locations.items():
                        if 'lat' not in loc_data or 'lon' not in loc_data:
                            print(f"Warning: Invalid location data for {loc_key}")
                            continue
                    
                    return locations
            
            print("❌ extracted_locations.json not found in any expected location")
            return self._get_fallback_rwanda_locations()
            
        except Exception as e:
            print(f"❌ Error loading locations from JSON: {e}")
            return self._get_fallback_rwanda_locations()
    
    def _get_fallback_rwanda_locations(self):
        """Fallback Rwanda locations based on actual geographic distribution"""
        return {
            # Northern Rwanda
            'LOC_-1.047_29.698': {
                'lat': -1.047, 'lon': 29.698, 'type': 'urban', 
                'region': 'Northern Province (Musanze)', 'source': 'fallback'
            },
            'LOC_-1.204_29.987': {
                'lat': -1.204, 'lon': 29.987, 'type': 'urban', 
                'region': 'Northern Province (Byumba)', 'source': 'fallback'
            },
            
            # Central Rwanda (Kigali Area)
            'LOC_-1.882_29.883': {
                'lat': -1.882, 'lon': 29.883, 'type': 'urban', 
                'region': 'Kigali City Center', 'source': 'fallback'
            },
            'LOC_-1.956_30.128': {
                'lat': -1.956, 'lon': 30.128, 'type': 'industrial', 
                'region': 'Kigali Industrial Zone', 'source': 'fallback'
            },
            
            # Western Rwanda (Lake Kivu Region)
            'LOC_-1.678_29.238': {
                'lat': -1.678, 'lon': 29.238, 'type': 'coastal', 
                'region': 'Western Province (Gisenyi)', 'source': 'fallback'
            },
            'LOC_-2.285_29.339': {
                'lat': -2.285, 'lon': 29.339, 'type': 'coastal', 
                'region': 'Western Province (Kibuye)', 'source': 'fallback'
            },
            
            # Eastern Rwanda
            'LOC_-1.532_30.597': {
                'lat': -1.532, 'lon': 30.597, 'type': 'industrial', 
                'region': 'Eastern Province (Rwamagana)', 'source': 'fallback'
            },
            'LOC_-1.378_30.835': {
                'lat': -1.378, 'lon': 30.835, 'type': 'urban', 
                'region': 'Eastern Province (Kayonza)', 'source': 'fallback'
            },
            
            # Southern Rwanda
            'LOC_-2.451_30.471': {
                'lat': -2.451, 'lon': 30.471, 'type': 'industrial', 
                'region': 'Southern Province (Huye)', 'source': 'fallback'
            },
            'LOC_-2.598_29.756': {
                'lat': -2.598, 'lon': 29.756, 'type': 'urban', 
                'region': 'Southern Province (Nyamagabe)', 'source': 'fallback'
            },
            
            # Northwestern Region
            'LOC_-1.510_29.290': {
                'lat': -1.510, 'lon': 29.290, 'type': 'industrial', 
                'region': 'Northwestern Region (Rubavu)', 'source': 'fallback'
            },
            'LOC_-1.628_29.472': {
                'lat': -1.628, 'lon': 29.472, 'type': 'industrial', 
                'region': 'Northwestern Region (Rutsiro)', 'source': 'fallback'
            }
        }
    
    def get_locations(self):
        """Return all monitoring locations"""
        return self.locations
    
    def predict_emission(self, latitude, longitude, so2_density=None, no2_density=None, co_density=None, year=2023, week_no=None):
        """Predict emission and calculate CO2 equivalent"""
        
        if week_no is None:
            week_no = datetime.now().isocalendar()[1]
        
        if self.model is None:
            # Enhanced mock prediction with location-specific patterns
            base_emission = 30 + abs(latitude * 15) + abs(longitude * 8)
            
            # Add location type variations
            location_key = f"LOC_{latitude}_{longitude}"
            location_info = None
            
            # Find closest location
            min_distance = float('inf')
            for loc_key, loc_data in self.locations.items():
                distance = np.sqrt((loc_data['lat'] - latitude)**2 + (loc_data['lon'] - longitude)**2)
                if distance < min_distance:
                    min_distance = distance
                    location_info = loc_data
            
            if location_info:
                type_multipliers = {
                    'industrial': 1.5,
                    'urban': 1.0,
                    'coastal': 0.7
                }
                base_emission *= type_multipliers.get(location_info['type'], 1.0)
            
            # Add time-based variation
            current_hour = datetime.now().hour
            time_factor = 1.0 + 0.3 * np.sin(2 * np.pi * current_hour / 24)
            
            # Add gas density influence
            gas_influence = 1.0
            if so2_density: gas_influence += so2_density * 500000
            if no2_density: gas_influence += no2_density * 800000
            if co_density: gas_influence += co_density * 50
            
            emission = base_emission * time_factor * gas_influence + np.random.normal(0, base_emission * 0.2)
            emission = max(0, emission)
        else:
            # Real model prediction (when model is available)
            input_data = {}
            for feature in self.feature_names:
                input_data[feature] = self.feature_defaults[feature]
            
            input_data['latitude'] = latitude
            input_data['longitude'] = longitude
            input_data['year'] = year
            input_data['week_no'] = week_no
            
            if so2_density is not None:
                input_data['SulphurDioxide_SO2_column_number_density'] = so2_density
                so2_features = [f for f in self.feature_names if 'SulphurDioxide' in f]
                for feature in so2_features:
                    if 'roll_mean' in feature:
                        input_data[feature] = so2_density
            
            if no2_density is not None:
                input_data['NitrogenDioxide_NO2_column_number_density'] = no2_density
                no2_features = [f for f in self.feature_names if 'NitrogenDioxide' in f]
                for feature in no2_features:
                    if 'roll_mean' in feature:
                        input_data[feature] = no2_density
            
            if co_density is not None:
                input_data['CarbonMonoxide_CO_column_number_density'] = co_density
                co_features = [f for f in self.feature_names if 'CarbonMonoxide' in f]
                for feature in co_features:
                    if 'roll_mean' in feature:
                        input_data[feature] = co_density
            
            df = pd.DataFrame([input_data])
            df = df[self.feature_names]
            emission = self.model.predict(df)[0]
        
        # Enhanced CO2 equivalent calculation
        co2_equivalent = 0
        if so2_density: co2_equivalent += so2_density * 2000000  # SO2 to CO2 conversion factor
        if no2_density: co2_equivalent += no2_density * 3100000  # NO2 to CO2 conversion factor
        if co_density: co2_equivalent += co_density * 2300       # CO to CO2 conversion factor
        
        return {
            'emission': float(emission),
            'co2_equivalent': float(co2_equivalent),
            'location': {'lat': latitude, 'lon': longitude},
            'timestamp': datetime.now().isoformat(),
            'gas_levels': {
                'SO2': float(so2_density) if so2_density else 0,
                'NO2': float(no2_density) if no2_density else 0,
                'CO': float(co_density) if co_density else 0
            }
        }

def simulate_sensor_data(location_type='urban', base_multiplier=1.0, location_lat=0, location_lon=0):
    """Enhanced sensor data simulation with location-specific patterns"""
    base_values = {
        'urban': {'so2': 0.00008, 'no2': 0.00004, 'co': 0.016},
        'industrial': {'so2': 0.00015, 'no2': 0.00008, 'co': 0.025},
        'coastal': {'so2': 0.00005, 'no2': 0.00002, 'co': 0.010}
    }
    
    base = base_values.get(location_type, base_values['urban'])
    
    # Add time-based variations (daily and weekly cycles)
    current_hour = datetime.now().hour
    current_day = datetime.now().weekday()
    
    # Daily cycle (higher during day, lower at night)
    daily_factor = 1.0 + 0.4 * np.sin(2 * np.pi * (current_hour - 6) / 24)
    
    # Weekly cycle (higher on weekdays for industrial/urban)
    weekly_factor = 1.0
    if location_type in ['industrial', 'urban']:
        weekly_factor = 1.2 if current_day < 5 else 0.8  # Weekday vs weekend
    
    # Location-specific geographical influence
    geo_factor = 1.0 + 0.1 * np.sin(location_lat * 2) + 0.1 * np.cos(location_lon * 2)
    
    total_factor = daily_factor * weekly_factor * geo_factor * base_multiplier
    
    return {
        'so2': max(0, np.random.normal(base['so2'] * total_factor, base['so2'] * 0.3)),
        'no2': max(0, np.random.normal(base['no2'] * total_factor, base['no2'] * 0.3)),
        'co': max(0, np.random.normal(base['co'] * total_factor, base['co'] * 0.3))
    }

# Initialize the monitor
monitor = RealTimeEmissionMonitor()

# Store real-time data
real_time_data = []
locations = monitor.get_locations()

def generate_real_time_data():
    """Enhanced background thread to generate realistic real-time data"""
    print("🔄 Starting real-time data generation...")
    
    while True:
        timestamp = datetime.now()
        
        # Generate data for all locations
        for location_name, location_info in locations.items():
            # Enhanced variation based on location properties
            coord_factor = 1.0 + 0.15 * np.sin(location_info['lat'] * 3) + 0.15 * np.cos(location_info['lon'] * 3)
            
            # Add random events (occasional spikes)
            event_factor = 1.0
            if np.random.random() < 0.05:  # 5% chance of event
                event_factor = 1.5 + np.random.random() * 1.0
            
            sensor_data = simulate_sensor_data(
                location_info['type'], 
                coord_factor * event_factor,
                location_info['lat'],
                location_info['lon']
            )
            
            result = monitor.predict_emission(
                latitude=location_info['lat'],
                longitude=location_info['lon'],
                so2_density=sensor_data['so2'],
                no2_density=sensor_data['no2'],
                co_density=sensor_data['co']
            )
            
            # Enhance result with location metadata
            result.update({
                'location_name': location_name,
                'location_type': location_info['type'],
                'region': location_info['region'],
                'source': location_info.get('source', 'unknown'),
                'data_quality': 'good' if event_factor < 1.3 else 'anomaly_detected'
            })
            
            # Store the data
            real_time_data.append(result)
            
            # Keep only recent data (last 3000 points for better analysis)
            if len(real_time_data) > 3000:
                real_time_data.pop(0)
        
        time.sleep(3)  # Update every 3 seconds

# Start background data generation
data_thread = threading.Thread(target=generate_real_time_data, daemon=True)
data_thread.start()

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Get all monitoring locations with enhanced metadata"""
    enhanced_locations = {}
    
    for location_name, location_info in locations.items():
        # Get recent data for this location
        recent_data = [d for d in real_time_data if d.get('location_name') == location_name]
        latest_data = recent_data[-1] if recent_data else None
        
        enhanced_locations[location_name] = {
            **location_info,
            'data_points': len(recent_data),
            'last_update': latest_data['timestamp'] if latest_data else None,
            'current_emission': latest_data['emission'] if latest_data else 0,
            'data_quality': latest_data.get('data_quality', 'unknown') if latest_data else 'no_data'
        }
    
    return jsonify(enhanced_locations)

@app.route('/api/locations-geojson', methods=['GET'])
def get_locations_geojson():
    """Get locations in enhanced GeoJSON format optimized for mapping"""
    features = []
    
    for location_name, location_info in locations.items():
        # Get latest data for this location
        location_data = [d for d in real_time_data if d.get('location_name') == location_name]
        latest_data = location_data[-1] if location_data else None
        
        if latest_data:
            emission = latest_data['emission']
            gas_levels = latest_data['gas_levels']
            timestamp = latest_data['timestamp']
            data_quality = latest_data.get('data_quality', 'unknown')
        else:
            emission = 0
            gas_levels = {'SO2': 0, 'NO2': 0, 'CO': 0}
            timestamp = datetime.now().isoformat()
            data_quality = 'no_data'
        
        # Enhanced status determination
        if emission > 100:
            status = "HIGH"
            color = "#dc2626"
            priority = 3
        elif emission > 50:
            status = "MEDIUM"
            color = "#ea580c"
            priority = 2
        else:
            status = "LOW"
            color = "#059669"
            priority = 1
        
        # Calculate air quality index based on gas levels
        aqi_so2 = (gas_levels['SO2'] * 1000000) / 0.075 * 100  # Simplified AQI calculation
        aqi_no2 = (gas_levels['NO2'] * 1000000) / 0.053 * 100
        aqi_co = (gas_levels['CO'] * 1000) / 9.0 * 100
        overall_aqi = max(aqi_so2, aqi_no2, aqi_co)
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [location_info['lon'], location_info['lat']]
            },
            "properties": {
                "location_name": location_name,
                "region": location_info['region'],
                "location_type": location_info['type'],
                "source": location_info.get('source', 'unknown'),
                "emission": round(emission, 2),
                "status": status,
                "color": color,
                "priority": priority,
                "gas_levels": gas_levels,
                "air_quality_index": round(overall_aqi, 1),
                "timestamp": timestamp,
                "data_quality": data_quality,
                "coordinates_formatted": f"{location_info['lat']:.4f}, {location_info['lon']:.4f}"
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "total_locations": len(features),
            "generation_time": datetime.now().isoformat(),
            "coordinate_system": "WGS84",
            "country": "Rwanda",
            "data_source": "CO2 Emissions Monitoring Network"
        }
    }
    
    return jsonify(geojson)

@app.route('/api/predict', methods=['POST'])
def predict_single():
    """Get prediction for a single location with validation"""
    data = request.json
    
    # Validate input coordinates
    lat = data.get('latitude')
    lon = data.get('longitude')
    
    if lat is None or lon is None:
        return jsonify({'error': 'Latitude and longitude are required'}), 400
    
    # Check if coordinates are within Rwanda bounds (approximate)
    if not (-2.8 <= lat <= -1.0 and 28.8 <= lon <= 30.9):
        return jsonify({'warning': 'Coordinates appear to be outside Rwanda boundaries'}), 200
    
    result = monitor.predict_emission(
        latitude=lat,
        longitude=lon,
        so2_density=data.get('so2_density'),
        no2_density=data.get('no2_density'),
        co_density=data.get('co_density')
    )
    
    return jsonify(result)

@app.route('/api/realtime-data', methods=['GET'])
def get_realtime_data():
    """Get enhanced real-time data with filtering options"""
    location_name = request.args.get('location')
    limit = request.args.get('limit', 100, type=int)
    
    if location_name:
        # Filter data for specific location
        location_data = [d for d in real_time_data if d.get('location_name') == location_name]
        recent_data = location_data[-limit:] if len(location_data) > limit else location_data
    else:
        # Get recent data for all locations
        recent_data = real_time_data[-limit:] if len(real_time_data) > limit else real_time_data
    
    return jsonify({
        'data': recent_data,
        'total_points': len(recent_data),
        'time_range': {
            'start': recent_data[0]['timestamp'] if recent_data else None,
            'end': recent_data[-1]['timestamp'] if recent_data else None
        }
    })

@app.route('/api/location-data/<location_name>', methods=['GET'])
def get_location_data(location_name):
    """Get enhanced detailed data for a specific location"""
    location_data = [d for d in real_time_data if d.get('location_name') == location_name]
    recent_data = location_data[-50:] if len(location_data) > 50 else location_data
    
    if not recent_data:
        return jsonify({'error': 'No data found for location'}), 404
    
    # Enhanced analytics
    latest = recent_data[-1] if recent_data else {}
    
    if len(recent_data) > 1:
        emissions = [d['emission'] for d in recent_data]
        so2_levels = [d['gas_levels']['SO2'] for d in recent_data]
        no2_levels = [d['gas_levels']['NO2'] for d in recent_data]
        co_levels = [d['gas_levels']['CO'] for d in recent_data]
        timestamps = [d['timestamp'] for d in recent_data]
        
        # Calculate trends
        emission_trend = 'stable'
        if len(emissions) >= 10:
            recent_avg = np.mean(emissions[-5:])
            older_avg = np.mean(emissions[-10:-5])
            if recent_avg > older_avg * 1.1:
                emission_trend = 'increasing'
            elif recent_avg < older_avg * 0.9:
                emission_trend = 'decreasing'
        
        response = {
            'location_name': location_name,
            'location_info': locations.get(location_name, {}),
            'current': latest,
            'trends': {
                'timestamps': timestamps,
                'emissions': emissions,
                'so2_levels': so2_levels,
                'no2_levels': no2_levels,
                'co_levels': co_levels,
                'emission_trend': emission_trend
            },
            'statistics': {
                'avg_emission': float(np.mean(emissions)),
                'max_emission': float(np.max(emissions)),
                'min_emission': float(np.min(emissions)),
                'std_emission': float(np.std(emissions)),
                'avg_so2': float(np.mean(so2_levels)),
                'avg_no2': float(np.mean(no2_levels)),
                'avg_co': float(np.mean(co_levels)),
                'data_quality_score': len([d for d in recent_data if d.get('data_quality') == 'good']) / len(recent_data)
            },
            'data_summary': {
                'total_readings': len(recent_data),
                'time_span_hours': (datetime.fromisoformat(timestamps[-1].replace('Z', '+00:00')) - 
                                  datetime.fromisoformat(timestamps[0].replace('Z', '+00:00'))).total_seconds() / 3600
            }
        }
    else:
        response = {
            'location_name': location_name,
            'location_info': locations.get(location_name, {}),
            'current': latest,
            'trends': {},
            'statistics': {},
            'data_summary': {'total_readings': len(recent_data)}
        }
    
    return jsonify(response)

@app.route('/api/current-status', methods=['GET'])
def get_current_status():
    """Get enhanced current status for all locations"""
    current_status = {}
    
    # Get latest data point for each location
    for location_name, location_info in locations.items():
        location_data = [d for d in real_time_data if d.get('location_name') == location_name]
        if location_data:
            latest = location_data[-1]
            emission = latest['emission']
            
            # Enhanced status classification
            if emission > 100:
                status = "HIGH"
                color = "red"
                alert_level = 3
            elif emission > 50:
                status = "MEDIUM" 
                color = "orange"
                alert_level = 2
            else:
                status = "LOW"
                color = "green"
                alert_level = 1
            
            # Calculate data freshness
            time_diff = (datetime.now() - datetime.fromisoformat(latest['timestamp'].replace('Z', '+00:00'))).total_seconds()
            data_freshness = 'fresh' if time_diff < 30 else 'stale' if time_diff < 300 else 'very_stale'
            
            current_status[location_name] = {
                'emission': round(emission, 2),
                'status': status,
                'color': color,
                'alert_level': alert_level,
                'timestamp': latest['timestamp'],
                'gas_levels': latest['gas_levels'],
                'location': latest['location'],
                'region': latest.get('region', 'Unknown'),
                'location_type': latest.get('location_type', 'unknown'),
                'source': latest.get('source', 'unknown'),
                'data_quality': latest.get('data_quality', 'unknown'),
                'data_freshness': data_freshness,
                'coordinates_string': f"{latest['location']['lat']:.4f}, {latest['location']['lon']:.4f}"
            }
    
    return jsonify(current_status)

@app.route('/api/rwanda-bounds', methods=['GET'])
def get_rwanda_bounds():
    """Get enhanced Rwanda geographical bounds with location statistics"""
    if not locations:
        return jsonify({
            'center': {'lat': -1.9, 'lon': 30.0},
            'bounds': [[-2.8, 28.8], [-1.0, 30.9]],
            'zoom_level': 6
        })
    
    lats = [loc['lat'] for loc in locations.values()]
    lons = [loc['lon'] for loc in locations.values()]
    
    # Calculate optimal center and bounds
    center_lat = (min(lats) + max(lats)) / 2
    center_lon = (min(lons) + max(lons)) / 2
    
    # Calculate optimal zoom level based on coordinate spread
    lat_range = max(lats) - min(lats)
    lon_range = max(lons) - min(lons)
    max_range = max(lat_range, lon_range)
    
    if max_range > 2.0:
        zoom_level = 6
    elif max_range > 1.0:
        zoom_level = 7
    else:
        zoom_level = 8
    
    return jsonify({
        'center': {'lat': center_lat, 'lon': center_lon},
        'bounds': [
            [min(lats) - 0.1, min(lons) - 0.1], 
            [max(lats) + 0.1, max(lons) + 0.1]
        ],
        'coordinate_range': {
            'lat_min': min(lats),
            'lat_max': max(lats),
            'lon_min': min(lons),
            'lon_max': max(lons),
            'lat_center': center_lat,
            'lon_center': center_lon
        },
        'zoom_level': zoom_level,
        'total_locations': len(locations),
        'geographic_coverage': {
            'lat_span': lat_range,
            'lon_span': lon_range,
            'area_coverage': f"{lat_range * lon_range:.4f} square degrees"
        }
    })

@app.route('/api/eda-data', methods=['GET'])
def get_eda_data():
    """Get enhanced data for EDA visualizations"""
    np.random.seed(42)
    
    # Enhanced emission trends using actual location data
    dates = pd.date_range(start='2019-01-01', end='2023-12-31', freq='W')
    emission_trends = []
    
    # Use actual location data for more realistic trends
    for date in dates[-52:]:  # Last year of data
        for location_name, location_info in locations.items():
            base_emission = {
                'industrial': 90,
                'urban': 55,
                'coastal': 35
            }.get(location_info['type'], 55)
            
            # Enhanced geographical and temporal factors
            coord_factor = 1.0 + 0.15 * np.sin(location_info['lat'] * 2) + 0.15 * np.cos(location_info['lon'] * 2)
            seasonal_factor = 1 + 0.4 * np.sin(2 * np.pi * date.dayofyear / 365)
            weekly_factor = 1.2 if date.weekday() < 5 else 0.8  # Weekday vs weekend
            
            emission = base_emission * seasonal_factor * coord_factor * weekly_factor + np.random.normal(0, 12)
            
            emission_trends.append({
                'date': date.isoformat(),
                'location': location_name,
                'emission': max(0, emission),
                'type': location_info['type'],
                'region': location_info['region'],
                'coordinates': [location_info['lat'], location_info['lon']]
            })
    
    # Enhanced correlation data from EDA analysis
    correlation_data = {
        'features': ['longitude', 'aerosol_height', 'surface_albedo', 'CO_density', 'NO2_density', 'SO2_density'],
        'correlations': [0.103, 0.069, 0.047, 0.041, 0.033, 0.028]
    }
    
    # Enhanced distribution data
    if real_time_data:
        emissions = [d['emission'] for d in real_time_data[-2000:]]  # Last 2000 points
        distribution_data = emissions
    else:
        # Generate realistic distribution based on Rwanda data patterns
        distribution_data = np.concatenate([
            np.random.lognormal(mean=3.2, sigma=1.1, size=700),  # Main distribution
            np.random.lognormal(mean=4.2, sigma=0.8, size=200),  # Industrial peaks
            np.random.lognormal(mean=2.8, sigma=1.3, size=100)   # Low emission areas
        ]).tolist()
    
    # Location summary with enhanced metrics
    location_types = {}
    regions = {}
    sources = {}
    
    for loc_data in locations.values():
        location_types[loc_data['type']] = location_types.get(loc_data['type'], 0) + 1
        regions[loc_data['region']] = regions.get(loc_data['region'], 0) + 1
        sources[loc_data.get('source', 'unknown')] = sources.get(loc_data.get('source', 'unknown'), 0) + 1
    
    return jsonify({
        'emission_trends': emission_trends,
        'correlation_data': correlation_data,
        'distribution_data': distribution_data,
        'location_summary': {
            'total_locations': len(locations),
            'location_types': location_types,
            'regions': regions,
            'data_sources': sources
        },
        'data_quality_metrics': {
            'total_data_points': len(real_time_data),
            'active_locations': len([loc for loc in locations.keys() if any(d.get('location_name') == loc for d in real_time_data[-100:])]),
            'update_frequency': '3 seconds',
            'coverage_area': 'Rwanda'
        }
    })

@app.route('/api/export-data', methods=['GET'])
def export_data():
    """Export current data in various formats"""
    export_format = request.args.get('format', 'json')
    
    # Prepare export data
    export_data = {
        'metadata': {
            'export_time': datetime.now().isoformat(),
            'total_locations': len(locations),
            'total_data_points': len(real_time_data),
            'country': 'Rwanda',
            'coordinate_system': 'WGS84'
        },
        'locations': locations,
        'current_status': get_current_status().get_json(),
        'recent_data': real_time_data[-500:] if len(real_time_data) > 500 else real_time_data
    }
    
    if export_format == 'geojson':
        return get_locations_geojson()
    else:
        return jsonify(export_data)

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check with system status"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'locations_loaded': len(locations),
        'data_points_collected': len(real_time_data),
        'model_status': 'loaded' if monitor.model else 'mock_mode',
        'last_data_update': real_time_data[-1]['timestamp'] if real_time_data else 'no_data',
        'system_info': {
            'python_backend': 'Flask',
            'data_update_interval': '3 seconds',
            'max_stored_points': 3000
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Enhanced Flask CO2 Monitoring Server...")
    print("=" * 60)
    print("📍 Rwanda CO2 Emissions Real-time Monitoring Dashboard")
    print("=" * 60)
    print("Available API endpoints:")
    print("  GET  /api/health                    - System health check")
    print("  GET  /api/locations                 - All monitoring locations")
    print("  GET  /api/locations-geojson         - Locations in GeoJSON format")
    print("  GET  /api/rwanda-bounds             - Rwanda geographical bounds")
    print("  POST /api/predict                   - Single location prediction")
    print("  GET  /api/realtime-data             - Real-time data stream")
    print("  GET  /api/location-data/<location>  - Detailed location analysis")
    print("  GET  /api/current-status            - Current status overview")
    print("  GET  /api/eda-data                  - EDA visualization data")
    print("  GET  /api/export-data               - Data export endpoint")
    print("=" * 60)
    print(f"📊 Monitoring {len(locations)} locations across Rwanda")
    print("🔄 Real-time data generation active")
    print("🌐 CORS enabled for frontend integration")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)