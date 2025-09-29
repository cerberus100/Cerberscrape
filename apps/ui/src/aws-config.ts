// AWS Amplify configuration for DataForge UI

export const awsConfig = {
  // API Gateway endpoint (will be set by Amplify)
  apiEndpoint: process.env.REACT_APP_API_ENDPOINT || 'http://localhost:8000',
  
  // S3 bucket for file downloads
  s3Bucket: process.env.REACT_APP_S3_BUCKET || '',
  
  // Environment
  environment: process.env.NODE_ENV || 'development',
  
  // Amplify region
  region: process.env.REACT_APP_AWS_REGION || 'us-east-1',
};

// Helper function to get full API URL
export const getApiUrl = (endpoint: string): string => {
  const baseUrl = awsConfig.apiEndpoint.replace(/\/$/, '');
  const cleanEndpoint = endpoint.replace(/^\//, '');
  return `${baseUrl}/${cleanEndpoint}`;
};

// Helper function to get S3 download URL
export const getS3DownloadUrl = (s3Key: string): string => {
  if (awsConfig.s3Bucket) {
    return `https://${awsConfig.s3Bucket}.s3.${awsConfig.region}.amazonaws.com/${s3Key}`;
  }
  return s3Key; // Fallback to local path
};

