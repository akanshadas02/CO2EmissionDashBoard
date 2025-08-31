# CO2 Emissions Prediction Analysis

## Project Overview

This project analyzes and predicts CO2 emissions using satellite-derived atmospheric data from various gas sensors and meteorological measurements. The dataset contains measurements from Rwanda region spanning 2019-2022, with the goal of predicting emissions for 2022 based on historical patterns and atmospheric conditions.

## Dataset Description

### Data Structure
- **Training Data**: 79,023 observations with 76 features (2019-2021)
- **Test Data**: 24,353 observations with 75 features (2022)
- **Train/Test Ratio**: ~76% train, ~24% test

### Key Features
The dataset includes measurements from multiple atmospheric sensors:

#### Gas Concentration Measurements
- **Sulphur Dioxide (SO2)**: Column number density, air mass factor, slant column density
- **Carbon Monoxide (CO)**: Column number density, H2O content, cloud height
- **Nitrogen Dioxide (NO2)**: Tropospheric and stratospheric measurements, slant column density
- **Formaldehyde (HCHO)**: Tropospheric column density and air mass factor
- **Ozone (O3)**: Column number density, effective temperature

#### Meteorological Data
- **Cloud Properties**: Top/base height and pressure, optical depth, surface albedo
- **Sensor Geometry**: Azimuth and zenith angles for solar and sensor positions
- **Aerosol Data**: Height, pressure, optical depth, UV aerosol index

#### Temporal and Spatial Features
- **Location**: Latitude and longitude coordinates
- **Time**: Year (2019-2022) and week number (0-52)

## Exploratory Data Analysis Results

### Target Variable Distribution
- **Mean Emission**: 81.94 units
- **Standard Deviation**: 144.30 units
- **Range**: 0.00 to 3,167.77 units
- **Distribution**: Highly right-skewed (skewness ≈ 10.17)

The extreme right skew indicates the presence of significant outliers and suggests that most locations have relatively low emissions with occasional high-emission events.

### Geographic Distribution
The coordinates indicate the dataset focuses on Rwanda and surrounding regions:
- **Latitude Range**: -3.299° to -0.510° (Southern to Equatorial Africa)
- **Longitude Range**: 28.228° to 31.532° (Eastern Africa)

Geographic visualization reveals distinct spatial patterns with training and test locations well-distributed across the region.

### Temporal Patterns
- **Consistent Annual Coverage**: Equal observations across 2019, 2020, and 2021
- **Weekly Distribution**: Relatively uniform across all 53 weeks
- **Cyclical Patterns**: Time series analysis reveals seasonal emission patterns at specific locations

### Missing Data Analysis
Both training and test datasets contain missing values, particularly in:
- Gas sensor measurements (SO2, NO2, CO, HCHO)
- Cloud and aerosol properties
- Meteorological parameters

Missing data patterns suggest sensor availability issues or measurement quality constraints.

### Feature Correlations
Top correlated features with CO2 emissions:
1. **Longitude** (0.103): Geographic location significantly influences emissions
2. **UV Aerosol Layer Height** (0.069): Atmospheric aerosol conditions
3. **UV Aerosol Layer Pressure** (0.068): Related atmospheric pressure effects
4. **Cloud Surface Albedo** (0.047): Surface reflectance properties
5. **Gas Concentrations**: Various CO, SO2, HCHO, and NO2 measurements

The moderate correlation values suggest emissions are influenced by multiple atmospheric factors rather than dominated by a single variable.

## Feature Engineering

### Rolling Mean Features
Created 2-week rolling averages for all atmospheric measurements to capture:
- **Temporal Smoothing**: Reduce noise in sensor measurements
- **Trend Detection**: Identify gradual changes in atmospheric conditions
- **Cyclical Patterns**: Better represent recurring seasonal effects

This engineering approach resulted in 70 additional features (144 total), effectively doubling the feature space.

### Location Encoding
Generated unique location identifiers from latitude-longitude pairs to enable location-specific temporal analysis and rolling calculations.

## Model Performance

### Random Forest Regressor Results
- **RMSE Score**: 27.50
- **Model Type**: Random Forest with default hyperparameters
- **Features Used**: 144 (original + engineered rolling means)
- **Training Samples**: 55,316 (after train-test split)

### Feature Importance Analysis
The model identified key predictive features, with engineered rolling mean features likely contributing significantly to performance given the temporal nature of atmospheric data.

### Error Analysis
- **High Error Cases**: Locations with coordinates (-2.079, 29.321) showed prediction errors up to 1,873 units
- **Perfect Predictions**: Many zero-emission cases were predicted accurately
- **Error Pattern**: Larger errors typically occurred at locations with higher actual emissions

## Model Deployment and Real-time Predictions

### Prediction System
The final model includes a comprehensive prediction system capable of:
- **Real-time Monitoring**: Continuous emission predictions with realistic sensor simulation
- **Location Comparison**: Analysis across different geographic and environmental contexts
- **Manual Prediction**: Custom predictions with user-specified parameters

### Sample Predictions
The deployed model shows realistic prediction patterns:
- **Rural/Clean Areas**: Lower emissions (5-6 units)
- **Urban Areas**: Moderate emissions (50-200 units)
- **Industrial Areas**: Higher potential emissions (>100 units)

## Key Insights and Limitations

### Insights
1. **Geographic Influence**: Location (longitude specifically) is the strongest predictor of emissions
2. **Atmospheric Complexity**: Multiple gas concentrations and meteorological factors collectively influence emissions
3. **Temporal Patterns**: Weekly and seasonal variations exist but require rolling averages to capture effectively
4. **Data Quality**: Missing sensor data is a significant challenge requiring robust imputation strategies

### Limitations
1. **Regional Scope**: Model trained specifically on Rwanda region data, limiting generalizability
2. **Missing Data**: Substantial missing values in sensor measurements may impact prediction accuracy
3. **Skewed Distribution**: Extreme right skew in target variable may bias predictions toward lower values
4. **Feature Complexity**: High dimensionality (144 features) may lead to overfitting despite ensemble approach

### Recommendations for Improvement
1. **Advanced Imputation**: Implement sophisticated missing value handling techniques
2. **Target Transformation**: Apply log or box-cox transformation to address skewness
3. **Outlier Treatment**: Develop robust outlier detection and treatment strategies
4. **Cross-validation**: Implement spatial or temporal cross-validation for better model evaluation
5. **Hyperparameter Tuning**: Optimize Random Forest parameters for improved performance
6. **Feature Selection**: Apply dimensionality reduction techniques to identify most informative features

## Technical Implementation

The analysis demonstrates a complete machine learning pipeline from data exploration through model deployment, with particular strengths in:
- Comprehensive EDA with both statistical and visual analysis
- Geographic visualization using folium mapping
- Feature engineering with domain-appropriate rolling averages
- Model persistence and real-time prediction capabilities
- Error analysis and feature importance evaluation

The RMSE of 27.50 suggests reasonable predictive performance, though the high variance in the target variable (std=144.30) indicates significant room for improvement through advanced modeling techniques and better handling of the data's inherent challenges.