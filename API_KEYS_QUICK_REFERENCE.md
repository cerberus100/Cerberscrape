# API Keys Quick Reference

## 🚀 **Quick Setup (5 minutes)**

### **1. Get API Keys**
```bash
# OpenCorporates (Business Data)
open https://opencorporates.com/api_accounts/new

# SAM.gov (RFP Data)  
open https://sam.gov/content/api-keys
```

### **2. Configure Environment**
```bash
# Copy template
cp .env.sample .env

# Edit with your keys
nano .env
```

### **3. Add to .env file**
```bash
DATAFORGE_OPENCORP_API_KEY=your_opencorp_token_here
DATAFORGE_SAM_API_KEY=your_sam_api_key_here
```

### **4. Test Setup**
```bash
./setup.sh
python3 verify_api_keys.py
```

---

## 🔑 **API Key Details**

| Service | URL | Cost | Rate Limit | Format |
|---------|-----|------|------------|--------|
| **OpenCorporates** | https://opencorporates.com/api_accounts/new | Free: 500/month<br>$15: 5,000/month | ~16/day (free)<br>~166/day (paid) | `abc123def456` |
| **SAM.gov** | https://sam.gov/content/api-keys | Free | No limits | `12345678-1234-1234-1234-123456789012` |
| **Census Geocoder** | No signup needed | Free | No limits | No key required |

---

## 🧪 **Test Commands**

```bash
# Test API keys
python3 verify_api_keys.py

# Test small data pull
dataforge biz pull --states CA --limit 10
dataforge rfp pull --states CA --limit 10

# Test real data
dataforge biz pull --states CA,TX --naics 621111 --limit 100
```

---

## 🚨 **Troubleshooting**

| Issue | Solution |
|-------|----------|
| API key not working | Check .env file format, no quotes/spaces |
| Database connection failed | Run `docker-compose up -d db` |
| Rate limit exceeded | Wait 1 hour or upgrade OpenCorporates plan |
| Dependencies missing | Run `pip3 install -r requirements.txt` |

---

## 📞 **Support**

- **OpenCorporates**: support@opencorporates.com
- **SAM.gov**: support@sam.gov  
- **Census**: geo.geocoding.services@census.gov

---

**Total setup time: ~15 minutes to start pulling real data!**
