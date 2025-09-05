import yfinance as yf
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app)

# Disable dotenv loading to avoid Unicode errors
app.config['LOAD_DOTENV'] = False

# The tool to fetch financial data from Yahoo
@app.route('/get_yahoo_data', methods=['POST'])
def get_yahoo_data():
    data = request.get_json()
    stock_data = data.get('stock_data', '')
    print(f"[debug-server] get_yahoo_data({stock_data})")

    try:
        stock = yf.Ticker(stock_data)
        financial_data = stock.history(period="5d")
        return jsonify({
            'success': True,
            'data': financial_data.to_dict('records')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# The tool to fetch financial data from Reddit
@app.route('/get_reddit_data', methods=['POST'])
def get_reddit_data():
    data = request.get_json()
    stock_data = data.get('stock_data', '')
    print(f"[debug-server] get_reddit_data({stock_data})")

    try:
        endpoint = f"https://www.reddit.com/r/all/search.json?q={stock_data}&restrict_sr=on&sort=relevance&t=all"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            return jsonify({
                'success': True,
                'data': response.json()
            })
        else:
            return jsonify({
                'success': False,
                'error': f"HTTP {response.status_code}"
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

def run_server():
    app.run(host='0.0.0.0', port=8000, debug=False)

if __name__ == "__main__":
    print("Starting Financial Data Server on http://localhost:8000")
    run_server()
