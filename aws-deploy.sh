#!/bin/bash

# DataForge AWS Deployment Script
set -e

echo "🚀 Deploying DataForge to AWS..."

# Check if required tools are installed
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI not found. Please install it first." >&2; exit 1; }
command -v serverless >/dev/null 2>&1 || { echo "❌ Serverless Framework not found. Please install it first." >&2; exit 1; }

# Set default values
STAGE=${1:-dev}
REGION=${2:-us-east-1}

echo "📋 Deployment Configuration:"
echo "   Stage: $STAGE"
echo "   Region: $REGION"

# Check AWS credentials
echo "🔐 Checking AWS credentials..."
aws sts get-caller-identity >/dev/null || { echo "❌ AWS credentials not configured." >&2; exit 1; }

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install serverless plugins
echo "🔌 Installing Serverless plugins..."
npm install -g serverless-python-requirements serverless-s3-remover

# Deploy backend
echo "🏗️  Deploying backend services..."
serverless deploy --stage $STAGE --region $REGION

# Get deployment outputs
echo "📊 Getting deployment outputs..."
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name dataforge-$STAGE \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`ServiceEndpoint`].OutputValue' \
  --output text)

S3_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name dataforge-$STAGE \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
  --output text)

echo "✅ Backend deployed successfully!"
echo "   API Endpoint: $API_ENDPOINT"
echo "   S3 Bucket: $S3_BUCKET"

# Deploy frontend to Amplify
echo "🎨 Deploying frontend to Amplify..."
cd apps/ui

# Create environment file for Amplify
cat > .env.production << EOF
REACT_APP_API_ENDPOINT=$API_ENDPOINT
REACT_APP_S3_BUCKET=$S3_BUCKET
REACT_APP_AWS_REGION=$REGION
EOF

echo "📝 Frontend environment configured:"
echo "   API Endpoint: $API_ENDPOINT"
echo "   S3 Bucket: $S3_BUCKET"
echo "   Region: $REGION"

echo ""
echo "🎉 DataForge deployment complete!"
echo ""
echo "Next steps:"
echo "1. Set up your Amplify app and connect it to this repository"
echo "2. Configure environment variables in Amplify console"
echo "3. Set up RDS database and update environment variables"
echo "4. Configure API keys in AWS Secrets Manager"
echo ""
echo "Environment variables for Amplify:"
echo "   REACT_APP_API_ENDPOINT=$API_ENDPOINT"
echo "   REACT_APP_S3_BUCKET=$S3_BUCKET"
echo "   REACT_APP_AWS_REGION=$REGION"

