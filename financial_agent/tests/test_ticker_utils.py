from financial_research_agent.agents.ticker_utils import resolve_ticker


def test_resolve_ticker_from_company_name():
    assert resolve_ticker("Analyze Apple latest earnings") == "AAPL"
    assert resolve_ticker("Dell Technologies risk profile") == "DELL"


def test_resolve_ticker_from_symbol():
    assert resolve_ticker("MSFT most recent quarter") == "MSFT"


def test_resolve_ticker_ignores_noise_words():
    assert resolve_ticker("SEC filing risk analysis") is None
