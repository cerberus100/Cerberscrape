# DataForge API Data Pulling Guide

## 🎯 **What You Need to Actually Pull Real Data**

This guide shows you exactly what needs to be done to pull real data from each API once DataForge is deployed.

---

## 🔑 **Step 1: Get API Keys (REQUIRED)**

### **OpenCorporates API Key** (Required for Business Data)
```bash
# 1. Visit: https://opencorporates.com/api_accounts/new
# 2. Sign up for an account
# 3. Choose a plan:
#    - Free: 500 requests/month (very limited)
#    - Starter: $15/month for 5,000 requests
#    - Business: $125/month for 50,000 requests
# 4. Copy your API token
# 5. Add to .env: DATAFORGE_OPENCORP_API_KEY=your_token_here
```

**Why you need this:**
- Without it: Returns empty results
- With it: Pulls real company data from 50+ million companies worldwide
- Rate limit: 500 requests/month (free) or 5,000+ (paid)

### **SAM.gov API Key** (Required for RFP Data)
```bash
# 1. Visit: https://sam.gov/content/api-keys
# 2. Register for a free account (no credit card required)
# 3. Request an API key (instant approval)
# 4. Copy your API key
# 5. Add to .env: DATAFORGE_SAM_API_KEY=your_key_here
```

**Why you need this:**
- Without it: Returns mock data only
- With it: Pulls real federal contract opportunities
- Rate limit: No documented limits (generous free tier)

---

## 🚀 **Step 2: Deploy and Configure**

### **Local Development**
```bash
cd dataforge

# 1. Run setup
./setup.sh

# 2. Edit .env with your API keys
nano .env
# Add:
# DATAFORGE_OPENCORP_API_KEY=your_opencorp_key
# DATAFORGE_SAM_API_KEY=your_sam_key

# 3. Verify API keys work
python3 verify_api_keys.py

# 4. Start the system
docker-compose up -d
```

### **AWS Production Deployment**
```bash
# 1. Store API keys in AWS Secrets Manager
aws secretsmanager create-secret \
  --name dataforge/api-keys \
  --secret-string '{"opencorp_api_key":"YOUR_OPENCORP_KEY","sam_api_key":"YOUR_SAM_KEY"}'

# 2. Deploy to AWS
./aws-deploy.sh dev us-east-1

# 3. The system will automatically:
#    - Pull API keys from Secrets Manager
#    - Configure RDS database
#    - Set up S3 for exports
#    - Deploy Lambda functions
#    - Launch Amplify frontend
```

---

## 📊 **Step 3: Pull Real Data**

### **Business Data (OpenCorporates + NPPES)**

#### **Via CLI**
```bash
# Pull 1000 companies from California in healthcare
dataforge biz pull \
  --states CA \
  --naics 621111,621112,621210 \
  --keywords "telehealth,healthcare,medical" \
  --limit 1000 \
  --enable-geocoder

# Pull small businesses only
dataforge biz pull \
  --states TX,FL \
  --small-business-only \
  --limit 500

# Pull specific business size
dataforge biz pull \
  --states NY \
  --business-size medium \
  --limit 2000
```

#### **Via API**
```bash
curl -X POST http://localhost:8000/pull/business \
  -H "Content-Type: application/json" \
  -d '{
    "states": ["CA", "TX"],
    "naics": ["621111", "541511"],
    "keywords": ["telehealth", "healthcare"],
    "limit": 1000,
    "enable_geocoder": true,
    "small_business_only": false
  }'
```

#### **Via UI**
1. Open http://localhost:3000 (or your Amplify URL)
2. Select "Business Data" mode
3. Choose states: CA, TX, NY
4. Enter business type: "621111, telehealth, healthcare"
5. Set batch size: 1000
6. Check "Include county/FIPS lookup"
7. Click "Pull Business Data"

### **RFP Data (SAM.gov + Grants.gov)**

#### **Via CLI**
```bash
# Pull RFPs from last 30 days
dataforge rfp pull \
  --states CA,TX,NY \
  --naics 541511,621111 \
  --keywords "telehealth,healthcare" \
  --posted-from 2024-01-01 \
  --posted-to 2024-01-31 \
  --limit 500
```

#### **Via API**
```bash
curl -X POST http://localhost:8000/pull/rfps \
  -H "Content-Type: application/json" \
  -d '{
    "states": ["CA", "TX"],
    "naics": ["541511", "621111"],
    "keywords": ["telehealth", "healthcare"],
    "posted_from": "2024-01-01",
    "posted_to": "2024-01-31",
    "limit": 500
  }'
```

#### **Via UI**
1. Select "RFPs" mode
2. Choose states: CA, TX, NY
3. Enter NAICS: "541511, 621111"
4. Enter keywords: "telehealth, healthcare"
5. Set date range: Last 30 days
6. Set batch size: 500
7. Click "Pull RFPs"

---

## 📈 **What Data You'll Actually Get**

### **Business Data Sources**

#### **OpenCorporates (Primary)**
```json
{
  "company_name": "Acme Healthcare LLC",
  "domain": "acmehealthcare.com",
  "phone": "+1-555-123-4567",
  "email": "info@acmehealthcare.com",
  "address_line1": "123 Main St",
  "city": "Los Angeles",
  "state": "CA",
  "postal_code": "90210",
  "country": "US",
  "county": "Los Angeles County",
  "county_fips": "06037",
  "naics_code": "621111",
  "industry": "Offices of Physicians",
  "founded_year": 2015,
  "years_in_business": 9,
  "employee_count": 25,
  "annual_revenue_usd": 2500000,
  "business_size": "small",
  "is_small_business": true,
  "source": "opencorporates",
  "last_verified": "2024-01-15T10:30:00Z",
  "quality_score": 85
}
```

#### **NPPES (Healthcare Organizations)**
```json
{
  "company_name": "Dr. Smith Medical Practice",
  "phone": "+1-555-987-6543",
  "address_line1": "456 Oak Ave",
  "city": "San Francisco",
  "state": "CA",
  "postal_code": "94102",
  "naics_code": "621111",
  "industry": "Family Medicine",
  "npi": "1234567890",
  "taxonomy_code": "207Q00000X",
  "source": "nppes",
  "quality_score": 75
}
```

### **RFP Data Sources**

#### **SAM.gov (Federal Contracts)**
```json
{
  "notice_id": "SAM-2024-001234",
  "title": "Telehealth Services for Veterans",
  "agency": "Department of Veterans Affairs",
  "naics": "621111",
  "solicitation_number": "VA-2024-001",
  "notice_type": "Solicitation",
  "posted_date": "2024-01-15",
  "close_date": "2024-02-15",
  "place_of_performance_state": "CA",
  "description": "Comprehensive telehealth services...",
  "url": "https://sam.gov/opp/SAM-2024-001234",
  "contact_name": "John Smith",
  "contact_email": "john.smith@va.gov",
  "estimated_value": 5000000,
  "source": "sam.gov",
  "last_checked": "2024-01-15T10:30:00Z"
}
```

#### **Grants.gov (Federal Grants)**
```json
{
  "notice_id": "HHS-2024-001",
  "title": "Rural Telehealth Initiative",
  "agency": "Department of Health and Human Services",
  "naics": "621111",
  "posted_date": "2024-01-10",
  "close_date": "2024-03-10",
  "place_of_performance_state": "TX",
  "description": "Funding for rural telehealth programs...",
  "estimated_value": 2000000,
  "source": "grants.gov"
}
```

---

## ⚡ **Real-World Usage Examples**

### **Example 1: Healthcare Lead Generation**
```bash
# Pull 2000 healthcare companies in California
dataforge biz pull \
  --states CA \
  --naics 621111,621112,621210,621310 \
  --keywords "telehealth,telemedicine,digital health" \
  --limit 2000 \
  --enable-geocoder \
  --small-business-only

# Result: ~1500 companies with:
# - Company names, addresses, phones
# - County and FIPS codes
# - Business size classification
# - Quality scores
# - Years in business
```

### **Example 2: Government Contract Opportunities**
```bash
# Pull healthcare RFPs from last 60 days
dataforge rfp pull \
  --states CA,TX,NY,FL \
  --naics 541511,621111,621112 \
  --keywords "telehealth,healthcare,medical" \
  --posted-from 2023-12-01 \
  --posted-to 2024-01-31 \
  --limit 1000

# Result: ~300-500 opportunities with:
# - Contract titles and descriptions
# - Agency information
# - Contact details
# - Estimated values
# - Deadline dates
```

### **Example 3: Multi-State Business Intelligence**
```bash
# Pull medium-sized businesses across 5 states
dataforge biz pull \
  --states CA,TX,NY,FL,IL \
  --naics 541511,541512,541611 \
  --business-size medium \
  --limit 5000 \
  --enable-geocoder

# Result: ~4000 companies with:
# - Geographic distribution
# - Industry classification
# - Revenue and employee data
# - County-level analysis
```

---

## 📊 **Data Volume Expectations**

### **Business Data (OpenCorporates)**
- **California**: ~50,000 companies per NAICS code
- **Texas**: ~40,000 companies per NAICS code
- **New York**: ~35,000 companies per NAICS code
- **Rate Limit**: 500 requests/month (free) = ~16 requests/day
- **Recommendation**: Use paid tier ($15/month) for production

### **Healthcare Data (NPPES)**
- **Total**: ~1.2 million healthcare providers
- **California**: ~150,000 providers
- **Texas**: ~120,000 providers
- **No Rate Limits**: Bulk file download
- **File Size**: 7+ GB compressed

### **RFP Data (SAM.gov)**
- **Daily Postings**: ~200-500 new opportunities
- **Healthcare RFPs**: ~20-50 per day
- **No Rate Limits**: Generous free tier
- **Historical Data**: Available for years

---

## 🔄 **Automated Data Pulling**

### **Scheduled Jobs**
```python
# Daily business data refresh
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=2, minute=0)  # 2 AM daily
def daily_business_refresh():
    # Pull fresh business data
    payload = BusinessPullRequest(
        states=["CA", "TX", "NY", "FL"],
        naics=["621111", "541511"],
        limit=1000,
        enable_geocoder=True
    )
    result = run_business_pipeline(payload)
    print(f"Daily refresh: {result.message}")

@scheduler.scheduled_job('cron', hour=0, minute=0)  # Hourly
def hourly_rfp_refresh():
    # Pull new RFPs
    payload = RFPPullRequest(
        states=["CA", "TX", "NY", "FL"],
        naics=["541511", "621111"],
        posted_from=datetime.now() - timedelta(hours=1),
        posted_to=datetime.now(),
        limit=100
    )
    result = run_rfp_pipeline(payload)
    print(f"Hourly RFP refresh: {result.message}")

scheduler.start()
```

### **AWS Lambda Scheduled Functions**
```yaml
# serverless.yml
functions:
  dailyBusinessRefresh:
    handler: scripts.scheduled_jobs.daily_business_refresh
    events:
      - schedule: cron(0 2 * * ? *)  # 2 AM daily
    environment:
      DATAFORGE_S3_BUCKET: ${self:custom.bucketName}
      
  hourlyRfpRefresh:
    handler: scripts.scheduled_jobs.hourly_rfp_refresh
    events:
      - schedule: cron(0 * * * ? *)  # Every hour
```

---

## 📁 **Output Files**

### **CSV Export Location**
```bash
# Local development
./exports/business-20240115-CA-621111-telehealth.csv
./exports/rfps-20240115-CA-541511-healthcare.csv

# AWS S3
s3://your-bucket/exports/business-20240115-CA-621111-telehealth.csv
s3://your-bucket/exports/rfps-20240115-CA-541511-healthcare.csv
```

### **File Contents**
```csv
# Business CSV (22 columns)
company_name,domain,phone,email,address_line1,city,state,postal_code,country,county,county_fips,naics_code,industry,founded_year,years_in_business,employee_count,annual_revenue_usd,business_size,is_small_business,source,last_verified,quality_score

# RFP CSV (15 columns)
notice_id,title,agency,naics,solicitation_number,notice_type,posted_date,close_date,place_of_performance_state,description,url,contact_name,contact_email,estimated_value,source,last_checked
```

---

## 🚨 **Important Considerations**

### **Rate Limits**
- **OpenCorporates Free**: 500 requests/month (very limited)
- **OpenCorporates Paid**: 5,000+ requests/month ($15/month)
- **SAM.gov**: No documented limits (generous)
- **Census Geocoder**: No documented limits (respectful usage)

### **Data Quality**
- **OpenCorporates**: High quality, regularly updated
- **NPPES**: Official government data, very reliable
- **SAM.gov**: Official government data, real-time
- **Grants.gov**: Official government data, may have delays

### **Costs**
- **OpenCorporates**: $15/month minimum for production use
- **SAM.gov**: Free
- **Census Geocoder**: Free
- **NPPES**: Free
- **AWS**: ~$50-200/month depending on usage

---

## 🎯 **Quick Start Commands**

### **Test with Small Data First**
```bash
# Test business data (10 records)
dataforge biz pull --states CA --keywords telehealth --limit 10

# Test RFP data (10 records)
dataforge rfp pull --states CA --keywords telehealth --limit 10

# Verify API keys work
python3 verify_api_keys.py
```

### **Production Data Pull**
```bash
# Business data (1000 records)
dataforge biz pull \
  --states CA,TX,NY \
  --naics 621111,541511 \
  --keywords "telehealth,healthcare" \
  --limit 1000 \
  --enable-geocoder

# RFP data (500 records)
dataforge rfp pull \
  --states CA,TX,NY \
  --naics 541511,621111 \
  --keywords "telehealth,healthcare" \
  --posted-from 2024-01-01 \
  --posted-to 2024-01-31 \
  --limit 500
```

---

## ✅ **Summary: What You Need to Do**

1. **Get API Keys** (10 minutes)
   - OpenCorporates: https://opencorporates.com/api_accounts/new
   - SAM.gov: https://sam.gov/content/api-keys

2. **Configure Environment** (5 minutes)
   ```bash
   cd dataforge
   ./setup.sh
   nano .env  # Add your API keys
   python3 verify_api_keys.py
   ```

3. **Pull Real Data** (5 minutes)
   ```bash
   dataforge biz pull --states CA --limit 100
   dataforge rfp pull --states CA --limit 100
   ```

4. **Deploy to Production** (15 minutes)
   ```bash
   ./aws-deploy.sh dev us-east-1
   ```

**Total time: ~35 minutes to get real data flowing!** 🚀

The system is ready to pull real data from all APIs once you have the API keys configured.
