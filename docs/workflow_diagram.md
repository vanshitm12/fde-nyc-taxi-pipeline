# Workflow Diagram

## Trip Workflow State Machine

```mermaid
graph TB
    Start([Raw Trip Event]) --> Ingest[Ingest: Fetch from TLC]
    Ingest --> Preserve[Preserve: Save raw CSV/Parquet]
    Preserve --> Validate[Validate: Apply quality rules]
    
    Validate --> ValidQ{Passes all<br/>validation?}
    
    ValidQ -->|Yes| Valid[State: VALID]
    ValidQ -->|No Critical| Invalid[State: INVALID]
    ValidQ -->|Edge Case| Suspicious[State: SUSPICIOUS]
    
    Valid --> Enrich[Enrich: Add zone info]
    Suspicious --> Enrich
    
    Enrich --> Transform[Transform: Calculate derived fields]
    Transform --> Model[Model: Build trip workflow]
    
    Model --> Segment[Segment by time/location]
    Segment --> Metrics[Calculate metrics]
    
    Metrics --> Output[Output: Dashboard & Reports]
    
    Invalid --> Log[Log: Record failure reason]
    Log --> Investigate[Manual investigation queue]
    
    style Valid fill:#90EE90
    style Invalid fill:#FFB6C1
    style Suspicious fill:#FFD700
    style Output fill:#87CEEB
```

## Entity Relationship Model

```mermaid
erDiagram
    TRIP {
        int trip_id PK
        timestamp pickup_datetime
        timestamp dropoff_datetime
        int pickup_location_id FK
        int dropoff_location_id FK
        decimal trip_distance
        decimal fare_amount
        decimal total_amount
        int payment_type
        int passenger_count
        string validation_status
    }
    
    ZONE {
        int location_id PK
        string borough
        string zone_name
        string service_zone
    }
    
    TIME_SEGMENT {
        int segment_id PK
        date trip_date
        int hour_of_day
        string day_of_week
        bool is_peak_hour
        bool is_weekend
    }
    
    TRIP_METRICS {
        int metric_id PK
        string period
        int total_trips
        int valid_trips
        decimal avg_duration
        decimal avg_distance
        decimal revenue_per_mile
        decimal completion_rate
    }
    
    TRIP ||--o{ ZONE : "pickup_zone"
    TRIP ||--o{ ZONE : "dropoff_zone"
    TRIP ||--|| TIME_SEGMENT : "occurs_during"
    TRIP }o--|| TRIP_METRICS : "aggregates_to"
```

## Data Flow Pipeline

```mermaid
flowchart LR
    A[TLC API/Files] -->|Download| B[Raw Storage]
    B -->|Read| C[Validation Engine]
    
    C -->|Pass| D[Validated Storage]
    C -->|Fail| E[Error Log]
    
    D -->|Load| F[Transformation Layer]
    Z[Zone Lookup] -->|Join| F
    
    F -->|Process| G[Workflow Model]
    G -->|Aggregate| H[Metrics Calculator]
    
    H -->|Generate| I[CSV Report]
    H -->|Generate| J[JSON Quality]
    H -->|Generate| K[HTML Dashboard]
    
    E -->|Alert| L[Operations Team]
    
    style B fill:#FFE4B5
    style D fill:#90EE90
    style E fill:#FFB6C1
    style I fill:#87CEEB
    style J fill:#87CEEB
    style K fill:#87CEEB
```

## Pipeline Orchestration

```
┌─────────────────────────────────────────────────────────────┐
│                     MAIN PIPELINE                            │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  PHASE 1   │  │  PHASE 2   │  │  PHASE 3   │           │
│  │  INGEST    │→ │  VALIDATE  │→ │  TRANSFORM │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│        ↓              ↓                ↓                    │
│   [Raw Files]   [Quality Report]  [Enriched Data]          │
│                                                              │
│  ┌────────────┐  ┌────────────┐                            │
│  │  PHASE 4   │  │  PHASE 5   │                            │
│  │  MODEL     │→ │  METRICS   │                            │
│  └────────────┘  └────────────┘                            │
│        ↓              ↓                                     │
│  [Workflow DB]   [Dashboard + Reports]                     │
│                                                              │
│  ┌──────────────────────────────────────┐                  │
│  │     CROSS-CUTTING CONCERNS           │                  │
│  │  • Logging (every phase)             │                  │
│  │  • Error handling (try/catch/log)    │                  │
│  │  • Progress tracking (% complete)    │                  │
│  │  • Checkpointing (resume on failure) │                  │
│  │  • Alerting (critical failures)      │                  │
│  └──────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## Metric Calculation Flow

```
Valid Trips (filtered)
    │
    ├─→ Count → Trip Completion Rate = valid / total * 100
    │
    ├─→ Duration Calc → avg(dropoff_time - pickup_time)
    │
    ├─→ Revenue Calc → avg(total_amount / trip_distance)
    │                   [exclude distance = 0]
    │
    ├─→ Time Filter → Peak Hours (7-9 AM, 5-7 PM weekdays)
    │              → Peak Utilization = peak_trips / total * 100
    │
    └─→ Zone Join → Count distinct zones
                 → Coverage Quality = matched / total * 100
```

## Validation Decision Tree

```
Trip Record
    │
    ├─ Is pickup_time valid datetime?
    │   NO → INVALID (reason: bad_pickup_time)
    │   YES ↓
    │
    ├─ Is dropoff_time > pickup_time?
    │   NO → INVALID (reason: time_paradox)
    │   YES ↓
    │
    ├─ Is duration < 180 minutes?
    │   NO → SUSPICIOUS (reason: extremely_long_trip)
    │   YES ↓
    │
    ├─ Is trip_distance >= 0 and < 100 miles?
    │   NO → INVALID (reason: impossible_distance)
    │   YES ↓
    │
    ├─ Is trip_distance = 0?
    │   YES → Check duration > 2 min AND fare > $2.50
    │         YES → VALID (reason: waiting_time_charge)
    │         NO → INVALID (reason: zero_distance_zero_fare)
    │   NO ↓
    │
    ├─ Is fare_amount < 0?
    │   YES → INVALID (reason: negative_fare)
    │   NO ↓
    │
    ├─ Are location IDs in range 1-263?
    │   NO → SUSPICIOUS (reason: unknown_zone)
    │   YES ↓
    │
    └─ VALID (passed all checks)
```

## Key Business Rules

### Rule 1: Trip Duration Bounds
- **Min:** 1 minute (excludes spurious records)
- **Max:** 180 minutes (3 hours - flags unusual trips)
- **Rationale:** 99% of trips are under 2 hours; >3 hours likely data error or exceptional case

### Rule 2: Distance Validation
- **Min:** 0 miles (allow stopped traffic charges)
- **Max:** 100 miles (NYC metro area practical limit)
- **Special:** 0 distance requires duration >= 2 min AND fare >= $2.50
- **Rationale:** Zero distance can be valid (waiting charges) but not zero time+fare

### Rule 3: Fare Validation
- **Min:** $0 (allow no-charge trips)
- **No negative:** Refunds not in trip records
- **Max:** None (no upper bound, some trips to airports are expensive)
- **Rationale:** Negative fares are data errors, not business logic

### Rule 4: Geographic Validation
- **LocationID:** Must be 1-263 per zone lookup
- **Exception:** 264-265 appear in data - flag as SUSPICIOUS not INVALID
- **Same pickup/dropoff:** VALID (short trips within zone)
- **Rationale:** Strict validation on known IDs, graceful handling of edge cases

### Rule 5: Time Validation
- **Pickup:** Must be valid datetime, not future
- **Dropoff:** Must be after pickup
- **Max lookback:** No limit (historical data OK)
- **Rationale:** Logical consistency required, historical analysis accepted

## Operational Workflow States

### VALID
- Passed all validation rules
- Included in metrics calculations
- ~95-97% of trips expected

### SUSPICIOUS
- Edge case that needs review
- Included in metrics with flag
- Logged for manual investigation
- Examples: very long trips, unknown zones
- ~1-3% of trips expected

### INVALID
- Critical validation failure
- Excluded from metrics
- Logged with specific reason code
- Examples: negative fare, time paradox, missing required fields
- ~1-2% of trips expected

## Pipeline Failure Handling

### Failure Types

**Transient Failures:**
- Network timeout during download
- **Action:** Retry up to 3 times with exponential backoff
- **Log:** Warning level

**Data Quality Failures:**
- High % of invalid trips (>10%)
- **Action:** Complete pipeline, raise alert, flag report
- **Log:** Warning level + alert

**Critical Failures:**
- Cannot download source data
- Cannot write to output
- Code exception/crash
- **Action:** Stop pipeline, log full traceback, send alert
- **Log:** Error level + alert

### Checkpointing
- After each phase completes, write checkpoint file
- On restart, check for checkpoint and resume from last completed phase
- Prevents re-downloading data on validation failure

### Idempotency
- Pipeline can be run multiple times for same period
- Overwrites previous output files
- Raw data preserved (never deleted by pipeline)
