"""Application configuration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# from core.aws import RDSManager, SecretsManager  # Avoid circular import


class Settings(BaseSettings):
    """Global application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="DATAFORGE_", case_sensitive=False, extra="ignore")

    # Database
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5433/dataforge"
    
    # Storage
    export_bucket_path: Path = Path("./exports")
    s3_bucket: Optional[str] = None
    
    # API Keys
    opencorp_api_key: Optional[str] = None
    sam_api_key: Optional[str] = None
    
    # Features
    smtp_probe: bool = False
    enable_geocoder_default: bool = False
    allowed_scrape_domains: List[str] = []
    
    # CORS
    cors_allow_origins: List[str] = ["*"]
    
    # Environment
    environment: str = "development"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # AWS-specific configuration
        if os.getenv("AWS_REGION"):
            self._configure_aws()
    
    def _configure_aws(self):
        """Configure AWS-specific settings."""
        # Use RDS if available
        from core.aws import RDSManager
        rds_url = RDSManager.get_connection_string()
        if rds_url != self.database_url:
            self.database_url = rds_url
        
        # Get API keys from Secrets Manager
        if not self.opencorp_api_key or not self.sam_api_key:
            from core.aws import SecretsManager
            secrets = SecretsManager()
            api_keys = secrets.get_api_keys()
            if api_keys.get('opencorp_api_key'):
                self.opencorp_api_key = api_keys['opencorp_api_key']
            if api_keys.get('sam_api_key'):
                self.sam_api_key = api_keys['sam_api_key']
        
        # Configure S3 export path
        if os.getenv("DATAFORGE_S3_BUCKET"):
            self.s3_bucket = os.getenv("DATAFORGE_S3_BUCKET")
            self.export_bucket_path = Path("/tmp/exports")  # Lambda temp directory


settings = Settings()


