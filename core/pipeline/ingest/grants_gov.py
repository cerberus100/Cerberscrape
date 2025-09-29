"""
Grants.gov Search2 API connector.

Endpoint: https://www.grants.gov/api/search2
Auth: None for search2 (per docs)
Key params: keywords, posted date range
Tag: source="grants.gov"
"""
import logging
import time
from typing import Dict, List, Optional, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import settings

logger = logging.getLogger(__name__)

GRANTS_GOV_ENDPOINT = "https://www.grants.gov/api/search2"
MAX_PER_PAGE = 100  # API limit


class GrantsGovConnector:
    """Grants.gov Search2 API connector."""
    
    def __init__(self):
        self.enabled = getattr(settings, 'include_grants', False)
        if not self.enabled:
            logger.info("Grants.gov connector disabled - set include_grants=true to enable")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with retry logic."""
        if not self.enabled:
            return {"results": []}
        
        try:
            response = httpx.get(
                GRANTS_GOV_ENDPOINT,
                params=params,
                timeout=30,
                headers={"User-Agent": "DataForge/1.0"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Grants.gov API request failed: {e}")
            return {"results": []}
    
    def search_grants(
        self,
        keywords: Optional[List[str]] = None,
        posted_from: Optional[str] = None,
        posted_to: Optional[str] = None,
        limit: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Search grants from Grants.gov.
        
        Args:
            keywords: Optional list of keywords
            posted_from: ISO date string
            posted_to: ISO date string
            limit: Maximum number of results to return
            
        Returns:
            List of grant records
        """
        if not self.enabled:
            logger.info("Grants.gov connector disabled - returning empty results")
            return []
        
        all_grants = []
        
        # Build search parameters
        params = {
            "limit": min(MAX_PER_PAGE, limit),
            "offset": 0
        }
        
        # Add keywords
        if keywords:
            params["q"] = " ".join(keywords)
        
        # Add date range
        if posted_from:
            params["postedFrom"] = posted_from
        if posted_to:
            params["postedTo"] = posted_to
        
        logger.info(f"Searching Grants.gov with params: {params}")
        
        # Paginate through results
        while len(all_grants) < limit:
            params["offset"] = len(all_grants)
            params["limit"] = min(MAX_PER_PAGE, limit - len(all_grants))
            
            logger.debug(f"Grants.gov API call: {GRANTS_GOV_ENDPOINT} with params: {params}")
            
            data = self._make_request(params)
            grants = data.get("results", [])
            
            if not grants:
                logger.info(f"No more grants found at offset {params['offset']}")
                break
            
            # Process and normalize grant data
            for grant in grants:
                if len(all_grants) >= limit:
                    break
                
                normalized = self._normalize_grant(grant)
                if normalized:
                    all_grants.append(normalized)
            
            # Rate limiting
            time.sleep(0.1)
            
            if len(all_grants) >= limit:
                break
        
        logger.info(f"Grants.gov search completed: {len(all_grants)} grants found")
        return all_grants[:limit]
    
    def _normalize_grant(self, grant: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize Grants.gov grant data to our RFP schema."""
        try:
            # Extract basic info
            opportunity_id = grant.get("opportunityId", "").strip()
            if not opportunity_id:
                return None
            
            title = grant.get("title", "").strip()
            agency = grant.get("agency", "").strip()
            
            # Extract NAICS (if available)
            naics = grant.get("naics", "").strip()
            
            # Extract solicitation info
            solicitation_number = grant.get("opportunityNumber", "").strip()
            notice_type = "Grant"  # Grants.gov is primarily for grants
            
            # Extract dates
            posted_date = grant.get("postedDate", "").strip()
            close_date = grant.get("closeDate", "").strip()
            
            # Extract location
            state = grant.get("state", "").strip()
            
            # Extract description
            description = grant.get("description", "").strip()
            
            # Extract URL
            url = grant.get("url", "").strip()
            
            # Extract contact info
            contact_name = grant.get("contactName", "").strip()
            contact_email = grant.get("contactEmail", "").strip()
            
            # Extract estimated value
            estimated_value = grant.get("estimatedValue", 0)
            
            return {
                "notice_id": opportunity_id,
                "title": title,
                "agency": agency,
                "naics": naics,
                "solicitation_number": solicitation_number,
                "notice_type": notice_type,
                "posted_date": posted_date,
                "close_date": close_date,
                "place_of_performance_state": state,
                "description": description,
                "url": url,
                "contact_name": contact_name,
                "contact_email": contact_email,
                "estimated_value": estimated_value,
                "source": "grants.gov",
                "last_checked": None  # Will be set by pipeline
            }
            
        except Exception as e:
            logger.error(f"Error normalizing Grants.gov grant: {e}")
            return None


# Global instance
grants_connector = GrantsGovConnector()


def ingest_grants_gov(
    keywords: Optional[List[str]] = None,
    posted_from: Optional[str] = None,
    posted_to: Optional[str] = None,
    limit: int = 500
) -> List[Dict[str, Any]]:
    """
    Ingest grant opportunities from Grants.gov.
    
    Args:
        keywords: Optional list of keywords
        posted_from: ISO date string
        posted_to: ISO date string
        limit: Maximum number of results to return
        
    Returns:
        List of raw grant records
    """
    return grants_connector.search_grants(keywords, posted_from, posted_to, limit)

