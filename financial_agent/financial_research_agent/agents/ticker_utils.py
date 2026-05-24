from __future__ import annotations

import re


COMPANY_TICKERS: dict[str, str] = {
    "alphabet": "GOOGL",
    "amazon": "AMZN",
    "amd": "AMD",
    "apple": "AAPL",
    "berkshire hathaway": "BRK-B",
    "dell": "DELL",
    "dell technologies": "DELL",
    "google": "GOOGL",
    "ibm": "IBM",
    "intel": "INTC",
    "meta": "META",
    "meta platforms": "META",
    "microsoft": "MSFT",
    "netflix": "NFLX",
    "nvidia": "NVDA",
    "oracle": "ORCL",
    "salesforce": "CRM",
    "tesla": "TSLA",
}


_TICKER_PATTERN = re.compile(r"\b[A-Z]{1,5}(?:[-.][A-Z])?\b")
_NOISE_WORDS = {
    "CEO",
    "CFO",
    "EPS",
    "ETF",
    "IPO",
    "LLC",
    "NYSE",
    "SEC",
    "USA",
}


def resolve_ticker(text: str) -> str | None:
    """Resolve a user/search phrase to a likely stock ticker."""
    if not text:
        return None

    normalized = text.lower()
    for company, ticker in COMPANY_TICKERS.items():
        if company in normalized:
            return ticker

    for candidate in _TICKER_PATTERN.findall(text):
        if candidate not in _NOISE_WORDS:
            return candidate.replace(".", "-")

    return None
