"""RFP pipeline implementation."""

from __future__ import annotations

from pathlib import Path
from typing import List

from core.pipeline.ingest.sam_opps import fetch_rfps
from core.pipeline.ingest.grants_gov import ingest_grants_gov
from core.pipeline.normalize import normalize_rfp_record
from core.pipeline.export import export_rfp_csv
from core.pipeline.qa import run_rfp_qa
from core.preview import rfp_preview_store
from core.schemas import DataForgeResponse, RFPCanonical, RFPPullRequest


def run_rfp_pipeline(payload: RFPPullRequest) -> DataForgeResponse:
    raw_items = _ingest_rfps(payload)
    normalized = [normalize_rfp_record(item) for item in raw_items]

    limited = normalized[: payload.limit]
    if not limited:
        return DataForgeResponse(ok=True, message="No RFP records found", export_path=None, qa_report=None)

    export_path = export_rfp_csv(limited, payload)
    qa_report = run_rfp_qa(limited)

    rfp_preview_store.save_records(limited)

    message = f"Exported {len(limited)} RFP records"
    return DataForgeResponse(ok=qa_report.passed, message=message, export_path=export_path, qa_report=qa_report)


def _ingest_rfps(payload: RFPPullRequest) -> List[dict]:
    """Ingest RFP data from multiple sources."""
    records = []
    
    # SAM.gov - Primary RFP source
    try:
        sam_records = fetch_rfps(payload)
        records.extend(sam_records)
    except Exception as e:
        print(f"SAM.gov ingestion failed: {e}")
    
    # Grants.gov - Optional grants source
    try:
        grants_records = ingest_grants_gov(
            keywords=payload.keywords,
            posted_from=payload.posted_from.isoformat() if payload.posted_from else None,
            posted_to=payload.posted_to.isoformat() if payload.posted_to else None,
            limit=payload.limit
        )
        records.extend(grants_records)
    except Exception as e:
        print(f"Grants.gov ingestion failed: {e}")
    
    # Sort deterministically by notice_id
    records.sort(key=lambda r: (r.get("notice_id") or ""))
    return records

