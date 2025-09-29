# Backend API Setup Guide

## 🎯 **Overview**

This guide provides step-by-step instructions for backend developers to obtain and configure the required API keys for DataForge to pull real data from external sources.

---

## 🔑 **Required API Keys**

### **1. OpenCorporates API Key** (Primary Business Data Source)
- **Purpose**: Pull business data from 50+ million companies worldwide
- **Cost**: Free tier (500 requests/month) or $15/month (5,000 requests)
- **Required for**: Business data extraction

### **2. SAM.gov API Key** (Primary RFP Data Source)
- **Purpose**: Pull federal contract opportunities
- **Cost**: Free (no limits)
- **Required for**: RFP data extraction

### **3. Census Geocoder** (Address Enhancement)
- **Purpose**: Get county and FIPS codes for addresses
- **Cost**: Free (no API key required)
- **Required for**: Address geocoding

---

## 📋 **Step-by-Step API Key Acquisition**

### **Step 1: OpenCorporates API Key**

#### **1.1 Visit the Registration Page**
```
URL: https://opencorporates.com/api_accounts/new
```

#### **1.2 Create Account**
1. Click "Sign Up" or "Create Account"
2. Fill in required information:
   - Email address
   - Password
   - Company name (optional)
3. Verify your email address

#### **1.3 Choose a Plan**
**Free Plan (Limited)**
- 500 requests per month
- Good for testing and small projects
- Rate limit: ~16 requests per day

**Starter Plan (Recommended)**
- $15/month
- 5,000 requests per month
- Rate limit: ~166 requests per day
- Better for production use

**Business Plan**
- $125/month
- 50,000 requests per month
- Rate limit: ~1,666 requests per day
- For high-volume production

#### **1.4 Get Your API Token**
1. After signup, go to your account dashboard
2. Navigate to "API Keys" or "API Access"
3. Copy your API token (it looks like: `abc123def456ghi789`)

#### **1.5 Test Your Key**
```bash
curl "https://api.opencorporates.com/v0.4/companies/search?api_token=YOUR_TOKEN&q=test&jurisdiction_code=us_ca"
```

---

### **Step 2: SAM.gov API Key**

#### **2.1 Visit the API Key Page**
```
URL: https://sam.gov/content/api-keys
```

#### **2.2 Register for Account**
1. Click "Register" or "Create Account"
2. Fill in required information:
   - Email address
   - Password
   - First name, Last name
   - Organization (optional)
3. Verify your email address

#### **2.3 Request API Key**
1. Log into your SAM.gov account
2. Navigate to "API Keys" section
3. Click "Request API Key"
4. Fill out the form:
   - Purpose: "Data extraction for business intelligence"
   - Description: "Pulling federal contract opportunities for analysis"
5. Submit the request

#### **2.4 Get Your API Key**
- **Instant Approval**: Most requests are approved immediately
- **API Key Format**: Looks like `12345678-1234-1234-1234-123456789012`
- **Copy the key** from your dashboard

#### **2.5 Test Your Key**
```bash
curl "https://api.sam.gov/opportunities/v1/search?api_key=YOUR_KEY&postedFrom=2024-01-01&postedTo=2024-01-31&limit=10"
```

---

### **Step 3: Census Geocoder (No Key Required)**

#### **3.1 No Registration Needed**
- Census Geocoder is completely free
- No API key required
- No rate limits (use responsibly)

#### **3.2 Test the Service**
```bash
curl "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address=1600+Pennsylvania+Ave+Washington+DC&benchmark=Public_AR_Current&format=json"
```

---

## ⚙️ **Configuration Instructions**

### **Step 1: Environment Setup**

#### **1.1 Clone the Repository**
```bash
git clone https://github.com/cerberus100/Cerberscrape.git
cd Cerberscrape
```

#### **1.2 Copy Environment Template**
```bash
cp .env.sample .env
```

#### **1.3 Edit Environment File**
```bash
nano .env
# or
vim .env
# or
code .env
```

#### **1.4 Add Your API Keys**
```bash
# Add these lines to your .env file:
DATAFORGE_OPENCORP_API_KEY=your_opencorp_token_here
DATAFORGE_SAM_API_KEY=your_sam_api_key_here

# Example:
DATAFORGE_OPENCORP_API_KEY=abc123def456ghi789
DATAFORGE_SAM_API_KEY=12345678-1234-1234-1234-123456789012
```

### **Step 2: Install Dependencies**
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Or use the automated setup
./setup.sh
```

### **Step 3: Start Database**
```bash
# Start PostgreSQL database
docker-compose up -d db

# Verify database is running
docker-compose ps
```

### **Step 4: Verify Configuration**
```bash
# Test all API keys and connections
python3 verify_api_keys.py
```

**Expected Output:**
```
🔍 DataForge API Key Verification
==================================================

1️⃣  Testing environment configuration...
   ✅ Settings loaded successfully

2️⃣  Testing OpenCorporates API key...
   ✅ OpenCorporates API key is configured

3️⃣  Testing SAM.gov API key...
   ✅ SAM.gov API key is configured

4️⃣  Testing Census Geocoder...
   ✅ Census Geocoder is accessible

5️⃣  Testing database connection...
   ✅ Database connection successful

==================================================
📋 Verification Summary
==================================================
✅ OpenCorporates API
✅ SAM.gov API
✅ Census Geocoder
✅ Database
```

---

## 🧪 **Testing Real Data Pulling**

### **Step 1: Test with Small Data**
```bash
# Test business data (10 records)
dataforge biz pull --states CA --keywords telehealth --limit 10

# Test RFP data (10 records)
dataforge rfp pull --states CA --keywords telehealth --limit 10
```

### **Step 2: Test with Larger Data**
```bash
# Business data (100 records)
dataforge biz pull --states CA,TX --naics 621111 --limit 100

# RFP data (50 records)
dataforge rfp pull --states CA,TX --naics 541511 --limit 50
```

### **Step 3: Test Full Pipeline**
```bash
# Run comprehensive test
python3 test_real_data_pull.py
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Issue 1: OpenCorporates API Key Not Working**
**Symptoms:**
```
⚠️  OpenCorporates API key is NOT configured
```

**Solutions:**
1. Check if the key is correctly added to `.env`
2. Verify the key format (no spaces, quotes, or special characters)
3. Test the key directly:
   ```bash
   curl "https://api.opencorporates.com/v0.4/companies/search?api_token=YOUR_KEY&q=test"
   ```

#### **Issue 2: SAM.gov API Key Not Working**
**Symptoms:**
```
⚠️  SAM.gov API key is NOT configured
```

**Solutions:**
1. Check if the key is correctly added to `.env`
2. Verify the key format (UUID format)
3. Test the key directly:
   ```bash
   curl "https://api.sam.gov/opportunities/v1/search?api_key=YOUR_KEY&postedFrom=2024-01-01&postedTo=2024-01-31&limit=1"
   ```

#### **Issue 3: Database Connection Failed**
**Symptoms:**
```
⚠️  Database connection failed: No module named 'psycopg'
```

**Solutions:**
1. Install dependencies: `pip3 install -r requirements.txt`
2. Start database: `docker-compose up -d db`
3. Check database URL in `.env` file

#### **Issue 4: Rate Limit Exceeded**
**Symptoms:**
```
HTTP 429: Too Many Requests
```

**Solutions:**
1. Wait for rate limit to reset (usually 1 hour)
2. Upgrade to paid OpenCorporates plan
3. Reduce request frequency

---

## 📊 **API Usage Guidelines**

### **OpenCorporates Rate Limits**
- **Free**: 500 requests/month (~16/day)
- **Starter**: 5,000 requests/month (~166/day)
- **Business**: 50,000 requests/month (~1,666/day)

### **SAM.gov Rate Limits**
- **No documented limits** (use responsibly)
- **Recommended**: Max 100 requests/minute

### **Census Geocoder Rate Limits**
- **No documented limits** (use responsibly)
- **Recommended**: Max 50 requests/minute

### **Best Practices**
1. **Start small**: Test with 10-50 records first
2. **Monitor usage**: Check your API usage regularly
3. **Cache results**: Don't re-request the same data
4. **Batch requests**: Group similar requests together
5. **Handle errors**: Implement proper error handling and retries

---

## 🔒 **Security Best Practices**

### **API Key Security**
1. **Never commit API keys** to version control
2. **Use environment variables** for all keys
3. **Rotate keys regularly** (every 90 days)
4. **Monitor key usage** for unusual activity
5. **Use different keys** for different environments

### **Environment Separation**
```bash
# Development
DATAFORGE_OPENCORP_API_KEY=dev_key_here

# Staging
DATAFORGE_OPENCORP_API_KEY=staging_key_here

# Production
DATAFORGE_OPENCORP_API_KEY=prod_key_here
```

---

## 📞 **Support Contacts**

### **OpenCorporates Support**
- **Email**: support@opencorporates.com
- **Documentation**: https://opencorporates.com/api_documentation
- **Status Page**: https://status.opencorporates.com

### **SAM.gov Support**
- **Email**: support@sam.gov
- **Documentation**: https://open.gsa.gov/api/entity-api/
- **Help Desk**: https://sam.gov/content/help

### **Census Geocoder Support**
- **Email**: geo.geocoding.services@census.gov
- **Documentation**: https://geocoding.geo.census.gov/geocoder/

---

## ✅ **Checklist for Backend Team**

### **Pre-Setup**
- [ ] Clone the repository
- [ ] Review the codebase structure
- [ ] Understand the data sources

### **API Key Acquisition**
- [ ] Get OpenCorporates API key
- [ ] Get SAM.gov API key
- [ ] Test both keys independently

### **Configuration**
- [ ] Copy `.env.sample` to `.env`
- [ ] Add API keys to `.env` file
- [ ] Install Python dependencies
- [ ] Start PostgreSQL database

### **Verification**
- [ ] Run `python3 verify_api_keys.py`
- [ ] All systems show ✅ status
- [ ] Test with small data pulls

### **Production Readiness**
- [ ] Test with larger data volumes
- [ ] Verify error handling
- [ ] Check rate limit compliance
- [ ] Document any custom configurations

---

## 🎯 **Quick Start Commands**

```bash
# 1. Clone and setup
git clone https://github.com/cerberus100/Cerberscrape.git
cd Cerberscrape
cp .env.sample .env

# 2. Add API keys to .env file
nano .env

# 3. Install and start
./setup.sh
docker-compose up -d db

# 4. Verify everything works
python3 verify_api_keys.py

# 5. Test real data
dataforge biz pull --states CA --limit 10
```

---

**Total setup time: ~30 minutes (including API key acquisition)**

**Once configured, you can pull real data from 50+ million companies and federal contracts!**
