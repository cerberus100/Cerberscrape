# DataForge Deployment Checklist

## ✅ Pre-Deployment Verification

### Local Testing
- [x] Core modules import successfully
- [x] Pydantic schemas validate correctly
- [x] Configuration loads properly
- [x] AWS utilities initialize
- [x] Python 3.9+ compatibility verified
- [x] All files created and structured correctly

### Code Quality
- [x] Type hints compatible with Python 3.9
- [x] Circular imports resolved
- [x] Error handling implemented
- [x] Documentation complete

## 🚀 AWS Deployment Steps

### 1. Prerequisites
- [ ] AWS CLI configured with appropriate permissions
- [ ] Node.js and npm installed
- [ ] Python 3.11+ available
- [ ] Serverless Framework installed: `npm install -g serverless`

### 2. Backend Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Deploy backend services
./aws-deploy.sh dev us-east-1
```

### 3. Database Setup
- [ ] Create RDS PostgreSQL instance
- [ ] Configure security groups
- [ ] Set environment variables:
  - `DATAFORGE_RDS_HOST`
  - `DATAFORGE_RDS_PASSWORD`
  - `DATAFORGE_RDS_DATABASE`

### 4. Secrets Management
- [ ] Store OpenCorporates API key in Secrets Manager
- [ ] Store SAM.gov API key in Secrets Manager
- [ ] Verify IAM permissions for Lambda to access secrets

### 5. Frontend Deployment (Amplify)
- [ ] Connect GitHub repository to Amplify
- [ ] Configure build settings with `amplify.yml`
- [ ] Set environment variables:
  - `REACT_APP_API_ENDPOINT`
  - `REACT_APP_S3_BUCKET`
  - `REACT_APP_AWS_REGION`

### 6. Testing
- [ ] Verify API endpoints respond correctly
- [ ] Test business data extraction
- [ ] Test RFP extraction
- [ ] Verify S3 file uploads
- [ ] Test UI functionality

## 🔧 Configuration Files

### Environment Variables
```bash
# Database
DATAFORGE_RDS_HOST=your-rds-endpoint.amazonaws.com
DATAFORGE_RDS_PASSWORD=YourSecurePassword
DATAFORGE_RDS_DATABASE=dataforge

# AWS
DATAFORGE_S3_BUCKET=your-dataforge-exports-bucket
AWS_REGION=us-east-1

# API Keys (stored in Secrets Manager)
# dataforge/opencorp-api-key
# dataforge/sam-api-key
```

### Amplify Environment Variables
```bash
REACT_APP_API_ENDPOINT=https://your-api-gateway-url.amazonaws.com/prod
REACT_APP_S3_BUCKET=your-dataforge-exports-bucket
REACT_APP_AWS_REGION=us-east-1
```

## 📊 Expected Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Amplify UI    │    │  API Gateway    │    │   Lambda        │
│   (React)       │───▶│   (FastAPI)     │───▶│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐              │
                       │   RDS           │◀─────────────┘
                       │   (PostgreSQL)  │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   S3 Bucket     │
                       │   (Exports)     │
                       └─────────────────┘
```

## 🧪 Post-Deployment Testing

### API Endpoints
- [ ] `GET /healthz` returns 200 OK
- [ ] `POST /pull/business` processes requests
- [ ] `POST /pull/rfps` processes requests
- [ ] `GET /preview/business` returns data
- [ ] `GET /preview/rfps` returns data

### Data Pipeline
- [ ] Business data ingestion works
- [ ] RFP data ingestion works
- [ ] Deduplication functions correctly
- [ ] CSV export generates properly
- [ ] S3 uploads succeed
- [ ] QA validation passes

### UI Functionality
- [ ] Mode selection works
- [ ] State selection works
- [ ] Form submission works
- [ ] Results display correctly
- [ ] Download links work
- [ ] QA summaries show

## 🔒 Security Checklist

- [ ] RDS in private subnets
- [ ] Security groups properly configured
- [ ] IAM roles follow least privilege
- [ ] Secrets encrypted in Secrets Manager
- [ ] S3 bucket access restricted
- [ ] CORS configured appropriately
- [ ] HTTPS enforced everywhere

## 📈 Monitoring Setup

- [ ] CloudWatch alarms configured
- [ ] Error rate monitoring
- [ ] Latency monitoring
- [ ] S3 access logging
- [ ] API Gateway logging
- [ ] Lambda function logging

## 🚨 Troubleshooting

### Common Issues
1. **CORS Errors**: Check API Gateway CORS configuration
2. **Database Connection**: Verify RDS security groups and credentials
3. **S3 Access**: Check IAM permissions for Lambda
4. **Secrets Access**: Verify secret names and IAM permissions
5. **Build Failures**: Check Node.js/Python versions in Amplify

### Useful Commands
```bash
# View Lambda logs
serverless logs -f api --stage dev

# Check API Gateway
aws apigateway get-rest-apis

# Test S3 access
aws s3 ls s3://your-bucket-name

# Check secrets
aws secretsmanager list-secrets
```

## ✅ Success Criteria

- [ ] All API endpoints respond correctly
- [ ] Business data extraction produces valid CSV
- [ ] RFP extraction produces valid CSV
- [ ] UI loads and functions properly
- [ ] File downloads work from S3
- [ ] No critical errors in logs
- [ ] Performance meets requirements (< 30s for typical requests)

## 📝 Next Steps After Deployment

1. **Monitor**: Set up alerts and dashboards
2. **Optimize**: Review performance and costs
3. **Scale**: Configure auto-scaling if needed
4. **Backup**: Set up automated backups
5. **Documentation**: Update user guides
6. **Training**: Train users on the system

