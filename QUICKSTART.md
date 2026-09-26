# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Setup Environment

```bash
cd fde-nyc-taxi-pipeline

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run the Pipeline

```bash
# Run complete pipeline
python src/pipeline/main_pipeline.py
```

This will:
1. ✅ Fetch zone lookup data from TLC
2. ✅ Create sample trip data (10,000 records for demo)
3. ✅ Validate all records with business rules
4. ✅ Build workflow model with derived fields
5. ✅ Calculate 5 operational metrics
6. ✅ Generate HTML dashboard

**Expected output:**
```
============================================================
NYC TAXI PIPELINE COMPLETED SUCCESSFULLY
============================================================
Duration: XX.XX seconds
Phases completed: 5
Records processed: 9,XXX

Output files in: data/output
```

### Step 3: View Results

```bash
# View metrics
cat data/output/metrics_202401.csv

# Open dashboard in browser
open data/output/dashboard_202401.html  # On Mac
# Or on Windows: start data/output/dashboard_202401.html
# Or on Linux: xdg-open data/output/dashboard_202401.html

# View logs
tail -100 logs/pipeline_$(date +%Y%m%d).log
```

### Step 4: Explore with Jupyter

```bash
# Start Jupyter
jupyter notebook

# Open notebooks/01_data_exploration.ipynb
```

---

## 📂 What Was Created

After running the pipeline, you'll find:

```
data/
├── raw/
│   ├── taxi_zone_lookup.csv          # 263 NYC taxi zones
│   └── yellow_tripdata_sample.parquet # 10,000 sample trips
├── validated/
│   ├── trips_validated.parquet        # Validated trips with status
│   └── trips_workflow.parquet         # Enriched workflow model
└── output/
    ├── metrics_202401.csv             # 5 key metrics
    ├── dashboard_202401.html          # Interactive dashboard ← OPEN THIS
    ├── quality_report.json            # Validation statistics
    ├── workflow_summary.json          # Workflow summary
    └── metrics_breakdown.json         # Detailed breakdowns

logs/
└── pipeline_YYYYMMDD.log              # Execution logs
```

---

## 🔧 Running Individual Modules

If you want to run steps separately:

```bash
# Step 1: Ingest data
python src/ingestion/fetch_csv.py

# Step 2: Validate
python src/validation/validators.py

# Step 3: Build workflow model
python src/modeling/workflow_model.py

# Step 4: Calculate metrics
python src/metrics/calculator.py
```

---

## 🧪 Testing the Pipeline

### Test with Reset

```bash
# Run from scratch (clears checkpoint)
python src/pipeline/main_pipeline.py --reset-checkpoint
```

### Test Checkpoint/Recovery

```bash
# Run pipeline
python src/pipeline/main_pipeline.py

# Simulate failure by stopping it (Ctrl+C)
# Then run again - it will resume from last checkpoint
python src/pipeline/main_pipeline.py
```

---

## 📊 Understanding the Metrics

### 1. Trip Completion Rate: 95-97%
- **What it means:** Percentage of trips that passed all validation rules
- **Why it matters:** Indicates data quality - low rate means investigation needed
- **Decision support:** If rate drops below 90%, alert operations team

### 2. Average Trip Duration: ~15 minutes
- **What it means:** Mean time from pickup to dropoff
- **Why it matters:** Baseline for service level expectations
- **Decision support:** Track trends over time - increasing duration may indicate traffic issues

### 3. Revenue per Mile: ~$12-15
- **What it means:** Average fare divided by distance
- **Why it matters:** Pricing efficiency metric
- **Decision support:** Compare by borough to optimize pricing strategy

### 4. Peak Hour Utilization: 30-40%
- **What it means:** Percentage of trips during peak hours (7-9 AM, 5-7 PM weekdays)
- **Why it matters:** Fleet allocation efficiency
- **Decision support:** Low utilization = opportunity to shift vehicles to peak times

### 5. Geographic Coverage Quality: ~99%
- **What it means:** Percentage of trips with valid zone mapping
- **Why it matters:** Data completeness for location-based analysis
- **Decision support:** Drops indicate zone lookup table needs update

---

## 🎯 Key Files to Understand

For your demo video, focus on these:

1. **README.md** - Problem statement and overview
2. **src/validation/validators.py** - The zero-distance judgment logic (lines 105-125)
3. **src/config.py** - Validation rules and configuration
4. **data/output/dashboard_202401.html** - Final output

---

## ❓ Troubleshooting

### "ModuleNotFoundError"
```bash
# Make sure venv is activated and dependencies installed
source venv/bin/activate
pip install -r requirements.txt
```

### "File not found" errors
```bash
# Make sure you're in the project root
cd fde-nyc-taxi-pipeline
python src/pipeline/main_pipeline.py
```

### Pipeline runs but no output
```bash
# Check logs
ls -la logs/
cat logs/pipeline_*.log
```

### Want to use real TLC data instead of sample?
Edit `src/ingestion/fetch_csv.py`:
- Comment out line calling `create_sample_data()`
- Uncomment lines calling `fetch_trip_data()`
- Note: Real data is 300-500MB per month!

---

## 📝 Next Steps for Assignment Submission

1. ✅ **Test the pipeline** - Make sure everything runs
2. ✅ **Push to GitHub** - Create a public repo and push this code

---

## 🎥 Recording Your Demo


**Quick version:**
2. Show the problem (README)
3. Explain your zero-distance validation judgment (30 seconds of code walkthrough)
4. Run the pipeline
5. Show the dashboard output
6. Wrap up - 3-5 minutes total

---

## 📧 Questions?

- Check the main README.md
- Read docs/source_map.md for data source details
- Review docs/workflow_diagram.md for architecture

Good luck! 🚀
