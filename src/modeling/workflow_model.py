"""
Build workflow model from validated data
Models entities, events, states, and relationships
"""
import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    RAW_DATA_DIR,
    VALIDATED_DATA_DIR,
    OUTPUT_DATA_DIR,
    STATUS_VALID,
    STATUS_SUSPICIOUS,
    PEAK_HOURS_WEEKDAY,
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


class TripWorkflowModel:
    """Models the trip workflow with entities, events, and states"""

    def __init__(self, trip_df: pd.DataFrame, zone_df: pd.DataFrame):
        """
        Initialize workflow model

        Args:
            trip_df: Validated trip data
            zone_df: Zone lookup data
        """
        self.trip_df = trip_df
        self.zone_df = zone_df
        self.workflow_df = None

    def enrich_with_zones(self) -> pd.DataFrame:
        """
        Enrich trips with zone information

        Returns:
            Enriched DataFrame
        """
        logger.info("=" * 60)
        logger.info("ENRICHING WITH ZONE DATA")
        logger.info("=" * 60)

        # Merge pickup zone
        df = self.trip_df.merge(
            self.zone_df[['LocationID', 'Borough', 'Zone', 'service_zone']],
            left_on='PULocationID',
            right_on='LocationID',
            how='left',
            suffixes=('', '_pickup')
        )
        df.rename(columns={
            'Borough': 'pickup_borough',
            'Zone': 'pickup_zone',
            'service_zone': 'pickup_service_zone'
        }, inplace=True)
        df.drop('LocationID', axis=1, inplace=True)

        # Merge dropoff zone
        df = df.merge(
            self.zone_df[['LocationID', 'Borough', 'Zone', 'service_zone']],
            left_on='DOLocationID',
            right_on='LocationID',
            how='left',
            suffixes=('', '_dropoff')
        )
        df.rename(columns={
            'Borough': 'dropoff_borough',
            'Zone': 'dropoff_zone',
            'service_zone': 'dropoff_service_zone'
        }, inplace=True)
        df.drop('LocationID', axis=1, inplace=True)

        logger.info(f"Enriched {len(df)} trips with zone information")

        # Check for unmatched zones
        unmatched_pickup = df['pickup_zone'].isna().sum()
        unmatched_dropoff = df['dropoff_zone'].isna().sum()

        if unmatched_pickup > 0:
            logger.warning(f"Unmatched pickup zones: {unmatched_pickup}")
        if unmatched_dropoff > 0:
            logger.warning(f"Unmatched dropoff zones: {unmatched_dropoff}")

        return df

    def calculate_derived_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived fields for workflow analysis

        Args:
            df: Enriched trip data

        Returns:
            DataFrame with derived fields
        """
        logger.info("=" * 60)
        logger.info("CALCULATING DERIVED FIELDS")
        logger.info("=" * 60)

        # Ensure datetime columns are parsed
        df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
        df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

        # Trip duration in minutes
        df['trip_duration_minutes'] = (
            df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']
        ).dt.total_seconds() / 60

        # Time segments
        df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
        df['pickup_day_of_week'] = df['tpep_pickup_datetime'].dt.day_name()
        df['pickup_date'] = df['tpep_pickup_datetime'].dt.date
        df['pickup_month'] = df['tpep_pickup_datetime'].dt.to_period('M').astype(str)
        df['is_weekend'] = df['tpep_pickup_datetime'].dt.dayofweek >= 5

        # Peak hour classification
        def is_peak_hour(row):
            if row['is_weekend']:
                return False
            hour = row['pickup_hour']
            morning_start, morning_end = PEAK_HOURS_WEEKDAY['morning']
            evening_start, evening_end = PEAK_HOURS_WEEKDAY['evening']
            return (morning_start <= hour < morning_end) or (evening_start <= hour < evening_end)

        df['is_peak_hour'] = df.apply(is_peak_hour, axis=1)

        # Revenue per mile (exclude zero distance)
        df['revenue_per_mile'] = np.where(
            df['trip_distance'] > 0,
            df['total_amount'] / df['trip_distance'],
            np.nan
        )

        # Trip type classification
        def classify_trip_type(row):
            if row['trip_distance'] == 0:
                return 'waiting_charge'
            elif row['trip_distance'] < 1:
                return 'short_trip'
            elif row['trip_distance'] < 5:
                return 'medium_trip'
            elif row['trip_distance'] < 10:
                return 'long_trip'
            else:
                return 'very_long_trip'

        df['trip_type'] = df.apply(classify_trip_type, axis=1)

        # Geographic flow
        df['is_same_zone'] = df['PULocationID'] == df['DOLocationID']
        df['is_interborough'] = df['pickup_borough'] != df['dropoff_borough']

        # Payment method label
        payment_labels = {
            1: 'Credit Card',
            2: 'Cash',
            3: 'No Charge',
            4: 'Dispute',
            5: 'Unknown',
            6: 'Voided'
        }
        df['payment_method'] = df['payment_type'].map(payment_labels)

        logger.info("Derived fields calculated:")
        logger.info(f"  - Trip duration (minutes)")
        logger.info(f"  - Time segments (hour, day, month)")
        logger.info(f"  - Peak hour classification")
        logger.info(f"  - Revenue per mile")
        logger.info(f"  - Trip type classification")
        logger.info(f"  - Geographic flow indicators")

        return df

    def build_workflow_model(self) -> pd.DataFrame:
        """
        Build complete workflow model

        Returns:
            Workflow DataFrame
        """
        logger.info("=" * 60)
        logger.info("BUILDING WORKFLOW MODEL")
        logger.info("=" * 60)

        # Step 1: Enrich with zones
        df = self.enrich_with_zones()

        # Step 2: Calculate derived fields
        df = self.calculate_derived_fields(df)

        # Step 3: Filter to valid/suspicious only (exclude invalid)
        initial_count = len(df)
        df = df[df['validation_status'].isin([STATUS_VALID, STATUS_SUSPICIOUS])]
        filtered_count = len(df)

        logger.info(f"Filtered data: {initial_count:,} → {filtered_count:,} records")
        logger.info(f"Removed {initial_count - filtered_count:,} invalid records")

        self.workflow_df = df

        logger.info("=" * 60)
        logger.info("WORKFLOW MODEL COMPLETE")
        logger.info("=" * 60)

        return df

    def get_workflow_summary(self) -> Dict:
        """Get workflow model summary statistics"""
        if self.workflow_df is None:
            return {}

        df = self.workflow_df

        return {
            'total_trips': len(df),
            'valid_trips': len(df[df['validation_status'] == STATUS_VALID]),
            'suspicious_trips': len(df[df['validation_status'] == STATUS_SUSPICIOUS]),
            'date_range': {
                'start': str(df['tpep_pickup_datetime'].min()),
                'end': str(df['tpep_pickup_datetime'].max()),
            },
            'trip_types': df['trip_type'].value_counts().to_dict(),
            'peak_hour_trips': int(df['is_peak_hour'].sum()),
            'weekend_trips': int(df['is_weekend'].sum()),
            'payment_methods': df['payment_method'].value_counts().to_dict(),
            'top_pickup_zones': df['pickup_zone'].value_counts().head(10).to_dict(),
            'top_dropoff_zones': df['dropoff_zone'].value_counts().head(10).to_dict(),
        }


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("NYC TAXI WORKFLOW MODELING STARTED")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info("=" * 60)

    # Load zone lookup
    zone_path = RAW_DATA_DIR / "taxi_zone_lookup.csv"
    if not zone_path.exists():
        logger.error(f"Zone lookup file not found: {zone_path}")
        return 1

    zone_df = pd.read_csv(zone_path)
    logger.info(f"Loaded {len(zone_df)} zones")

    # Load validated trip data
    trip_path = VALIDATED_DATA_DIR / "trips_validated.parquet"
    if not trip_path.exists():
        logger.error(f"Validated trip data not found: {trip_path}")
        logger.error("Run validators.py first to validate data")
        return 1

    trip_df = pd.read_parquet(trip_path)
    logger.info(f"Loaded {len(trip_df)} validated trip records")

    # Build workflow model
    model = TripWorkflowModel(trip_df, zone_df)
    workflow_df = model.build_workflow_model()

    # Save workflow data
    output_path = VALIDATED_DATA_DIR / "trips_workflow.parquet"
    workflow_df.to_parquet(output_path)
    logger.info(f"Workflow model saved to: {output_path}")

    # Save workflow summary
    summary = model.get_workflow_summary()
    summary_path = OUTPUT_DATA_DIR / "workflow_summary.json"
    import json
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    logger.info(f"Workflow summary saved to: {summary_path}")

    # Display summary
    logger.info("\n" + "=" * 60)
    logger.info("WORKFLOW SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total trips: {summary['total_trips']:,}")
    logger.info(f"Valid trips: {summary['valid_trips']:,}")
    logger.info(f"Suspicious trips: {summary['suspicious_trips']:,}")
    logger.info(f"Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")
    logger.info(f"\nPeak hour trips: {summary['peak_hour_trips']:,}")
    logger.info(f"Weekend trips: {summary['weekend_trips']:,}")

    logger.info("\nTrip types:")
    for trip_type, count in summary['trip_types'].items():
        logger.info(f"  {trip_type}: {count:,}")

    logger.info("\n" + "=" * 60)
    logger.info("Next step: Calculate metrics (python src/metrics/calculator.py)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
