"""In-memory preview storage for API responses."""

from __future__ import annotations

from collections import deque
from typing import Deque, Iterable, List

from core.schemas import (
    BusinessCanonical,
    BusinessPreviewItem,
    BusinessPreviewResponse,
    PaginatedResponse,
    PreviewQuery,
    RFPCanonical,
    RFPPreviewItem,
    RFPPreviewResponse,
)


class _PreviewStore:
    def __init__(self, capacity: int = 500) -> None:
        self.capacity = capacity
        self._records: Deque = deque(maxlen=capacity)

    def save_records(self, records: Iterable) -> None:
        for record in records:
            self._records.appendleft(record)

    def paginate(self, query: PreviewQuery, transform) -> PaginatedResponse:
        start = (query.page - 1) * query.page_size
        end = start + query.page_size
        items = list(self._records)
        return transform(items[start:end], total=len(items), query=query)


class BusinessPreviewStore(_PreviewStore):
    def list_records(self, query: PreviewQuery) -> BusinessPreviewResponse:
        def build(records, total: int, query: PreviewQuery) -> BusinessPreviewResponse:
            items = [
                BusinessPreviewItem(
                    company_name=record.company_name,
                    state=record.state,
                    domain=record.domain,
                    quality_score=record.quality_score,
                )
                for record in records
            ]
            return BusinessPreviewResponse(page=query.page, page_size=query.page_size, total=total, items=items)

        return self.paginate(query, build)


class RFPPreviewStore(_PreviewStore):
    def list_records(self, query: PreviewQuery) -> RFPPreviewResponse:
        def build(records, total: int, query: PreviewQuery) -> RFPPreviewResponse:
            items = [
                RFPPreviewItem(
                    notice_id=record.notice_id,
                    title=record.title,
                    agency=record.agency,
                    posted_date=record.posted_date,
                )
                for record in records
            ]
            return RFPPreviewResponse(page=query.page, page_size=query.page_size, total=total, items=items)

        return self.paginate(query, build)


business_preview_store = BusinessPreviewStore()
rfp_preview_store = RFPPreviewStore()

