from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app import propublica
from app.schemas import OrganizationProfile, SearchResponse

app = FastAPI(title="Nonprofit Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/search", response_model=SearchResponse)
async def search(q: str = Query(min_length=2)) -> SearchResponse:
    return await propublica.search_organizations(q)


@app.get("/organizations/{ein}", response_model=OrganizationProfile)
async def organization(ein: str) -> OrganizationProfile:
    profile = await propublica.get_organization(ein)
    if profile is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return profile