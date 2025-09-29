"""Quality scoring for business records."""

from __future__ import annotations

from typing import Iterable, List

from core.schemas import BusinessCanonical


def score_business_records(records: Iterable[BusinessCanonical]) -> List[BusinessCanonical]:
    scored = []
    for record in records:
        score = 100
        if not record.domain:
            score -= 20
        if not record.phone:
            score -= 10
        if not record.address_line1:
            score -= 10
        if not record.naics_code:
            score -= 10

        # Email check stub; assume MX verified
        if not record.email:
            score -= 5

        score = max(0, min(score, 100))
        scored.append(record.model_copy(update={"quality_score": score}))
    return scored



