"""Ingest the IRS Exempt Organizations Business Master File (BMF).

Downloads the per-state CSV from irs.gov and upserts every
organization into the organizations table.

Usage:
    uv run python -m app.ingest.bmf            # California
    uv run python -m app.ingest.bmf --state dc
"""

import argparse
import csv
import io

import httpx
from pydantic import BaseModel, ValidationError, field_validator
from sqlalchemy.dialects.postgresql import insert

from app.db import engine
from app.models import Organization

BMF_URL = "https://www.irs.gov/pub/irs-soi/eo_{state}.csv"
BATCH_SIZE = 1000


class BmfRow(BaseModel):
    ein: str
    name: str
    city: str | None
    state: str | None
    ntee_code: str | None
    subsection: str | None
    ruling_year: int | None

    @field_validator("ein")
    @classmethod
    def ein_is_nine_digits(cls, v: str) -> str:
        v = v.strip().zfill(9)  # CSV drops leading zeros
        if not v.isdigit():
            raise ValueError("EIN must be numeric")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name is empty")
        return v.strip()


def parse_row(raw: dict) -> BmfRow:
    ruling = (raw.get("RULING") or "").strip()
    year = ruling[:4]
    return BmfRow(
        ein=raw.get("EIN", ""),
        name=(raw.get("NAME") or "")[:255],
        city=(raw.get("CITY") or "").strip()[:100] or None,
        state=(raw.get("STATE") or "").strip()[:2] or None,
        ntee_code=(raw.get("NTEE_CD") or "").strip()[:10] or None,
        subsection=(raw.get("SUBSECTION") or "").strip()[:5] or None,
        ruling_year=int(year) if year.isdigit() and year != "0000" else None,
    )


def upsert_batch(conn, rows: list[dict]) -> None:
    stmt = insert(Organization).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["ein"],
        set_={
            "name": stmt.excluded.name,
            "city": stmt.excluded.city,
            "state": stmt.excluded.state,
            "ntee_code": stmt.excluded.ntee_code,
            "subsection": stmt.excluded.subsection,
            "ruling_year": stmt.excluded.ruling_year,
        },
    )
    conn.execute(stmt)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="ca")
    args = parser.parse_args()

    url = BMF_URL.format(state=args.state.lower())
    print(f"Downloading {url} ...")
    resp = httpx.get(url, timeout=120, follow_redirects=True)
    resp.raise_for_status()
    print(f"Downloaded {len(resp.content) / 1_000_000:.1f} MB")

    reader = csv.DictReader(io.StringIO(resp.text))

    ok, skipped = 0, 0
    batch: list[dict] = []
    with engine.begin() as conn:
        for raw in reader:
            try:
                row = parse_row(raw)
            except ValidationError:
                skipped += 1
                continue
            batch.append(row.model_dump())
            if len(batch) >= BATCH_SIZE:
                upsert_batch(conn, batch)
                ok += len(batch)
                batch = []
                if ok % 25_000 == 0:
                    print(f"  upserted {ok:,} ...")
        if batch:
            upsert_batch(conn, batch)
            ok += len(batch)

    print(f"Done: {ok:,} organizations upserted, {skipped:,} rows skipped")


if __name__ == "__main__":
    main()