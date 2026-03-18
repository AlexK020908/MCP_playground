"""
Filters for email search results (e.g. tax-filing-only).
"""


def _looks_like_news(row: dict) -> bool:
    """True if this looks like a news headline/newsletter, not a tax document or notice."""
    text = (row.get("subject", "") + " " + row.get("snippet", "") + " " + row.get("from", "")).lower()
    news_indicators = (
        "what's news", "whats news", "headlines", "newsletter", "daily digest", "breaking news",
        "wsj.com", "wsj ", "wall street journal", "interactive.wsj", "nytimes", "reuters",
        "bloomberg", "the economist", "news alert", "catch up on", "understand the news",
    )
    return any(n in text for n in news_indicators)


def filter_tax_filing_only(rows: list[dict]) -> list[dict]:
    """Keep only rows that look like property tax, tax filing, or official government tax; drop payment/receipt tax and news."""
    filing_keywords = (
        "property tax", "tax return", "irs", "1040", "w-2", "w2", "file taxes", "tax filing",
        "tax assessment", "department of revenue", "tax form", "tax authority", "income tax",
        "form 1040", "extension", "tax deadline", "filing deadline", "federal tax", "state tax",
        "tax refund", "1099", "tax year", "property tax assessment", "assessor", "tax bill",
        "tax notice", "advance tax", "empty homes tax", "tax billing", "propertytax",
    )
    kept: list[dict] = []
    for r in rows:
        if _looks_like_news(r):
            continue
        text = (r.get("subject", "") + " " + r.get("snippet", "") + " " + r.get("from", "")).lower()
        if any(f in text for f in filing_keywords):
            kept.append(r)
    return kept
