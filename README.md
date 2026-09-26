<div align="center">

# 🚕 NYC Taxi Operations Analytics Pipeline

*Enterprise Data Engineering Solution for Operational Intelligence*

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Pipeline Status](https://img.shields.io/badge/pipeline-passing-brightgreen.svg)]()
[![Data Quality](https://img.shields.io/badge/data%20quality-98.9%25-success.svg)]()

**From fragmented taxi data to actionable business metrics through dependable, production-ready pipelines.**

</div>

---

## 📋 Problem & Solution

**Challenge:** NYC taxi fleet managers face inefficient operations due to fragmented data across multiple systems, with no unified view of trip performance or service quality.

**Solution:** End-to-end FDE pipeline that consolidates NYC TLC data, implements business-informed validation, models trip workflows, and generates 5 operational metrics for fleet allocation decisions.

**Business Impact:**
- **Fleet Managers:** Optimize vehicle deployment with peak hour insights
- **Operations:** Monitor data quality (98.9% completion rate) proactively  
- **Finance:** Track revenue efficiency ($19.34/mile average)
- **Regulators:** Ensure service compliance standards

---

## 🎯 Key Features

**Multi-Source Data Ingestion**
- NYC TLC Trip Records (Parquet, 10K+ trips)
- Taxi Zone Lookup (CSV, 265 zones)
- Preserves raw data as immutable source of truth

**Intelligent Validation**
- Business-oriented rules (not just schema checks)
- 98.9% validation pass rate with detailed failure tracking
- Explicit documentation of assumptions and limitations

**Workflow Modeling**
- Entity relationships: Trips ↔ Zones ↔ Time Segments
- Derived metrics: Peak hours, trip types, revenue efficiency
- Geographic and temporal pattern analysis

**Production Metrics**
1. Trip Completion Rate: 100%
2. Avg Trip Duration: 20.1 minutes
3. Revenue per Mile: $19.34
4. Peak Hour Utilization: 11.5%
5. Geographic Coverage: 100%

**Enterprise Reliability**
- Checkpointing & error recovery
- Comprehensive logging & audit trail
- Retry logic for network failures

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/vanshitm12/fde-nyc-taxi-pipeline.git
cd fde-nyc-taxi-pipeline

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run pipeline
python src/pipeline/main_pipeline.py

# View dashboard
open data/output/dashboard_advanced_202401.html
```

**Output:**
- `dashboard_advanced_202401.html` - Interactive dashboard with charts
- `metrics_202401.csv` - 5 key metrics
- `quality_report.json` - Validation statistics
- `workflow_summary.json` - Business insights

---

## 🏗️ Architecture

```
NYC TLC Sources → Ingest → Validate → Model → Metrics → Dashboard
     ↓              ↓         ↓         ↓         ↓
  Raw Data    Preserved   Quality    Enriched   Reports
                         Checked     Workflow
```

**Pipeline Phases:**
1. **INGEST:** Fetch data from NYC TLC (CSV/Parquet)
2. **VALIDATE:** Apply business rules, track failures
3. **MODEL:** Build workflow entities with zone mapping
4. **METRICS:** Calculate 5 operational KPIs
5. **OUTPUT:** Generate interactive dashboard

---

## 📁 Project Structure

```
fde-nyc-taxi-pipeline/
├── data/
│   ├── raw/              # Source data (CSV, Parquet)
│   ├── validated/        # Quality-checked data
│   └── output/           # 📊 Metrics & dashboard
├── src/
│   ├── ingestion/        # Data retrieval
│   ├── validation/       # Business rules
│   ├── modeling/         # Workflow logic
│   ├── metrics/          # KPI calculation
│   ├── pipeline/         # Orchestration
│   └── dashboard/        # Visualization
├── docs/                 # Architecture & source mapping
├── notebooks/            # Jupyter analysis
└── logs/                 # Execution logs
```

---

## 📊 Data Sources

| Source | Format | Records | Purpose |
|--------|--------|---------|---------|
| **NYC TLC Trip Records** | Parquet | 10,000 | Trip events (pickup → dropoff) |
| **Taxi Zone Lookup** | CSV | 265 | Geographic reference data |

**Source URLs:**
- Trip Data: `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_YYYY-MM.parquet`
- Zone Lookup: `https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv`

**Data Owner:** NYC Taxi & Limousine Commission (Public Dataset)

---

## 🔑 Key FDE Judgment: Zero-Distance Trips

**Problem:** 3-5% of trips show `distance = 0` but positive fares/durations.

**Decision:** Accept if `duration ≥ 2 min` AND `fare ≥ $2.50`

**Rationale:** NYC taxis charge for waiting time. Rejecting all would undercount revenue by 2%; accepting all would include data errors.

**Implementation:**
```python
if distance == 0:
    if duration_minutes >= 2 and fare >= 2.50:
        return STATUS_VALID  # Waiting time charge
    else:
        return STATUS_INVALID  # Data error
```

**Impact:** Correctly categorizes 100 trips (~1%): 53 valid, 47 invalid

**Documentation:** Code comments, config thresholds, README assumptions

---

## 🧠 Known / Unknown / Assumptions / Limitations

**✅ Known**
- Data grain: One record per completed trip
- Valid LocationIDs: 1-263 per TLC zone file
- Peak hours: 7-9 AM, 5-7 PM weekdays
- Sample size: 10,000 trips for demonstration

**❓ Unknown**
- Cancelled trips (not in records)
- Driver breaks/availability
- Passenger no-shows
- Trip requests vs. actual trips

**📝 Assumptions**
- Trip duration 1-180 minutes is valid
- Zero distance with fare ≥$2.50 and duration ≥2min = valid waiting charge
- Negative fares = data errors (not refunds)
- Same pickup/dropoff zone = valid (short trips)

**⚠️ Limitations**
- Sample data (10K trips for demo; production uses millions)
- Batch processing only (no real-time streaming)
- Static zone lookup (boundary changes not tracked)
- No external factors (weather, traffic, events)

---

## 🧪 Testing

```bash
# Full pipeline test
python src/pipeline/main_pipeline.py --reset-checkpoint

# Individual modules
python src/ingestion/fetch_csv.py
python src/validation/validators.py
python src/modeling/workflow_model.py
python src/metrics/calculator.py

# View logs
tail -50 logs/pipeline_*.log
```

---

## 🚀 Future Enhancements

- Real-time streaming with Kafka/Flink
- Machine learning: Demand forecasting & anomaly detection
- Interactive geographic visualization (Folium/Deck.gl)
- External data integration (weather, traffic, events)
- REST API for metric access

---

## 📖 Documentation

- **docs/source_map.md** - Complete source system documentation
- **docs/workflow_diagram.md** - Architecture diagrams & workflow details
- **QUICKSTART.md** - 5-minute setup guide
- **DEPLOYMENT_SUMMARY.md** - Full deployment documentation

---

## 📊 Dashboard Location

**Advanced Dashboard (Interactive):**
```
data/output/dashboard_advanced_202401.html
```

Features: Plotly charts, hourly distributions, borough analysis, responsive design

---

## 🤝 Contributing

```bash
git clone https://github.com/vanshitm12/fde-nyc-taxi-pipeline.git
cd fde-nyc-taxi-pipeline
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Make changes, test, commit, push
```

---

## 📜 License

MIT License - Educational project for FDE Data Foundations Assignment

---

## 📧 Contact

**Vanshit Malik**  
🔗 [GitHub](https://github.com/vanshitm12)

**Issues:** [Report Bugs](https://github.com/vanshitm12/fde-nyc-taxi-pipeline/issues)

---

<div align="center">

**⭐ Star this repo if you found it helpful!**

*Building trustworthy data pipelines, one validation rule at a time.*

</div>
