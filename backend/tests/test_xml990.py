from pathlib import Path

import pytest

from app.ingest.xml990 import UnsupportedFiling, Parsed990, parse_990

FIXTURES = Path(__file__).parent / "fixtures"


def load(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def test_parses_sierra_club_filing():
    parsed = parse_990(load("sierra_club.xml"))
    assert parsed.ein == "941153307"
    assert parsed.form_type == "990"
    assert parsed.tax_year == 2025
    assert parsed.total_revenue == 83752990
    assert parsed.total_expenses == 84895816
    assert parsed.total_assets == 152292481


def test_parses_habitat_filing():
    parsed = parse_990(load("habitat_for_humanity_east_bay.xml"))
    assert parsed.form_type == "990"
    assert parsed.ein == "943053687"
    assert parsed.tax_year == 2024
    assert parsed.total_revenue == 29469732


def test_parses_food_bank_filing():
    parsed = parse_990(load("san_francisco_food_bank.xml"))
    assert parsed.form_type == "990"
    assert parsed.ein == "943041517"
    assert parsed.tax_year == 2024
    assert parsed.total_revenue == 167084763


def test_rejects_real_ez_filing():
    with pytest.raises(UnsupportedFiling):
        parse_990(load("ez_filing.xml"))


def test_rejects_non_990_form():
    xml = b"""<Return xmlns="http://www.irs.gov/efile">
      <ReturnHeader><ReturnTypeCd>990EZ</ReturnTypeCd></ReturnHeader>
    </Return>"""
    with pytest.raises(UnsupportedFiling):
        parse_990(xml)


@pytest.mark.parametrize(
    "fixture",
    [
        "sierra_club.xml",
        "habitat_for_humanity_east_bay.xml",
        "san_francisco_food_bank.xml",
    ],
)
def test_all_financial_fields_extracted(fixture):
    parsed = parse_990(load(fixture))
    missing = [
        f for f in Parsed990.model_fields if getattr(parsed, f) is None
    ]
    assert missing == [], f"{fixture}: fields came back None: {missing}"