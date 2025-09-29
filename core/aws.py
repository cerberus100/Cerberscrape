"""AWS-specific utilities for DataForge."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from core.config import settings


class S3Exporter:
    """S3-based export storage for DataForge."""
    
    def __init__(self, bucket_name: Optional[str] = None):
        self.bucket_name = bucket_name or os.getenv("DATAFORGE_S3_BUCKET")
        self.s3_client = boto3.client('s3') if self.bucket_name else None
    
    def upload_file(self, local_path: Path, s3_key: str) -> str:
        """Upload file to S3 and return public URL."""
        if not self.s3_client:
            return str(local_path)  # Fallback to local path
        
        try:
            self.s3_client.upload_file(
                str(local_path), 
                self.bucket_name, 
                s3_key
            )
            return f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
        except ClientError as e:
            print(f"Failed to upload to S3: {e}")
            return str(local_path)  # Fallback to local path
    
    def download_file(self, s3_key: str, local_path: Path) -> bool:
        """Download file from S3."""
        if not self.s3_client:
            return False
        
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, str(local_path))
            return True
        except ClientError as e:
            print(f"Failed to download from S3: {e}")
            return False


class RDSManager:
    """RDS connection management for AWS."""
    
    @staticmethod
    def get_connection_string() -> str:
        """Get RDS connection string from environment."""
        host = os.getenv("DATAFORGE_RDS_HOST")
        port = os.getenv("DATAFORGE_RDS_PORT", "5432")
        database = os.getenv("DATAFORGE_RDS_DATABASE", "dataforge")
        username = os.getenv("DATAFORGE_RDS_USERNAME", "postgres")
        password = os.getenv("DATAFORGE_RDS_PASSWORD")
        
        if not all([host, password]):
            return settings.database_url  # Fallback to local config
        
        return f"postgresql+psycopg://{username}:{password}@{host}:{port}/{database}"


class SecretsManager:
    """AWS Secrets Manager integration."""
    
    def __init__(self):
        self.secrets_client = boto3.client('secretsmanager')
    
    def get_secret(self, secret_name: str) -> Optional[str]:
        """Retrieve secret from AWS Secrets Manager."""
        try:
            response = self.secrets_client.get_secret_value(SecretId=secret_name)
            return response['SecretString']
        except ClientError as e:
            print(f"Failed to retrieve secret {secret_name}: {e}")
            return None
    
    def get_api_keys(self) -> dict:
        """Get API keys from Secrets Manager."""
        return {
            'opencorp_api_key': self.get_secret('dataforge/opencorp-api-key'),
            'sam_api_key': self.get_secret('dataforge/sam-api-key'),
        }

