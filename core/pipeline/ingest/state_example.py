"""Placeholder state portal ingestion."""

from __future__ import annotations

import logging
from typing import Dict, List

from core.schemas import BusinessPullRequest


logger = logging.getLogger(__name__)


def fetch_businesses(payload: BusinessPullRequest) -> List[Dict]:
    logger.info("state_example fetch invoked", extra={"states": payload.states})
    mock = []
    for state in payload.states:
        mock.append(
            {
                "company_name": f"Sample Co {state}",
                "state": state,
                "source": "state.example",
                "founded_year": 2015,
            }
        )
    return mock



