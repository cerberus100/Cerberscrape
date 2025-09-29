"""Business data extraction pipeline."""

from __future__ import annotations

import datetime as dt
from collections import OrderedDict
from pathlib import Path
from typing import Iterable, List

from core.config import settings
from core.pipeline.dedupe import dedupe_businesses
from core.pipeline.export import export_business_csv
from core.pipeline.normalize import normalize_business_record
from core.pipeline.qa import run_business_qa
from core.pipeline.score import score_business_records
from core.pipeline.ingest import opencorporates, nppes, state_manual
from core.pipeline.enrich.geocode_census import geocode_records
from core.pipeline.business_size import classify_by_naics_and_size
from core.preview import business_preview_store
from core.schemas import BusinessCanonical, BusinessPullRequest, DataForgeResponse


def run_business_pipeline(payload: BusinessPullRequest) -> DataForgeResponse:
    """Execute the business pipeline end-to-end."""

    raw_records = _ingest(payload)
    normalized = [normalize_business_record(item) for item in raw_records]

    # Enrichment steps
    enable_geocode = payload.enable_geocoder if payload.enable_geocoder is not None else settings.enable_geocoder_default
    if enable_geocode:
        normalized = geocode_records(normalized)
    
    # Apply business size classification
    normalized = [classify_by_naics_and_size(record) for record in normalized]

    deduped = dedupe_businesses(normalized)
    filtered = _apply_filters(deduped, payload)
    scored = score_business_records(filtered)
    limited = scored[: payload.limit]

    if not limited:
        return DataForgeResponse(ok=True, message="No records matched filters", export_path=None, qa_report=None)

    export_path = export_business_csv(limited, payload)
    qa_report = run_business_qa(limited, enable_geocode)

    business_preview_store.save_records(limited)

    message = f"Exported {len(limited)} business records"
    return DataForgeResponse(ok=qa_report.passed, message=message, export_path=export_path, qa_report=qa_report)


def _ingest(payload: BusinessPullRequest) -> List[dict]:
    records: List[dict] = []
    
    # OpenCorporates - Primary business data source
    try:
        opencorp_records = opencorporates.fetch_businesses(payload)
        records.extend(opencorp_records)
    except Exception as e:
        print(f"OpenCorporates ingestion failed: {e}")
    
    # NPPES - Healthcare organizations
    try:
        nppes_records = nppes.ingest_nppes(
            states=payload.states,
            keywords=payload.keywords,
            limit=payload.limit
        )
        records.extend(nppes_records)
    except Exception as e:
        print(f"NPPES ingestion failed: {e}")
    
    # State Manual - CSV drop functionality
    try:
        state_records = state_manual.ingest_state_manual(
            states=payload.states,
            keywords=payload.keywords,
            limit=payload.limit
        )
        records.extend(state_records)
    except Exception as e:
        print(f"State manual ingestion failed: {e}")
    
    # Sort deterministically by company name
    records.sort(key=lambda r: (r.get("company_name") or ""))
    return records


def _apply_filters(records: Iterable[BusinessCanonical], payload: BusinessPullRequest) -> List[BusinessCanonical]:
    keywords = set((payload.keywords or []) + (payload.naics or []))
    lower_keywords = {k.lower() for k in keywords if k}

    min_years = payload.min_years
    max_years = payload.max_years

    filtered: List[BusinessCanonical] = []
    for record in records:
        # NAICS filter
        if payload.naics and record.naics_code and record.naics_code not in payload.naics:
            continue
        
        # Keywords filter
        if lower_keywords:
            haystack = " ".join(
                filter(
                    None,
                    (
                        record.company_name,
                        record.industry or "",
                        record.domain or "",
                        record.naics_code or "",
                    ),
                )
            ).lower()
            if not any(keyword in haystack for keyword in lower_keywords):
                continue

        # Years in business filter
        years = record.years_in_business
        if min_years is not None and years is not None and years < min_years:
            continue
        if max_years is not None and years is not None and years > max_years:
            continue

        # Small business filter
        if payload.small_business_only is True and record.is_small_business is not True:
            continue
        
        # Specific business size filter
        if payload.business_size and record.business_size != payload.business_size:
            continue

        filtered.append(record)

    return filtered

