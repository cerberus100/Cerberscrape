"""Test CSV export functionality."""

import csv
import tempfile
from pathlib import Path
from datetime import datetime

import pytest
from core.schemas import BusinessCanonical, BusinessPullRequest, RFPCanonical, RFPPullRequest
from core.pipeline.export import export_business_csv, export_rfp_csv, BUSINESS_HEADER, RFP_HEADER


def test_business_csv_header_order():
    """Test that business CSV has exact header order."""
    records = [
        BusinessCanonical(company_name="Test Co", state="CA", source="test")
    ]
    payload = BusinessPullRequest(states=["CA"], limit=100)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        export_path = Path(tmpdir) / "test.csv"
        result_path = export_business_csv(records, payload)
        
        with open(result_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            assert header == BUSINESS_HEADER


def test_rfp_csv_header_order():
    """Test that RFP CSV has exact header order."""
    records = [
        RFPCanonical(notice_id="test-001", title="Test RFP", source="test")
    ]
    payload = RFPPullRequest(states=["CA"], limit=100)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        export_path = Path(tmpdir) / "test.csv"
        result_path = export_rfp_csv(records, payload)
        
        with open(result_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            assert header == RFP_HEADER


def test_business_csv_deterministic_filename():
    """Test deterministic filename generation for business CSV."""
    records = [BusinessCanonical(company_name="Test Co", state="CA", source="test")]
    payload = BusinessPullRequest(states=["CA", "TX"], naics=["621111"], limit=100)
    
    result_path = export_business_csv(records, payload)
    filename = result_path.name
    
    assert filename.startswith("business-")
    assert "CA-TX" in filename or "TX-CA" in filename  # sorted states
    assert "621111" in filename
    assert filename.endswith(".csv")


def test_rfp_csv_deterministic_filename():
    """Test deterministic filename generation for RFP CSV."""
    records = [RFPCanonical(notice_id="test-001", title="Test RFP", source="test")]
    payload = RFPPullRequest(states=["NY"], keywords=["telehealth"], limit=100)
    
    result_path = export_rfp_csv(records, payload)
    filename = result_path.name
    
    assert filename.startswith("rfps-")
    assert "NY" in filename
    assert "telehealth" in filename
    assert filename.endswith(".csv")


def test_business_csv_geocoder_fields():
    """Test that geocoder fields are included when present."""
    records = [
        BusinessCanonical(
            company_name="Test Co", 
            state="CA", 
            county="Los Angeles",
            county_fips="06037",
            source="test"
        )
    ]
    payload = BusinessPullRequest(states=["CA"], limit=100)
    
    result_path = export_business_csv(records, payload)
    
    with open(result_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        row = next(reader)
        
        county_idx = header.index("county")
        county_fips_idx = header.index("county_fips")
        
        assert row[county_idx] == "Los Angeles"
        assert row[county_fips_idx] == "06037"


def test_business_csv_years_in_business():
    """Test that years_in_business field is included."""
    records = [
        BusinessCanonical(
            company_name="Test Co", 
            state="CA", 
            founded_year=2020,
            years_in_business=4,
            source="test"
        )
    ]
    payload = BusinessPullRequest(states=["CA"], limit=100)
    
    result_path = export_business_csv(records, payload)
    
    with open(result_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        row = next(reader)
        
        founded_idx = header.index("founded_year")
        years_idx = header.index("years_in_business")
        
        assert row[founded_idx] == "2020"
        assert row[years_idx] == "4"

