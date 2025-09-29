"""Business size classification utilities."""

from __future__ import annotations

from typing import Optional

from core.schemas import BusinessCanonical


def classify_business_size(employee_count: Optional[int], annual_revenue: Optional[int]) -> tuple[Optional[str], Optional[bool]]:
    """
    Classify business size based on employee count and annual revenue.
    
    Returns:
        tuple: (business_size, is_small_business)
        - business_size: "micro", "small", "medium", "large"
        - is_small_business: True if small business (micro + small)
    """
    if employee_count is None and annual_revenue is None:
        return None, None
    
    # Primary classification by employee count
    if employee_count is not None:
        if employee_count <= 9:
            return "micro", True
        elif employee_count <= 49:
            return "small", True
        elif employee_count <= 249:
            return "medium", False
        else:
            return "large", False
    
    # Fallback to revenue classification if no employee count
    if annual_revenue is not None:
        # Revenue thresholds (in USD)
        if annual_revenue <= 1_000_000:  # $1M
            return "micro", True
        elif annual_revenue <= 10_000_000:  # $10M
            return "small", True
        elif annual_revenue <= 50_000_000:  # $50M
            return "medium", False
        else:
            return "large", False
    
    return None, None


def apply_business_size_classification(record: BusinessCanonical) -> BusinessCanonical:
    """Apply business size classification to a record."""
    business_size, is_small_business = classify_business_size(
        record.employee_count, 
        record.annual_revenue_usd
    )
    
    return record.model_copy(update={
        "business_size": business_size,
        "is_small_business": is_small_business,
    })


def get_small_business_naics_thresholds() -> dict[str, int]:
    """
    Get SBA small business size standards by NAICS code.
    Returns employee count thresholds for small business classification.
    """
    # Common NAICS codes with their small business thresholds
    # These are simplified examples - in production, you'd want the full SBA table
    return {
        "541511": 1500,  # Custom Computer Programming Services
        "541512": 1500,  # Computer Systems Design Services
        "541513": 1500,  # Computer Facilities Management Services
        "541519": 1500,  # Other Computer Related Services
        "621111": 1500,  # Offices of Physicians (except Mental Health Specialists)
        "621112": 1500,  # Offices of Physicians, Mental Health Specialists
        "621210": 1500,  # Offices of Dentists
        "621310": 1500,  # Offices of Chiropractors
        "621320": 1500,  # Offices of Optometrists
        "621330": 1500,  # Offices of Mental Health Practitioners
        "621340": 1500,  # Offices of Physical, Occupational and Speech Therapists
        "621391": 1500,  # Offices of Podiatrists
        "621399": 1500,  # Offices of All Other Miscellaneous Health Practitioners
        "541611": 1500,  # Administrative Management and General Management Consulting Services
        "541612": 1500,  # Human Resources Consulting Services
        "541613": 1500,  # Marketing Consulting Services
        "541614": 1500,  # Process, Physical Distribution, and Logistics Consulting Services
        "541618": 1500,  # Other Management Consulting Services
        "541690": 1500,  # Other Scientific and Technical Consulting Services
        "541810": 1500,  # Advertising Agencies
        "541820": 1500,  # Public Relations Agencies
        "541830": 1500,  # Media Buying Agencies
        "541840": 1500,  # Media Representatives
        "541850": 1500,  # Display Advertising
        "541860": 1500,  # Direct Mail Advertising
        "541870": 1500,  # Advertising Material Distribution Services
        "541890": 1500,  # Other Services Related to Advertising
        "541910": 1500,  # Marketing Research and Public Opinion Polling
        "541920": 1500,  # Photographic Services
        "541930": 1500,  # Translation and Interpretation Services
        "541940": 1500,  # Veterinary Services
        "541990": 1500,  # All Other Professional, Scientific, and Technical Services
    }


def classify_by_naics_and_size(record: BusinessCanonical) -> BusinessCanonical:
    """
    Enhanced classification using NAICS-specific thresholds.
    Falls back to general classification if NAICS not found.
    """
    if not record.naics_code:
        return apply_business_size_classification(record)
    
    thresholds = get_small_business_naics_thresholds()
    threshold = thresholds.get(record.naics_code)
    
    if threshold is None:
        # Fall back to general classification
        return apply_business_size_classification(record)
    
    # Use NAICS-specific threshold
    if record.employee_count is not None:
        is_small = record.employee_count <= threshold
        if record.employee_count <= 9:
            business_size = "micro"
        elif record.employee_count <= 49:
            business_size = "small"
        elif record.employee_count <= threshold:
            business_size = "small"  # Still small by NAICS standards
        elif record.employee_count <= 249:
            business_size = "medium"
        else:
            business_size = "large"
    else:
        # Fall back to general classification
        return apply_business_size_classification(record)
    
    return record.model_copy(update={
        "business_size": business_size,
        "is_small_business": is_small,
    })

