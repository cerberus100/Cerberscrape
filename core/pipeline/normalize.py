"""Normalization helpers for pipeline records."""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict, Optional

import phonenumbers
import usaddress
from pydantic import ValidationError

from core.schemas import BusinessCanonical, RFPCanonical


def normalize_business_record(raw: Dict[str, Any]) -> BusinessCanonical:
    state = (raw.get("state") or "").upper()
    try:
        parsed_address, _ = usaddress.tag(raw.get("address", ""))
    except usaddress.RepeatedLabelError:
        parsed_address = {}

    phone = normalize_phone(raw.get("phone"))

    founded_year = _coerce_int(raw.get("founded_year"))
    years_in_business = None
    if founded_year:
        years_in_business = dt.datetime.utcnow().year - founded_year
        years_in_business = max(years_in_business, 0)

    canonical = BusinessCanonical(
        company_name=raw.get("company_name", "").strip() or "Unknown",
        domain=_normalize_str(raw.get("domain")),
        phone=phone,
        email=_normalize_str(raw.get("email")),
        address_line1=_normalize_str(raw.get("address_line1") or raw.get("address")),
        city=_normalize_str(raw.get("city") or parsed_address.get("PlaceName")),
        state=state,
        postal_code=_normalize_str(raw.get("postal_code") or parsed_address.get("ZipCode")),
        country=_normalize_str(raw.get("country")) or "US",
        county=_normalize_str(raw.get("county")),
        county_fips=_normalize_str(raw.get("county_fips")),
        naics_code=_normalize_str(raw.get("naics_code")),
        industry=_normalize_str(raw.get("industry")),
        founded_year=founded_year,
        years_in_business=years_in_business,
        employee_count=_coerce_int(raw.get("employee_count")),
        annual_revenue_usd=_coerce_int(raw.get("annual_revenue_usd")),
        business_size=_normalize_str(raw.get("business_size")),
        is_small_business=raw.get("is_small_business"),
        source=_normalize_str(raw.get("source")) or "unknown",
        last_verified=_coerce_datetime(raw.get("last_verified")) or dt.datetime.utcnow(),
        quality_score=int(raw.get("quality_score", 0) or 0),
    )
    return canonical


def normalize_rfp_record(raw: Dict[str, Any]) -> RFPCanonical:
    canonical = RFPCanonical(
        notice_id=str(raw.get("notice_id")),
        title=_normalize_str(raw.get("title")) or "Untitled",
        agency=_normalize_str(raw.get("agency")),
        naics=_normalize_str(raw.get("naics")),
        solicitation_number=_normalize_str(raw.get("solicitation_number")),
        notice_type=_normalize_str(raw.get("notice_type")),
        posted_date=_coerce_date(raw.get("posted_date")),
        close_date=_coerce_date(raw.get("close_date")),
        place_of_performance_state=_normalize_str(raw.get("place_of_performance_state")),
        description=_normalize_str(raw.get("description")),
        url=_normalize_str(raw.get("url")),
        contact_name=_normalize_str(raw.get("contact_name")),
        contact_email=_normalize_str(raw.get("contact_email")),
        estimated_value=_normalize_str(raw.get("estimated_value")),
        source=_normalize_str(raw.get("source")) or "sam.gov",
        last_checked=_coerce_datetime(raw.get("last_checked")) or dt.datetime.utcnow(),
    )
    return canonical


def normalize_phone(phone: Any) -> Optional[str]:
    if not phone:
        return None
    digits = "".join(filter(str.isdigit, str(phone)))
    if not digits:
        return None
    try:
        parsed = phonenumbers.parse(digits, "US")
        if phonenumbers.is_possible_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        return None
    return digits


def _normalize_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    string = str(value).strip()
    return string or None


def _coerce_int(value: Any) -> Optional[int]:
    try:
        if value is None:
            return None
        return int(value)
    except (ValueError, TypeError):
        return None


def _coerce_datetime(value: Any) -> Optional[dt.datetime]:
    if isinstance(value, dt.datetime):
        return value
    if isinstance(value, dt.date):
        return dt.datetime.combine(value, dt.time.min)
    if isinstance(value, str):
        try:
            return dt.datetime.fromisoformat(value)
        except ValueError:
            return None
    return None


def _coerce_date(value: Any) -> Optional[dt.date]:
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


