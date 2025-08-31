import pandas as pd
import numpy as np
import os
import json

def extract_locations_from_dataset(data_path=r'C:\Users\ADMIN\Desktop\co2em\co2-emissions-dashboard\backend\playground-series-s3e20'):
    """
    Extract unique locations from train.csv and test.csv
    Returns a dictionary of locations suitable for the Flask app
    """
    
    locations = {}
    
    try:
        # Load train data
        train_path = os.path.join(data_path, 'train.csv')
        test_path = os.path.join(data_path, 'test.csv')
        
        print("Loading dataset files...")
        
        if os.path.exists(train_path):
            print("Loading train.csv...")
            train = pd.read_csv(train_path)
            train_coords = train.drop_duplicates(subset=['latitude', 'longitude'])[['latitude', 'longitude']]
            print(f"Found {len(train_coords)} unique locations in train.csv")
            
            for idx, row in train_coords.iterrows():
                lat, lon = round(row['latitude'], 3), round(row['longitude'], 3)
                location_key = f"LOC_{lat}_{lon}"
                
                locations[location_key] = {
                    'lat': lat,
                    'lon': lon,
                    'type': determine_location_type(lat, lon),
                    'region': get_region_name(lat, lon),
                    'source': 'train'
                }
        
        if os.path.exists(test_path):
            print("Loading test.csv...")
            test = pd.read_csv(test_path)
            test_coords = test.drop_duplicates(subset=['latitude', 'longitude'])[['latitude', 'longitude']]
            print(f"Found {len(test_coords)} unique locations in test.csv")
            
            for idx, row in test_coords.iterrows():
                lat, lon = round(row['latitude'], 3), round(row['longitude'], 3)
                location_key = f"LOC_{lat}_{lon}"
                
                if location_key not in locations:
                    locations[location_key] = {
                        'lat': lat,
                        'lon': lon,
                        'type': determine_location_type(lat, lon),
                        'region': get_region_name(lat, lon),
                        'source': 'test'
                    }
                else:
                    # Mark as present in both datasets
                    locations[location_key]['source'] = 'both'
        
        print(f"\nTotal unique locations extracted: {len(locations)}")
        
        # Print statistics
        location_types = {}
        regions = {}
        sources = {}
        
        for loc_data in locations.values():
            location_types[loc_data['type']] = location_types.get(loc_data['type'], 0) + 1
            regions[loc_data['region']] = regions.get(loc_data['region'], 0) + 1
            sources[loc_data['source']] = sources.get(loc_data['source'], 0) + 1
        
        print(f"\nLocation Types: {location_types}")
        print(f"Regions: {regions}")
        print(f"Data Sources: {sources}")
        
        # Sample coordinates bounds
        lats = [loc['lat'] for loc in locations.values()]
        lons = [loc['lon'] for loc in locations.values()]
        print(f"\nCoordinate Bounds:")
        print(f"Latitude: {min(lats):.3f} to {max(lats):.3f}")
        print(f"Longitude: {min(lons):.3f} to {max(lons):.3f}")
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return get_fallback_locations()
    
    return locations

def determine_location_type(lat, lon):
    """Determine location type based on coordinates (Rwanda context)"""
    # Based on Rwanda's geography and the EDA insights
    
    if lat > -1.0:  # Northern Rwanda (includes Kigali area)
        if lon > 30.0:
            return 'urban'  # Eastern urban areas
        else:
            return 'industrial'  # Northwestern industrial areas
    elif lat < -2.5:  # Southern Rwanda
        if lon > 30.0:
            return 'industrial'  # Southeastern industrial
        else:
            return 'coastal'  # Southwestern (near Lake Kivu)
    else:  # Central Rwanda
        if lon > 30.0:
            return 'urban'  # Central-east urban
        else:
            return 'urban'  # Central-west urban

def get_region_name(lat, lon):
    """Generate descriptive region names for Rwanda"""
    
    # Rwanda provinces and notable areas
    if lat > -1.0 and lon > 30.0:
        return "Eastern Province"
    elif lat > -1.0 and lon < 29.5:
        return "Northwestern Region"
    elif lat > -1.0:
        return "Northern Province" 
    elif lat < -2.5 and lon > 30.0:
        return "Southeastern Region"
    elif lat < -2.5 and lon < 29.5:
        return "Western Province (Lake Kivu)"
    elif lat < -2.5:
        return "Southern Province"
    elif lon > 30.0:
        return "Central-Eastern Region"
    elif lon < 29.5:
        return "Western Region"
    else:
        return "Central Rwanda (Kigali Area)"

def get_fallback_locations():
    """Fallback locations if dataset files are not found"""
    return {
        'LOC_-0.510_29.290': {
            'lat': -0.510, 'lon': 29.290, 'type': 'urban', 
            'region': 'Northwestern Region', 'source': 'fallback'
        },
        'LOC_-1.882_29.883': {
            'lat': -1.882, 'lon': 29.883, 'type': 'urban', 
            'region': 'Central Rwanda (Kigali Area)', 'source': 'fallback'
        },
        'LOC_-2.451_30.471': {
            'lat': -2.451, 'lon': 30.471, 'type': 'industrial', 
            'region': 'Southeastern Region', 'source': 'fallback'
        }
    }

def save_locations_to_json(locations, output_file='extracted_locations.json'):
    """Save extracted locations to JSON file for reference"""
    with open(output_file, 'w') as f:
        json.dump(locations, f, indent=2)
    print(f"Locations saved to {output_file}")

if __name__ == "__main__":
    # Extract locations
    print("Extracting locations from CO2 emissions dataset...")
    print("=" * 50)
    
    # Specify your data path here
    DATA_PATH = r'C:\Users\ADMIN\Desktop\co2em\co2-emissions-dashboard\backend\playground-series-s3e20'  # Adjust this path as needed
    
    locations = extract_locations_from_dataset(DATA_PATH)
    
    # Save to JSON file for reference
    save_locations_to_json(locations)
    
    print("\n" + "=" * 50)
    print("Location extraction completed!")
    print("You can now use these locations in your Flask app.")
    
    # Show first 5 locations as sample
    print(f"\nSample locations (showing first 5 out of {len(locations)}):")
    for i, (loc_key, loc_data) in enumerate(list(locations.items())[:5]):
        print(f"{i+1}. {loc_key}: {loc_data}")