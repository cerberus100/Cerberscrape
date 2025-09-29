"""CSV export helpers."""

from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path
from typing import Iterable, List

from core.config import settings
from core.schemas import BusinessCanonical, BusinessPullRequest, RFPCanonical, RFPPullRequest
from core.aws import S3Exporter


BUSINESS_HEADER = [
    "company_name",
    "domain",
    "phone",
    "email",
    "address_line1",
    "city",
    "state",
    "postal_code",
    "country",
    "county",
    "county_fips",
    "naics_code",
    "industry",
    "founded_year",
    "years_in_business",
    "employee_count",
    "annual_revenue_usd",
    "business_size",
    "is_small_business",
    "source",
    "last_verified",
    "quality_score",
]

RFP_HEADER = [
    "notice_id",
    "title",
    "agency",
    "naics",
    "solicitation_number",
    "notice_type",
    "posted_date",
    "close_date",
    "place_of_performance_state",
    "description",
    "url",
    "contact_name",
    "contact_email",
    "estimated_value",
    "source",
    "last_checked",
]


def ensure_export_dir() -> Path:
    export_dir = settings.export_bucket_path
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def export_business_csv(records: Iterable[BusinessCanonical], payload: BusinessPullRequest) -> str:
    export_dir = ensure_export_dir()
    states_slug = "-".join(sorted(payload.states))
    filter_slug = "-".join((payload.naics or payload.keywords or ["all"]))
    date_prefix = dt.datetime.utcnow().strftime("%Y%m%d")
    filename = f"business-{date_prefix}-{states_slug}-{filter_slug}.csv"
    path = export_dir / filename

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(BUSINESS_HEADER)
        for record in records:
            writer.writerow(
                [
                    record.company_name,
                    record.domain or "",
                    record.phone or "",
                    record.email or "",
                    record.address_line1 or "",
                    record.city or "",
                    record.state,
                    record.postal_code or "",
                    record.country,
                    record.county or "",
                    record.county_fips or "",
                    record.naics_code or "",
                    record.industry or "",
                    record.founded_year or "",
                    record.years_in_business or "",
                    record.employee_count or "",
                    record.annual_revenue_usd or "",
                    record.business_size or "",
                    record.is_small_business or "",
                    record.source,
                    record.last_verified.isoformat(),
                    record.quality_score,
                ]
            )
    
    # Upload to S3 if configured
    if settings.s3_bucket:
        s3_exporter = S3Exporter(settings.s3_bucket)
        s3_key = f"exports/{filename}"
        return s3_exporter.upload_file(path, s3_key)
    
    return str(path)


def export_rfp_csv(records: Iterable[RFPCanonical], payload: RFPPullRequest) -> str:
    export_dir = ensure_export_dir()
    states_slug = "-".join(sorted(payload.states))
    filter_slug = "-".join((payload.naics or payload.keywords or ["all"]))
    date_prefix = dt.datetime.utcnow().strftime("%Y%m%d")
    filename = f"rfps-{date_prefix}-{states_slug}-{filter_slug}.csv"
    path = export_dir / filename

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(RFP_HEADER)
        for record in records:
            writer.writerow(
                [
                    record.notice_id,
                    record.title,
                    record.agency or "",
                    record.naics or "",
                    record.solicitation_number or "",
                    record.notice_type or "",
                    record.posted_date.isoformat() if record.posted_date else "",
                    record.close_date.isoformat() if record.close_date else "",
                    record.place_of_performance_state or "",
                    record.description or "",
                    record.url or "",
                    record.contact_name or "",
                    record.contact_email or "",
                    record.estimated_value or "",
                    record.source,
                    record.last_checked.isoformat(),
                ]
            )
    
    # Upload to S3 if configured
    if settings.s3_bucket:
        s3_exporter = S3Exporter(settings.s3_bucket)
        s3_key = f"exports/{filename}"
        return s3_exporter.upload_file(path, s3_key)
    
    return str(path)


