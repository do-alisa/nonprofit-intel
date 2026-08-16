"""Client for the ProPublica Nonprofit Explorer API (prototype data source).

Docs: https://projects.propublica.org/nonprofits/api
This module is the ONLY place that knows ProPublica's field names.
Everything past this boundary uses our own schemas.
"""

import httpx

from app.schemas import (
    FilingYear,
    OrganizationProfile,
    OrganizationSummary,
    SearchResponse,
)

BASE_URL = "https://projects.propublica.org/nonprofits/api/v2"


async def search_organizations(query: str) -> SearchResponse:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BASE_URL}/search.json", params={"q": query})
        resp.raise_for_status()
    data = resp.json()

    results = [
        OrganizationSummary(
            ein=str(org.get("ein", "")),
            name=org.get("name", ""),
            city=org.get("city"),
            state=org.get("state"),
            ntee_category=org.get("ntee_code"),
        )
        for org in data.get("organizations", [])
    ]
    return SearchResponse(
        query=query,
        total_results=data.get("total_results", len(results)),
        results=results,
    )


def _filing_to_year(filing: dict) -> FilingYear:
    return FilingYear(
        tax_year=filing.get("tax_prd_yr"),
        total_revenue=filing.get("totrevenue"),
        total_expenses=filing.get("totfuncexpns"),
        total_assets=filing.get("totassetsend"),
        total_liabilities=filing.get("totliabend"),
        contributions=filing.get("totcntrbgfts"),
        program_revenue=filing.get("totprgmrevnue"),
    )


async def get_organization(ein: str) -> OrganizationProfile | None:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BASE_URL}/organizations/{ein}.json")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
    data = resp.json()

    org = data.get("organization", {})
    filings = [
        _filing_to_year(f)
        for f in data.get("filings_with_data", [])
        if f.get("tax_prd_yr")
    ]
    filings.sort(key=lambda f: f.tax_year)

    return OrganizationProfile(
        ein=str(org.get("ein", ein)),
        name=org.get("name", ""),
        city=org.get("city"),
        state=org.get("state"),
        ntee_category=org.get("ntee_code"),
        filings=filings,
    )