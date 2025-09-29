"""Pydantic schemas used across DataForge."""

from __future__ import annotations

import datetime as dt
from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator


VALID_STATES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "DC",
}


class HealthResponse(BaseModel):
    ok: bool
    ts: dt.datetime


class QAReport(BaseModel):
    passed: bool
    total_rows: int
    dupes: int
    errors: List[str] = []


class DataForgeResponse(BaseModel):
    ok: bool = True
    message: Optional[str] = None
    export_path: Optional[str] = None
    qa_report: Optional[QAReport] = None


def _validate_states(states: List[str]) -> List[str]:
    upper_states = [s.upper() for s in states]
    invalid = [s for s in upper_states if s not in VALID_STATES]
    if invalid:
        raise ValueError(f"Invalid state codes: {', '.join(invalid)}")
    return upper_states


class BusinessPullRequest(BaseModel):
    states: List[str]
    naics: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    min_emp: Optional[int] = Field(default=None, ge=0)
    max_emp: Optional[int] = Field(default=None, ge=0)
    min_rev: Optional[int] = Field(default=None, ge=0)
    max_rev: Optional[int] = Field(default=None, ge=0)
    min_years: Optional[int] = Field(default=None, ge=0)
    max_years: Optional[int] = Field(default=None, ge=0)
    limit: int = Field(default=500, ge=1, le=2000000)
    enable_geocoder: Optional[bool] = None
    small_business_only: Optional[bool] = Field(default=None, description="Filter for small businesses only")
    business_size: Optional[str] = Field(default=None, description="Specific business size: micro, small, medium, large")

    @field_validator("states")
    def check_states(cls, states: List[str]) -> List[str]:
        return _validate_states(states)

    @field_validator("naics")
    def normalize_naics(cls, values: Optional[List[str]]) -> Optional[List[str]]:
        if values is None:
            return None
        return [v.strip() for v in values if v.strip()]

    @field_validator("keywords")
    def normalize_keywords(cls, values: Optional[List[str]]) -> Optional[List[str]]:
        if values is None:
            return None
        return [v.strip() for v in values if v.strip()]
    
    @field_validator("business_size")
    def validate_business_size(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        valid_sizes = {"micro", "small", "medium", "large"}
        if value.lower() not in valid_sizes:
            raise ValueError(f"business_size must be one of: {', '.join(valid_sizes)}")
        return value.lower()


class RFPPullRequest(BaseModel):
    states: List[str]
    naics: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    posted_from: Optional[dt.date] = None
    posted_to: Optional[dt.date] = None
    limit: int = Field(default=500, ge=1, le=10000)

    @field_validator("states")
    def check_states(cls, states: List[str]) -> List[str]:
        return _validate_states(states)

    @field_validator("posted_to")
    def validate_date_range(cls, posted_to: Optional[dt.date], values: dict) -> Optional[dt.date]:
        posted_from = values.get("posted_from")
        if posted_to and posted_from and posted_to < posted_from:
            raise ValueError("posted_to must be greater than or equal to posted_from")
        return posted_to


class PreviewQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=200)


class PaginatedResponse(BaseModel):
    page: int
    page_size: int
    total: int


class BusinessPreviewItem(BaseModel):
    company_name: str
    state: str
    domain: Optional[str] = None
    quality_score: Optional[int] = None


class BusinessPreviewResponse(PaginatedResponse):
    items: List[BusinessPreviewItem]


class RFPPreviewItem(BaseModel):
    notice_id: str
    title: str
    agency: Optional[str]
    posted_date: Optional[dt.date]


class RFPPreviewResponse(PaginatedResponse):
    items: List[RFPPreviewItem]


class BusinessCanonical(BaseModel):
    company_name: str
    domain: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: str
    postal_code: Optional[str] = None
    country: str = "US"
    county: Optional[str] = None
    county_fips: Optional[str] = None
    naics_code: Optional[str] = None
    industry: Optional[str] = None
    founded_year: Optional[int] = None
    years_in_business: Optional[int] = None
    employee_count: Optional[int] = None
    annual_revenue_usd: Optional[int] = None
    business_size: Optional[str] = None  # micro, small, medium, large
    is_small_business: Optional[bool] = None
    source: str
    last_verified: dt.datetime
    quality_score: int = 0


class RFPCanonical(BaseModel):
    notice_id: str
    title: str
    agency: Optional[str] = None
    naics: Optional[str] = None
    solicitation_number: Optional[str] = None
    notice_type: Optional[str] = None
    posted_date: Optional[dt.date] = None
    close_date: Optional[dt.date] = None
    place_of_performance_state: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    estimated_value: Optional[str] = None
    source: str
    last_checked: dt.datetime


