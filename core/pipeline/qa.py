"""QA validation for exported records."""

from __future__ import annotations

import re
from typing import Iterable, List

from core.pipeline.export import BUSINESS_HEADER, RFP_HEADER
from core.schemas import BusinessCanonical, QAReport, RFPCanonical


PHONE_PATTERN = re.compile(r"^\+?\d{10,11}$")
FIPS_PATTERN = re.compile(r"^\d{5}$")


def run_business_qa(records: Iterable[BusinessCanonical], geocode_enabled: bool) -> QAReport:
    errors: List[str] = []
    records_list = list(records)

    for record in records_list:
        if record.state.upper() not in {"AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"}:
            errors.append(f"Invalid state {record.state}")
        if record.phone:
            sanitized = record.phone.replace("+", "")
            if not PHONE_PATTERN.match(sanitized):
                errors.append(f"Bad phone {record.phone}")
        if geocode_enabled and record.county_fips and not FIPS_PATTERN.match(record.county_fips):
            errors.append(f"Invalid county_fips {record.county_fips}")
        if record.founded_year and record.years_in_business is not None:
            expected_years = max(0, record.last_verified.year - record.founded_year)
            if abs(expected_years - record.years_in_business) > 1:
                errors.append(f"years_in_business mismatch for {record.company_name}")
    report = QAReport(
        passed=not errors,
        total_rows=len(records_list),
        dupes=0,
        errors=errors,
    )
    return report


def run_rfp_qa(records: Iterable[RFPCanonical]) -> QAReport:
    errors: List[str] = []
    seen_notice_ids = set()
    records_list = list(records)
    for record in records_list:
        if record.notice_id in seen_notice_ids:
            errors.append(f"Duplicate notice_id {record.notice_id}")
        seen_notice_ids.add(record.notice_id)

    report = QAReport(
        passed=not errors,
        total_rows=len(records_list),
        dupes=len(records_list) - len(seen_notice_ids),
        errors=errors,
    )
    return report

