"""
U.S. Census Geocoder - County & FIPS lookup.

Endpoints:
- One-line: https://geocoding.geo.census.gov/geocoder/locations/onelineaddress
- Component: https://geocoding.geo.census.gov/geocoder/locations/address

Output: county name + 5-digit county FIPS
"""

from __future__ import annotations

import logging
import time
from typing import Iterable, List, Optional, Dict, Any
from urllib.parse import quote

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from core.schemas import BusinessCanonical

logger = logging.getLogger(__name__)

# Census Geocoder endpoints
ONELINE_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
COMPONENT_URL = "https://geocoding.geo.census.gov/geocoder/locations/address"


class CensusGeocoder:
    """U.S. Census Geocoder for county and FIPS lookup."""
    
    def __init__(self):
        self.enabled = True  # Always available (no API key required)
    
    def _build_oneline_address(self, record: BusinessCanonical) -> str:
        """Build a single-line address string for geocoding."""
        parts = []
        
        if record.address_line1:
            parts.append(record.address_line1)
        if record.city:
            parts.append(record.city)
        if record.state:
            parts.append(record.state)
        if record.postal_code:
            parts.append(record.postal_code)
        
        return ", ".join(parts)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8)
    )
    def _geocode_oneline(self, address: str) -> Optional[Dict[str, Any]]:
        """Geocode using the one-line address endpoint."""
        try:
            params = {
                "address": address,
                "benchmark": "Public_AR_Current",
                "format": "json"
            }
            
            response = httpx.get(ONELINE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            matches = data.get("result", {}).get("addressMatches", [])
            if matches:
                return matches[0]
            
        except httpx.HTTPError as e:
            logger.warning(f"Census geocoder one-line request failed: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error in Census geocoder: {e}")
        
        return None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8)
    )
    def _geocode_component(self, record: BusinessCanonical) -> Optional[Dict[str, Any]]:
        """Geocode using the component address endpoint."""
        try:
            params = {
                "street": record.address_line1 or "",
                "city": record.city or "",
                "state": record.state or "",
                "zip": record.postal_code or "",
                "benchmark": "Public_AR_Current",
                "format": "json"
            }
            
            response = httpx.get(COMPONENT_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            matches = data.get("result", {}).get("addressMatches", [])
            if matches:
                return matches[0]
            
        except httpx.HTTPError as e:
            logger.warning(f"Census geocoder component request failed: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error in Census geocoder: {e}")
        
        return None
    
    def geocode_record(self, record: BusinessCanonical) -> BusinessCanonical:
        """Geocode a single business record to get county and FIPS."""
        if not self.enabled:
            return record
        
        # Skip if we don't have enough address info
        if not record.address_line1 and not record.postal_code:
            return record
        
        # Try one-line address first (more reliable)
        if record.address_line1 and record.city and record.state:
            address = self._build_oneline_address(record)
            match = self._geocode_oneline(address)
        else:
            # Fall back to component geocoding
            match = self._geocode_component(record)
        
        if not match:
            logger.debug(f"No geocoding match found for: {record.company_name}")
            return record
        
        # Extract county and FIPS from the match
        county = None
        county_fips = None
        
        try:
            # Get county name from address components
            components = match.get("addressComponents", {})
            county = components.get("county", "").strip()
            
            # Get county FIPS from geographies
            geographies = match.get("geographies", {})
            counties = geographies.get("Counties", [])
            
            if counties:
                county_fips = counties[0].get("COUNTY", "").strip()
                
                # Ensure FIPS is 5 digits
                if county_fips and len(county_fips) == 5 and county_fips.isdigit():
                    pass  # Valid 5-digit FIPS
                else:
                    county_fips = None
            
            # Log successful geocoding
            if county or county_fips:
                logger.debug(f"Geocoded {record.company_name}: county={county}, fips={county_fips}")
            
        except Exception as e:
            logger.warning(f"Error parsing geocoding result for {record.company_name}: {e}")
        
        # Update record with geocoding results
        return record.model_copy(update={
            "county": county,
            "county_fips": county_fips,
        })
    
    def geocode_records(self, records: Iterable[BusinessCanonical]) -> List[BusinessCanonical]:
        """Geocode multiple business records."""
        if not self.enabled:
            return list(records)
        
        enriched = []
        for record in records:
            try:
                geocoded = self.geocode_record(record)
                enriched.append(geocoded)
                
                # Rate limiting to be respectful to the API
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error geocoding record {record.company_name}: {e}")
                enriched.append(record)  # Keep original record on error
        
        return enriched


# Global instance
census_geocoder = CensusGeocoder()


def geocode_records(records: Iterable[BusinessCanonical]) -> List[BusinessCanonical]:
    """Legacy function for backward compatibility."""
    return census_geocoder.geocode_records(records)


