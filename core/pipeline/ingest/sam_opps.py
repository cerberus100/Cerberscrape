"""
SAM.gov Contract Opportunities API connector.

Endpoint: https://api.sam.gov/opportunities/v1/search
Auth: api_key=<SAM_API_KEY>
Key params: postedFrom, postedTo, ncode (NAICS), placeOfPerformance.state, noticeType
"""

from __future__ import annotations

import datetime as dt
import logging
import time
from typing import Dict, List, Optional, Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import settings
from core.schemas import RFPPullRequest

logger = logging.getLogger(__name__)

SAM_ENDPOINT = "https://api.sam.gov/opportunities/v1/search"
MAX_PER_PAGE = 1000  # API limit


class SAMConnector:
    """SAM.gov Contract Opportunities API connector."""
    
    def __init__(self):
        self.api_key = settings.sam_api_key
        if not self.api_key:
            logger.warning("SAM_API_KEY not set - SAM.gov connector will return mock data")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with retry logic."""
        if not self.api_key:
            return {"opportunitiesData": []}
        
        try:
            headers = {"X-API-KEY": self.api_key}
            response = httpx.get(
                SAM_ENDPOINT,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"SAM.gov API request failed: {e}")
            return {"opportunitiesData": []}
    
    def search_opportunities(
        self,
        states: List[str],
        naics: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        posted_from: Optional[str] = None,
        posted_to: Optional[str] = None,
        notice_type: str = "Solicitation",
        limit: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Search contract opportunities from SAM.gov.
        
        Args:
            states: List of 2-letter state codes
            naics: Optional list of NAICS codes
            keywords: Optional list of keywords
            posted_from: ISO date string (required by API)
            posted_to: ISO date string (required by API)
            notice_type: Type of notice (default: Solicitation)
            limit: Maximum number of results to return
            
        Returns:
            List of opportunity records
        """
        if not self.api_key:
            logger.info("SAM.gov API key not available - returning mock data")
            return self._get_mock_data(states, naics, keywords, posted_from, posted_to, limit)
        
        # SAM.gov requires postedFrom and postedTo
        if not posted_from or not posted_to:
            # Default to last 30 days
            end_date = dt.date.today()
            start_date = end_date - dt.timedelta(days=30)
            posted_from = start_date.isoformat()
            posted_to = end_date.isoformat()
        
        all_opportunities = []
        
        # Build search parameters
        params = {
            "postedFrom": posted_from,
            "postedTo": posted_to,
            "noticeType": notice_type,
            "limit": min(MAX_PER_PAGE, limit),
            "offset": 0
        }
        
        # Add NAICS codes
        if naics:
            params["ncode"] = ",".join(naics)
        
        # Add states
        if states:
            params["placeOfPerformance.state"] = ",".join(states)
        
        # Add keywords
        if keywords:
            params["q"] = " ".join(keywords)
        
        logger.info(f"Searching SAM.gov with params: {params}")
        
        # Paginate through results
        while len(all_opportunities) < limit:
            params["offset"] = len(all_opportunities)
            params["limit"] = min(MAX_PER_PAGE, limit - len(all_opportunities))
            
            logger.debug(f"SAM.gov API call: {SAM_ENDPOINT} with params: {params}")
            
            data = self._make_request(params)
            opportunities = data.get("opportunitiesData", [])
            
            if not opportunities:
                logger.info(f"No more opportunities found at offset {params['offset']}")
                break
            
            # Process and normalize opportunity data
            for opportunity in opportunities:
                if len(all_opportunities) >= limit:
                    break
                
                normalized = self._normalize_opportunity(opportunity)
                if normalized:
                    all_opportunities.append(normalized)
            
            # Rate limiting
            time.sleep(0.1)
            
            if len(all_opportunities) >= limit:
                break
        
        logger.info(f"SAM.gov search completed: {len(all_opportunities)} opportunities found")
        return all_opportunities[:limit]
    
    def _normalize_opportunity(self, opportunity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize SAM.gov opportunity data to our schema."""
        try:
            # Extract basic info
            notice_id = opportunity.get("noticeId", "").strip()
            if not notice_id:
                return None
            
            title = opportunity.get("title", "").strip()
            agency = opportunity.get("department", {}).get("name", "").strip()
            
            # Extract NAICS
            naics = opportunity.get("naicsCode", {}).get("code", "").strip()
            
            # Extract solicitation info
            solicitation_number = opportunity.get("solicitationNumber", "").strip()
            notice_type = opportunity.get("noticeType", "").strip()
            
            # Extract dates
            posted_date = opportunity.get("postedDate", "").strip()
            close_date = opportunity.get("responseDeadline", "").strip()
            
            # Extract location
            place_of_performance = opportunity.get("placeOfPerformance", {})
            state = place_of_performance.get("state", "").strip()
            
            # Extract description
            description = opportunity.get("description", "").strip()
            
            # Extract URL
            url = opportunity.get("uiLink", "").strip()
            
            # Extract contact info
            point_of_contact = opportunity.get("pointOfContact", {})
            contact_name = point_of_contact.get("fullName", "").strip()
            contact_email = point_of_contact.get("email", "").strip()
            
            # Extract estimated value
            estimated_value = opportunity.get("award", {}).get("awardAmount", 0)
            
            return {
                "notice_id": notice_id,
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
                "source": "sam.gov",
                "last_checked": None  # Will be set by pipeline
            }
            
        except Exception as e:
            logger.error(f"Error normalizing SAM.gov opportunity: {e}")
            return None
    
    def _get_mock_data(
        self,
        states: List[str],
        naics: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        posted_from: Optional[str] = None,
        posted_to: Optional[str] = None,
        limit: int = 500
    ) -> List[Dict[str, Any]]:
        """Generate mock data when API key is not available."""
        logger.info("Generating mock SAM.gov data")
        
        today = dt.date.today()
        mock_opportunities = []
        
        for i in range(min(limit, 10)):  # Generate up to 10 mock records
            state = states[i % len(states)] if states else "DC"
            naics_code = naics[i % len(naics)] if naics else "541511"
            
            mock_opportunities.append({
                "notice_id": f"mock-{i+1:03d}",
                "title": f"Mock {keywords[0] if keywords else 'Telehealth'} Services - {state}",
                "agency": f"Mock Agency {i+1}",
                "naics": naics_code,
                "solicitation_number": f"MOCK-{i+1:04d}",
                "notice_type": "Solicitation",
                "posted_date": (today - dt.timedelta(days=i)).isoformat(),
                "close_date": (today + dt.timedelta(days=14-i)).isoformat(),
                "place_of_performance_state": state,
                "description": f"Mock opportunity for {keywords[0] if keywords else 'telehealth'} services in {state}",
                "url": f"https://sam.gov/opp/mock-{i+1:03d}",
                "contact_name": f"Mock Officer {i+1}",
                "contact_email": f"mock{i+1}@example.com",
                "estimated_value": 100000 + (i * 50000),
                "source": "sam.gov (mock)",
                "last_checked": None
            })
        
        return mock_opportunities


# Global instance
sam_connector = SAMConnector()


def fetch_rfps(payload: RFPPullRequest) -> List[Dict]:
    """Legacy function for backward compatibility."""
    return sam_connector.search_opportunities(
        states=payload.states,
        naics=payload.naics,
        keywords=payload.keywords,
        posted_from=payload.posted_from.isoformat() if payload.posted_from else None,
        posted_to=payload.posted_to.isoformat() if payload.posted_to else None,
        limit=payload.limit
    )


def ingest_sam_opportunities(
    states: List[str],
    naics: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
    posted_from: Optional[str] = None,
    posted_to: Optional[str] = None,
    limit: int = 500
) -> List[Dict[str, Any]]:
    """
    Ingest contract opportunities from SAM.gov.
    
    Args:
        states: List of 2-letter state codes
        naics: Optional list of NAICS codes
        keywords: Optional list of keywords
        posted_from: ISO date string
        posted_to: ISO date string
        limit: Maximum number of results to return
        
    Returns:
        List of raw opportunity records
    """
    return sam_connector.search_opportunities(
        states, naics, keywords, posted_from, posted_to, limit=limit
    )


