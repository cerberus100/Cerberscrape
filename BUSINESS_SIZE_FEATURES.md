# Business Size Classification Features

## 🎯 Overview

DataForge now includes comprehensive business size classification and filtering capabilities, allowing users to target specific business sizes for their data pulls.

## 📊 Business Size Categories

### Standard Classification
- **Micro**: ≤9 employees or ≤$1M annual revenue
- **Small**: 10-49 employees or ≤$10M annual revenue  
- **Medium**: 50-249 employees or ≤$50M annual revenue
- **Large**: 250+ employees or >$50M annual revenue

### NAICS-Specific Classification
Uses SBA (Small Business Administration) size standards for accurate classification:
- **Healthcare (621111)**: ≤1,500 employees
- **IT Services (541511)**: ≤1,500 employees
- **Consulting (541611)**: ≤1,500 employees
- **And many more...**

## 🔧 Implementation Details

### Backend Changes
- **New Schema Fields**: `business_size`, `is_small_business`
- **Classification Logic**: `core/pipeline/business_size.py`
- **Filtering**: Enhanced `_apply_filters()` function
- **CSV Export**: Updated headers and data export

### API Enhancements
```json
{
  "states": ["CA", "TX"],
  "small_business_only": true,
  "business_size": "small",
  "limit": 1000
}
```

### CLI Options
```bash
# Small businesses only
dataforge biz pull --states CA --small-business-only --limit 500

# Specific business size
dataforge biz pull --states TX --business-size small --limit 1000

# Combined with other filters
dataforge biz pull --states CA,TX --naics 621111 --small-business-only --enable-geocoder
```

## 🖥️ UI Features

### Business Mode Filters
- **Checkbox**: "Small businesses only" (micro + small)
- **Dropdown**: Specific business size selection
- **Smart Defaults**: Only shows for business mode, not RFP mode

### User Experience
- Clear descriptions of each business size category
- Employee count ranges displayed
- Optional filtering (can be left blank)

## 📈 Data Pipeline Integration

### Classification Process
1. **Ingest**: Raw business data with employee count/revenue
2. **Normalize**: Standardize data formats
3. **Classify**: Apply business size classification
4. **Filter**: Apply size-based filters
5. **Export**: Include size data in CSV output

### CSV Output
New columns added to business CSV:
```
business_size,is_small_business
```

## 🧪 Testing

### Test Coverage
- **Unit Tests**: `test_business_size.py`
- **Classification Logic**: Employee count and revenue-based
- **NAICS-Specific**: Industry-specific thresholds
- **Filtering**: Small business and specific size filters
- **Validation**: Schema validation for business size values

### Test Examples
```python
# Test small business classification
size, is_small = classify_business_size(25, None)
assert size == "small"
assert is_small is True

# Test filtering
payload = BusinessPullRequest(states=["CA"], small_business_only=True)
filtered = _apply_filters(records, payload)
```

## 🎯 Use Cases

### Lead Generation
- **Small Business Focus**: Target companies with <50 employees
- **Enterprise Sales**: Filter for large companies (250+ employees)
- **Local Businesses**: Micro businesses for local service providers

### Market Research
- **Industry Analysis**: Compare business sizes across sectors
- **Competitive Intelligence**: Identify small vs. large competitors
- **Market Segmentation**: Analyze by business size categories

### Sales Prospecting
- **SMB Sales**: Target small and medium businesses
- **Enterprise Sales**: Focus on large corporations
- **Startup Outreach**: Identify micro businesses and startups

## 🔍 Business Size Logic

### Primary Classification (Employee Count)
```python
if employee_count <= 9:
    return "micro", True
elif employee_count <= 49:
    return "small", True
elif employee_count <= 249:
    return "medium", False
else:
    return "large", False
```

### Fallback Classification (Revenue)
```python
if annual_revenue <= 1_000_000:
    return "micro", True
elif annual_revenue <= 10_000_000:
    return "small", True
elif annual_revenue <= 50_000_000:
    return "medium", False
else:
    return "large", False
```

### NAICS-Specific Thresholds
```python
# Example: Healthcare services
if naics_code == "621111" and employee_count <= 1500:
    return "small", True  # Small by SBA standards
```

## 📊 Benefits

### For Users
- **Precise Targeting**: Filter by exact business size needs
- **Compliance**: Use SBA standards for government contracting
- **Efficiency**: Reduce irrelevant leads in data pulls
- **Flexibility**: Choose between general or NAICS-specific classification

### For Data Quality
- **Standardization**: Consistent business size classification
- **Accuracy**: Industry-specific thresholds when available
- **Completeness**: Fallback to revenue when employee count unavailable
- **Validation**: Schema validation prevents invalid size values

## 🚀 Future Enhancements

### Potential Improvements
- **Dynamic Thresholds**: Real-time SBA size standard updates
- **Industry-Specific**: More detailed NAICS code coverage
- **Revenue Ranges**: More granular revenue-based classification
- **Geographic Variations**: Region-specific business size standards
- **Historical Data**: Track business size changes over time

### Integration Opportunities
- **Government Contracts**: SBA size certification integration
- **Credit Scoring**: Business size for risk assessment
- **Market Analysis**: Size-based market segmentation
- **Compliance**: Regulatory reporting by business size

---

**Business size classification is now fully integrated into DataForge, providing powerful filtering capabilities for targeted data extraction!** 🎯

