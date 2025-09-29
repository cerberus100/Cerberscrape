"""Test deduplication logic for business records."""

import pytest
from core.schemas import BusinessCanonical
from core.pipeline.dedupe import dedupe_businesses


def test_dedupe_by_domain():
    """Test deduplication by domain."""
    records = [
        BusinessCanonical(company_name="Company A", domain="example.com", state="CA", source="test1"),
        BusinessCanonical(company_name="Company B", domain="example.com", state="CA", source="test2"),
    ]
    
    deduped = dedupe_businesses(records)
    assert len(deduped) == 1
    assert deduped[0].source == "test1;test2"


def test_dedupe_by_phone():
    """Test deduplication by phone number."""
    records = [
        BusinessCanonical(company_name="Company A", phone="+1234567890", state="CA", source="test1"),
        BusinessCanonical(company_name="Company B", phone="+1234567890", state="CA", source="test2"),
    ]
    
    deduped = dedupe_businesses(records)
    assert len(deduped) == 1
    assert deduped[0].source == "test1;test2"


def test_dedupe_fuzzy_name_zip():
    """Test fuzzy deduplication by name and postal code."""
    records = [
        BusinessCanonical(company_name="Acme Corporation", postal_code="12345", state="CA", source="test1"),
        BusinessCanonical(company_name="Acme Corp", postal_code="12345", state="CA", source="test2"),
    ]
    
    deduped = dedupe_businesses(records)
    assert len(deduped) == 1


def test_no_dedupe_different_zip():
    """Test that records with different postal codes are not deduplicated."""
    records = [
        BusinessCanonical(company_name="Acme Corporation", postal_code="12345", state="CA", source="test1"),
        BusinessCanonical(company_name="Acme Corp", postal_code="67890", state="CA", source="test2"),
    ]
    
    deduped = dedupe_businesses(records)
    assert len(deduped) == 2


def test_merge_policy_freshest_verified():
    """Test merge policy prefers freshest last_verified."""
    from datetime import datetime, timedelta
    
    now = datetime.utcnow()
    older = now - timedelta(days=1)
    newer = now + timedelta(days=1)
    
    records = [
        BusinessCanonical(
            company_name="Company A", 
            domain="example.com", 
            state="CA", 
            source="test1",
            last_verified=older
        ),
        BusinessCanonical(
            company_name="Company B", 
            domain="example.com", 
            state="CA", 
            source="test2",
            last_verified=newer
        ),
    ]
    
    deduped = dedupe_businesses(records)
    assert len(deduped) == 1
    assert deduped[0].last_verified == newer


def test_merge_policy_keep_non_null():
    """Test merge policy keeps non-null fields."""
    records = [
        BusinessCanonical(company_name="Company A", domain="example.com", state="CA", source="test1"),
        BusinessCanonical(company_name="Company B", domain="example.com", phone="+1234567890", state="CA", source="test2"),
    ]
    
    deduped = dedupe_businesses(records)
    assert len(deduped) == 1
    assert deduped[0].phone == "+1234567890"

