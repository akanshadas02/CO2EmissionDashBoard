# import joblib
# import pandas as pd
# import numpy as np
# import warnings
# import time
# from datetime import datetime
# import random

# warnings.filterwarnings('ignore')

# class SimplePredictor:
#     def __init__(self, model_path='emission_model_complete.pkl'):
#         """Load the saved model"""
#         try:
#             model_package = joblib.load(model_path)
#             self.model = model_package['model']
#             self.feature_names = model_package['feature_names']
#             self.feature_defaults = model_package['feature_defaults']
#             print(f"Model loaded successfully! Features: {len(self.feature_names)}")
#         except FileNotFoundError:
#             print("Model file not found. Please train the model first.")
#             raise
    
#     def predict_emission(self, latitude, longitude, so2_density=None, no2_density=None, co_density=None, year=2023, week_no=25):
#         """Predict emission using key parameters"""
#         input_data = {}
        
#         # Fill all features with defaults first
#         for feature in self.feature_names:
#             input_data[feature] = self.feature_defaults[feature]
        
#         # Update with provided values
#         input_data['latitude'] = latitude
#         input_data['longitude'] = longitude
#         input_data['year'] = year
#         input_data['week_no'] = week_no
        
#         # Update gas densities if provided
#         if so2_density is not None:
#             input_data['SulphurDioxide_SO2_column_number_density'] = so2_density
#             so2_features = [f for f in self.feature_names if 'SulphurDioxide' in f]
#             for feature in so2_features:
#                 if 'roll_mean' in feature:
#                     input_data[feature] = so2_density
        
#         if no2_density is not None:
#             input_data['NitrogenDioxide_NO2_column_number_density'] = no2_density
#             no2_features = [f for f in self.feature_names if 'NitrogenDioxide' in f]
#             for feature in no2_features:
#                 if 'roll_mean' in feature:
#                     input_data[feature] = no2_density
        
#         if co_density is not None:
#             input_data['CarbonMonoxide_CO_column_number_density'] = co_density
#             co_features = [f for f in self.feature_names if 'CarbonMonoxide' in f]
#             for feature in co_features:
#                 if 'roll_mean' in feature:
#                     input_data[feature] = co_density
        
#         # Convert to DataFrame and predict
#         df = pd.DataFrame([input_data])
#         df = df[self.feature_names]
#         prediction = self.model.predict(df)[0]
#         return prediction

# class RealtimeEmissionMonitor:
#     def __init__(self, model_path='emission_model_complete.pkl'):
#         self.predictor = SimplePredictor(model_path)
        
#         # Suggested locations based on major cities and industrial areas
#         self.locations = [
#             # Major African Cities (Industrial/Urban Areas)
#             {"name": "Lagos, Nigeria", "lat": 6.5244, "lon": 3.3792, "type": "Industrial"},
#             {"name": "Cairo, Egypt", "lat": 30.0444, "lon": 31.2357, "type": "Urban"},
#             {"name": "Johannesburg, SA", "lat": -26.2041, "lon": 28.0473, "type": "Industrial"},
#             {"name": "Nairobi, Kenya", "lat": -1.2921, "lon": 36.8219, "type": "Urban"},
#             {"name": "Casablanca, Morocco", "lat": 33.5731, "lon": -7.5898, "type": "Industrial"},
            
#             # Asian Industrial Centers
#             {"name": "Mumbai, India", "lat": 19.0760, "lon": 72.8777, "type": "Industrial"},
#             {"name": "Beijing, China", "lat": 39.9042, "lon": 116.4074, "type": "Industrial"},
#             {"name": "Tokyo, Japan", "lat": 35.6762, "lon": 139.6503, "type": "Urban"},
#             {"name": "Bangkok, Thailand", "lat": 13.7563, "lon": 100.5018, "type": "Urban"},
#             {"name": "Jakarta, Indonesia", "lat": -6.2088, "lon": 106.8456, "type": "Industrial"},
            
#             # European Cities
#             {"name": "London, UK", "lat": 51.5074, "lon": -0.1278, "type": "Urban"},
#             {"name": "Berlin, Germany", "lat": 52.5200, "lon": 13.4050, "type": "Urban"},
#             {"name": "Milan, Italy", "lat": 45.4642, "lon": 9.1900, "type": "Industrial"},
            
#             # American Cities
#             {"name": "Los Angeles, USA", "lat": 34.0522, "lon": -118.2437, "type": "Industrial"},
#             {"name": "Mexico City, Mexico", "lat": 19.4326, "lon": -99.1332, "type": "Urban"},
#             {"name": "São Paulo, Brazil", "lat": -23.5558, "lon": -46.6396, "type": "Industrial"},
            
#             # Remote/Clean Areas (for comparison)
#             {"name": "Rural Montana, USA", "lat": 47.0527, "lon": -109.6333, "type": "Rural"},
#             {"name": "Norwegian Coast", "lat": 69.6492, "lon": 18.9553, "type": "Clean"},
#             {"name": "Amazon Basin", "lat": -3.4653, "lon": -62.2159, "type": "Clean"}
#         ]
    
#     def generate_realistic_sensor_data(self, location_type="Urban"):
#         """Generate realistic sensor data based on location type"""
        
#         # Base values and variations by location type
#         sensor_profiles = {
#             "Industrial": {
#                 "so2": {"mean": 0.00015, "std": 0.00008},
#                 "no2": {"mean": 0.00008, "std": 0.00004},
#                 "co": {"mean": 0.025, "std": 0.008}
#             },
#             "Urban": {
#                 "so2": {"mean": 0.00010, "std": 0.00005},
#                 "no2": {"mean": 0.00006, "std": 0.00003},
#                 "co": {"mean": 0.020, "std": 0.006}
#             },
#             "Rural": {
#                 "so2": {"mean": 0.00004, "std": 0.00002},
#                 "no2": {"mean": 0.00002, "std": 0.00001},
#                 "co": {"mean": 0.012, "std": 0.003}
#             },
#             "Clean": {
#                 "so2": {"mean": 0.00002, "std": 0.00001},
#                 "no2": {"mean": 0.00001, "std": 0.000005},
#                 "co": {"mean": 0.008, "std": 0.002}
#             }
#         }
        
#         profile = sensor_profiles.get(location_type, sensor_profiles["Urban"])
        
#         # Add daily and weekly variations
#         hour = datetime.now().hour
#         day_factor = 1.5 if 6 <= hour <= 18 else 0.8  # Higher during day
        
#         return {
#             "so2": max(0, np.random.normal(profile["so2"]["mean"] * day_factor, profile["so2"]["std"])),
#             "no2": max(0, np.random.normal(profile["no2"]["mean"] * day_factor, profile["no2"]["std"])),
#             "co": max(0, np.random.normal(profile["co"]["mean"] * day_factor, profile["co"]["std"]))
#         }
    
#     def get_emission_status(self, emission_value):
#         """Determine emission status and color"""
#         if emission_value > 100:
#             return "HIGH", "RED"
#         elif emission_value > 50:
#             return "MEDIUM", "YELLOW"
#         else:
#             return "LOW", "GREEN"
    
#     def run_realtime_monitoring(self, interval_seconds=3, duration_minutes=5):
#         """Run real-time emission monitoring"""
#         print("=" * 80)
#         print("REAL-TIME EMISSION MONITORING SYSTEM")
#         print("=" * 80)
#         print(f"Monitoring Duration: {duration_minutes} minutes")
#         print(f"Update Interval: {interval_seconds} seconds")
#         print("Press Ctrl+C to stop early")
#         print("=" * 80)
        
#         start_time = time.time()
#         end_time = start_time + (duration_minutes * 60)
#         iteration = 1
        
#         try:
#             while time.time() < end_time:
#                 # Select random location
#                 location = random.choice(self.locations)
                
#                 # Generate realistic sensor data
#                 sensor_data = self.generate_realistic_sensor_data(location["type"])
                
#                 # Make prediction
#                 prediction_start = time.time()
#                 emission = self.predictor.predict_emission(
#                     latitude=location["lat"],
#                     longitude=location["lon"],
#                     so2_density=sensor_data["so2"],
#                     no2_density=sensor_data["no2"],
#                     co_density=sensor_data["co"],
#                     week_no=datetime.now().isocalendar()[1]
#                 )
#                 prediction_time = (time.time() - prediction_start) * 1000
                
#                 # Get status
#                 status, color = self.get_emission_status(emission)
                
#                 # Display results
#                 timestamp = datetime.now().strftime("%H:%M:%S")
#                 print(f"[{iteration:3d}] {timestamp} | {location['name']:18} | "
#                       f"Emission: {emission:8.4f} ({status:6}) | "
#                       f"SO2: {sensor_data['so2']:.6f} | "
#                       f"NO2: {sensor_data['no2']:.6f} | "
#                       f"CO: {sensor_data['co']:.6f} | "
#                       f"Pred: {prediction_time:.1f}ms")
                
#                 iteration += 1
#                 time.sleep(interval_seconds)
                
#         except KeyboardInterrupt:
#             print(f"\nMonitoring stopped by user after {iteration-1} readings.")
        
#         print("=" * 80)
#         print("MONITORING COMPLETED")
#         print("=" * 80)
    
#     def run_location_comparison(self):
#         """Compare emissions across different location types"""
#         print("=" * 80)
#         print("LOCATION TYPE COMPARISON")
#         print("=" * 80)
        
#         # Group locations by type
#         location_types = {}
#         for loc in self.locations:
#             loc_type = loc["type"]
#             if loc_type not in location_types:
#                 location_types[loc_type] = []
#             location_types[loc_type].append(loc)
        
#         for loc_type, locations in location_types.items():
#             print(f"\n{loc_type.upper()} LOCATIONS:")
#             print("-" * 40)
            
#             for location in locations[:3]:  # Show max 3 per type
#                 sensor_data = self.generate_realistic_sensor_data(location["type"])
#                 emission = self.predictor.predict_emission(
#                     latitude=location["lat"],
#                     longitude=location["lon"],
#                     so2_density=sensor_data["so2"],
#                     no2_density=sensor_data["no2"],
#                     co_density=sensor_data["co"]
#                 )
#                 status, _ = self.get_emission_status(emission)
                
#                 print(f"{location['name']:20} | Emission: {emission:8.4f} ({status})")
    
#     def manual_prediction(self):
#         """Interactive manual prediction"""
#         print("=" * 80)
#         print("MANUAL EMISSION PREDICTION")
#         print("=" * 80)
        
#         try:
#             lat = float(input("Enter latitude: "))
#             lon = float(input("Enter longitude: "))
            
#             print("\nOptional sensor readings (press Enter to use defaults):")
#             so2_input = input("SO2 density (e.g., 0.0001): ")
#             no2_input = input("NO2 density (e.g., 0.00005): ")
#             co_input = input("CO density (e.g., 0.018): ")
            
#             so2 = float(so2_input) if so2_input else None
#             no2 = float(no2_input) if no2_input else None
#             co = float(co_input) if co_input else None
            
#             emission = self.predictor.predict_emission(lat, lon, so2, no2, co)
#             status, _ = self.get_emission_status(emission)
            
#             print(f"\nPREDICTION RESULT:")
#             print(f"Location: ({lat}, {lon})")
#             print(f"Predicted Emission: {emission:.6f}")
#             print(f"Status: {status}")
            
#         except ValueError:
#             print("Invalid input. Please enter numeric values.")

# def main():
#     """Main menu system"""
#     monitor = RealtimeEmissionMonitor()
    
#     while True:
#         print("\n" + "=" * 50)
#         print("EMISSION MONITORING SYSTEM")
#         print("=" * 50)
#         print("1. Run Real-time Monitoring (5 minutes)")
#         print("2. Compare Location Types")
#         print("3. Manual Prediction")
#         print("4. Quick Demo (30 seconds)")
#         print("5. Exit")
        
#         choice = input("\nSelect option (1-5): ")
        
#         if choice == "1":
#             monitor.run_realtime_monitoring(interval_seconds=3, duration_minutes=5)
#         elif choice == "2":
#             monitor.run_location_comparison()
#         elif choice == "3":
#             monitor.manual_prediction()
#         elif choice == "4":
#             monitor.run_realtime_monitoring(interval_seconds=2, duration_minutes=0.5)
#         elif choice == "5":
#             print("Exiting...")
#             break
#         else:
#             print("Invalid choice. Please select 1-5.")

# if __name__ == "__main__":
#     main()


import joblib
import pandas as pd
import numpy as np
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class RealTimeEmissionMonitor:
    def __init__(self, model_path='emission_model_complete.pkl'):
        """Initialize the real-time emission monitor"""
        try:
            model_package = joblib.load(model_path)
            self.model = model_package['model']
            self.feature_names = model_package['feature_names']
            self.feature_defaults = model_package['feature_defaults']
            
            print("Model loaded successfully!")
            print(f"Total features: {len(self.feature_names)}")
            
        except FileNotFoundError:
            print("Model file not found. Please train the model first.")
            raise
    
    def predict_emission(self, latitude, longitude, so2_density=None, no2_density=None, co_density=None, year=2023, week_no=None):
        """Predict emission and calculate CO2 equivalent"""
        
        if week_no is None:
            # Calculate current week number
            week_no = datetime.now().isocalendar()[1]
        
        # Create input data with all features
        input_data = {}
        
        # Fill all features with defaults first
        for feature in self.feature_names:
            input_data[feature] = self.feature_defaults[feature]
        
        # Update with provided values
        input_data['latitude'] = latitude
        input_data['longitude'] = longitude
        input_data['year'] = year
        input_data['week_no'] = week_no
        
        # Update gas densities if provided
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
        
        # Convert to DataFrame and predict
        df = pd.DataFrame([input_data])
        df = df[self.feature_names]
        
        emission = self.model.predict(df)[0]
        
        # Calculate CO2 equivalent (simplified conversion)
        # These are approximate conversion factors for demonstration
        co2_equivalent = 0
        if so2_density: co2_equivalent += so2_density * 2000000  # SO2 to CO2 equiv factor
        if no2_density: co2_equivalent += no2_density * 3100000  # NO2 to CO2 equiv factor  
        if co_density: co2_equivalent += co_density * 2300       # CO to CO2 equiv factor
        
        return {
            'emission': emission,
            'co2_equivalent': co2_equivalent,
            'location': (latitude, longitude),
            'timestamp': datetime.now(),
            'gas_levels': {
                'SO2': so2_density,
                'NO2': no2_density,
                'CO': co_density
            }
        }

def get_suggested_locations():
    """Return suggested latitude/longitude coordinates for different regions"""
    return {
        'East Africa - Nairobi': (-1.2921, 36.8219),
        'East Africa - Kampala': (0.3476, 32.5825),
        'East Africa - Kigali': (-1.9441, 30.0619),
        'East Africa - Addis Ababa': (9.1450, 40.4897),
        'East Africa - Dar es Salaam': (-6.7924, 39.2083),
        'West Africa - Lagos': (6.5244, 3.3792),
        'West Africa - Accra': (5.6037, -0.1870),
        'North Africa - Cairo': (30.0444, 31.2357),
        'South Africa - Cape Town': (-33.9249, 18.4241),
        'South Africa - Johannesburg': (-26.2041, 28.0473),
        'India - Mumbai': (19.0760, 72.8777),
        'India - Delhi': (28.7041, 77.1025),
        'China - Beijing': (39.9042, 116.4074),
        'Europe - London': (51.5074, -0.1278),
        'Europe - Berlin': (52.5200, 13.4050),
        'Americas - New York': (40.7128, -74.0060),
        'Americas - Los Angeles': (34.0522, -118.2437)
    }

def simulate_sensor_data():
    """Simulate realistic sensor data variations"""
    return {
        'so2': max(0, np.random.normal(0.00008, 0.00003)),  # Ensure non-negative
        'no2': max(0, np.random.normal(0.00004, 0.00001)),
        'co': max(0, np.random.normal(0.016, 0.004))
    }

def run_realtime_monitoring(monitor, location_name, lat, lon, duration_minutes=5, interval_seconds=3):
    """Run real-time monitoring for specified duration"""
    
    print(f"Starting real-time monitoring for {location_name}")
    print(f"Location: {lat:.4f}, {lon:.4f}")
    print(f"Duration: {duration_minutes} minutes, Interval: {interval_seconds} seconds")
    print("=" * 80)
    print(f"{'Time':<8} {'Emission':<12} {'CO2 Equiv':<12} {'SO2':<10} {'NO2':<10} {'CO':<10} {'Status'}")
    print("=" * 80)
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    measurements = []
    
    try:
        while time.time() < end_time:
            # Simulate sensor readings
            sensor_data = simulate_sensor_data()
            
            # Make prediction
            result = monitor.predict_emission(
                latitude=lat,
                longitude=lon,
                so2_density=sensor_data['so2'],
                no2_density=sensor_data['no2'],
                co_density=sensor_data['co']
            )
            
            # Store measurement
            measurements.append(result)
            
            # Determine status
            emission = result['emission']
            if emission > 100:
                status = "HIGH"
            elif emission > 50:
                status = "MEDIUM" 
            else:
                status = "LOW"
            
            # Display results
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"{current_time} {emission:11.4f} {result['co2_equivalent']:11.4f} "
                  f"{sensor_data['so2']:9.6f} {sensor_data['no2']:9.6f} "
                  f"{sensor_data['co']:9.6f} {status}")
            
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    
    # Summary statistics
    if measurements:
        emissions = [m['emission'] for m in measurements]
        co2_values = [m['co2_equivalent'] for m in measurements]
        
        print("\n" + "=" * 80)
        print("MONITORING SUMMARY")
        print("=" * 80)
        print(f"Total measurements: {len(measurements)}")
        print(f"Average emission: {np.mean(emissions):.4f}")
        print(f"Max emission: {np.max(emissions):.4f}")
        print(f"Min emission: {np.min(emissions):.4f}")
        print(f"Average CO2 equivalent: {np.mean(co2_values):.4f}")
        print(f"High emission periods: {sum(1 for e in emissions if e > 100)} measurements")

def main():
    """Main function to run the real-time monitoring system"""
    
    # Load the monitor
    try:
        monitor = RealTimeEmissionMonitor('emission_model_complete.pkl')
    except FileNotFoundError:
        print("Please ensure you have trained and saved the model first!")
        return
    
    # Show suggested locations
    print("\nSUGGESTED LOCATIONS:")
    print("=" * 50)
    locations = get_suggested_locations()
    for i, (name, (lat, lon)) in enumerate(locations.items(), 1):
        print(f"{i:2d}. {name:<25} ({lat:8.4f}, {lon:9.4f})")
    
    print("\n" + "=" * 50)
    
    # Let user choose location or use default
    print("\nChoose a location by number (1-17) or press Enter for default (Nairobi):")
    try:
        choice = input().strip()
        if choice:
            choice = int(choice) - 1
            location_items = list(locations.items())
            location_name, (lat, lon) = location_items[choice]
        else:
            location_name, (lat, lon) = "East Africa - Nairobi", (-1.2921, 36.8219)
    except (ValueError, IndexError):
        location_name, (lat, lon) = "East Africa - Nairobi", (-1.2921, 36.8219)
        print("Using default location: Nairobi")
    
    # Set monitoring parameters
    print(f"\nSelected location: {location_name}")
    print("Enter monitoring duration in minutes (default 2): ", end="")
    try:
        duration = float(input().strip() or "2")
    except ValueError:
        duration = 2
    
    print("Enter update interval in seconds (default 3): ", end="")
    try:
        interval = float(input().strip() or "3")
    except ValueError:
        interval = 3
    
    print(f"\nPress Ctrl+C to stop monitoring early")
    print("Starting in 3 seconds...")
    time.sleep(3)
    
    # Start monitoring
    run_realtime_monitoring(monitor, location_name, lat, lon, duration, interval)

if __name__ == "__main__":
    main()