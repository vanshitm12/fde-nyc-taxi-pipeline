# Data Source Map

## Business Question Mapping

| Business Question | Information Needed | Source System | Field(s) |
|-------------------|-------------------|---------------|----------|
| Are trips completing successfully? | Trip start/end times, status | TLC Trip Records | pickup_datetime, dropoff_datetime |
| How long do trips take? | Duration calculation | TLC Trip Records | pickup_datetime, dropoff_datetime |
| What's our revenue efficiency? | Fare and distance | TLC Trip Records | fare_amount, trip_distance |
| Where are trips happening? | Geographic zones | TLC Trip Records + Zone Lookup | PULocationID, DOLocationID, zone_name, borough |
| When is peak demand? | Time patterns | TLC Trip Records | pickup_datetime (hour extraction) |
| What payment methods are used? | Payment type | TLC Trip Records | payment_type |
| How many passengers per trip? | Passenger count | TLC Trip Records | passenger_count |

## Source System Details

### Source 1: NYC TLC Yellow Taxi Trip Records

**Owner:** NYC Taxi & Limousine Commission (TLC)  
**System Type:** Public dataset repository  
**Update Frequency:** Monthly (with 2-month delay)  
**Grain:** One record per completed taxi trip  
**Access Method:** Direct HTTPS download (CSV/Parquet)  
**URL Pattern:** `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_YYYY-MM.parquet`

**Schema:**

| Field Name | Data Type | Description | Validation Rule |
|------------|-----------|-------------|-----------------|
| VendorID | integer | Provider code (1=Creative, 2=VeriFone) | 1 or 2 |
| tpep_pickup_datetime | timestamp | Trip start time | Valid datetime, not future |
| tpep_dropoff_datetime | timestamp | Trip end time | After pickup, not future |
| passenger_count | integer | Number of passengers | 0-6 typical, 0 means not recorded |
| trip_distance | decimal | Distance in miles | >= 0, < 100 |
| RatecodeID | integer | Rate type (1=standard, 2=JFK, etc.) | 1-6 |
| store_and_fwd_flag | char | Y/N if trip stored before sending | Y or N |
| PULocationID | integer | Pickup taxi zone | 1-263 (validate against zone lookup) |
| DOLocationID | integer | Dropoff taxi zone | 1-263 (validate against zone lookup) |
| payment_type | integer | 1=Credit, 2=Cash, 3=No charge, 4=Dispute, 5=Unknown, 6=Voided | 1-6 |
| fare_amount | decimal | Base fare | >= 0 |
| extra | decimal | Extras and surcharges | >= 0 |
| mta_tax | decimal | MTA tax | >= 0 |
| tip_amount | decimal | Tip (credit cards only) | >= 0 |
| tolls_amount | decimal | Tolls | >= 0 |
| improvement_surcharge | decimal | Improvement surcharge | >= 0 |
| total_amount | decimal | Total charged | >= 0 |
| congestion_surcharge | decimal | Congestion charge | >= 0 |
| airport_fee | decimal | Airport pickup fee | >= 0 |

**Known Issues:**
- Some records have negative fares (refunds or data errors)
- Passenger count frequently 0 (not captured by all vendors)
- Trip distance occasionally 0 for valid trips (stopped traffic)
- Future dates appear occasionally (clock sync issues)

**Data Completeness:** ~99% of trips have all required fields

---

### Source 2: NYC Taxi Zone Lookup

**Owner:** NYC TLC  
**System Type:** Static reference data  
**Update Frequency:** Infrequent (last updated 2021)  
**Grain:** One record per taxi zone  
**Access Method:** Direct CSV download  
**URL:** `https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv`

**Schema:**

| Field Name | Data Type | Description | Notes |
|------------|-----------|-------------|-------|
| LocationID | integer | Zone identifier (1-263) | Primary key |
| Borough | string | NYC borough name | Manhattan, Bronx, Brooklyn, Queens, Staten Island, EWR |
| Zone | string | Zone name/description | Human-readable area name |
| service_zone | string | Service classification | Yellow Zone, Boro Zone, Airports, EWR |

**Known Issues:**
- Zone 264 and 265 exist in some trip data but not in lookup (likely Unknown zones)
- LocationID=1 is "EWR" (Newark Airport - outside NYC)
- Some zones are water bodies (valid for ferry/boat services)

**Data Completeness:** 100% - complete reference table

---

## Source Ownership & Contacts

### NYC TLC (Taxi & Limousame Commission)
- **Organization:** New York City Government
- **Website:** https://www.nyc.gov/site/tlc/
- **Data Portal:** https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- **Contact:** For data issues, use TLC website contact form
- **SLA:** No formal SLA (public dataset)
- **Retention:** Data available from 2009-present

---

## Data Gaps & Limitations

### What We Have
✅ Completed trip records (pickup → dropoff)  
✅ Fare and payment information  
✅ Geographic zones  
✅ Timestamps at minute granularity  
✅ Distance metered by taxi  

### What We Don't Have
❌ **Cancelled trips**: Trips cancelled before dropoff not recorded  
❌ **Driver breaks**: No data on driver shifts or availability  
❌ **Dispatch data**: No record of trip requests vs. actual trips  
❌ **Customer ratings**: No feedback or quality scores  
❌ **Traffic conditions**: No realtime traffic or delay data  
❌ **Vehicle details**: No vehicle age, condition, or type beyond vendor  
❌ **Driver information**: No driver ID or experience level  
❌ **Weather**: No weather conditions during trip  
❌ **Events**: No correlation with sports, concerts, emergencies  

### Impact on Analysis
- **Trip Completion Rate**: Can only calculate among completed trips, not requested trips
- **Demand Analysis**: Can see satisfied demand, not unmet demand (rejected or failed requests)
- **Delay Attribution**: Can see long trips but not why (traffic vs. route vs. driver)
- **Quality Issues**: Can't correlate poor service with specific drivers or vehicles

---

## Retrieval Strategy

### Initial Load (Backfill)
1. Download 2 months of trip data (Jan-Feb 2024) - ~4-6 GB
2. Download zone lookup once - ~10 KB
3. Store in `data/raw/` preserving original format
4. Log retrieval timestamp and source URL

### Incremental Updates
1. Monthly cron job triggers on 1st of month
2. Check for new month's data (T+60 days)
3. Download only new month if available
4. Append to existing validated dataset
5. Regenerate metrics for new month + YTD

### Completeness Checks
- Verify file size > 0
- Check record count > 1000 (sanity check)
- Verify date range in filename matches data content
- Compare record count to prior months (flag if 50% difference)
- Check for duplicate records (same trip shouldn't appear twice)

---

## Source Selection Rationale

**Why NYC TLC data?**
1. **Public & Reliable**: Government dataset with consistent schema
2. **Operational Focus**: Real business problem (taxi operations)
3. **Complete Workflow**: Captures full trip lifecycle
4. **Multiple Sources**: Requires joining trip data + zone reference
5. **Real Quality Issues**: Has actual data quality problems to validate

**Alternative sources considered:**
- Uber/Lyft: Not publicly available
- Synthetic data: Wouldn't show real-world validation challenges
- Other city taxi data: Less complete or less accessible

**Source priority ranking:**
1. TLC Trip Records (PRIMARY) - core business events
2. Zone Lookup (REQUIRED) - needed for geographic analysis
3. Weather API (FUTURE) - nice-to-have for advanced analysis
