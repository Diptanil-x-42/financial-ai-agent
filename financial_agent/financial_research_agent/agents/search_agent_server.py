import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf

from financial_research_agent.agents.ticker_utils import resolve_ticker

app = Flask(__name__)
CORS(app)

# Disable dotenv loading to avoid Unicode errors
app.config["LOAD_DOTENV"] = False

# The tool to fetch financial data from Yahoo
@app.route("/get_yahoo_data", methods=["POST"])
def get_yahoo_data():
    data = request.get_json(silent=True) or {}
    stock_data = data.get("stock_data", "")
    ticker = data.get("ticker") or resolve_ticker(stock_data)
    print(f"[debug-server] get_yahoo_data({stock_data})")

    if not ticker:
        return jsonify({
            "success": False,
            "error": "Could not resolve a ticker symbol from the request.",
            "source": "Yahoo Finance",
            "query": stock_data,
        })

    try:
        stock = yf.Ticker(ticker)
        financial_data = stock.history(period="5d")
        if financial_data.empty:
            return jsonify({
                "success": False,
                "error": f"No Yahoo Finance history returned for ticker {ticker}.",
                "source": "Yahoo Finance",
                "query": stock_data,
                "ticker": ticker,
            })

        return jsonify({
            "success": True,
            "source": "Yahoo Finance",
            "query": stock_data,
            "ticker": ticker,
            "data": financial_data.reset_index().to_dict("records"),
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "source": "Yahoo Finance",
            "query": stock_data,
            "ticker": ticker,
        })

# The tool to fetch financial data from Reddit
@app.route("/get_reddit_data", methods=["POST"])
def get_reddit_data():
    data = request.get_json(silent=True) or {}
    stock_data = data.get("stock_data", "")
    print(f"[debug-server] get_reddit_data({stock_data})")

    try:
        endpoint = f"https://www.reddit.com/r/all/search.json?q={stock_data}&restrict_sr=on&sort=relevance&t=all"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(endpoint, headers=headers, timeout=10)

        if response.status_code == 200:
            payload = response.json()
            posts = payload.get("data", {}).get("children", [])[:5]
            summaries = [
                {
                    "title": post.get("data", {}).get("title"),
                    "subreddit": post.get("data", {}).get("subreddit"),
                    "url": f"https://www.reddit.com{post.get('data', {}).get('permalink', '')}",
                    "score": post.get("data", {}).get("score"),
                }
                for post in posts
            ]
            return jsonify({
                "success": True,
                "source": "Reddit",
                "query": stock_data,
                "data": summaries,
                "source_url": endpoint,
            })
        else:
            return jsonify({
                "success": False,
                "error": f"HTTP {response.status_code}",
                "source": "Reddit",
                "query": stock_data,
                "source_url": endpoint,
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "source": "Reddit",
            "query": stock_data,
        })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


def run_server():
    app.run(host="0.0.0.0", port=8000, debug=False)


if __name__ == "__main__":
    print("Starting Financial Data Server on http://localhost:8000")
    run_server()
