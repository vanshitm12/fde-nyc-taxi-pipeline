"""
Calculate operational metrics from workflow model
Produces 3-5 key metrics linked to business KPIs
"""
import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    VALIDATED_DATA_DIR,
    OUTPUT_DATA_DIR,
    STATUS_VALID,
    METRICS,
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


class MetricsCalculator:
    """Calculates operational metrics from workflow data"""

    def __init__(self, workflow_df: pd.DataFrame):
        """
        Initialize metrics calculator

        Args:
            workflow_df: Workflow-modeled trip data
        """
        self.workflow_df = workflow_df
        self.metrics = {}

    def calculate_trip_completion_rate(self) -> float:
        """
        Metric 1: Trip Completion Rate
        Percentage of valid trips out of total trips processed

        Returns:
            Completion rate as percentage
        """
        logger.info("Calculating Metric 1: Trip Completion Rate")

        # Note: In validated workflow data, invalid trips are already filtered
        # So we compare valid vs. all (valid + suspicious)
        total_trips = len(self.workflow_df)
        valid_trips = len(self.workflow_df[self.workflow_df['validation_status'] == STATUS_VALID])

        completion_rate = (valid_trips / total_trips * 100) if total_trips > 0 else 0

        logger.info(f"  Total trips (in workflow): {total_trips:,}")
        logger.info(f"  Valid trips: {valid_trips:,}")
        logger.info(f"  Completion Rate: {completion_rate:.2f}%")

        return completion_rate

    def calculate_avg_trip_duration(self) -> float:
        """
        Metric 2: Average Trip Duration
        Mean time from pickup to dropoff in minutes

        Returns:
            Average duration in minutes
        """
        logger.info("Calculating Metric 2: Average Trip Duration")

        df = self.workflow_df[self.workflow_df['validation_status'] == STATUS_VALID]
        avg_duration = df['trip_duration_minutes'].mean()

        logger.info(f"  Average duration: {avg_duration:.2f} minutes")
        logger.info(f"  Median duration: {df['trip_duration_minutes'].median():.2f} minutes")
        logger.info(f"  Min duration: {df['trip_duration_minutes'].min():.2f} minutes")
        logger.info(f"  Max duration: {df['trip_duration_minutes'].max():.2f} minutes")

        return avg_duration

    def calculate_revenue_per_mile(self) -> float:
        """
        Metric 3: Revenue per Mile
        Average total fare divided by trip distance

        Returns:
            Revenue per mile in dollars
        """
        logger.info("Calculating Metric 3: Revenue per Mile")

        df = self.workflow_df[self.workflow_df['validation_status'] == STATUS_VALID]

        # Exclude trips with zero or very small distance
        df_with_distance = df[df['trip_distance'] >= 0.1]

        if len(df_with_distance) == 0:
            logger.warning("  No trips with measurable distance")
            return 0.0

        revenue_per_mile = df_with_distance['revenue_per_mile'].mean()

        logger.info(f"  Trips analyzed: {len(df_with_distance):,}")
        logger.info(f"  Average revenue per mile: ${revenue_per_mile:.2f}")
        logger.info(f"  Median revenue per mile: ${df_with_distance['revenue_per_mile'].median():.2f}")

        return revenue_per_mile

    def calculate_peak_hour_utilization(self) -> float:
        """
        Metric 4: Peak Hour Utilization
        Percentage of trips occurring during peak hours

        Returns:
            Peak hour utilization as percentage
        """
        logger.info("Calculating Metric 4: Peak Hour Utilization")

        df = self.workflow_df[self.workflow_df['validation_status'] == STATUS_VALID]

        total_trips = len(df)
        peak_trips = df['is_peak_hour'].sum()

        utilization = (peak_trips / total_trips * 100) if total_trips > 0 else 0

        logger.info(f"  Total trips: {total_trips:,}")
        logger.info(f"  Peak hour trips: {peak_trips:,}")
        logger.info(f"  Peak Hour Utilization: {utilization:.2f}%")

        return utilization

    def calculate_geographic_coverage_quality(self) -> float:
        """
        Metric 5: Geographic Coverage Quality
        Percentage of trips with successfully matched zones

        Returns:
            Coverage quality as percentage
        """
        logger.info("Calculating Metric 5: Geographic Coverage Quality")

        df = self.workflow_df[self.workflow_df['validation_status'] == STATUS_VALID]

        total_trips = len(df)
        trips_with_zones = len(df[df['pickup_zone'].notna() & df['dropoff_zone'].notna()])

        coverage_quality = (trips_with_zones / total_trips * 100) if total_trips > 0 else 0

        logger.info(f"  Total trips: {total_trips:,}")
        logger.info(f"  Trips with valid zones: {trips_with_zones:,}")
        logger.info(f"  Coverage Quality: {coverage_quality:.2f}%")

        return coverage_quality

    def calculate_all_metrics(self) -> Dict[str, float]:
        """
        Calculate all metrics

        Returns:
            Dictionary of metric name -> value
        """
        logger.info("=" * 60)
        logger.info("CALCULATING OPERATIONAL METRICS")
        logger.info("=" * 60)

        self.metrics = {
            'trip_completion_rate': self.calculate_trip_completion_rate(),
            'avg_trip_duration_minutes': self.calculate_avg_trip_duration(),
            'revenue_per_mile': self.calculate_revenue_per_mile(),
            'peak_hour_utilization': self.calculate_peak_hour_utilization(),
            'geographic_coverage_quality': self.calculate_geographic_coverage_quality(),
        }

        logger.info("=" * 60)
        logger.info("ALL METRICS CALCULATED")
        logger.info("=" * 60)

        return self.metrics

    def generate_metrics_table(self, period: str = "sample") -> pd.DataFrame:
        """
        Generate metrics table for output

        Args:
            period: Time period label (e.g., "2024-01")

        Returns:
            DataFrame with metrics
        """
        metrics_data = []

        for metric_name, metric_value in self.metrics.items():
            metrics_data.append({
                'period': period,
                'metric_name': metric_name,
                'metric_value': metric_value,
                'calculated_at': datetime.now().isoformat(),
            })

        return pd.DataFrame(metrics_data)

    def generate_detailed_breakdown(self) -> Dict:
        """
        Generate detailed breakdown by segments

        Returns:
            Dictionary with breakdowns
        """
        logger.info("Generating detailed breakdowns...")

        df = self.workflow_df[self.workflow_df['validation_status'] == STATUS_VALID]

        breakdown = {
            'by_hour': {},
            'by_day_of_week': {},
            'by_borough': {},
            'by_trip_type': {},
            'by_payment_method': {},
        }

        # By hour
        for hour in range(24):
            hour_df = df[df['pickup_hour'] == hour]
            if len(hour_df) > 0:
                breakdown['by_hour'][hour] = {
                    'trip_count': len(hour_df),
                    'avg_duration': float(hour_df['trip_duration_minutes'].mean()),
                    'avg_fare': float(hour_df['total_amount'].mean()),
                }

        # By day of week
        for day in df['pickup_day_of_week'].unique():
            day_df = df[df['pickup_day_of_week'] == day]
            breakdown['by_day_of_week'][day] = {
                'trip_count': len(day_df),
                'avg_duration': float(day_df['trip_duration_minutes'].mean()),
                'avg_fare': float(day_df['total_amount'].mean()),
            }

        # By pickup borough
        for borough in df['pickup_borough'].dropna().unique():
            borough_df = df[df['pickup_borough'] == borough]
            breakdown['by_borough'][borough] = {
                'trip_count': len(borough_df),
                'avg_duration': float(borough_df['trip_duration_minutes'].mean()),
                'avg_fare': float(borough_df['total_amount'].mean()),
            }

        # By trip type
        for trip_type in df['trip_type'].unique():
            type_df = df[df['trip_type'] == trip_type]
            breakdown['by_trip_type'][trip_type] = {
                'trip_count': len(type_df),
                'avg_duration': float(type_df['trip_duration_minutes'].mean()),
                'avg_fare': float(type_df['total_amount'].mean()),
            }

        # By payment method
        for payment in df['payment_method'].dropna().unique():
            payment_df = df[df['payment_method'] == payment]
            breakdown['by_payment_method'][payment] = {
                'trip_count': len(payment_df),
                'avg_fare': float(payment_df['total_amount'].mean()),
            }

        return breakdown


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("NYC TAXI METRICS CALCULATION STARTED")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info("=" * 60)

    # Load workflow data
    workflow_path = VALIDATED_DATA_DIR / "trips_workflow.parquet"
    if not workflow_path.exists():
        logger.error(f"Workflow data not found: {workflow_path}")
        logger.error("Run workflow_model.py first to build workflow model")
        return 1

    workflow_df = pd.read_parquet(workflow_path)
    logger.info(f"Loaded {len(workflow_df)} workflow records")

    # Calculate metrics
    calculator = MetricsCalculator(workflow_df)
    metrics = calculator.calculate_all_metrics()

    # Generate metrics table
    metrics_table = calculator.generate_metrics_table(period="202401")
    metrics_csv_path = OUTPUT_DATA_DIR / "metrics_202401.csv"
    metrics_table.to_csv(metrics_csv_path, index=False)
    logger.info(f"Metrics table saved to: {metrics_csv_path}")

    # Generate detailed breakdown
    breakdown = calculator.generate_detailed_breakdown()
    breakdown_path = OUTPUT_DATA_DIR / "metrics_breakdown.json"
    with open(breakdown_path, 'w') as f:
        json.dump(breakdown, f, indent=2)
    logger.info(f"Detailed breakdown saved to: {breakdown_path}")

    # Display metrics
    logger.info("\n" + "=" * 60)
    logger.info("FINAL METRICS SUMMARY")
    logger.info("=" * 60)
    for metric_name, metric_value in metrics.items():
        logger.info(f"{metric_name}: {metric_value:.2f}")

    logger.info("\n" + "=" * 60)
    logger.info("METRICS CALCULATION COMPLETE")
    logger.info("=" * 60)
    logger.info("\nNext step: Run full pipeline (python src/pipeline/main_pipeline.py)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
