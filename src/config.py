"""
Configuration file for NYC Taxi Pipeline
Contains all constants, file paths, and validation rules
"""
import os
from pathlib import Path
from datetime import datetime

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
VALIDATED_DATA_DIR = DATA_DIR / "validated"
OUTPUT_DATA_DIR = DATA_DIR / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, VALIDATED_DATA_DIR, OUTPUT_DATA_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data source URLs
TLC_BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
ZONE_LOOKUP_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv"

# Default data period (for sample)
DEFAULT_YEAR = 2024
DEFAULT_MONTHS = [1, 2]  # January and February

# Validation rules
VALIDATION_RULES = {
    "min_trip_duration_minutes": 1,
    "max_trip_duration_minutes": 180,
    "min_trip_distance_miles": 0,
    "max_trip_distance_miles": 100,
    "min_fare_amount": 0,
    "min_passenger_count": 0,
    "max_passenger_count": 6,
    "valid_vendor_ids": [1, 2],
    "valid_payment_types": [1, 2, 3, 4, 5, 6],
    "valid_rate_codes": [1, 2, 3, 4, 5, 6],
    "min_location_id": 1,
    "max_location_id": 263,
    # Special rules for zero distance
    "zero_distance_min_duration_minutes": 2,
    "zero_distance_min_fare": 2.50,
}

# Peak hour definitions (for utilization metric)
PEAK_HOURS_WEEKDAY = {
    "morning": (7, 9),  # 7 AM - 9 AM
    "evening": (17, 19),  # 5 PM - 7 PM
}

# Validation status codes
STATUS_VALID = "VALID"
STATUS_INVALID = "INVALID"
STATUS_SUSPICIOUS = "SUSPICIOUS"

# Metric definitions
METRICS = [
    "trip_completion_rate",
    "avg_trip_duration_minutes",
    "revenue_per_mile",
    "peak_hour_utilization",
    "geographic_coverage_quality",
]

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = "INFO"

# Pipeline configuration
RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 5
CHECKPOINT_ENABLED = True
CHECKPOINT_FILE = LOGS_DIR / "pipeline_checkpoint.json"

# Output file naming
def get_output_filename(prefix: str, period: str, extension: str = "csv") -> Path:
    """Generate output filename with period"""
    return OUTPUT_DATA_DIR / f"{prefix}_{period}.{extension}"

def get_log_filename(date: str = None) -> Path:
    """Generate log filename for date"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    return LOGS_DIR / f"pipeline_{date}.log"

# Column name mappings (TLC dataset uses specific column names)
TRIP_COLUMNS = {
    "vendor_id": "VendorID",
    "pickup_datetime": "tpep_pickup_datetime",
    "dropoff_datetime": "tpep_dropoff_datetime",
    "passenger_count": "passenger_count",
    "trip_distance": "trip_distance",
    "rate_code": "RatecodeID",
    "store_and_fwd": "store_and_fwd_flag",
    "pickup_location_id": "PULocationID",
    "dropoff_location_id": "DOLocationID",
    "payment_type": "payment_type",
    "fare_amount": "fare_amount",
    "extra": "extra",
    "mta_tax": "mta_tax",
    "tip_amount": "tip_amount",
    "tolls_amount": "tolls_amount",
    "improvement_surcharge": "improvement_surcharge",
    "total_amount": "total_amount",
    "congestion_surcharge": "congestion_surcharge",
}

ZONE_COLUMNS = {
    "location_id": "LocationID",
    "borough": "Borough",
    "zone": "Zone",
    "service_zone": "service_zone",
}

# Sample data URLs (using sample data for demo - replace with full data for production)
SAMPLE_DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"

# For demo purposes, we'll use a smaller sample
# In production, you would use: f"{TLC_BASE_URL}/yellow_tripdata_{year:04d}-{month:02d}.parquet"
