"""
Main Pipeline - Orchestrates end-to-end data processing
Demonstrates: dependable pipeline with logging, error handling, checkpointing
"""
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
import json
import traceback
from typing import Dict, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    RAW_DATA_DIR,
    VALIDATED_DATA_DIR,
    OUTPUT_DATA_DIR,
    CHECKPOINT_FILE,
    CHECKPOINT_ENABLED,
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


class PipelineCheckpoint:
    """Manages pipeline checkpointing for recovery"""

    def __init__(self, checkpoint_file: Path):
        self.checkpoint_file = checkpoint_file
        self.checkpoint_data = self.load()

    def load(self) -> Dict:
        """Load checkpoint data"""
        if not self.checkpoint_file.exists():
            return {}

        try:
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load checkpoint: {e}")
            return {}

    def save(self, phase: str, status: str, metadata: Dict = None):
        """Save checkpoint"""
        self.checkpoint_data[phase] = {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(self.checkpoint_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def is_completed(self, phase: str) -> bool:
        """Check if phase is completed"""
        return phase in self.checkpoint_data and \
               self.checkpoint_data[phase]['status'] == 'completed'

    def reset(self):
        """Reset checkpoint"""
        self.checkpoint_data = {}
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()


class NYCTaxiPipeline:
    """Main pipeline orchestrator"""

    def __init__(self, period: str = "sample", skip_download: bool = False):
        """
        Initialize pipeline

        Args:
            period: Data period (e.g., "2024-01")
            skip_download: Skip data download if already exists
        """
        self.period = period
        self.skip_download = skip_download
        self.checkpoint = PipelineCheckpoint(CHECKPOINT_FILE) if CHECKPOINT_ENABLED else None
        self.pipeline_stats = {
            'start_time': datetime.now(),
            'end_time': None,
            'phases_completed': [],
            'phases_failed': [],
            'total_records_processed': 0,
        }

    def run_phase(self, phase_name: str, phase_func, skip_if_completed: bool = True):
        """
        Run a pipeline phase with error handling and checkpointing

        Args:
            phase_name: Name of the phase
            phase_func: Function to execute
            skip_if_completed: Skip if already completed in checkpoint

        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 60)
        logger.info(f"PHASE: {phase_name}")
        logger.info("=" * 60)

        # Check checkpoint
        if skip_if_completed and self.checkpoint and self.checkpoint.is_completed(phase_name):
            logger.info(f"Phase '{phase_name}' already completed (from checkpoint). Skipping.")
            return True

        try:
            # Execute phase
            result = phase_func()

            # Mark as completed
            if self.checkpoint:
                self.checkpoint.save(phase_name, 'completed', {'result': str(result)})

            self.pipeline_stats['phases_completed'].append(phase_name)
            logger.info(f"Phase '{phase_name}' completed successfully")
            return True

        except Exception as e:
            logger.error(f"Phase '{phase_name}' failed: {e}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")

            if self.checkpoint:
                self.checkpoint.save(phase_name, 'failed', {'error': str(e)})

            self.pipeline_stats['phases_failed'].append(phase_name)
            return False

    def phase_ingest(self):
        """Phase 1: Ingest data from sources"""
        logger.info("Starting data ingestion...")

        # Import ingestion modules
        from ingestion.fetch_csv import fetch_zone_lookup, create_sample_data

        # Fetch zone lookup
        zone_df, zone_path = fetch_zone_lookup()
        if zone_df is None:
            raise Exception("Failed to fetch zone lookup data")

        # Create/fetch trip data
        trip_df, trip_path = create_sample_data()
        if trip_df is None:
            raise Exception("Failed to fetch trip data")

        logger.info(f"Ingestion complete: {len(zone_df)} zones, {len(trip_df)} trips")
        return {'zones': len(zone_df), 'trips': len(trip_df)}

    def phase_validate(self):
        """Phase 2: Validate data"""
        logger.info("Starting data validation...")

        # Import validation modules
        import pandas as pd
        from validation.validators import TripValidator

        # Load data
        zone_path = RAW_DATA_DIR / "taxi_zone_lookup.csv"
        trip_path = RAW_DATA_DIR / "yellow_tripdata_sample.parquet"

        zone_df = pd.read_csv(zone_path)
        trip_df = pd.read_parquet(trip_path)

        # Create validator and validate
        validator = TripValidator(zone_df)
        profile = validator.profile_data(trip_df)
        validated_df = validator.validate_dataframe(trip_df)

        # Save results
        output_path = VALIDATED_DATA_DIR / "trips_validated.parquet"
        validated_df.to_parquet(output_path)

        quality_report = validator.get_quality_report()
        report_path = OUTPUT_DATA_DIR / "quality_report.json"
        with open(report_path, 'w') as f:
            json.dump(quality_report, f, indent=2)

        self.pipeline_stats['total_records_processed'] = len(validated_df)

        logger.info(f"Validation complete: {quality_report['validation_stats']['valid']} valid trips")
        return quality_report

    def phase_model(self):
        """Phase 3: Build workflow model"""
        logger.info("Starting workflow modeling...")

        # Import modeling modules
        import pandas as pd
        from modeling.workflow_model import TripWorkflowModel

        # Load data
        zone_path = RAW_DATA_DIR / "taxi_zone_lookup.csv"
        trip_path = VALIDATED_DATA_DIR / "trips_validated.parquet"

        zone_df = pd.read_csv(zone_path)
        trip_df = pd.read_parquet(trip_path)

        # Build model
        model = TripWorkflowModel(trip_df, zone_df)
        workflow_df = model.build_workflow_model()

        # Save results
        output_path = VALIDATED_DATA_DIR / "trips_workflow.parquet"
        workflow_df.to_parquet(output_path)

        summary = model.get_workflow_summary()
        summary_path = OUTPUT_DATA_DIR / "workflow_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info(f"Modeling complete: {summary['total_trips']} trips modeled")
        return summary

    def phase_metrics(self):
        """Phase 4: Calculate metrics"""
        logger.info("Starting metrics calculation...")

        # Import metrics modules
        import pandas as pd
        from metrics.calculator import MetricsCalculator

        # Load data
        workflow_path = VALIDATED_DATA_DIR / "trips_workflow.parquet"
        workflow_df = pd.read_parquet(workflow_path)

        # Calculate metrics
        calculator = MetricsCalculator(workflow_df)
        metrics = calculator.calculate_all_metrics()

        # Save results
        metrics_table = calculator.generate_metrics_table(period=self.period)
        metrics_csv_path = OUTPUT_DATA_DIR / f"metrics_{self.period}.csv"
        metrics_table.to_csv(metrics_csv_path, index=False)

        breakdown = calculator.generate_detailed_breakdown()
        breakdown_path = OUTPUT_DATA_DIR / "metrics_breakdown.json"
        with open(breakdown_path, 'w') as f:
            json.dump(breakdown, f, indent=2)

        logger.info(f"Metrics complete: {len(metrics)} metrics calculated")
        return metrics

    def phase_output(self):
        """Phase 5: Generate final output dashboard"""
        logger.info("Generating final output...")

        # Create a simple HTML dashboard
        html_content = self._generate_dashboard_html()

        output_path = OUTPUT_DATA_DIR / f"dashboard_{self.period}.html"
        with open(output_path, 'w') as f:
            f.write(html_content)

        logger.info(f"Dashboard saved to: {output_path}")
        return {'dashboard_path': str(output_path)}

    def _generate_dashboard_html(self) -> str:
        """Generate simple HTML dashboard"""
        # Load metrics
        metrics_path = OUTPUT_DATA_DIR / f"metrics_{self.period}.csv"
        import pandas as pd

        if not metrics_path.exists():
            return "<html><body><h1>No metrics available</h1></body></html>"

        metrics_df = pd.read_csv(metrics_path)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NYC Taxi Operations Dashboard - {self.period}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background-color: #FFD700;
                    color: #000;
                    padding: 20px;
                    border-radius: 5px;
                }}
                .metric-card {{
                    background-color: white;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .metric-value {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #4CAF50;
                }}
                .metric-name {{
                    font-size: 18px;
                    color: #666;
                    margin-bottom: 10px;
                }}
                .footer {{
                    margin-top: 40px;
                    padding: 20px;
                    background-color: #fff;
                    border-radius: 5px;
                    font-size: 14px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚕 NYC Taxi Operations Dashboard</h1>
                <p>Period: {self.period} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        """

        for _, row in metrics_df.iterrows():
            metric_name = row['metric_name'].replace('_', ' ').title()
            metric_value = row['metric_value']

            # Format value based on metric
            if 'rate' in row['metric_name'] or 'utilization' in row['metric_name'] or 'quality' in row['metric_name']:
                formatted_value = f"{metric_value:.2f}%"
            elif 'revenue' in row['metric_name']:
                formatted_value = f"${metric_value:.2f}"
            else:
                formatted_value = f"{metric_value:.2f}"

            html += f"""
            <div class="metric-card">
                <div class="metric-name">{metric_name}</div>
                <div class="metric-value">{formatted_value}</div>
            </div>
            """

        html += """
            <div class="footer">
                <h3>Known / Unknown / Assumptions / Limitations</h3>
                <h4>Known:</h4>
                <ul>
                    <li>Trip data includes completed trips only</li>
                    <li>Valid LocationIDs: 1-263 per TLC zone file</li>
                    <li>Peak hours: 7-9 AM, 5-7 PM weekdays</li>
                </ul>
                <h4>Unknown:</h4>
                <ul>
                    <li>Cancelled trips not captured</li>
                    <li>Driver breaks not tracked</li>
                    <li>Passenger no-shows not recorded</li>
                </ul>
                <h4>Assumptions:</h4>
                <ul>
                    <li>Trip duration 1-180 minutes is valid range</li>
                    <li>Zero distance trips with fare ≥ $2.50 are waiting charges</li>
                    <li>Negative fares are data errors</li>
                </ul>
                <h4>Limitations:</h4>
                <ul>
                    <li>Sample data used for demonstration</li>
                    <li>No real-time streaming capability</li>
                    <li>External factors (weather, events) not incorporated</li>
                </ul>
            </div>
        </body>
        </html>
        """

        return html

    def run(self) -> bool:
        """
        Run complete pipeline

        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 60)
        logger.info("NYC TAXI PIPELINE STARTED")
        logger.info(f"Period: {self.period}")
        logger.info(f"Timestamp: {self.pipeline_stats['start_time']}")
        logger.info("=" * 60)

        # Phase 1: Ingest
        if not self.run_phase("INGEST", self.phase_ingest):
            logger.error("Pipeline failed at INGEST phase")
            return False

        # Phase 2: Validate
        if not self.run_phase("VALIDATE", self.phase_validate):
            logger.error("Pipeline failed at VALIDATE phase")
            return False

        # Phase 3: Model
        if not self.run_phase("MODEL", self.phase_model):
            logger.error("Pipeline failed at MODEL phase")
            return False

        # Phase 4: Metrics
        if not self.run_phase("METRICS", self.phase_metrics):
            logger.error("Pipeline failed at METRICS phase")
            return False

        # Phase 5: Output
        if not self.run_phase("OUTPUT", self.phase_output):
            logger.error("Pipeline failed at OUTPUT phase")
            return False

        # Pipeline complete
        self.pipeline_stats['end_time'] = datetime.now()
        duration = (self.pipeline_stats['end_time'] - self.pipeline_stats['start_time']).total_seconds()

        logger.info("=" * 60)
        logger.info("NYC TAXI PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Phases completed: {len(self.pipeline_stats['phases_completed'])}")
        logger.info(f"Records processed: {self.pipeline_stats['total_records_processed']:,}")
        logger.info(f"\nOutput files in: {OUTPUT_DATA_DIR}")
        logger.info(f"Logs in: {get_log_filename()}")

        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='NYC Taxi Operations Pipeline')
    parser.add_argument('--period', default='202401', help='Data period (e.g., 202401)')
    parser.add_argument('--reset-checkpoint', action='store_true', help='Reset checkpoint and run from scratch')
    args = parser.parse_args()

    # Reset checkpoint if requested
    if args.reset_checkpoint:
        checkpoint = PipelineCheckpoint(CHECKPOINT_FILE)
        checkpoint.reset()
        logger.info("Checkpoint reset")

    # Run pipeline
    pipeline = NYCTaxiPipeline(period=args.period)
    success = pipeline.run()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
