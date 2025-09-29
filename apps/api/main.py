"""FastAPI application entrypoint for DataForge."""

from __future__ import annotations

import datetime as dt
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.pipeline.business import run_business_pipeline
from core.pipeline.rfp import run_rfp_pipeline
from core.schemas import (
    BusinessPreviewResponse,
    BusinessPullRequest,
    DataForgeResponse,
    HealthResponse,
    PreviewQuery,
    RFPPullRequest,
    RFPPreviewResponse,
)
from core.preview import business_preview_store, rfp_preview_store


app = FastAPI(title="DataForge", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    """Simple health endpoint."""

    return HealthResponse(ok=True, ts=dt.datetime.utcnow())


@app.post("/pull/business", response_model=DataForgeResponse)
def pull_business(body: BusinessPullRequest) -> DataForgeResponse:
    """Trigger the business pipeline."""

    try:
        result = run_business_pipeline(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - safety net for runtime
        raise HTTPException(status_code=500, detail="Business pipeline failed") from exc

    return result


@app.post("/pull/rfps", response_model=DataForgeResponse)
def pull_rfps(body: RFPPullRequest) -> DataForgeResponse:
    """Trigger the RFP pipeline."""

    try:
        result = run_rfp_pipeline(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="RFP pipeline failed") from exc

    return result


def get_preview_query(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=200),
) -> PreviewQuery:
    return PreviewQuery(page=page, page_size=page_size)


@app.get("/preview/business", response_model=BusinessPreviewResponse)
def preview_business(
    query: PreviewQuery = Depends(get_preview_query),
    store=Depends(lambda: business_preview_store),
) -> Any:
    page = store.list_records(query)
    return page


@app.get("/preview/rfps", response_model=RFPPreviewResponse)
def preview_rfps(
    query: PreviewQuery = Depends(get_preview_query),
    store=Depends(lambda: rfp_preview_store),
) -> Any:
    page = store.list_records(query)
    return page


@app.exception_handler(ValueError)
def value_error_handler(_: Any, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"ok": False, "message": str(exc)})

