"""Dedupe logic for business records."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from rapidfuzz import fuzz

from core.schemas import BusinessCanonical


def dedupe_businesses(records: Iterable[BusinessCanonical]) -> List[BusinessCanonical]:
    by_domain: Dict[str, BusinessCanonical] = {}
    by_phone: Dict[str, BusinessCanonical] = {}
    unique: List[BusinessCanonical] = []

    for record in records:
        key = _canonical_key(record)
        if key and key in by_domain:
            merged = _merge_records(by_domain[key], record)
            by_domain[key] = merged
            continue

        if record.phone and record.phone in by_phone:
            merged = _merge_records(by_phone[record.phone], record)
            by_phone[record.phone] = merged
            continue

        # Fuzzy matching with name and postal_code
        matched = False
        for existing in unique:
            if record.postal_code and existing.postal_code and record.postal_code == existing.postal_code:
                score = fuzz.token_sort_ratio(record.company_name, existing.company_name)
                if score >= 90:
                    merged = _merge_records(existing, record)
                    unique[unique.index(existing)] = merged
                    matched = True
                    break
        if matched:
            continue

        unique.append(record)
        if key:
            by_domain[key] = record
        if record.phone:
            by_phone[record.phone] = record

    return unique


def _canonical_key(record: BusinessCanonical) -> Optional[str]:
    if record.domain:
        return record.domain.lower()
    return None


def _merge_records(primary: BusinessCanonical, incoming: BusinessCanonical) -> BusinessCanonical:
    data = primary.model_dump()
    for field, value in incoming.model_dump().items():
        if not value:
            continue
        current = data.get(field)
        if not current:
            data[field] = value
        elif field == "source" and value not in current:
            data[field] = ";".join(sorted(set(current.split(";") + [value])))
        elif field == "last_verified":
            if value > current:
                data[field] = value
    return BusinessCanonical(**data)


