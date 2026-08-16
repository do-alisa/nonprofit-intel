from pydantic import BaseModel


class OrganizationSummary(BaseModel):
    """One search result row."""

    ein: str
    name: str
    city: str | None = None
    state: str | None = None
    ntee_category: str | None = None


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: list[OrganizationSummary]


class FilingYear(BaseModel):
    """One year of financials for an organization."""

    tax_year: int
    total_revenue: float | None = None
    total_expenses: float | None = None
    total_assets: float | None = None
    total_liabilities: float | None = None
    contributions: float | None = None
    program_revenue: float | None = None


class OrganizationProfile(BaseModel):
    ein: str
    name: str
    city: str | None = None
    state: str | None = None
    ntee_category: str | None = None
    filings: list[FilingYear]