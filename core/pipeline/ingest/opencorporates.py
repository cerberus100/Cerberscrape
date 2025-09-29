"""
OpenCorporates Companies Search API connector.

Endpoint: https://api.opencorporates.com/v0.4/companies/search
Auth: api_token=<OPENCORP_API_KEY>
Key params: q=free-text, jurisdiction_code=us_<state>, pagination
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional, Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import settings
from core.schemas import BusinessPullRequest

logger = logging.getLogger(__name__)

API_BASE = "https://api.opencorporates.com/v0.4/companies/search"
MAX_PER_PAGE = 100  # API limit


class OpenCorporatesConnector:
    """OpenCorporates API connector for business data."""
    
    def __init__(self):
        self.api_key = settings.opencorp_api_key
        if not self.api_key:
            logger.warning("OPENCORP_API_KEY not set - OpenCorporates connector will return empty results")
    
    def _map_state_to_jurisdiction(self, state: str) -> str:
        """Map 2-letter state code to OpenCorporates jurisdiction format."""
        state = state.upper().strip()
        if len(state) == 2:
            return f"us_{state.lower()}"
        return state
    
    def _build_search_query(self, naics: List[str], keywords: List[str]) -> str:
        """Build search query from NAICS codes and keywords."""
        query_parts = []
        
        # Add NAICS codes
        if naics:
            query_parts.extend(naics)
        
        # Add keywords
        if keywords:
            query_parts.extend(keywords)
        
        # Join with spaces for free-text search
        return " ".join(query_parts)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with retry logic."""
        if not self.api_key:
            return {"companies": []}
        
        try:
            response = httpx.get(
                API_BASE,
                params=params,
                timeout=30,
                headers={"User-Agent": "DataForge/1.0"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"OpenCorporates API request failed: {e}")
            return {"companies": []}
    
    def search_companies(
        self, 
        states: List[str], 
        naics: Optional[List[str]] = None, 
        keywords: Optional[List[str]] = None,
        limit: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Search companies across multiple states.
        
        Args:
            states: List of 2-letter state codes
            naics: Optional list of NAICS codes
            keywords: Optional list of keywords
            limit: Maximum number of results to return
            
        Returns:
            List of company records
        """
        if not self.api_key:
            logger.info("OpenCorporates API key not available - returning empty results")
            return []
        
        all_companies = []
        query = self._build_search_query(naics or [], keywords or [])
        
        if not query.strip():
            logger.warning("No search query built from NAICS/keywords - returning empty results")
            return []
        
        for state in states:
            jurisdiction = self._map_state_to_jurisdiction(state)
            logger.info(f"Searching OpenCorporates for state: {state} (jurisdiction: {jurisdiction})")
            
            page = 1
            while len(all_companies) < limit:
                params = {
                    "api_token": self.api_key,
                    "q": query,
                    "jurisdiction_code": jurisdiction,
                    "per_page": min(MAX_PER_PAGE, limit - len(all_companies)),
                    "page": page
                }
                
                # Log params without exposing API key
                safe_params = {k: v for k, v in params.items() if k != 'api_token'}
                safe_params['api_token'] = '***' if self.api_key else None
                logger.debug(f"OpenCorporates API call: {API_BASE} with params: {safe_params}")
                
                data = self._make_request(params)
                companies = data.get("companies", [])
                
                if not companies:
                    logger.info(f"No more companies found for {state} at page {page}")
                    break
                
                # Process and normalize company data
                for company in companies:
                    if len(all_companies) >= limit:
                        break
                    
                    normalized = self._normalize_company(company, state)
                    if normalized:
                        all_companies.append(normalized)
                
                page += 1
                
                # Rate limiting
                time.sleep(0.1)
                
                if len(all_companies) >= limit:
                    break
        
        logger.info(f"OpenCorporates search completed: {len(all_companies)} companies found")
        return all_companies[:limit]
    
    def _normalize_company(self, company: Dict[str, Any], state: str) -> Optional[Dict[str, Any]]:
        """Normalize OpenCorporates company data to our schema."""
        try:
            company_data = company.get("company", {})
            
            # Extract basic info
            name = company_data.get("name", "").strip()
            if not name:
                return None
            
            # Extract address
            address = company_data.get("registered_address", {})
            street = address.get("street_address", "").strip()
            city = address.get("locality", "").strip()
            postal_code = address.get("postal_code", "").strip()
            
            # Extract other fields
            domain = company_data.get("homepage_url", "").strip()
            phone = company_data.get("phone_number", "").strip()
            email = company_data.get("email", "").strip()
            
            # Extract dates
            incorporation_date = company_data.get("incorporation_date", "")
            dissolution_date = company_data.get("dissolution_date", "")
            
            # Determine if company is active
            is_active = not bool(dissolution_date)
            
            return {
                "company_name": name,
                "domain": domain,
                "phone": phone,
                "email": email,
                "address_line1": street,
                "city": city,
                "state": state.upper(),
                "postal_code": postal_code,
                "country": "US",
                "naics_code": None,  # Will be enriched later
                "industry": None,    # Will be enriched later
                "founded_year": self._extract_year(incorporation_date),
                "years_in_business": None,  # Will be calculated
                "employee_count": None,
                "annual_revenue_usd": None,
                "business_size": None,
                "is_small_business": None,
                "source": "opencorporates",
                "last_verified": None,  # Will be set by pipeline
                "quality_score": 0,
                "is_active": is_active,
                "incorporation_date": incorporation_date,
                "dissolution_date": dissolution_date
            }
            
        except Exception as e:
            logger.error(f"Error normalizing OpenCorporates company: {e}")
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


# Global instance
opencorp_connector = OpenCorporatesConnector()


def fetch_businesses(payload: BusinessPullRequest) -> List[Dict]:
    """Legacy function for backward compatibility."""
    return opencorp_connector.search_companies(
        states=payload.states,
        naics=payload.naics,
        keywords=payload.keywords,
        limit=payload.limit
    )


def ingest_opencorporates(
    states: List[str], 
    naics: Optional[List[str]] = None, 
    keywords: Optional[List[str]] = None,
    limit: int = 500
) -> List[Dict[str, Any]]:
    """
    Ingest business data from OpenCorporates.
    
    Args:
        states: List of 2-letter state codes
        naics: Optional list of NAICS codes
        keywords: Optional list of keywords
        limit: Maximum number of results to return
        
    Returns:
        List of raw business records
    """
    return opencorp_connector.search_companies(states, naics, keywords, limit)


