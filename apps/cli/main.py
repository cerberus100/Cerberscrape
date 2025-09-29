"""CLI entrypoint for DataForge."""

from __future__ import annotations

import json
from typing import Optional

import typer

from core.pipeline.business import run_business_pipeline
from core.pipeline.rfp import run_rfp_pipeline
from core.schemas import BusinessPullRequest, RFPPullRequest


app = typer.Typer(help="DataForge CLI")


def parse_list(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


@app.command("biz")
def biz_pull(
    states: str = typer.Option(..., help="Comma-separated states"),
    naics: Optional[str] = typer.Option(None, help="Comma-separated NAICS codes"),
    keywords: Optional[str] = typer.Option(None, help="Comma-separated keywords"),
    limit: int = typer.Option(500, help="Limit records", min=1, max=2000000),
    min_years: Optional[int] = typer.Option(None),
    max_years: Optional[int] = typer.Option(None),
    enable_geocoder: bool = typer.Option(False, help="Enable Census geocoder"),
    small_business_only: bool = typer.Option(False, help="Filter for small businesses only"),
    business_size: Optional[str] = typer.Option(None, help="Specific business size: micro, small, medium, large"),
) -> None:
    payload = BusinessPullRequest(
        states=parse_list(states) or [],
        naics=parse_list(naics),
        keywords=parse_list(keywords),
        limit=limit,
        min_years=min_years,
        max_years=max_years,
        enable_geocoder=enable_geocoder,
        small_business_only=small_business_only,
        business_size=business_size,
    )
    result = run_business_pipeline(payload)
    typer.echo(json.dumps(result.model_dump(), indent=2, default=str))


@app.command("rfp")
def rfp_pull(
    states: str = typer.Option(..., help="Comma-separated states"),
    naics: Optional[str] = typer.Option(None),
    keywords: Optional[str] = typer.Option(None),
    posted_from: Optional[str] = typer.Option(None),
    posted_to: Optional[str] = typer.Option(None),
    limit: int = typer.Option(500, min=1, max=10_000),
) -> None:
    payload = RFPPullRequest(
        states=parse_list(states) or [],
        naics=parse_list(naics),
        keywords=parse_list(keywords),
        posted_from=posted_from,
        posted_to=posted_to,
        limit=limit,
    )
    result = run_rfp_pipeline(payload)
    typer.echo(json.dumps(result.model_dump(), indent=2, default=str))


def main() -> None:
    app()


if __name__ == "__main__":
    main()

