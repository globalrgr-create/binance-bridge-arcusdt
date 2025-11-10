from flask import Flask, jsonify
import requests, time

app = Flask(__name__)

SYMBOL = "ARCUSDT"
BASE = "https://fapi.binance.com/fapi/v1"

def get_snapshot():
    try:
        price = requests.get(f"{BASE}/ticker/price?symbol={SYMBOL}").json()
        depth = requests.get(f"{BASE}/depth?symbol={SYMBOL}&limit=50").json()
        oi = requests.get(f"{BASE}/openInterest?symbol={SYMBOL}").json()
        fr = requests.get(f"{BASE}/fundingRate?symbol={SYMBOL}&limit=1").json()

        return {
            "symbol": SYMBOL,
            "timestamp": int(time.time() * 1000),
            "price": price,
            "orderbook": depth,
            "openInterest": oi,
            "fundingRate": fr
        }
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def home():
    return jsonify(get_snapshot())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
