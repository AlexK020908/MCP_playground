"""
Filters for email search results (e.g. tax-filing-only).
"""


def filter_tax_filing_only(rows: list[dict]) -> list[dict]:
    """Keep only rows that look like property tax, tax filing, or official government tax; drop payment/receipt tax."""
    filing_keywords = (
        "property tax", "tax return", "irs", "1040", "w-2", "w2", "file taxes", "tax filing",
        "tax assessment", "department of revenue", "tax form", "tax authority", "income tax",
        "form 1040", "extension", "tax deadline", "filing deadline", "federal tax", "state tax",
        "tax refund", "1099", "tax year", "property tax assessment", "assessor", "tax bill",
    )
    kept: list[dict] = []
    for r in rows:
        text = (r.get("subject", "") + " " + r.get("snippet", "") + " " + r.get("from", "")).lower()
        if any(f in text for f in filing_keywords):
            kept.append(r)
    return kept
