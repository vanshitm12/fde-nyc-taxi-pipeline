"""
Data validation with business-oriented rules
Profiles data, identifies quality issues, records assumptions
"""
import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    RAW_DATA_DIR,
    VALIDATED_DATA_DIR,
    OUTPUT_DATA_DIR,
    VALIDATION_RULES,
    STATUS_VALID,
    STATUS_INVALID,
    STATUS_SUSPICIOUS,
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


class TripValidator:
    """Validates trip data according to business rules"""

    def __init__(self, zone_df: pd.DataFrame):
        """
        Initialize validator with zone lookup data

        Args:
            zone_df: DataFrame with valid location IDs
        """
        self.zone_df = zone_df
        self.valid_location_ids = set(zone_df['LocationID'].values)
        self.validation_stats = {
            'total_records': 0,
            'valid': 0,
            'invalid': 0,
            'suspicious': 0,
            'failure_reasons': {}
        }

    def profile_data(self, df: pd.DataFrame) -> Dict:
        """
        Profile the raw data to understand distributions and quality

        Args:
            df: Raw trip data

        Returns:
            Dictionary with profiling statistics
        """
        logger.info("=" * 60)
        logger.info("DATA PROFILING")
        logger.info("=" * 60)

        profile = {
            'record_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            'missing_values': df.isnull().sum().to_dict(),
            'numeric_stats': {},
            'categorical_stats': {},
            'datetime_stats': {},
        }

        # Numeric column statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            profile['numeric_stats'][col] = {
                'mean': float(df[col].mean()) if not df[col].isna().all() else None,
                'median': float(df[col].median()) if not df[col].isna().all() else None,
                'std': float(df[col].std()) if not df[col].isna().all() else None,
                'min': float(df[col].min()) if not df[col].isna().all() else None,
                'max': float(df[col].max()) if not df[col].isna().all() else None,
                'negative_count': int((df[col] < 0).sum()),
                'zero_count': int((df[col] == 0).sum()),
            }

        # Categorical column statistics
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            profile['categorical_stats'][col] = {
                'unique_count': int(df[col].nunique()),
                'top_values': value_counts.head(10).to_dict(),
            }

        # Datetime statistics
        datetime_cols = df.select_dtypes(include=['datetime64']).columns
        for col in datetime_cols:
            profile['datetime_stats'][col] = {
                'min': str(df[col].min()),
                'max': str(df[col].max()),
                'null_count': int(df[col].isnull().sum()),
            }

        # Log key findings
        logger.info(f"Total records: {profile['record_count']:,}")
        logger.info(f"Columns: {profile['column_count']}")
        logger.info(f"Memory usage: {profile['memory_usage_mb']:.2f} MB")

        logger.info("\nMissing values:")
        for col, count in profile['missing_values'].items():
            if count > 0:
                pct = (count / len(df)) * 100
                logger.info(f"  {col}: {count:,} ({pct:.2f}%)")

        logger.info("\nKey numeric statistics:")
        for col in ['trip_distance', 'fare_amount', 'total_amount']:
            if col in profile['numeric_stats']:
                stats = profile['numeric_stats'][col]
                logger.info(f"  {col}:")
                logger.info(f"    Mean: {stats['mean']:.2f}, Median: {stats['median']:.2f}")
                logger.info(f"    Min: {stats['min']:.2f}, Max: {stats['max']:.2f}")
                logger.info(f"    Negative: {stats['negative_count']}, Zero: {stats['zero_count']}")

        return profile

    def validate_record(self, row: pd.Series) -> Tuple[str, List[str]]:
        """
        Validate a single trip record

        Args:
            row: Trip record

        Returns:
            Tuple of (status, reasons)
        """
        reasons = []

        # Rule 1: Valid pickup datetime
        try:
            pickup = pd.to_datetime(row['tpep_pickup_datetime'])
            if pd.isna(pickup):
                reasons.append('missing_pickup_time')
            elif pickup > datetime.now():
                reasons.append('future_pickup_time')
        except:
            reasons.append('invalid_pickup_time')
            return STATUS_INVALID, reasons

        # Rule 2: Valid dropoff datetime
        try:
            dropoff = pd.to_datetime(row['tpep_dropoff_datetime'])
            if pd.isna(dropoff):
                reasons.append('missing_dropoff_time')
            elif dropoff > datetime.now():
                reasons.append('future_dropoff_time')
        except:
            reasons.append('invalid_dropoff_time')
            return STATUS_INVALID, reasons

        # Rule 3: Dropoff after pickup
        if dropoff <= pickup:
            reasons.append('time_paradox')
            return STATUS_INVALID, reasons

        # Calculate duration
        duration_minutes = (dropoff - pickup).total_seconds() / 60

        # Rule 4: Duration bounds
        if duration_minutes < VALIDATION_RULES['min_trip_duration_minutes']:
            reasons.append('trip_too_short')
            return STATUS_INVALID, reasons
        elif duration_minutes > VALIDATION_RULES['max_trip_duration_minutes']:
            reasons.append('extremely_long_trip')
            return STATUS_SUSPICIOUS, reasons

        # Rule 5: Distance validation
        distance = row['trip_distance']
        if pd.isna(distance):
            reasons.append('missing_distance')
            return STATUS_INVALID, reasons
        elif distance < 0:
            reasons.append('negative_distance')
            return STATUS_INVALID, reasons
        elif distance > VALIDATION_RULES['max_trip_distance_miles']:
            reasons.append('extremely_long_distance')
            return STATUS_SUSPICIOUS, reasons

        # Rule 6: Special handling for zero distance
        if distance == 0:
            fare = row['fare_amount']
            if duration_minutes >= VALIDATION_RULES['zero_distance_min_duration_minutes'] and \
               fare >= VALIDATION_RULES['zero_distance_min_fare']:
                # Valid waiting time charge
                reasons.append('zero_distance_valid_waiting')
            else:
                reasons.append('zero_distance_invalid')
                return STATUS_INVALID, reasons

        # Rule 7: Fare validation
        fare = row['fare_amount']
        if pd.isna(fare):
            reasons.append('missing_fare')
            return STATUS_INVALID, reasons
        elif fare < 0:
            reasons.append('negative_fare')
            return STATUS_INVALID, reasons

        # Rule 8: Location ID validation
        pickup_loc = row['PULocationID']
        dropoff_loc = row['DOLocationID']

        if pd.isna(pickup_loc) or pd.isna(dropoff_loc):
            reasons.append('missing_location')
            return STATUS_INVALID, reasons

        if pickup_loc not in self.valid_location_ids:
            reasons.append('unknown_pickup_zone')
            return STATUS_SUSPICIOUS, reasons

        if dropoff_loc not in self.valid_location_ids:
            reasons.append('unknown_dropoff_zone')
            return STATUS_SUSPICIOUS, reasons

        # Rule 9: Payment type validation
        payment = row['payment_type']
        if payment not in VALIDATION_RULES['valid_payment_types']:
            reasons.append('invalid_payment_type')
            return STATUS_SUSPICIOUS, reasons

        # All checks passed
        if not reasons:
            reasons.append('all_checks_passed')
        return STATUS_VALID, reasons

    def validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate entire DataFrame

        Args:
            df: Raw trip data

        Returns:
            DataFrame with validation_status and validation_reasons columns
        """
        logger.info("=" * 60)
        logger.info("VALIDATING TRIP DATA")
        logger.info("=" * 60)

        self.validation_stats['total_records'] = len(df)

        # Add validation columns
        df['validation_status'] = ''
        df['validation_reasons'] = ''

        # Validate each record
        logger.info(f"Validating {len(df):,} records...")

        for idx, row in df.iterrows():
            status, reasons = self.validate_record(row)
            df.at[idx, 'validation_status'] = status
            df.at[idx, 'validation_reasons'] = ','.join(reasons)

            # Update stats
            if status == STATUS_VALID:
                self.validation_stats['valid'] += 1
            elif status == STATUS_INVALID:
                self.validation_stats['invalid'] += 1
            elif status == STATUS_SUSPICIOUS:
                self.validation_stats['suspicious'] += 1

            # Track failure reasons
            for reason in reasons:
                if reason != 'all_checks_passed':
                    self.validation_stats['failure_reasons'][reason] = \
                        self.validation_stats['failure_reasons'].get(reason, 0) + 1

            # Progress logging
            if (idx + 1) % 1000 == 0:
                logger.info(f"Validated {idx + 1:,} / {len(df):,} records")

        # Log validation summary
        logger.info("=" * 60)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total records: {self.validation_stats['total_records']:,}")
        logger.info(f"Valid: {self.validation_stats['valid']:,} ({self.validation_stats['valid']/self.validation_stats['total_records']*100:.2f}%)")
        logger.info(f"Invalid: {self.validation_stats['invalid']:,} ({self.validation_stats['invalid']/self.validation_stats['total_records']*100:.2f}%)")
        logger.info(f"Suspicious: {self.validation_stats['suspicious']:,} ({self.validation_stats['suspicious']/self.validation_stats['total_records']*100:.2f}%)")

        logger.info("\nTop failure reasons:")
        sorted_reasons = sorted(self.validation_stats['failure_reasons'].items(),
                               key=lambda x: x[1], reverse=True)
        for reason, count in sorted_reasons[:10]:
            logger.info(f"  {reason}: {count:,}")

        return df

    def get_quality_report(self) -> Dict:
        """Get validation quality report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'validation_stats': self.validation_stats,
            'completion_rate': self.validation_stats['valid'] / self.validation_stats['total_records'] * 100,
        }


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("NYC TAXI DATA VALIDATION STARTED")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info("=" * 60)

    # Load zone lookup
    zone_path = RAW_DATA_DIR / "taxi_zone_lookup.csv"
    if not zone_path.exists():
        logger.error(f"Zone lookup file not found: {zone_path}")
        logger.error("Run fetch_csv.py first to download data")
        return 1

    zone_df = pd.read_csv(zone_path)
    logger.info(f"Loaded {len(zone_df)} zones")

    # Load trip data (using sample for demo)
    trip_path = RAW_DATA_DIR / "yellow_tripdata_sample.parquet"
    if not trip_path.exists():
        logger.error(f"Trip data not found: {trip_path}")
        logger.error("Run fetch_csv.py first to download data")
        return 1

    trip_df = pd.read_parquet(trip_path)
    logger.info(f"Loaded {len(trip_df)} trip records")

    # Create validator
    validator = TripValidator(zone_df)

    # Profile data
    profile = validator.profile_data(trip_df)

    # Save profile
    profile_path = OUTPUT_DATA_DIR / "data_profile.json"
    with open(profile_path, 'w') as f:
        # Convert numpy types to native Python types for JSON serialization
        json.dump(profile, f, indent=2, default=str)
    logger.info(f"Data profile saved to: {profile_path}")

    # Validate data
    validated_df = validator.validate_dataframe(trip_df)

    # Save validated data
    output_path = VALIDATED_DATA_DIR / "trips_validated.parquet"
    validated_df.to_parquet(output_path)
    logger.info(f"Validated data saved to: {output_path}")

    # Save quality report
    quality_report = validator.get_quality_report()
    report_path = OUTPUT_DATA_DIR / "quality_report.json"
    with open(report_path, 'w') as f:
        json.dump(quality_report, f, indent=2)
    logger.info(f"Quality report saved to: {report_path}")

    logger.info("=" * 60)
    logger.info("VALIDATION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"\nNext step: Run workflow modeling (python src/modeling/workflow_model.py)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
