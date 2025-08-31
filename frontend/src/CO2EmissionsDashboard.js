import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';

const CO2EmissionsDashboard = () => {
  const [realtimeData, setRealtimeData] = useState([]);
  const [currentStatus, setCurrentStatus] = useState({});
  const [locations, setLocations] = useState({});
  const [edaData, setEdaData] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [locationDetailData, setLocationDetailData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rwandaBounds, setRwandaBounds] = useState(null);
  const [mapView, setMapView] = useState('emissions'); // 'emissions' or 'gas_levels'

  // Fetch data from Flask API
  const fetchData = async () => {
    try {
      const [realtimeRes, statusRes, locationsRes, boundsRes] = await Promise.all([
        fetch('http://localhost:5000/api/realtime-data'),
        fetch('http://localhost:5000/api/current-status'),
        fetch('http://localhost:5000/api/locations'),
        fetch('http://localhost:5000/api/rwanda-bounds')
      ]);

      const realtimeData = await realtimeRes.json();
      const statusData = await statusRes.json();
      const locationsData = await locationsRes.json();
      const boundsData = await boundsRes.json();

      // Fix: Extract the data array from the response object
      setRealtimeData(Array.isArray(realtimeData) ? realtimeData : (realtimeData.data || []));
      setCurrentStatus(statusData || {});
      setLocations(locationsData || {});
      setRwandaBounds(boundsData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      // Set empty arrays/objects on error to prevent further errors
      setRealtimeData([]);
      setCurrentStatus({});
      setLocations({});
      setLoading(false);
    }
  };

  // Fetch EDA data
  const fetchEdaData = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/eda-data');
      const data = await res.json();
      setEdaData(data);
    } catch (error) {
      console.error('Error fetching EDA data:', error);
      setEdaData(null);
    }
  };

  // Fetch detailed data for selected location
  const fetchLocationData = async (locationName) => {
    try {
      const res = await fetch(`http://localhost:5000/api/location-data/${locationName}`);
      const data = await res.json();
      setLocationDetailData(data);
    } catch (error) {
      console.error('Error fetching location data:', error);
      setLocationDetailData(null);
    }
  };

  useEffect(() => {
    fetchData();
    fetchEdaData();
    
    // Update data every 3 seconds
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedLocation) {
      fetchLocationData(selectedLocation);
      // Update location data every 3 seconds when selected
      const locationInterval = setInterval(() => fetchLocationData(selectedLocation), 3000);
      return () => clearInterval(locationInterval);
    }
  }, [selectedLocation]);

  // Handle map marker click
  const handleMapClick = (event) => {
    if (event.points && event.points.length > 0) {
      const point = event.points[0];
      const locationName = point.customdata;
      setSelectedLocation(locationName);
    }
  };

  // Prepare map data with proper Rwanda coordinates
  const getMapData = () => {
    const mapPoints = Object.entries(currentStatus).map(([locationName, data]) => ({
      locationName,
      lat: data.location?.lat || 0,
      lon: data.location?.lon || 0,
      emission: data.emission,
      status: data.status,
      color: data.color,
      gasLevels: data.gas_levels,
      region: data.region,
      locationType: data.location_type,
      source: data.source
    }));

    // Filter out invalid coordinates
    return mapPoints.filter(point => point.lat !== 0 && point.lon !== 0);
  };

  // Get emission-based map traces
  const getEmissionMapTraces = () => {
    const mapData = getMapData();
    
    return [
      {
        type: 'scattergeo',
        lat: mapData.map(d => d.lat),
        lon: mapData.map(d => d.lon),
        mode: 'markers',
        marker: {
          size: mapData.map(d => Math.max(15, Math.min(35, d.emission / 2 + 15))),
          color: mapData.map(d => d.emission),
          colorscale: [
            [0, '#22c55e'],     // Green for low
            [0.3, '#eab308'],   // Yellow for medium-low
            [0.6, '#f97316'],   // Orange for medium-high
            [1, '#ef4444']      // Red for high
          ],
          showscale: true,
          colorbar: {
            title: 'CO₂ Emissions Level',
            thickness: 20,
            len: 0.7,
            x: 1.02
          },
          line: {
            width: 3,
            color: 'white'
          },
          opacity: 0.8
        },
        text: mapData.map(d => 
          `<b>${d.region}</b><br>` +
          `Location Type: ${d.locationType}<br>` +
          `Coordinates: ${d.lat.toFixed(3)}, ${d.lon.toFixed(3)}<br>` +
          `<b>CO₂ Emission: ${d.emission.toFixed(2)}</b><br>` +
          `Status: <b>${d.status}</b><br>` +
          `────────────────<br>` +
          `SO₂: ${(d.gasLevels.SO2 * 1000000).toFixed(3)} ppm<br>` +
          `NO₂: ${(d.gasLevels.NO2 * 1000000).toFixed(3)} ppm<br>` +
          `CO: ${(d.gasLevels.CO * 1000).toFixed(2)} ppm<br>` +
          `Data Source: ${d.source}`
        ),
        hovertemplate: '%{text}<extra></extra>',
        customdata: mapData.map(d => d.locationName),
        name: 'Monitoring Stations'
      }
    ];
  };

  // Get gas-levels based map traces
  const getGasLevelsMapTraces = () => {
    const mapData = getMapData();
    
    return [
      {
        type: 'scattergeo',
        lat: mapData.map(d => d.lat),
        lon: mapData.map(d => d.lon),
        mode: 'markers',
        marker: {
          size: mapData.map(d => Math.max(10, (d.gasLevels.SO2 * 10000000) + 10)),
          color: mapData.map(d => d.gasLevels.SO2 * 1000000),
          colorscale: 'Reds',
          showscale: true,
          colorbar: {
            title: 'SO₂ (ppm)',
            thickness: 15,
            len: 0.3,
            x: 1.02,
            y: 0.8
          },
          opacity: 0.7,
          symbol: 'circle'
        },
        text: mapData.map(d => 
          `<b>${d.region}</b><br>SO₂: ${(d.gasLevels.SO2 * 1000000).toFixed(3)} ppm`
        ),
        hovertemplate: '%{text}<extra></extra>',
        customdata: mapData.map(d => d.locationName),
        name: 'SO₂ Levels'
      }
    ];
  };

  // Prepare time series data with improved error handling and better y-axis range
  const getTimeSeriesData = () => {
    // Ensure realtimeData is an array
    const dataArray = Array.isArray(realtimeData) ? realtimeData : [];
    
    if (!selectedLocation && Object.keys(locations).length > 0) {
      // Show top 5 locations by default
      const locationNames = Object.keys(locations).slice(0, 5);
      const traces = [];

      locationNames.forEach((locationName, index) => {
        const locationData = dataArray
          .filter(d => d && d.location_name === locationName)
          .slice(-20);

        if (locationData.length > 0) {
          const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];
          traces.push({
            x: locationData.map(d => new Date(d.timestamp)),
            y: locationData.map(d => d.emission || 0),
            name: `${locations[locationName]?.region || locationName}`,
            type: 'scatter',
            mode: 'lines+markers',
            line: { width: 3, color: colors[index % colors.length] },
            marker: { size: 8 }
          });
        }
      });
      return traces;
    } else if (selectedLocation && locationDetailData?.trends) {
      return [{
        x: locationDetailData.trends.timestamps.map(t => new Date(t)),
        y: locationDetailData.trends.emissions,
        name: `CO₂ Emissions`,
        type: 'scatter',
        mode: 'lines+markers',
        line: { width: 4, color: '#3b82f6' },
        marker: { size: 10 },
        fill: 'tonexty',
        fillcolor: 'rgba(59, 130, 246, 0.1)'
      }];
    }
    
    return [];
  };

  // Calculate dynamic Y-axis range for better CO2 visualization
  const getOptimalYAxisRange = (data) => {
    if (!data || data.length === 0) return [0, 150];
    
    const values = data.flatMap(trace => trace.y || []);
    if (values.length === 0) return [0, 150];
    
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min;
    const padding = Math.max(range * 0.1, 5); // At least 5 units padding
    
    return [
      Math.max(0, min - padding),
      max + padding
    ];
  };

  // Prepare gas levels data for selected location
  const getGasLevelsData = () => {
    if (!locationDetailData?.trends) return [];

    const traces = [];
    const trends = locationDetailData.trends;
    const timestamps = trends.timestamps.map(t => new Date(t));

    traces.push({
      x: timestamps,
      y: trends.so2_levels.map(val => val * 1000000),
      name: 'SO₂',
      type: 'scatter',
      mode: 'lines+markers',
      line: { width: 3, color: '#ef4444' },
      marker: { size: 8 },
      yaxis: 'y'
    });

    traces.push({
      x: timestamps,
      y: trends.no2_levels.map(val => val * 1000000),
      name: 'NO₂',
      type: 'scatter',
      mode: 'lines+markers',
      line: { width: 3, color: '#f59e0b' },
      marker: { size: 8 },
      yaxis: 'y'
    });

    traces.push({
      x: timestamps,
      y: trends.co_levels.map(val => val * 1000),
      name: 'CO',
      type: 'scatter',
      mode: 'lines+markers',
      line: { width: 3, color: '#10b981' },
      marker: { size: 8 },
      yaxis: 'y2'
    });

    return traces;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-400 mx-auto mb-6"></div>
          <p className="text-2xl font-semibold">Loading Rwanda CO₂ Dashboard...</p>
          <p className="text-gray-400 mt-2">Fetching real-time emission data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
            Rwanda CO₂ Emissions Monitoring
          </h1>
          <p className="text-xl text-gray-300">Real-time Environmental Data Dashboard</p>
          <div className="mt-4 flex justify-center items-center space-x-4 text-sm">
            <span className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-2 animate-pulse"></div>
              Live Data Feed
            </span>
            <span className="text-gray-400">•</span>
            <span>{Object.keys(locations).length} Monitoring Stations</span>
            <span className="text-gray-400">•</span>
            <span>Updates every 3s</span>
          </div>
        </div>

        {/* Location Selection Info */}
        {selectedLocation && locationDetailData && (
          <div className="bg-gradient-to-r from-blue-900/40 to-purple-900/40 border border-blue-500/50 rounded-xl p-6 mb-8 backdrop-blur-sm">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-blue-300 mb-2">
                  📍 {locationDetailData.location_info?.region || 'Selected Location'}
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-gray-300"><strong>Coordinates:</strong></p>
                    <p className="text-blue-200">
                      {locationDetailData.location_info?.lat?.toFixed(4)}, {locationDetailData.location_info?.lon?.toFixed(4)}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-300"><strong>Location Type:</strong></p>
                    <p className="text-green-200 capitalize">{locationDetailData.location_info?.type || 'Unknown'}</p>
                  </div>
                  <div>
                    <p className="text-gray-300"><strong>Data Source:</strong></p>
                    <p className="text-yellow-200 capitalize">{locationDetailData.location_info?.source || 'Unknown'}</p>
                  </div>
                </div>
                {locationDetailData.statistics && (
                  <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div className="bg-gray-800/50 rounded-lg p-3">
                      <p className="text-gray-400">Current Emission</p>
                      <p className="text-2xl font-bold text-blue-300">
                        {locationDetailData.current?.emission?.toFixed(2)} CO₂
                      </p>
                    </div>
                    <div className="bg-gray-800/50 rounded-lg p-3">
                      <p className="text-gray-400">Average</p>
                      <p className="text-xl font-semibold text-green-300">
                        {locationDetailData.statistics.avg_emission?.toFixed(2)}
                      </p>
                    </div>
                    <div className="bg-gray-800/50 rounded-lg p-3">
                      <p className="text-gray-400">Range</p>
                      <p className="text-lg text-orange-300">
                        {locationDetailData.statistics.min_emission?.toFixed(1)} - {locationDetailData.statistics.max_emission?.toFixed(1)}
                      </p>
                    </div>
                  </div>
                )}
              </div>
              <button 
                onClick={() => {setSelectedLocation(null); setLocationDetailData(null);}}
                className="bg-red-600 hover:bg-red-700 px-6 py-2 rounded-lg text-sm font-semibold transition-colors ml-4"
              >
                ✕ Clear
              </button>
            </div>
          </div>
        )}

        {/* Location Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 mb-8">
          {Object.entries(currentStatus).slice(0, 20).map(([locationName, data]) => (
            <div
              key={locationName}
              className={`p-4 rounded-xl border-2 cursor-pointer transition-all duration-300 location-card backdrop-blur-sm ${
                selectedLocation === locationName 
                  ? 'border-blue-400 bg-blue-900/40 shadow-lg shadow-blue-500/25 selected-location' 
                  : `border-gray-600 bg-gray-800/80 hover:border-gray-400 hover:bg-gray-700/80 ${
                      data.color === 'red' ? 'hover:border-red-400' :
                      data.color === 'orange' ? 'hover:border-orange-400' : 'hover:border-green-400'
                    }`
              }`}
              onClick={() => setSelectedLocation(locationName)}
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-xs font-semibold text-gray-200 flex-1">
                  {data.region || 'Unknown Region'}
                </h3>
                <span className={`px-2 py-1 rounded-full text-xs font-bold ml-2 ${
                  data.color === 'red' ? 'bg-red-600 text-white' :
                  data.color === 'orange' ? 'bg-orange-600 text-white' : 'bg-green-600 text-white'
                }`}>
                  {data.status}
                </span>
              </div>
              
              <div className="text-xs text-gray-400 mb-2">
                📍 {data.location?.lat?.toFixed(3)}, {data.location?.lon?.toFixed(3)}
              </div>
              
              <div className="text-2xl font-bold mb-3 text-center">
                <span className={`${
                  data.color === 'red' ? 'text-red-400' :
                  data.color === 'orange' ? 'text-orange-400' : 'text-green-400'
                }`}>
                  {data.emission.toFixed(1)}
                </span>
                <div className="text-xs text-gray-400 font-normal">CO₂ Units</div>
              </div>
              
              <div className="space-y-1 text-xs">
                <div className="flex justify-between">
                  <span className="text-red-300">SO₂:</span>
                  <span className="text-white">{(data.gas_levels?.SO2 * 1000000 || 0).toFixed(3)} ppm</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-yellow-300">NO₂:</span>
                  <span className="text-white">{(data.gas_levels?.NO2 * 1000000 || 0).toFixed(3)} ppm</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-300">CO:</span>
                  <span className="text-white">{(data.gas_levels?.CO * 1000 || 0).toFixed(2)} ppm</span>
                </div>
              </div>
              
              <div className="mt-2 text-xs text-gray-500 capitalize">
                Type: {data.location_type}
              </div>
            </div>
          ))}
        </div>

        {/* Interactive Rwanda Map */}
        <div className="bg-gray-800/90 rounded-xl p-6 mb-8 backdrop-blur-sm border border-gray-700">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-blue-300">
              🇷🇼 Rwanda CO₂ Monitoring Network
            </h2>
            <div className="flex space-x-2">
              <button
                onClick={() => setMapView('emissions')}
                className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                  mapView === 'emissions' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                CO₂ Emissions
              </button>
              <button
                onClick={() => setMapView('gas_levels')}
                className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                  mapView === 'gas_levels' 
                    ? 'bg-red-600 text-white' 
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                Gas Levels
              </button>
            </div>
          </div>
          
          {rwandaBounds && (
            <div className="text-sm text-gray-400 mb-4">
              Coordinate Range: Lat {rwandaBounds.coordinate_range?.lat_min?.toFixed(3)} to {rwandaBounds.coordinate_range?.lat_max?.toFixed(3)}, 
              Lon {rwandaBounds.coordinate_range?.lon_min?.toFixed(3)} to {rwandaBounds.coordinate_range?.lon_max?.toFixed(3)}
            </div>
          )}
          
          <div className="map-container">
            {getMapData().length > 0 ? (
              <Plot
                data={mapView === 'emissions' ? getEmissionMapTraces() : getGasLevelsMapTraces()}
                layout={{
                  geo: {
                    scope: 'africa',
                    resolution: 50,
                    showframe: false,
                    showcoastlines: true,
                    projection: {
                      type: 'natural earth'
                    },
                    center: rwandaBounds ? rwandaBounds.center : { lat: -1.9, lon: 30.0 },
                    bgcolor: 'rgba(31, 41, 55, 0.8)',
                    coastlinecolor: '#4b5563',
                    countrycolor: '#6b7280',
                    lakecolor: '#1e40af',
                    landcolor: '#374151',
                    lonaxis: {
                      range: rwandaBounds ? [rwandaBounds.coordinate_range.lon_min - 0.2, rwandaBounds.coordinate_range.lon_max + 0.2] : [28.5, 31.0]
                    },
                    lataxis: {
                      range: rwandaBounds ? [rwandaBounds.coordinate_range.lat_min - 0.2, rwandaBounds.coordinate_range.lat_max + 0.2] : [-3.0, -1.0]
                    }
                  },
                  height: 600,
                  margin: { t: 0, b: 0, l: 0, r: 0 },
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  plot_bgcolor: 'rgba(0,0,0,0)',
                  font: { color: 'white' },
                  showlegend: false
                }}
                config={{ 
                  displayModeBar: false,
                  scrollZoom: true,
                  doubleClick: 'reset'
                }}
                className="w-full"
                onClick={handleMapClick}
              />
            ) : (
              <div className="flex items-center justify-center h-96 bg-gray-700/30 rounded-lg border-2 border-dashed border-gray-600">
                <div className="text-center text-gray-400">
                  <div className="text-4xl mb-4">🗺️</div>
                  <p className="text-lg">Loading map data...</p>
                  <p className="text-sm mt-2">Waiting for location data from API</p>
                </div>
              </div>
            )}
          </div>
          
          <div className="mt-4 text-center text-gray-400 text-sm">
            Click on any marker to view detailed location data • 
            Marker size indicates emission intensity • 
            Color represents current status level
          </div>
        </div>

        {/* Enhanced Time Series Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* CO2 Emissions Over Time */}
          <div className="bg-gray-800/90 rounded-xl p-6 backdrop-blur-sm border border-gray-700">
            <h2 className="text-xl font-bold mb-4 text-blue-300">
              📈 {selectedLocation ? 'Location CO₂ Trends' : 'Top Locations CO₂ Trends'}
            </h2>
            {selectedLocation && locationDetailData && (
              <div className="text-sm text-gray-400 mb-4 bg-gray-700/50 rounded-lg p-3">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <strong>Current:</strong> {locationDetailData.current?.emission?.toFixed(2)} CO₂
                  </div>
                  <div>
                    <strong>Region:</strong> {locationDetailData.location_info?.region}
                  </div>
                </div>
              </div>
            )}
            <Plot
              data={getTimeSeriesData()}
              layout={{
                height: 400,
                xaxis: { 
                  title: 'Time',
                  color: 'white',
                  gridcolor: '#374151',
                  linecolor: '#6b7280'
                },
                yaxis: { 
                  title: 'CO₂ Emissions',
                  color: 'white',
                  gridcolor: '#374151',
                  linecolor: '#6b7280',
                  range: getOptimalYAxisRange(getTimeSeriesData())
                },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(31, 41, 55, 0.5)',
                font: { color: 'white' },
                legend: { 
                  orientation: 'h', 
                  y: -0.2,
                  bgcolor: 'rgba(0,0,0,0.3)'
                }
              }}
              config={{ displayModeBar: false }}
              className="w-full"
            />
          </div>

          {/* Gas Levels for Selected Location */}
          <div className="bg-gray-800/90 rounded-xl p-6 backdrop-blur-sm border border-gray-700">
            <h2 className="text-xl font-bold mb-4 text-blue-300">
              🧪 {selectedLocation ? 'Pollutant Gas Analysis' : 'Select Location for Gas Data'}
            </h2>
            {selectedLocation && locationDetailData?.statistics && (
              <div className="grid grid-cols-3 gap-2 text-xs mb-4">
                <div className="bg-red-900/30 rounded-lg p-2 text-center border border-red-500/30">
                  <div className="text-red-300 font-bold">SO₂ Avg</div>
                  <div className="text-white">{(locationDetailData.statistics.avg_so2 * 1000000).toFixed(3)} ppm</div>
                </div>
                <div className="bg-yellow-900/30 rounded-lg p-2 text-center border border-yellow-500/30">
                  <div className="text-yellow-300 font-bold">NO₂ Avg</div>
                  <div className="text-white">{(locationDetailData.statistics.avg_no2 * 1000000).toFixed(3)} ppm</div>
                </div>
                <div className="bg-green-900/30 rounded-lg p-2 text-center border border-green-500/30">
                  <div className="text-green-300 font-bold">CO Avg</div>
                  <div className="text-white">{(locationDetailData.statistics.avg_co * 1000).toFixed(2)} ppm</div>
                </div>
              </div>
            )}
            {selectedLocation ? (
              <Plot
                data={getGasLevelsData()}
                layout={{
                  height: 400,
                  xaxis: { 
                    title: 'Time',
                    color: 'white',
                    gridcolor: '#374151',
                    linecolor: '#6b7280'
                  },
                  yaxis: { 
                    title: 'SO₂ & NO₂ (ppm)',
                    color: 'white',
                    gridcolor: '#374151',
                    linecolor: '#6b7280',
                    side: 'left'
                  },
                  yaxis2: {
                    title: 'CO (ppm)',
                    color: 'white',
                    gridcolor: '#374151',
                    linecolor: '#6b7280',
                    overlaying: 'y',
                    side: 'right'
                  },
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  plot_bgcolor: 'rgba(31, 41, 55, 0.5)',
                  font: { color: 'white' },
                  legend: { 
                    orientation: 'h', 
                    y: -0.2,
                    bgcolor: 'rgba(0,0,0,0.3)'
                  }
                }}
                config={{ displayModeBar: false }}
                className="w-full"
              />
            ) : (
              <div className="flex items-center justify-center h-96 text-gray-500">
                <div className="text-center">
                  <div className="text-6xl mb-4">🗺️</div>
                  <p className="text-lg">Click on a location marker on the map above</p>
                  <p className="text-sm mt-2">to view detailed gas level analysis</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Gas Correlation Analysis for Selected Location */}
        {selectedLocation && locationDetailData?.trends && (
          <div className="bg-gray-800/90 rounded-xl p-6 mb-8 backdrop-blur-sm border border-gray-700">
            <h2 className="text-xl font-bold mb-4 text-blue-300">
              📊 Gas-CO₂ Correlation Analysis - {locationDetailData.location_info?.region}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* SO2 vs CO2 */}
              <div className="bg-gray-900/50 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-red-300 mb-2">SO₂ vs CO₂ Relationship</h3>
                <Plot
                  data={[
                    {
                      x: locationDetailData.trends.so2_levels.map(val => val * 1000000),
                      y: locationDetailData.trends.emissions,
                      mode: 'markers',
                      type: 'scatter',
                      name: 'SO₂ vs CO₂',
                      marker: { 
                        size: 10, 
                        color: '#ef4444',
                        opacity: 0.7,
                        line: { width: 1, color: 'white' }
                      }
                    }
                  ]}
                  layout={{
                    height: 300,
                    xaxis: { title: 'SO₂ (ppm)', color: 'white', gridcolor: '#374151', titlefont: { size: 12 } },
                    yaxis: { title: 'CO₂', color: 'white', gridcolor: '#374151', titlefont: { size: 12 } },
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(31, 41, 55, 0.3)',
                    font: { color: 'white', size: 10 },
                    margin: { t: 20, b: 40, l: 50, r: 20 }
                  }}
                  config={{ displayModeBar: false }}
                  className="w-full"
                />
              </div>
              
              {/* NO2 vs CO2 */}
              <div className="bg-gray-900/50 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-yellow-300 mb-2">NO₂ vs CO₂ Relationship</h3>
                <Plot
                  data={[
                    {
                      x: locationDetailData.trends.no2_levels.map(val => val * 1000000),
                      y: locationDetailData.trends.emissions,
                      mode: 'markers',
                      type: 'scatter',
                      name: 'NO₂ vs CO₂',
                      marker: { 
                        size: 10, 
                        color: '#f59e0b',
                        opacity: 0.7,
                        line: { width: 1, color: 'white' }
                      }
                    }
                  ]}
                  layout={{
                    height: 300,
                    xaxis: { title: 'NO₂ (ppm)', color: 'white', gridcolor: '#374151', titlefont: { size: 12 } },
                    yaxis: { title: 'CO₂', color: 'white', gridcolor: '#374151', titlefont: { size: 12 } },
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(31, 41, 55, 0.3)',
                    font: { color: 'white', size: 10 },
                    margin: { t: 20, b: 40, l: 50, r: 20 }
                  }}
                  config={{ displayModeBar: false }}
                  className="w-full"
                />
              </div>
              
              {/* CO vs CO2 */}
              <div className="bg-gray-900/50 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-green-300 mb-2">CO vs CO₂ Relationship</h3>
                <Plot
                  data={[
                    {
                      x: locationDetailData.trends.co_levels.map(val => val * 1000),
                      y: locationDetailData.trends.emissions,
                      mode: 'markers',
                      type: 'scatter',
                      name: 'CO vs CO₂',
                      marker: { 
                        size: 10, 
                        color: '#10b981',
                        opacity: 0.7,
                        line: { width: 1, color: 'white' }
                      }
                    }
                  ]}
                  layout={{
                    height: 300,
                    xaxis: { title: 'CO (ppm)', color: 'white', gridcolor: '#374151', titlefont: { size: 12 } },
                    yaxis: { title: 'CO₂', color: 'white', gridcolor: '#374151', titlefont: { size: 12 } },
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(31, 41, 55, 0.3)',
                    font: { color: 'white', size: 10 },
                    margin: { t: 20, b: 40, l: 50, r: 20 }
                  }}
                  config={{ displayModeBar: false }}
                  className="w-full"
                />
              </div>
            </div>
          </div>
        )}

        {/* EDA Visualizations */}
        {edaData && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Emission Distribution */}
            <div className="bg-gray-800/90 rounded-xl p-6 backdrop-blur-sm border border-gray-700">
              <h2 className="text-xl font-bold mb-4 text-blue-300">Historical Emission Distribution</h2>
              <Plot
                data={[
                  {
                    x: edaData.distribution_data || [],
                    type: 'histogram',
                    nbinsx: 30,
                    marker: { 
                      color: '#38bdf8', 
                      opacity: 0.8,
                      line: { width: 1, color: 'white' }
                    },
                    name: 'Emission Distribution'
                  }
                ]}
                layout={{
                  height: 400,
                  xaxis: { 
                    title: 'CO₂ Emissions',
                    color: 'white',
                    gridcolor: '#374151',
                    linecolor: '#6b7280'
                  },
                  yaxis: { 
                    title: 'Frequency',
                    color: 'white',
                    gridcolor: '#374151',
                    linecolor: '#6b7280'
                  },
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  plot_bgcolor: 'rgba(31, 41, 55, 0.5)',
                  font: { color: 'white' }
                }}
                config={{ displayModeBar: false }}
                className="w-full"
              />
            </div>
            {/* Feature Correlations */}
            <div className="bg-gray-800/90 rounded-xl p-6 backdrop-blur-sm border border-gray-700">
              <h2 className="text-xl font-bold mb-4 text-blue-300">Feature Correlations with CO₂</h2>
              <Plot
                data={[
                  {
                    x: edaData.correlation_data?.features || [],
                    y: edaData.correlation_data?.correlations || [],
                    type: 'bar',
                    marker: { 
                      color: (edaData.correlation_data?.correlations || []).map(val => 
                        val > 0.05 ? '#10b981' : val > 0.03 ? '#f59e0b' : '#ef4444'
                      ),
                      opacity: 0.8,
                      line: { width: 1, color: 'white' }
                    },
                    name: 'Correlations'
                  }
                ]}
                layout={{
                  height: 400,
                  xaxis: { 
                    title: 'Features',
                    color: 'white',
                    gridcolor: '#374151',
                    linecolor: '#6b7280',
                    tickangle: -45
                  },
                  yaxis: { 
                    title: 'Correlation with Emissions',
                    color: 'white',
                    gridcolor: '#374151',
                    linecolor: '#6b7280'
                  },
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  plot_bgcolor: 'rgba(31, 41, 55, 0.5)',
                  font: { color: 'white' },
                  margin: { b: 100 }
                }}
                config={{ displayModeBar: false }}
                className="w-full"
              />
            </div>
          </div>
        )}

        {/* Historical Trends by Location Type */}
        {edaData && edaData.emission_trends && (
          <div className="bg-gray-800/90 rounded-xl p-6 mb-8 backdrop-blur-sm border border-gray-700">
            <h2 className="text-xl font-bold mb-4 text-blue-300">Historical Emission Trends by Location Type</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 text-sm">
              <div className="bg-red-900/20 rounded-lg p-3 border border-red-500/30">
                <div className="text-red-300 font-bold">Industrial Locations</div>
                <div className="text-gray-300">
                  {edaData.location_summary?.location_types?.industrial || 0} stations
                </div>
              </div>
              <div className="bg-blue-900/20 rounded-lg p-3 border border-blue-500/30">
                <div className="text-blue-300 font-bold">Urban Locations</div>
                <div className="text-gray-300">
                  {edaData.location_summary?.location_types?.urban || 0} stations
                </div>
              </div>
              <div className="bg-green-900/20 rounded-lg p-3 border border-green-500/30">
                <div className="text-green-300 font-bold">Coastal Locations</div>
                <div className="text-gray-300">
                  {edaData.location_summary?.location_types?.coastal || 0} stations
                </div>
              </div>
            </div>
            <Plot
              data={[
                {
                  x: (edaData.emission_trends || [])
                    .filter(d => d.type === 'industrial')
                    .map(d => d.date),
                  y: (edaData.emission_trends || [])
                    .filter(d => d.type === 'industrial')
                    .map(d => d.emission),
                  name: 'Industrial Areas',
                  type: 'scatter',
                  mode: 'lines',
                  line: { color: '#ef4444', width: 3 }
                },
                {
                  x: (edaData.emission_trends || [])
                    .filter(d => d.type === 'urban')
                    .map(d => d.date),
                  y: (edaData.emission_trends || [])
                    .filter(d => d.type === 'urban')
                    .map(d => d.emission),
                  name: 'Urban Areas',
                  type: 'scatter',
                  mode: 'lines',
                  line: { color: '#3b82f6', width: 3 }
                },
                {
                  x: (edaData.emission_trends || [])
                    .filter(d => d.type === 'coastal')
                    .map(d => d.date),
                  y: (edaData.emission_trends || [])
                    .filter(d => d.type === 'coastal')
                    .map(d => d.emission),
                  name: 'Coastal Areas',
                  type: 'scatter',
                  mode: 'lines',
                  line: { color: '#10b981', width: 3 }
                }
              ]}
              layout={{
                height: 500,
                xaxis: { 
                  title: 'Date',
                  color: 'white',
                  gridcolor: '#374151',
                  linecolor: '#6b7280'
                },
                yaxis: { 
                  title: 'CO₂ Emissions',
                  color: 'white',
                  gridcolor: '#374151',
                  linecolor: '#6b7280'
                },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(31, 41, 55, 0.5)',
                font: { color: 'white' },
                legend: { 
                  orientation: 'h', 
                  y: -0.15,
                  bgcolor: 'rgba(0,0,0,0.3)'
                }
              }}
              config={{ displayModeBar: false }}
              className="w-full"
            />
          </div>
        )}

        {/* Real-time Statistics Dashboard */}
        <div className="bg-gray-800/90 rounded-xl p-6 mb-8 backdrop-blur-sm border border-gray-700">
          <h2 className="text-xl font-bold mb-6 text-blue-300">Rwanda Monitoring Network Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center bg-gradient-to-br from-green-900/30 to-green-800/30 rounded-xl p-6 border border-green-500/30">
              <div className="text-4xl font-bold text-green-400 mb-2">
                {Object.keys(locations).length}
              </div>
              <div className="text-gray-300 font-semibold">Active Monitoring Stations</div>
              <div className="text-xs text-green-300 mt-2">Real-time Data Collection</div>
            </div>
            
            <div className="text-center bg-gradient-to-br from-blue-900/30 to-blue-800/30 rounded-xl p-6 border border-blue-500/30">
              <div className="text-4xl font-bold text-blue-400 mb-2">
                {Object.values(currentStatus).length > 0 ? 
                  Object.values(currentStatus).reduce((sum, loc) => sum + (loc.emission || 0), 0).toFixed(0) : '0'}
              </div>
              <div className="text-gray-300 font-semibold">Total CO₂ Emissions</div>
              <div className="text-xs text-blue-300 mt-2">All Stations Combined</div>
            </div>
            
            <div className="text-center bg-gradient-to-br from-red-900/30 to-red-800/30 rounded-xl p-6 border border-red-500/30">
              <div className="text-4xl font-bold text-red-400 mb-2">
                {Object.values(currentStatus).filter(loc => loc.status === 'HIGH').length}
              </div>
              <div className="text-gray-300 font-semibold">High Alert Locations</div>
              <div className="text-xs text-red-300 mt-2">Requires Attention</div>
            </div>
            
            <div className="text-center bg-gradient-to-br from-yellow-900/30 to-yellow-800/30 rounded-xl p-6 border border-yellow-500/30">
              <div className="text-4xl font-bold text-yellow-400 mb-2">
                {Object.values(currentStatus).length > 0 ? 
                  (Object.values(currentStatus).reduce((sum, loc) => sum + (loc.emission || 0), 0) / Object.values(currentStatus).length).toFixed(1) : '0'}
              </div>
              <div className="text-gray-300 font-semibold">Average Emission</div>
              <div className="text-xs text-yellow-300 mt-2">Across All Stations</div>
            </div>
          </div>
          
          {/* Location Type Distribution */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
            {edaData?.location_summary?.location_types && Object.entries(edaData.location_summary.location_types).map(([type, count]) => (
              <div key={type} className="bg-gray-700/50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-white mb-1">{count}</div>
                <div className="text-gray-300 capitalize">{type} Locations</div>
                <div className="text-xs text-gray-400 mt-1">
                  {Object.keys(locations).length > 0 ? ((count / Object.keys(locations).length) * 100).toFixed(1) : '0'}% of total
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Data Export Section */}
        <div className="bg-gray-800/90 rounded-xl p-6 mb-8 backdrop-blur-sm border border-gray-700">
          <h2 className="text-xl font-bold mb-4 text-blue-300">Location Data Export</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-200 mb-3">Current Monitoring Locations (JSON)</h3>
              <div className="bg-gray-900 rounded-lg p-4 max-h-64 overflow-y-auto">
                <pre className="text-xs text-green-300">
                  {JSON.stringify(
                    Object.fromEntries(
                      Object.entries(locations).slice(0, 5).map(([key, value]) => [
                        key, 
                        {
                          lat: value.lat,
                          lon: value.lon,
                          type: value.type,
                          region: value.region,
                          current_emission: currentStatus[key]?.emission?.toFixed(2) || 'N/A'
                        }
                      ])
                    ), 
                    null, 
                    2
                  )}
                </pre>
              </div>
              <button 
                onClick={() => {
                  const exportData = Object.fromEntries(
                    Object.entries(locations).map(([key, value]) => [
                      key, 
                      {
                        ...value,
                        current_emission: currentStatus[key]?.emission || 0,
                        current_status: currentStatus[key]?.status || 'UNKNOWN'
                      }
                    ])
                  );
                  
                  const dataStr = JSON.stringify(exportData, null, 2);
                  const dataBlob = new Blob([dataStr], {type: 'application/json'});
                  const url = URL.createObjectURL(dataBlob);
                  const link = document.createElement('a');
                  link.href = url;
                  link.download = `rwanda_co2_locations_${new Date().toISOString().split('T')[0]}.json`;
                  link.click();
                  URL.revokeObjectURL(url);
                }}
                className="mt-3 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
              >
                Export Full Dataset (JSON)
              </button>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-200 mb-3">Current Status Summary</h3>
              <div className="space-y-3">
                <div className="bg-gray-900/50 rounded-lg p-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Data Freshness:</span>
                    <span className="text-green-400 flex items-center">
                      <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                      Live
                    </span>
                  </div>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Geographic Coverage:</span>
                    <span className="text-blue-400">Rwanda</span>
                  </div>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Data Points Collected:</span>
                    <span className="text-yellow-400">{realtimeData.length.toLocaleString()}</span>
                  </div>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Last Update:</span>
                    <span className="text-gray-400 text-sm">
                      {new Date().toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-gray-400 text-sm mt-12 border-t border-gray-700 pt-8">
          <div className="bg-gray-800/50 rounded-lg p-6">
            <p className="text-lg font-semibold mb-2">Real-time CO₂ Emissions Monitoring Dashboard</p>
            <p className="mb-2">Rwanda Environmental Data Collection Network</p>
            <div className="flex justify-center items-center space-x-6 text-xs">
              <span>📊 {Object.keys(locations).length} Active Stations</span>
              <span>🔄 3-Second Updates</span>
              <span>🌍 Rwanda Coverage</span>
              <span>📡 Live Data Stream</span>
            </div>
            {selectedLocation && locationDetailData && (
              <div className="mt-4 p-3 bg-blue-900/30 rounded-lg border border-blue-500/30">
                <p className="text-blue-300 font-semibold">
                  Currently Monitoring: {locationDetailData.location_info?.region || 'Selected Location'}
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  Click 'Clear' above or select another location to change focus
                </p>
              </div>
            )}
            <p className="text-xs text-gray-500 mt-4">
              Last system update: {new Date().toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CO2EmissionsDashboard;