# DataForge Data Sources

This document describes the data sources and connectors implemented in DataForge.

## Business Data Sources (Primary)

### 1. OpenCorporates - Companies Search API

**Endpoint**: `https://api.opencorporates.com/v0.4/companies/search`  
**Authentication**: `api_token=<OPENCORP_API_KEY>`  
**Documentation**: https://api.opencorporates.com

**Key Parameters**:
- `q`: Free-text search (built from NAICS keywords and user keywords)
- `jurisdiction_code`: One per run (map state → `us_<state>` e.g., CA → `us_ca`)
- `per_page`: Results per page (max 100)
- `page`: Page number for pagination

**Features**:
- ✅ Full pagination support
- ✅ State-based jurisdiction mapping
- ✅ Free-text search with NAICS and keywords
- ✅ Rate limiting and retry logic
- ✅ Graceful fallback when API key is missing
- ✅ Comprehensive data normalization

**Data Fields Extracted**:
- Company name, domain, phone, email
- Registered address (street, city, state, postal code)
- Incorporation date, dissolution date
- Company status (active/inactive)

**Usage**:
```python
from core.pipeline.ingest.opencorporates import ingest_opencorporates

records = ingest_opencorporates(
    states=["CA", "TX"],
    naics=["621111", "541511"],
    keywords=["telehealth", "healthcare"],
    limit=1000
)
```

### 2. NPPES - Healthcare Organizations

**Source**: https://download.cms.gov/nppes/NPI_Files.html  
**Method**: Download monthly ZIP files, parse organizations (Entity Type 2)  
**Tag**: `source="nppes"`

**Features**:
- ✅ Monthly bulk file download and caching
- ✅ Automatic file version detection
- ✅ CSV parsing with proper encoding handling
- ✅ Healthcare-specific data extraction
- ✅ State and keyword filtering

**Data Fields Extracted**:
- Provider organization name
- Practice location address
- Phone, fax numbers
- NPI (National Provider Identifier)
- Taxonomy codes and descriptions
- Enumeration and update dates

**Usage**:
```python
from core.pipeline.ingest.nppes import ingest_nppes

records = ingest_nppes(
    states=["CA", "NY"],
    keywords=["telehealth", "primary care"],
    limit=500
)
```

**File Structure**:
```
exports/nppes_cache/
├── NPPES_Data_Dissemination_January_2024.zip
├── NPPES_Data_Dissemination_February_2024.zip
└── ...
```

### 3. State Manual - CSV Drop Functionality

**Method**: Local CSV drop + YAML mapper for arbitrary state files  
**Tag**: `source="state_manual:<STATE>"`

**Features**:
- ✅ Flexible CSV file support
- ✅ YAML-based field mapping
- ✅ Automatic delimiter detection
- ✅ State-specific file organization
- ✅ Sample mapper generation

**File Structure**:
```
exports/state_manual/
├── ca_companies.csv
├── tx_businesses.csv
└── mappers/
    ├── ca_mapper.yaml
    └── tx_mapper.yaml
```

**Sample Mapper (YAML)**:
```yaml
company_name: "Company Name"
domain: "Website"
phone: "Phone"
email: "Email"
address_line1: "Address"
city: "City"
postal_code: "Zip Code"
naics_code: "NAICS"
industry: "Industry"
founded_year: "Founded Year"
employee_count: "Employees"
```

**Usage**:
```python
from core.pipeline.ingest.state_manual import ingest_state_manual, create_sample_mapper

# Create sample mapper for a state
create_sample_mapper("CA")

# Ingest from CSV files
records = ingest_state_manual(
    states=["CA"],
    keywords=["technology"],
    limit=1000
)
```

## RFP Data Sources (Secondary)

### 4. SAM.gov - Contract Opportunities API

**Endpoint**: `https://api.sam.gov/opportunities/v1/search`  
**Authentication**: `api_key=<SAM_API_KEY>`  
**Documentation**: https://open.gsa.gov/api/entity-api/

**Key Parameters**:
- `postedFrom`: ISO date string (required)
- `postedTo`: ISO date string (required)
- `ncode`: Comma-separated NAICS codes
- `placeOfPerformance.state`: Comma-separated states
- `noticeType`: Type of notice (default: "Solicitation")
- `limit`: Results per page (max 1000)
- `offset`: Pagination offset

**Features**:
- ✅ Full pagination support
- ✅ Date range filtering (required by API)
- ✅ State and NAICS filtering
- ✅ Mock data fallback when API key is missing
- ✅ Comprehensive opportunity data extraction

**Data Fields Extracted**:
- Notice ID, title, agency
- NAICS codes, solicitation number
- Posted/close dates
- Place of performance state
- Description, URL
- Contact information
- Estimated value

**Usage**:
```python
from core.pipeline.ingest.sam_opps import ingest_sam_opportunities

records = ingest_sam_opportunities(
    states=["CA", "TX"],
    naics=["541511", "621111"],
    keywords=["telehealth"],
    posted_from="2024-01-01",
    posted_to="2024-12-31",
    limit=1000
)
```

### 5. Grants.gov - Search2 API (Optional)

**Endpoint**: `https://www.grants.gov/api/search2`  
**Authentication**: None for search2 (per docs)  
**Tag**: `source="grants.gov"`

**Features**:
- ✅ No authentication required
- ✅ Keyword and date range filtering
- ✅ Grant-specific data extraction
- ✅ Optional inclusion (controlled by `include_grants` flag)

**Data Fields Extracted**:
- Opportunity ID, title, agency
- NAICS codes, opportunity number
- Posted/close dates
- State, description, URL
- Contact information
- Estimated value

**Usage**:
```python
from core.pipeline.ingest.grants_gov import ingest_grants_gov

records = ingest_grants_gov(
    keywords=["healthcare", "telehealth"],
    posted_from="2024-01-01",
    posted_to="2024-12-31",
    limit=500
)
```

## Geocoding & Address Verification

### 6. U.S. Census Geocoder - County & FIPS

**Endpoints**:
- One-line: `https://geocoding.geo.census.gov/geocoder/locations/onelineaddress`
- Component: `https://geocoding.geo.census.gov/geocoder/locations/address`

**Features**:
- ✅ No API key required
- ✅ Dual endpoint support (one-line and component)
- ✅ County name and 5-digit FIPS extraction
- ✅ Rate limiting and retry logic
- ✅ Graceful failure handling

**Output**:
- County name (e.g., "Los Angeles County")
- 5-digit county FIPS code (e.g., "06037")

**Usage**:
```python
from core.pipeline.enrich.geocode_census import geocode_records

# Enable geocoding in pipeline
enriched_records = geocode_records(business_records)
```

**Configuration**:
```python
# Enable by default
DATAFORGE_ENABLE_GEOCODER=true

# Or enable per request
payload = BusinessPullRequest(
    states=["CA"],
    enable_geocoder=True
)
```

## Request → Parameter Mapping

### Common Inputs
- `states[]`: List of 2-letter state codes
- `naics[]`: List of NAICS codes
- `keywords[]`: List of search keywords
- `date_window`: Date range for RFPs
- `limit`: Maximum results to return

### Connector-Specific Mapping

**OpenCorporates**:
- For each state: `jurisdiction_code=us_<state>`
- Query: `q` built from keywords/NAICS terms
- Pagination: `per_page` and `page`

**NPPES**:
- Load latest monthly org file once per month
- Filter by `states[]` (practice location state)
- Filter by `keywords[]`
- Cap to `limit`

**SAM.gov**:
- `ncode=<naics_list>`
- `placeOfPerformance.state=<states_list>`
- `postedFrom` and `postedTo` (required)
- Pagination: `limit` and `offset`

**Grants.gov**:
- `q=<keywords>`
- `postedFrom` and `postedTo`
- Pagination: `limit` and `offset`

**Census Geocoder**:
- For each business record: look up county and FIPS
- One-line address or component fields
- Rate limiting: 0.1s between requests

## Acceptance Criteria

### Each Connector Must:
- ✅ Log the final URL + params used
- ✅ Return empty iterable if required key is missing (no crashes)
- ✅ Include `source` and timestamp fields for provenance
- ✅ Handle rate limiting and retries gracefully
- ✅ Provide comprehensive error logging

### Geocoder Requirements:
- ✅ Only run when enabled (`ENABLE_GEOCODER=true` or request flag)
- ✅ County FIPS must be 5 digits when present
- ✅ Graceful failure (keep original address on error)
- ✅ Rate limiting to be respectful to the API

## Configuration

### Environment Variables
```bash
# API Keys
DATAFORGE_OPENCORP_API_KEY=your_opencorp_key
DATAFORGE_SAM_API_KEY=your_sam_key

# Features
DATAFORGE_ENABLE_GEOCODER=true
DATAFORGE_INCLUDE_GRANTS=false

# Paths
DATAFORGE_EXPORT_BUCKET_PATH=./exports
```

### AWS Configuration
```bash
# AWS-specific settings
AWS_REGION=us-east-1
DATAFORGE_S3_BUCKET=your-bucket-name
```

## Data Quality & Provenance

### Source Tracking
Every record includes:
- `source`: Data source identifier
- `last_verified`: Timestamp of data extraction
- `quality_score`: 0-100 quality assessment

### Source Identifiers
- `opencorporates`: OpenCorporates API
- `nppes`: NPPES healthcare data
- `state_manual:CA`: Manual state CSV (California)
- `sam.gov`: SAM.gov opportunities
- `sam.gov (mock)`: SAM.gov mock data
- `grants.gov`: Grants.gov search2

### Quality Scoring
- Start at 100 points
- Deduct for missing fields (domain, phone, address, etc.)
- Add for validated data (SMTP, phone lookup, etc.)
- Clamp to 0-100 range

## Error Handling & Resilience

### Connector Resilience
- Each connector runs independently
- Failures in one source don't affect others
- Comprehensive error logging
- Graceful degradation with mock data when appropriate

### Rate Limiting
- OpenCorporates: 0.1s between requests
- SAM.gov: 0.1s between requests
- Census Geocoder: 0.1s between requests
- NPPES: File-based (no rate limiting)

### Retry Logic
- 3 attempts with exponential backoff
- Configurable timeouts
- Circuit breaker pattern for persistent failures

## Legal & Compliance

### Data Usage
- Respect API terms of service
- Maintain attribution requirements
- Preserve data provenance
- No scraping of state portals (manual CSV only)

### Privacy & Security
- No PII logging
- Secure API key storage
- Rate limiting to prevent abuse
- Proper error handling without data leakage

