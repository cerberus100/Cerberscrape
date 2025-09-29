"""
Manual State SoS Bulk connector.

Method: Allow a local CSV drop + YAML mapper for arbitrary state files
Tag: source="state_manual:<STATE>"
"""
import logging
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

from core.config import settings

logger = logging.getLogger(__name__)


class StateManualConnector:
    """Manual state CSV connector with YAML mapping."""
    
    def __init__(self):
        self.data_dir = Path(settings.export_bucket_path) / "state_manual"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.mappers_dir = self.data_dir / "mappers"
        self.mappers_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_mapper(self, state: str) -> Optional[Dict[str, str]]:
        """Load YAML mapper for a state."""
        mapper_file = self.mappers_dir / f"{state.lower()}_mapper.yaml"
        
        if not mapper_file.exists():
            logger.warning(f"No mapper found for state {state}: {mapper_file}")
            return None
        
        try:
            with open(mapper_file, 'r') as f:
                mapper = yaml.safe_load(f)
            return mapper
        except Exception as e:
            logger.error(f"Error loading mapper for {state}: {e}")
            return None
    
    def _find_csv_files(self, state: str) -> List[Path]:
        """Find CSV files for a state."""
        csv_files = []
        
        # Look for CSV files with state name
        patterns = [
            f"{state.lower()}_*.csv",
            f"{state.upper()}_*.csv",
            f"*{state.lower()}*.csv",
            f"*{state.upper()}*.csv"
        ]
        
        for pattern in patterns:
            csv_files.extend(self.data_dir.glob(pattern))
        
        return csv_files
    
    def _normalize_record(self, row: Dict[str, str], mapper: Dict[str, str], state: str) -> Optional[Dict[str, Any]]:
        """Normalize a CSV row using the mapper."""
        try:
            # Apply field mapping
            normalized = {}
            for our_field, csv_field in mapper.items():
                if csv_field in row:
                    normalized[our_field] = row[csv_field].strip()
                else:
                    normalized[our_field] = None
            
            # Ensure we have a company name
            if not normalized.get("company_name"):
                return None
            
            # Set source
            normalized["source"] = f"state_manual:{state.upper()}"
            
            # Set default values for required fields
            normalized.setdefault("country", "US")
            normalized.setdefault("state", state.upper())
            normalized.setdefault("quality_score", 0)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing record: {e}")
            return None
    
    def search_companies(
        self,
        states: List[str],
        keywords: Optional[List[str]] = None,
        limit: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Search companies from manual state CSV files.
        
        Args:
            states: List of 2-letter state codes
            keywords: Optional list of keywords for filtering
            limit: Maximum number of results to return
            
        Returns:
            List of company records
        """
        all_companies = []
        
        for state in states:
            # Load mapper for this state
            mapper = self._load_mapper(state)
            if not mapper:
                logger.info(f"No mapper available for {state}, skipping")
                continue
            
            # Find CSV files for this state
            csv_files = self._find_csv_files(state)
            if not csv_files:
                logger.info(f"No CSV files found for {state}")
                continue
            
            logger.info(f"Processing {len(csv_files)} CSV files for {state}")
            
            for csv_file in csv_files:
                try:
                    companies = self._process_csv_file(csv_file, mapper, state, keywords, limit)
                    all_companies.extend(companies)
                    
                    if len(all_companies) >= limit:
                        break
                        
                except Exception as e:
                    logger.error(f"Error processing CSV file {csv_file}: {e}")
                    continue
            
            if len(all_companies) >= limit:
                break
        
        result = all_companies[:limit]
        logger.info(f"State manual search completed: {len(result)} companies found")
        return result
    
    def _process_csv_file(
        self,
        csv_file: Path,
        mapper: Dict[str, str],
        state: str,
        keywords: Optional[List[str]] = None,
        limit: int = 500
    ) -> List[Dict[str, Any]]:
        """Process a single CSV file."""
        companies = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                # Try to detect delimiter
                sample = f.read(1024)
                f.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(f, delimiter=delimiter)
                
                for row in reader:
                    if len(companies) >= limit:
                        break
                    
                    # Normalize the record
                    normalized = self._normalize_record(row, mapper, state)
                    if not normalized:
                        continue
                    
                    # Filter by keywords if provided
                    if keywords:
                        company_text = " ".join([
                            normalized.get("company_name", ""),
                            normalized.get("industry", ""),
                            normalized.get("naics_code", "")
                        ]).lower()
                        
                        if not any(keyword.lower() in company_text for keyword in keywords):
                            continue
                    
                    companies.append(normalized)
        
        except Exception as e:
            logger.error(f"Error reading CSV file {csv_file}: {e}")
        
        return companies
    
    def create_sample_mapper(self, state: str) -> Path:
        """Create a sample mapper YAML file for a state."""
        sample_mapper = {
            "company_name": "Company Name",
            "domain": "Website",
            "phone": "Phone",
            "email": "Email",
            "address_line1": "Address",
            "city": "City",
            "postal_code": "Zip Code",
            "naics_code": "NAICS",
            "industry": "Industry",
            "founded_year": "Founded Year",
            "employee_count": "Employees"
        }
        
        mapper_file = self.mappers_dir / f"{state.lower()}_mapper.yaml"
        
        with open(mapper_file, 'w') as f:
            yaml.dump(sample_mapper, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Created sample mapper for {state}: {mapper_file}")
        return mapper_file


# Global instance
state_manual_connector = StateManualConnector()


def ingest_state_manual(
    states: List[str],
    keywords: Optional[List[str]] = None,
    limit: int = 500
) -> List[Dict[str, Any]]:
    """
    Ingest business data from manual state CSV files.
    
    Args:
        states: List of 2-letter state codes
        keywords: Optional list of keywords for filtering
        limit: Maximum number of results to return
        
    Returns:
        List of raw business records
    """
    return state_manual_connector.search_companies(states, keywords, limit)


def create_sample_mapper(state: str) -> Path:
    """Create a sample mapper YAML file for a state."""
    return state_manual_connector.create_sample_mapper(state)

