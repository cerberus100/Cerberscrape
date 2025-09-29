"""
NPPES (Healthcare Organizations) connector.

Source: https://download.cms.gov/nppes/NPI_Files.html
Method: Download monthly ZIP files, parse organizations (Entity Type 2)
Extract: name, phones, practice address, taxonomy/specialty
Tag: source="nppes"
"""
import logging
import os
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import csv
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import settings

logger = logging.getLogger(__name__)

NPPES_BASE_URL = "https://download.cms.gov/nppes/NPI_Files.html"
NPPES_DOWNLOAD_URL = "https://download.cms.gov/nppes/NPPES_Data_Dissemination_{month}_{year}.zip"


class NPPESConnector:
    """NPPES healthcare organizations connector."""
    
    def __init__(self):
        self.cache_dir = Path(settings.export_bucket_path) / "nppes_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_latest_file_info(self) -> Dict[str, str]:
        """Get the latest NPPES file information from the download page."""
        try:
            response = requests.get(NPPES_BASE_URL, timeout=30)
            response.raise_for_status()
            content = response.text
            
            # Parse the HTML to find the latest ZIP file
            # This is a simplified parser - in production, you'd want more robust HTML parsing
            import re
            
            # Look for ZIP file links
            zip_pattern = r'href="([^"]*NPPES_Data_Dissemination_[^"]*\.zip)"'
            matches = re.findall(zip_pattern, content)
            
            if matches:
                # Get the most recent file
                latest_file = matches[-1]
                # Extract month and year from filename
                date_pattern = r'NPPES_Data_Dissemination_(\w+)_(\d{4})\.zip'
                date_match = re.search(date_pattern, latest_file)
                
                if date_match:
                    month, year = date_match.groups()
                    return {
                        "url": latest_file,
                        "month": month,
                        "year": year,
                        "filename": os.path.basename(latest_file)
                    }
            
            # Fallback to current month/year
            now = datetime.now()
            return {
                "url": NPPES_DOWNLOAD_URL.format(
                    month=now.strftime("%B"), 
                    year=now.year
                ),
                "month": now.strftime("%B"),
                "year": str(now.year),
                "filename": f"NPPES_Data_Dissemination_{now.strftime('%B')}_{now.year}.zip"
            }
            
        except Exception as e:
            logger.error(f"Error getting latest NPPES file info: {e}")
            # Fallback to current month/year
            now = datetime.now()
            return {
                "url": NPPES_DOWNLOAD_URL.format(
                    month=now.strftime("%B"), 
                    year=now.year
                ),
                "month": now.strftime("%B"),
                "year": str(now.year),
                "filename": f"NPPES_Data_Dissemination_{now.strftime('%B')}_{now.year}.zip"
            }
    
    def _is_file_cached(self, filename: str) -> bool:
        """Check if the NPPES file is already cached."""
        cache_file = self.cache_dir / filename
        return cache_file.exists()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _download_file(self, url: str, filename: str) -> Path:
        """Download NPPES ZIP file to cache."""
        cache_file = self.cache_dir / filename
        
        if self._is_file_cached(filename):
            logger.info(f"NPPES file already cached: {filename}")
            return cache_file
        
        logger.info(f"Downloading NPPES file: {url}")
        
        try:
            response = requests.get(url, timeout=300, stream=True)
            response.raise_for_status()
            
            with open(cache_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"NPPES file downloaded and cached: {filename}")
            return cache_file
            
        except Exception as e:
            logger.error(f"Error downloading NPPES file: {e}")
            raise
    
    def _extract_organizations(self, zip_path: Path) -> List[Dict[str, Any]]:
        """Extract organization records from NPPES ZIP file."""
        organizations = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Find the CSV file in the ZIP
                csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
                
                if not csv_files:
                    logger.error("No CSV files found in NPPES ZIP")
                    return organizations
                
                csv_file = csv_files[0]  # Use the first CSV file
                logger.info(f"Processing NPPES CSV file: {csv_file}")
                
                with zip_ref.open(csv_file) as csv_file_obj:
                    # Read CSV with proper encoding
                    content = csv_file_obj.read().decode('utf-8', errors='ignore')
                    csv_reader = csv.DictReader(content.splitlines())
                    
                    for row in csv_reader:
                        # Only process organizations (Entity Type 2)
                        if row.get('Entity Type Code') == '2':
                            org = self._normalize_organization(row)
                            if org:
                                organizations.append(org)
                
                logger.info(f"Extracted {len(organizations)} organizations from NPPES")
                
        except Exception as e:
            logger.error(f"Error extracting organizations from NPPES: {e}")
        
        return organizations
    
    def _normalize_organization(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Normalize NPPES organization data to our schema."""
        try:
            # Extract basic info
            name = row.get('Provider Organization Name (Legal Business Name)', '').strip()
            if not name:
                return None
            
            # Extract address (practice location)
            address_line1 = row.get('Provider First Line Business Practice Location Address', '').strip()
            city = row.get('Provider Business Practice Location Address City Name', '').strip()
            state = row.get('Provider Business Practice Location Address State Name', '').strip()
            postal_code = row.get('Provider Business Practice Location Address Postal Code', '').strip()
            
            # Extract contact info
            phone = row.get('Provider Business Practice Location Address Telephone Number', '').strip()
            fax = row.get('Provider Business Practice Location Address Fax Number', '').strip()
            
            # Extract taxonomy/specialty
            taxonomy_code = row.get('Healthcare Provider Taxonomy Code_1', '').strip()
            taxonomy_desc = row.get('Provider License Number_1', '').strip()  # Often contains specialty info
            
            # Extract NPI
            npi = row.get('NPI', '').strip()
            
            # Extract dates
            enumeration_date = row.get('Provider Enumeration Date', '').strip()
            last_update = row.get('Last Update Date', '').strip()
            
            return {
                "company_name": name,
                "domain": None,  # Will be enriched later
                "phone": phone,
                "email": None,  # Will be enriched later
                "address_line1": address_line1,
                "city": city,
                "state": state.upper() if state else None,
                "postal_code": postal_code,
                "country": "US",
                "naics_code": None,  # Will be enriched later
                "industry": taxonomy_desc or "Healthcare",
                "founded_year": self._extract_year(enumeration_date),
                "years_in_business": None,  # Will be calculated
                "employee_count": None,
                "annual_revenue_usd": None,
                "business_size": None,
                "is_small_business": None,
                "source": "nppes",
                "last_verified": None,  # Will be set by pipeline
                "quality_score": 0,
                "npi": npi,
                "taxonomy_code": taxonomy_code,
                "fax": fax,
                "enumeration_date": enumeration_date,
                "last_update": last_update
            }
            
        except Exception as e:
            logger.error(f"Error normalizing NPPES organization: {e}")
            return None
    
    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extract year from date string."""
        if not date_str:
            return None
        
        try:
            # Handle various date formats
            if "-" in date_str:
                year = int(date_str.split("-")[0])
            elif "/" in date_str:
                year = int(date_str.split("/")[-1])
            else:
                year = int(date_str[:4])
            
            # Sanity check
            if 1800 <= year <= 2030:
                return year
        except (ValueError, IndexError):
            pass
        
        return None
    
    def search_organizations(
        self,
        states: List[str],
        keywords: Optional[List[str]] = None,
        limit: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Search healthcare organizations from NPPES.
        
        Args:
            states: List of 2-letter state codes
            keywords: Optional list of keywords for filtering
            limit: Maximum number of results to return
            
        Returns:
            List of organization records
        """
        try:
            # Get latest file info
            file_info = self._get_latest_file_info()
            
            # Download and cache file
            zip_path = self._download_file(file_info["url"], file_info["filename"])
            
            # Extract organizations
            all_orgs = self._extract_organizations(zip_path)
            
            # Filter by states
            filtered_orgs = []
            for org in all_orgs:
                if org.get("state") in [s.upper() for s in states]:
                    filtered_orgs.append(org)
            
            # Filter by keywords if provided
            if keywords:
                keyword_filtered = []
                for org in filtered_orgs:
                    org_text = " ".join([
                        org.get("company_name", ""),
                        org.get("industry", ""),
                        org.get("taxonomy_code", "")
                    ]).lower()
                    
                    if any(keyword.lower() in org_text for keyword in keywords):
                        keyword_filtered.append(org)
                
                filtered_orgs = keyword_filtered
            
            # Limit results
            result = filtered_orgs[:limit]
            
            logger.info(f"NPPES search completed: {len(result)} organizations found")
            return result
            
        except Exception as e:
            logger.error(f"Error in NPPES search: {e}")
            return []


# Global instance
nppes_connector = NPPESConnector()


def ingest_nppes(
    states: List[str],
    keywords: Optional[List[str]] = None,
    limit: int = 500
) -> List[Dict[str, Any]]:
    """
    Ingest healthcare organization data from NPPES.
    
    Args:
        states: List of 2-letter state codes
        keywords: Optional list of keywords for filtering
        limit: Maximum number of results to return
        
    Returns:
        List of raw organization records
    """
    return nppes_connector.search_organizations(states, keywords, limit)

