"""
Fetch trip data and zone lookup from NYC TLC
Demonstrates multiple retrieval modes: CSV and Parquet
"""
import sys
import logging
from pathlib import Path
import requests
import pandas as pd
from typing import Optional, Tuple
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    RAW_DATA_DIR,
    ZONE_LOOKUP_URL,
    TLC_BASE_URL,
    RETRY_ATTEMPTS,
    RETRY_DELAY_SECONDS,
    get_log_filename,
    LOG_FORMAT,
    LOG_LEVEL,
)

# Setup logging
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(get_log_filename()),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def download_file(url: str, output_path: Path, retry_attempts: int = RETRY_ATTEMPTS) -> bool:
    """
    Download file from URL with retry logic

    Args:
        url: Source URL
        output_path: Destination file path
        retry_attempts: Number of retry attempts

    Returns:
        True if successful, False otherwise
    """
    for attempt in range(retry_attempts):
        try:
            logger.info(f"Downloading from {url} (attempt {attempt + 1}/{retry_attempts})")

            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()

            # Get file size if available
            total_size = int(response.headers.get('content-length', 0))
            logger.info(f"File size: {total_size / (1024*1024):.2f} MB")

            # Write to file
            with open(output_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0 and downloaded % (10 * 1024 * 1024) == 0:
                            logger.info(f"Progress: {downloaded / (1024*1024):.2f} MB / {total_size / (1024*1024):.2f} MB")

            logger.info(f"Successfully downloaded to {output_path}")
            return True

        except requests.exceptions.RequestException as e:
            logger.warning(f"Download attempt {attempt + 1} failed: {e}")
            if attempt < retry_attempts - 1:
                logger.info(f"Retrying in {RETRY_DELAY_SECONDS} seconds...")
                import time
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                logger.error(f"Failed to download after {retry_attempts} attempts")
                return False

    return False


def fetch_zone_lookup() -> Tuple[Optional[pd.DataFrame], Optional[Path]]:
    """
    Fetch taxi zone lookup table (CSV)

    Returns:
        Tuple of (DataFrame, file_path) or (None, None) if failed
    """
    logger.info("=" * 60)
    logger.info("FETCHING ZONE LOOKUP DATA")
    logger.info("=" * 60)

    output_path = RAW_DATA_DIR / "taxi_zone_lookup.csv"

    # Download file
    if not download_file(ZONE_LOOKUP_URL, output_path):
        return None, None

    # Verify file was created and has content
    if not output_path.exists():
        logger.error(f"File not found after download: {output_path}")
        return None, None

    file_size = output_path.stat().st_size
    logger.info(f"File size on disk: {file_size} bytes")

    if file_size == 0:
        logger.error("Downloaded file is empty")
        return None, None

    # Load and verify data
    try:
        df = pd.read_csv(output_path)
        logger.info(f"Loaded {len(df)} zone records")
        logger.info(f"Columns: {list(df.columns)}")
        logger.info(f"Sample data:\n{df.head()}")

        return df, output_path

    except Exception as e:
        logger.error(f"Failed to load CSV: {e}")
        return None, None


def fetch_trip_data(year: int, month: int) -> Tuple[Optional[pd.DataFrame], Optional[Path]]:
    """
    Fetch trip data for specific month (Parquet format)

    Args:
        year: Year (e.g., 2024)
        month: Month (1-12)

    Returns:
        Tuple of (DataFrame, file_path) or (None, None) if failed
    """
    logger.info("=" * 60)
    logger.info(f"FETCHING TRIP DATA: {year}-{month:02d}")
    logger.info("=" * 60)

    # Construct URL
    url = f"{TLC_BASE_URL}/yellow_tripdata_{year}-{month:02d}.parquet"
    output_path = RAW_DATA_DIR / f"yellow_tripdata_{year}{month:02d}.parquet"

    # Check if already downloaded
    if output_path.exists():
        logger.info(f"File already exists: {output_path}")
        logger.info("Loading existing file...")
        try:
            df = pd.read_parquet(output_path)
            logger.info(f"Loaded {len(df)} trip records from existing file")
            return df, output_path
        except Exception as e:
            logger.warning(f"Failed to load existing file: {e}")
            logger.info("Will re-download...")

    # Download file
    if not download_file(url, output_path):
        return None, None

    # Verify file
    if not output_path.exists():
        logger.error(f"File not found after download: {output_path}")
        return None, None

    file_size = output_path.stat().st_size
    logger.info(f"File size on disk: {file_size / (1024*1024):.2f} MB")

    if file_size == 0:
        logger.error("Downloaded file is empty")
        return None, None

    # Load and verify data
    try:
        df = pd.read_parquet(output_path)
        logger.info(f"Loaded {len(df)} trip records")
        logger.info(f"Columns: {list(df.columns)}")
        logger.info(f"Date range: {df['tpep_pickup_datetime'].min()} to {df['tpep_pickup_datetime'].max()}")
        logger.info(f"Sample data:\n{df.head()}")

        return df, output_path

    except Exception as e:
        logger.error(f"Failed to load Parquet: {e}")
        return None, None


def create_sample_data():
    """
    Create sample dataset for demo purposes (when full data unavailable)
    """
    logger.info("=" * 60)
    logger.info("CREATING SAMPLE DATA FOR DEMO")
    logger.info("=" * 60)

    import numpy as np
    from datetime import timedelta

    # Generate sample trip data
    n_trips = 10000
    base_date = datetime(2024, 1, 1)

    data = {
        'VendorID': np.random.choice([1, 2], n_trips),
        'tpep_pickup_datetime': [base_date + timedelta(minutes=np.random.randint(0, 43200)) for _ in range(n_trips)],
        'tpep_dropoff_datetime': [],
        'passenger_count': np.random.choice([1, 2, 3, 4, 5, 0], n_trips, p=[0.6, 0.2, 0.1, 0.05, 0.03, 0.02]),
        'trip_distance': np.random.exponential(3, n_trips),
        'RatecodeID': np.random.choice([1, 2, 3, 4, 5], n_trips, p=[0.9, 0.05, 0.02, 0.02, 0.01]),
        'store_and_fwd_flag': np.random.choice(['N', 'Y'], n_trips, p=[0.95, 0.05]),
        'PULocationID': np.random.randint(1, 264, n_trips),
        'DOLocationID': np.random.randint(1, 264, n_trips),
        'payment_type': np.random.choice([1, 2, 3, 4], n_trips, p=[0.7, 0.25, 0.03, 0.02]),
        'fare_amount': [],
        'extra': np.random.choice([0, 0.5, 1], n_trips, p=[0.7, 0.2, 0.1]),
        'mta_tax': [0.5] * n_trips,
        'tip_amount': [],
        'tolls_amount': np.random.choice([0, 5.76, 2.5], n_trips, p=[0.9, 0.08, 0.02]),
        'improvement_surcharge': [0.3] * n_trips,
        'total_amount': [],
        'congestion_surcharge': np.random.choice([0, 2.5], n_trips, p=[0.3, 0.7]),
    }

    # Calculate derived fields
    for i in range(n_trips):
        duration_minutes = np.random.exponential(15) + 5
        data['tpep_dropoff_datetime'].append(
            data['tpep_pickup_datetime'][i] + timedelta(minutes=duration_minutes)
        )

        distance = data['trip_distance'][i]
        base_fare = 2.5 + (distance * 2.5) + (duration_minutes * 0.5)
        data['fare_amount'].append(max(2.5, base_fare))

        # Tip only for credit card payments
        if data['payment_type'][i] == 1:
            data['tip_amount'].append(data['fare_amount'][i] * np.random.uniform(0.1, 0.25))
        else:
            data['tip_amount'].append(0)

        data['total_amount'].append(
            data['fare_amount'][i] + data['extra'][i] + data['mta_tax'][i] +
            data['tip_amount'][i] + data['tolls_amount'][i] +
            data['improvement_surcharge'][i] + data['congestion_surcharge'][i]
        )

    # Add some data quality issues for validation testing
    # Negative fares
    neg_indices = np.random.choice(n_trips, 50, replace=False)
    for idx in neg_indices:
        data['fare_amount'][idx] = -10.0

    # Future dates
    future_indices = np.random.choice(n_trips, 20, replace=False)
    for idx in future_indices:
        data['tpep_pickup_datetime'][idx] = datetime(2025, 1, 1)

    # Zero distance with zero fare
    zero_indices = np.random.choice(n_trips, 100, replace=False)
    for idx in zero_indices:
        data['trip_distance'][idx] = 0
        if np.random.random() < 0.5:
            data['fare_amount'][idx] = 0

    df = pd.DataFrame(data)

    # Save to file
    output_path = RAW_DATA_DIR / "yellow_tripdata_sample.parquet"
    df.to_parquet(output_path)
    logger.info(f"Created sample data: {len(df)} records")
    logger.info(f"Saved to: {output_path}")

    return df, output_path


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("NYC TAXI DATA INGESTION STARTED")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info("=" * 60)

    # Fetch zone lookup
    zone_df, zone_path = fetch_zone_lookup()
    if zone_df is None:
        logger.error("Failed to fetch zone lookup data")
        return 1

    logger.info(f"Zone lookup complete: {len(zone_df)} zones")

    # For demo, create sample data instead of downloading large files
    # In production, uncomment the lines below to fetch real data

    logger.info("\nNote: Using sample data for demo. In production, uncomment fetch_trip_data().")
    trip_df, trip_path = create_sample_data()

    # To use real data, uncomment these lines:
    # from config import DEFAULT_YEAR, DEFAULT_MONTHS
    # for month in DEFAULT_MONTHS:
    #     trip_df, trip_path = fetch_trip_data(DEFAULT_YEAR, month)
    #     if trip_df is None:
    #         logger.error(f"Failed to fetch trip data for {DEFAULT_YEAR}-{month:02d}")
    #         continue
    #     logger.info(f"Trip data complete: {len(trip_df)} trips")

    logger.info("=" * 60)
    logger.info("DATA INGESTION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"\nRaw data stored in: {RAW_DATA_DIR}")
    logger.info("Next step: Run validation (python src/validation/validators.py)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
