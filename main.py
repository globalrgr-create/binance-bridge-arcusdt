from flask import Flask, jsonify
import requests, time, os

app = Flask(__name__)

# ─────────────────────────────
# CONFIGURACIÓN DEL MERCADO
# ─────────────────────────────
SYMBOL = "ARCUSDT"  # par que queremos mirar
BASE = "https://fapi.binance.com/fapi/v1"  # Binance Futuros USDT-M

# ─────────────────────────────
# FUNCIÓN QUE LEE BINANCE
# ─────────────────────────────
def get_snapshot():
    try:
        # Precio 24h (incluye info extra: cambio %, volumen, etc.)
        price_24h = requests.get(
            f"{BASE}/ticker/24hr",
            params={"symbol": SYMBOL},
            timeout=6
        ).json()

        # Mejor precio actual (último price)
        last_price = requests.get(
            f"{BASE}/ticker/price",
            params={"symbol": SYMBOL},
            timeout=6
        ).json()

        # Libro de órdenes (50 niveles)
        depth = requests.get(
            f"{BASE}/depth",
            params={"symbol": SYMBOL, "limit": 50},
            timeout=6
        ).json()

        # Open interest
        oi = requests.get(
            f"{BASE}/openInterest",
            params={"symbol": SYMBOL},
            timeout=6
        ).json()

        # Última tasa de funding
        funding = requests.get(
            f"{BASE}/fundingRate",
            params={"symbol": SYMBOL, "limit": 1},
            timeout=6
        ).json()

        snapshot = {
            "symbol": SYMBOL,
            "timestamp": int(time.time() * 1000),
            "lastPrice": last_price,
            "stats24h": price_24h,
            "orderbook": {
                "bids": depth.get("bids", []),
                "asks": depth.get("asks", [])
            },
            "openInterest": oi,
            "fundingRate": funding[0] if isinstance(funding, list) and funding else funding
        }
        return snapshot

    except Exception as e:
        # Si algo falla, devolvemos el error
        return {"error": str(e), "timestamp": int(time.time() * 1000)}

# ─────────────────────────────
# RUTAS HTTP
# ─────────────────────────────
@app.route("/")
def home():
    return "Puente Binance ARCUSDT activo ✅ /snapshot para ver datos"

@app.route("/snapshot")
def snapshot():
    data = get_snapshot()
    return jsonify(data)

# ─────────────────────────────
# ARRANQUE LOCAL (Render usa gunicorn)
# ─────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
