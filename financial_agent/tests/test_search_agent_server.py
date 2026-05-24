from financial_research_agent.agents import search_agent_server


class FakeHistory:
    empty = False

    def reset_index(self):
        return self

    def to_dict(self, orient):
        assert orient == "records"
        return [{"Close": 123.45}]


class FakeTicker:
    def __init__(self, ticker):
        self.ticker = ticker

    def history(self, period):
        assert period == "5d"
        return FakeHistory()


def test_get_yahoo_data_resolves_company_name(monkeypatch):
    monkeypatch.setattr(search_agent_server.yf, "Ticker", FakeTicker)
    client = search_agent_server.app.test_client()

    response = client.post("/get_yahoo_data", json={"stock_data": "Apple earnings"})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["source"] == "Yahoo Finance"
    assert payload["ticker"] == "AAPL"
    assert payload["data"] == [{"Close": 123.45}]


def test_get_yahoo_data_rejects_unresolved_ticker():
    client = search_agent_server.app.test_client()

    response = client.post("/get_yahoo_data", json={"stock_data": "latest earnings"})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["success"] is False
    assert "ticker" in payload["error"].lower()
