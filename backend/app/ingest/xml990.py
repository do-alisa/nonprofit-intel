"""Parse IRS Form 990 e-file XML into our internal representation.

Handles the modern (2013+) IRS e-file schema for the full Form 990.
Field locations are configuration (FIELDS), not code: supporting
another schema year or form type should mean editing mappings, not
logic.
"""

from lxml import etree
from pydantic import BaseModel

NS = {"irs": "http://www.irs.gov/efile"}

# Our field name -> path within the Return element.
FIELDS = {
    "total_revenue": "irs:ReturnData/irs:IRS990/irs:CYTotalRevenueAmt",
    "total_expenses": "irs:ReturnData/irs:IRS990/irs:CYTotalExpensesAmt",
    "total_assets": "irs:ReturnData/irs:IRS990/irs:TotalAssetsEOYAmt",
    "total_liabilities": "irs:ReturnData/irs:IRS990/irs:TotalLiabilitiesEOYAmt",
    "contributions": "irs:ReturnData/irs:IRS990/irs:CYContributionsGrantsAmt",
    "program_revenue": "irs:ReturnData/irs:IRS990/irs:CYProgramServiceRevenueAmt",
    "program_expenses": (
        "irs:ReturnData/irs:IRS990/irs:TotalFunctionalExpensesGrp/"
        "irs:ProgramServicesAmt"
    ),
    "admin_expenses": (
        "irs:ReturnData/irs:IRS990/irs:TotalFunctionalExpensesGrp/"
        "irs:ManagementAndGeneralAmt"
    ),
    "fundraising_expenses": (
        "irs:ReturnData/irs:IRS990/irs:TotalFunctionalExpensesGrp/"
        "irs:FundraisingAmt"
    ),
}

EIN_PATH = "irs:ReturnHeader/irs:Filer/irs:EIN"
TAX_YEAR_PATH = "irs:ReturnHeader/irs:TaxYr"
FORM_TYPE_PATH = "irs:ReturnHeader/irs:ReturnTypeCd"


class Parsed990(BaseModel):
    ein: str
    tax_year: int
    form_type: str
    total_revenue: int | None = None
    total_expenses: int | None = None
    total_assets: int | None = None
    total_liabilities: int | None = None
    contributions: int | None = None
    program_revenue: int | None = None
    program_expenses: int | None = None
    admin_expenses: int | None = None
    fundraising_expenses: int | None = None


class UnsupportedFiling(Exception):
    """Filing is a form type or schema we don't handle yet."""


def _text(root: etree._Element, path: str) -> str | None:
    el = root.find(path, NS)
    if el is None or el.text is None:
        return None
    return el.text.strip() or None


def _amount(root: etree._Element, path: str) -> int | None:
    text = _text(root, path)
    if text is None:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def parse_990(xml_bytes: bytes) -> Parsed990:
    root = etree.fromstring(xml_bytes)

    form_type = _text(root, FORM_TYPE_PATH)
    if form_type != "990":
        raise UnsupportedFiling(f"form type {form_type!r} not supported yet")

    ein = _text(root, EIN_PATH)
    tax_year = _text(root, TAX_YEAR_PATH)
    if ein is None or tax_year is None:
        raise UnsupportedFiling("missing EIN or tax year in ReturnHeader")

    amounts = {name: _amount(root, path) for name, path in FIELDS.items()}
    return Parsed990(
        ein=ein.zfill(9),
        tax_year=int(tax_year),
        form_type=form_type,
        **amounts,
    )