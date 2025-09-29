"""Test RFP API functionality."""

import pytest
from unittest.mock import patch, MagicMock
from core.pipeline.ingest.sam_opps import fetch_rfps
from core.schemas import RFPPullRequest


@patch('core.pipeline.ingest.sam_opps.settings')
def test_sam_mock_when_no_api_key(mock_settings):
    """Test that mock data is returned when SAM API key is not configured."""
    mock_settings.sam_api_key = None
    
    payload = RFPPullRequest(states=["CA"], naics=["541511"], limit=100)
    results = fetch_rfps(payload)
    
    assert len(results) == 1
    assert results[0]["notice_id"] == "mock-001"
    assert results[0]["source"] == "sam.gov (mock)"
    assert results[0]["place_of_performance_state"] == "CA"


@patch('core.pipeline.ingest.sam_opps.httpx.get')
@patch('core.pipeline.ingest.sam_opps.settings')
def test_sam_real_api_call(mock_settings, mock_get):
    """Test real SAM API call when key is configured."""
    mock_settings.sam_api_key = "test-key"
    
    # Mock successful API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "opportunities": [
            {
                "noticeId": "real-001",
                "title": "Real Telehealth Services",
                "agency": "Real Agency",
                "naics": "541511",
                "solicitationNumber": "SOL-001",
                "noticeType": "Solicitation",
                "postedDate": "2025-01-15",
                "responseDeadline": "2025-02-15",
                "placeOfPerformance": {"state": "CA"},
                "description": "Real opportunity",
                "url": "https://sam.gov/opp/real-001",
                "pointOfContact": {
                    "name": "Real Officer",
                    "email": "real@example.com"
                }
            }
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    payload = RFPPullRequest(states=["CA"], naics=["541511"], limit=100)
    results = fetch_rfps(payload)
    
    assert len(results) == 1
    assert results[0]["notice_id"] == "real-001"
    assert results[0]["source"] == "sam.gov"
    assert results[0]["agency"] == "Real Agency"


@patch('core.pipeline.ingest.sam_opps.httpx.get')
@patch('core.pipeline.ingest.sam_opps.settings')
def test_sam_api_error_handling(mock_settings, mock_get):
    """Test SAM API error handling."""
    mock_settings.sam_api_key = "test-key"
    mock_get.side_effect = Exception("Network error")
    
    payload = RFPPullRequest(states=["CA"], limit=100)
    results = fetch_rfps(payload)
    
    # Should return empty list on error
    assert len(results) == 0


def test_rfp_normalization():
    """Test RFP record normalization."""
    from core.pipeline.normalize import normalize_rfp_record
    
    raw = {
        "notice_id": "test-001",
        "title": "  Test RFP  ",
        "agency": "Test Agency",
        "naics": "541511",
        "posted_date": "2025-01-15",
        "source": "sam.gov"
    }
    
    normalized = normalize_rfp_record(raw)
    
    assert normalized.notice_id == "test-001"
    assert normalized.title == "Test RFP"  # trimmed
    assert normalized.agency == "Test Agency"
    assert normalized.naics == "541511"
    assert normalized.source == "sam.gov"


def test_rfp_schema_mapping():
    """Test RFP schema field mapping."""
    from core.schemas import RFPCanonical
    
    rfp = RFPCanonical(
        notice_id="test-001",
        title="Test RFP",
        source="test"
    )
    
    assert rfp.notice_id == "test-001"
    assert rfp.title == "Test RFP"
    assert rfp.source == "test"

