"""Test business size classification and filtering."""

import pytest
from core.schemas import BusinessCanonical, BusinessPullRequest
from core.pipeline.business_size import classify_business_size, apply_business_size_classification, classify_by_naics_and_size
from core.pipeline.business import _apply_filters


def test_classify_business_size_by_employees():
    """Test business size classification by employee count."""
    
    # Micro business
    size, is_small = classify_business_size(5, None)
    assert size == "micro"
    assert is_small is True
    
    # Small business
    size, is_small = classify_business_size(25, None)
    assert size == "small"
    assert is_small is True
    
    # Medium business
    size, is_small = classify_business_size(100, None)
    assert size == "medium"
    assert is_small is False
    
    # Large business
    size, is_small = classify_business_size(500, None)
    assert size == "large"
    assert is_small is False


def test_classify_business_size_by_revenue():
    """Test business size classification by revenue when no employee count."""
    
    # Micro business by revenue
    size, is_small = classify_business_size(None, 500_000)
    assert size == "micro"
    assert is_small is True
    
    # Small business by revenue
    size, is_small = classify_business_size(None, 5_000_000)
    assert size == "small"
    assert is_small is True
    
    # Medium business by revenue
    size, is_small = classify_business_size(None, 25_000_000)
    assert size == "medium"
    assert is_small is False
    
    # Large business by revenue
    size, is_small = classify_business_size(None, 100_000_000)
    assert size == "large"
    assert is_small is False


def test_classify_business_size_no_data():
    """Test business size classification with no data."""
    size, is_small = classify_business_size(None, None)
    assert size is None
    assert is_small is None


def test_apply_business_size_classification():
    """Test applying business size classification to a record."""
    record = BusinessCanonical(
        company_name="Test Corp",
        state="CA",
        employee_count=30,
        annual_revenue_usd=5_000_000,
        source="test"
    )
    
    classified = apply_business_size_classification(record)
    
    assert classified.business_size == "small"
    assert classified.is_small_business is True


def test_classify_by_naics_and_size():
    """Test NAICS-specific business size classification."""
    record = BusinessCanonical(
        company_name="Tech Corp",
        state="CA",
        naics_code="541511",  # Custom Computer Programming Services
        employee_count=1000,  # Under 1500 threshold for this NAICS
        source="test"
    )
    
    classified = classify_by_naics_and_size(record)
    
    assert classified.business_size == "small"  # Small by NAICS standards
    assert classified.is_small_business is True


def test_small_business_filter():
    """Test filtering for small businesses only."""
    records = [
        BusinessCanonical(company_name="Micro Corp", state="CA", employee_count=5, source="test"),
        BusinessCanonical(company_name="Small Corp", state="CA", employee_count=25, source="test"),
        BusinessCanonical(company_name="Medium Corp", state="CA", employee_count=100, source="test"),
        BusinessCanonical(company_name="Large Corp", state="CA", employee_count=500, source="test"),
    ]
    
    # Apply business size classification
    classified = [apply_business_size_classification(record) for record in records]
    
    # Filter for small businesses only
    payload = BusinessPullRequest(states=["CA"], small_business_only=True, limit=100)
    filtered = _apply_filters(classified, payload)
    
    assert len(filtered) == 2
    assert all(record.is_small_business for record in filtered)
    assert any(record.company_name == "Micro Corp" for record in filtered)
    assert any(record.company_name == "Small Corp" for record in filtered)


def test_specific_business_size_filter():
    """Test filtering for specific business size."""
    records = [
        BusinessCanonical(company_name="Micro Corp", state="CA", employee_count=5, source="test"),
        BusinessCanonical(company_name="Small Corp", state="CA", employee_count=25, source="test"),
        BusinessCanonical(company_name="Medium Corp", state="CA", employee_count=100, source="test"),
        BusinessCanonical(company_name="Large Corp", state="CA", employee_count=500, source="test"),
    ]
    
    # Apply business size classification
    classified = [apply_business_size_classification(record) for record in records]
    
    # Filter for medium businesses only
    payload = BusinessPullRequest(states=["CA"], business_size="medium", limit=100)
    filtered = _apply_filters(classified, payload)
    
    assert len(filtered) == 1
    assert filtered[0].company_name == "Medium Corp"
    assert filtered[0].business_size == "medium"


def test_business_size_validation():
    """Test business size validation in schema."""
    # Valid business size
    payload = BusinessPullRequest(states=["CA"], business_size="small", limit=100)
    assert payload.business_size == "small"
    
    # Invalid business size should raise error
    with pytest.raises(ValueError, match="business_size must be one of"):
        BusinessPullRequest(states=["CA"], business_size="invalid", limit=100)


def test_business_size_case_insensitive():
    """Test that business size validation is case insensitive."""
    payload = BusinessPullRequest(states=["CA"], business_size="SMALL", limit=100)
    assert payload.business_size == "small"
    
    payload = BusinessPullRequest(states=["CA"], business_size="Large", limit=100)
    assert payload.business_size == "large"

