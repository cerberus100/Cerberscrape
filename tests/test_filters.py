"""Test filtering logic for business and RFP pipelines."""

import pytest
from core.schemas import BusinessCanonical, BusinessPullRequest, RFPPullRequest
from core.pipeline.business import _apply_filters


def test_business_state_filter():
    """Test state filtering in business pipeline."""
    records = [
        BusinessCanonical(company_name="Test CA", state="CA", source="test"),
        BusinessCanonical(company_name="Test TX", state="TX", source="test"),
        BusinessCanonical(company_name="Test NY", state="NY", source="test"),
    ]
    
    payload = BusinessPullRequest(states=["CA", "TX"], limit=100)
    filtered = _apply_filters(records, payload)
    
    assert len(filtered) == 2
    assert all(r.state in ["CA", "TX"] for r in filtered)


def test_business_naics_filter():
    """Test NAICS filtering in business pipeline."""
    records = [
        BusinessCanonical(company_name="Test 1", state="CA", naics_code="621111", source="test"),
        BusinessCanonical(company_name="Test 2", state="CA", naics_code="541511", source="test"),
        BusinessCanonical(company_name="Test 3", state="CA", naics_code="999999", source="test"),
    ]
    
    payload = BusinessPullRequest(states=["CA"], naics=["621111", "541511"], limit=100)
    filtered = _apply_filters(records, payload)
    
    assert len(filtered) == 2
    assert all(r.naics_code in ["621111", "541511"] for r in filtered)


def test_business_keyword_filter():
    """Test keyword filtering in business pipeline."""
    records = [
        BusinessCanonical(company_name="Telehealth Corp", state="CA", source="test"),
        BusinessCanonical(company_name="Logistics Inc", state="CA", source="test"),
        BusinessCanonical(company_name="Manufacturing Co", state="CA", source="test"),
    ]
    
    payload = BusinessPullRequest(states=["CA"], keywords=["telehealth", "logistics"], limit=100)
    filtered = _apply_filters(records, payload)
    
    assert len(filtered) == 2
    names = [r.company_name.lower() for r in filtered]
    assert any("telehealth" in name for name in names)
    assert any("logistics" in name for name in names)


def test_business_years_filter():
    """Test years in business filtering."""
    records = [
        BusinessCanonical(company_name="Old Co", state="CA", years_in_business=10, source="test"),
        BusinessCanonical(company_name="New Co", state="CA", years_in_business=2, source="test"),
        BusinessCanonical(company_name="Medium Co", state="CA", years_in_business=5, source="test"),
    ]
    
    payload = BusinessPullRequest(states=["CA"], min_years=3, max_years=8, limit=100)
    filtered = _apply_filters(records, payload)
    
    assert len(filtered) == 1
    assert filtered[0].company_name == "Medium Co"


def test_business_limit_boundaries():
    """Test limit boundaries in business requests."""
    with pytest.raises(ValueError):
        BusinessPullRequest(states=["CA"], limit=0)
    
    with pytest.raises(ValueError):
        BusinessPullRequest(states=["CA"], limit=2_000_001)


def test_rfp_date_range_validation():
    """Test RFP date range validation."""
    with pytest.raises(ValueError):
        RFPPullRequest(
            states=["CA"],
            posted_from="2025-09-30",
            posted_to="2025-09-01",
            limit=100
        )

