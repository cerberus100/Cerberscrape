# DataForge - Business Data & RFP Extraction Platform

A production-ready data extraction platform that pulls, cleans, dedupes, enriches, QA-checks, and exports CSVs for both business data and RFPs.

## 🚀 Features

- **Business Data Extraction**: Pull from OpenCorporates, NPPES, and state sources
- **RFP Data Extraction**: Pull from SAM.gov and Grants.gov
- **Geocoding**: Census Geocoder integration for county/FIPS data
- **Business Size Classification**: Small business filtering and classification
- **Data Enrichment**: Email/phone validation, address normalization
- **Deduplication**: Fuzzy matching and merge logic
- **Quality Assurance**: Automated QA checks and scoring
- **Multiple Interfaces**: REST API, CLI, and Web UI
- **AWS Ready**: Deploy to AWS Amplify, Lambda, RDS, S3

## 📊 Data Sources

### Business Data (Primary)
1. **OpenCorporates** - 50+ million companies worldwide
2. **NPPES** - 1.2 million healthcare providers
3. **State Manual** - Local CSV imports with YAML mapping

### RFP Data (Secondary)
4. **SAM.gov** - Federal contract opportunities
5. **Grants.gov** - Federal grant opportunities

### Enhancement
6. **Census Geocoder** - County and FIPS data (no API key required)

## 🛠️ Tech Stack

- **Backend**: Python 3.11, FastAPI, Pydantic v2, SQLAlchemy, PostgreSQL
- **UI**: React, Tailwind CSS, Vite
- **CLI**: Typer
- **Testing**: pytest, pytest-asyncio
- **Deployment**: Docker, AWS Amplify, Lambda, RDS, S3

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/cerberus100/Cerberscrape.git
cd Cerberscrape

# Run automated setup
./setup.sh

# Edit .env with your API keys
nano .env
```

### 2. Get API Keys
- **OpenCorporates**: https://opencorporates.com/api_accounts/new ($15/month recommended)
- **SAM.gov**: https://sam.gov/content/api-keys (free)

### 3. Test Setup
```bash
# Verify API keys
python3 verify_api_keys.py

# Test with small data pull
dataforge biz pull --states CA --limit 10
dataforge rfp pull --states CA --limit 10
```

### 4. Pull Real Data
```bash
# Business data
dataforge biz pull --states CA,TX,NY --naics 621111 --limit 1000

# RFP data
dataforge rfp pull --states CA,TX,NY --naics 541511 --limit 500
```

## 📁 Project Structure

```
dataforge/
├── apps/
│   ├── api/           # FastAPI application
│   ├── cli/           # CLI commands
│   └── ui/            # React frontend
├── core/
│   ├── config.py      # Configuration
│   ├── models.py      # SQLAlchemy models
│   ├── schemas.py     # Pydantic schemas
│   └── pipeline/      # Data processing pipeline
│       ├── ingest/    # Data source connectors
│       ├── enrich/    # Data enrichment
│       ├── dedupe.py  # Deduplication logic
│       ├── export.py  # CSV export
│       └── qa.py      # Quality assurance
├── tests/             # Test suite
├── docker-compose.yml # Local development
└── serverless.yml     # AWS deployment
```

## 🔧 API Endpoints

- `GET /healthz` - Health check
- `POST /pull/business` - Pull business data
- `POST /pull/rfps` - Pull RFP data
- `GET /preview/business` - Preview business data
- `GET /preview/rfps` - Preview RFP data

## 📊 CSV Output

### Business CSV (22 columns)
```
company_name,domain,phone,email,address_line1,city,state,postal_code,country,
county,county_fips,naics_code,industry,founded_year,years_in_business,
employee_count,annual_revenue_usd,business_size,is_small_business,
source,last_verified,quality_score
```

### RFP CSV (15 columns)
```
notice_id,title,agency,naics,solicitation_number,notice_type,
posted_date,close_date,place_of_performance_state,description,url,
contact_name,contact_email,estimated_value,source,last_checked
```

## 🐳 Docker Development

```bash
# Start all services
docker-compose up -d

# API available at http://localhost:8000
# UI available at http://localhost:3000
# Database at localhost:5433
```

## ☁️ AWS Deployment

```bash
# Deploy to AWS
./aws-deploy.sh dev us-east-1

# Includes:
# - AWS Amplify (frontend)
# - Lambda functions (backend)
# - RDS PostgreSQL (database)
# - S3 (file storage)
# - Secrets Manager (API keys)
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Test specific components
pytest tests/test_filters.py
pytest tests/test_dedupe.py
pytest tests/test_export.py
```

## 📚 Documentation

- [API Data Pulling Guide](API_DATA_PULLING_GUIDE.md)
- [Data Sources](DATA_SOURCES.md)
- [Business Size Features](BUSINESS_SIZE_FEATURES.md)
- [Production Ready Checklist](PRODUCTION_READY_CHECKLIST.md)

## ⚖️ Legal Notes

- Respect API terms of service
- Maintain data provenance via source fields
- Use responsibly and ethically
- Consider data privacy regulations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Ready to extract business data and RFPs? Get your API keys and start pulling real data in minutes!**