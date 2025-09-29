# DataForge AWS Deployment Guide

This guide walks you through deploying DataForge to AWS using Amplify and Serverless Framework.

## Prerequisites

1. **AWS CLI** configured with appropriate permissions
2. **Node.js** and **npm** installed
3. **Python 3.11** installed
4. **Serverless Framework** installed globally: `npm install -g serverless`

## Quick Deployment

```bash
# Deploy to AWS
./aws-deploy.sh dev us-east-1

# Or with custom stage/region
./aws-deploy.sh prod us-west-2
```

## Manual Setup Steps

### 1. Backend Deployment (Serverless)

```bash
# Install dependencies
pip install -r requirements.txt
npm install -g serverless-python-requirements serverless-s3-remover

# Deploy backend
serverless deploy --stage dev --region us-east-1
```

### 2. Database Setup (RDS)

Create an RDS PostgreSQL instance:

```bash
aws rds create-db-instance \
  --db-instance-identifier dataforge-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password YourSecurePassword \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxxxxx
```

### 3. Secrets Manager Setup

Store API keys securely:

```bash
# OpenCorporates API key
aws secretsmanager create-secret \
  --name dataforge/opencorp-api-key \
  --secret-string "your-opencorp-api-key"

# SAM.gov API key
aws secretsmanager create-secret \
  --name dataforge/sam-api-key \
  --secret-string "your-sam-api-key"
```

### 4. Environment Variables

Set these environment variables in your deployment:

```bash
export DATAFORGE_RDS_HOST=your-rds-endpoint.amazonaws.com
export DATAFORGE_RDS_PASSWORD=YourSecurePassword
export DATAFORGE_RDS_DATABASE=dataforge
```

### 5. Frontend Deployment (Amplify)

1. **Connect Repository**: Connect your GitHub repository to Amplify
2. **Configure Build**: Use the provided `amplify.yml`
3. **Set Environment Variables**:
   ```
   REACT_APP_API_ENDPOINT=https://your-api-gateway-url.amazonaws.com/prod
   REACT_APP_S3_BUCKET=your-dataforge-exports-bucket
   REACT_APP_AWS_REGION=us-east-1
   ```

## Architecture

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

## Cost Optimization

- **Lambda**: Pay per request, auto-scaling
- **RDS**: Use `db.t3.micro` for development
- **S3**: Standard storage with lifecycle policies
- **API Gateway**: Pay per API call

## Security Considerations

1. **IAM Roles**: Least privilege access
2. **VPC**: Deploy RDS in private subnets
3. **Secrets**: Use AWS Secrets Manager
4. **CORS**: Configure appropriate origins
5. **HTTPS**: All traffic encrypted in transit

## Monitoring

- **CloudWatch**: Logs and metrics
- **X-Ray**: Distributed tracing
- **Alarms**: Set up for errors and latency

## Troubleshooting

### Common Issues

1. **CORS Errors**: Check API Gateway CORS configuration
2. **Database Connection**: Verify RDS security groups
3. **S3 Access**: Check IAM permissions
4. **Secrets**: Verify secret names and permissions

### Logs

```bash
# View Lambda logs
serverless logs -f api --stage dev

# View API Gateway logs
aws logs describe-log-groups --log-group-name-prefix /aws/apigateway
```

## Production Checklist

- [ ] RDS in multi-AZ configuration
- [ ] S3 bucket with versioning enabled
- [ ] CloudWatch alarms configured
- [ ] Backup strategy implemented
- [ ] Security groups properly configured
- [ ] API keys rotated regularly
- [ ] Monitoring and alerting set up

