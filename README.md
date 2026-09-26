# NYC Taxi Operations Pipeline - FDE Assignment

## Problem Statement

**Business Problem:** NYC taxi operators need to understand trip performance, driver efficiency, and service quality to optimize operations and improve customer satisfaction.

**Users/Stakeholders:**
- Fleet managers: Need operational metrics to allocate vehicles efficiently
- Operations team: Monitor service quality and identify problem areas
- Finance team: Understand revenue patterns and pricing effectiveness
- City regulators: Track compliance and service standards

**Project KPI:** **Trip Completion Rate & Operational Efficiency**
- Primary metric: Percentage of successful trips with valid duration/distance
- Supporting metrics: Average trip duration, revenue per mile, peak hour utilization, geographic coverage quality

## Data Sources Overview

### Source 1: NYC TLC Trip Records (CSV/Parquet)
- **Owner:** NYC Taxi & Limousine Commission
- **Grain:** One record per completed trip
- **Access:** Public dataset via NYC Open Data portal
- **Fields:** pickup/dropoff datetime, locations, distances, fares, payment types
- **Retrieval:** Direct file download (CSV format)

### Source 2: NYC Taxi Zone Lookup (CSV)
- **Owner:** NYC TLC
- **Grain:** One record per taxi zone
- **Access:** Public reference data
- **Fields:** LocationID, Borough, Zone name, service_zone
- **Retrieval:** Static CSV file

### Source 3: Weather/External API (Optional Enhancement)
- **Owner:** External weather service
- **Purpose:** Correlate trip patterns with weather conditions

## Workflow Model

```
Raw Trip Event → Validation → Enrichment → Trip Workflow State → Metrics
     ↓               ↓            ↓              ↓                  ↓
  Ingest         Quality      Add zones      Completed          Dashboard
               Check rules    & segments     /Invalid
```

**Entities:**
- **Trip**: Core event with pickup/dropoff, fare, distance
- **Zone**: Geographic region (linked via LocationID)
- **Time Segment**: Hour, day, month classification

**States:**
- Valid: Passes all validation rules
- Invalid: Fails validation (logged with reasons)
- Suspicious: Edge cases requiring review

## Key Metrics

1. **Trip Completion Rate**: % of valid trips / total trips ingested
2. **Average Trip Duration**: Mean time from pickup to dropoff (minutes)
3. **Revenue per Mile**: Total fare amount / trip distance
4. **Peak Hour Utilization**: % of trips during peak hours (7-9 AM, 5-7 PM)
5. **Geographic Coverage Quality**: % of trips with valid zone mapping

## Setup & Installation

### Prerequisites
- Python 3.8+
- pip
- 500MB disk space for sample data

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd fde-nyc-taxi-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Pipeline

### Quick Start

```bash
# Run the complete pipeline
python src/pipeline/main_pipeline.py

# Run with specific month
python src/pipeline/main_pipeline.py --month 2024-01

# View logs
tail -f logs/pipeline_$(date +%Y%m%d).log
```

### Step-by-Step Execution

```bash
# 1. Fetch raw data
python src/ingestion/fetch_csv.py

# 2. Validate data
python src/validation/validators.py

# 3. Build workflow model
python src/modeling/workflow_model.py

# 4. Calculate metrics
python src/metrics/calculator.py
```

### Jupyter Notebooks

```bash
# Launch Jupyter
jupyter notebook

# Open notebooks in order:
# 1. notebooks/01_data_exploration.ipynb
# 2. notebooks/02_validation_analysis.ipynb
# 3. notebooks/03_metrics_dashboard.ipynb
```

## Output

The pipeline produces:
- **data/output/metrics_YYYYMM.csv**: Monthly metrics table
- **data/output/quality_report_YYYYMM.json**: Data quality summary
- **data/output/dashboard_YYYYMM.html**: Interactive metrics dashboard
- **logs/pipeline_YYYYMMDD.log**: Execution logs with validation details

## Decision Support

This pipeline supports the following decisions:

1. **Fleet Allocation**: Use peak hour utilization and geographic coverage to deploy vehicles efficiently
2. **Quality Improvement**: Identify zones/times with high invalid trip rates for operational review
3. **Pricing Strategy**: Revenue per mile trends inform dynamic pricing decisions
4. **Compliance Monitoring**: Trip completion rate ensures regulatory standards are met

## Known / Unknown / Assumptions / Limitations

### Known
- Trip data grain: one row per completed trip
- Valid LocationIDs range: 1-263 based on TLC zone file
- Peak hours defined: 7-9 AM, 5-7 PM weekdays
- Fare calculation includes base fare, distance, time, surcharges

### Unknown
- Cancelled trips: not captured in trip records
- Driver breaks: no distinction between idle and off-duty
- Passenger no-shows: not tracked separately
- Multi-passenger shared rides: counted as single trip

### Assumptions
- Trip duration > 0 and < 180 minutes is valid
- Trip distance > 0 and < 100 miles is valid
- Negative fares are data errors (not refunds)
- Trips with distance=0 are valid (waiting time charges)
- Same pickup/dropoff zone can be valid short trip

### Limitations
- Sample data: using 1-2 months for demonstration (full production would use years)
- No real-time streaming: batch processing only
- Zone lookup: static file, doesn't track zone boundary changes over time
- Payment failures: not distinguished from fare disputes
- External factors: weather, events, traffic not incorporated in base pipeline

## Project Structure

```
fde-nyc-taxi-pipeline/
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
├── docs/
│   ├── source_map.md          # Detailed source system documentation
│   └── workflow_diagram.png   # Visual workflow representation
├── data/
│   ├── raw/                   # Raw ingested data (preserved)
│   ├── validated/             # Cleaned, validated data
│   └── output/                # Final metrics and reports
├── src/
│   ├── config.py              # Configuration and constants
│   ├── ingestion/             # Data retrieval modules
│   ├── validation/            # Data quality rules
│   ├── modeling/              # Workflow model logic
│   ├── metrics/               # Metric calculations
│   └── pipeline/              # Main orchestration
├── notebooks/                 # Jupyter analysis notebooks
├── logs/                      # Pipeline execution logs
└── tests/                     # Unit tests

```

## Demo Video Guide

For the 3-5 minute demo, focus on:
1. **Problem context** (30 sec): Why this matters to taxi operations
2. **One key FDE judgment** (2 min): Example - "How we handle trips with same pickup/dropoff zone"
   - Show the validation rule
   - Explain why we kept them (waiting time charges are valid)
   - Show the assumption documented
   - Demonstrate impact on metrics
3. **Pipeline run** (1 min): Show end-to-end execution
4. **Output & decision** (1 min): Show metrics and what decision it supports

## Important FDE Judgment Call

**Decision: How to handle trips with zero distance**

Many trips show `trip_distance = 0` but positive fare and duration. 

**Options considered:**
1. Reject as invalid data
2. Accept all zero-distance trips
3. Accept if duration > threshold and fare > minimum

**Decision made:** Option 3 - Accept zero-distance trips if:
- Duration >= 2 minutes (not a data glitch)
- Fare >= $2.50 (NYC minimum fare)
- Pickup time != Dropoff time

**Rationale:**
- NYC taxis charge for waiting time and stopped traffic
- Short trips in same zone are valid (e.g., train station to nearby hotel)
- Complete rejection would undercount revenue
- Overly permissive acceptance would include data errors

**Impact:** Affects ~3-5% of trips, changes revenue metrics by ~2%

**Documented in:** validation rules with business context

## Author

Created for FDE Data Foundations Assignment (Classes 4-8)

## License

MIT License - Educational project
