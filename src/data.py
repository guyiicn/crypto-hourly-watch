import requests

# Bybit v5 public REST. If blocked, swap to api.binance.com / www.okx.com (paths differ).
BASE = "https://api.bybit.com"


def get_klines(pair: str, interval: str = "60", limit: int = 210) -> list[dict]:
    r = requests.get(
        f"{BASE}/v5/market/kline",
        params={"category": "spot", "symbol": pair, "interval": interval, "limit": limit},
        timeout=10,
    )
    r.raise_for_status()
    items = r.json()["result"]["list"]
    items = list(reversed(items))  # Bybit returns newest-first
    return [
        {
            "time": int(k[0]),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
        }
        for k in items
    ]


def get_ticker_24h(pair: str) -> dict:
    r = requests.get(
        f"{BASE}/v5/market/tickers",
        params={"category": "spot", "symbol": pair},
        timeout=10,
    )
    r.raise_for_status()
    item = r.json()["result"]["list"][0]
    return {
        "priceChangePercent": float(item["price24hPcnt"]) * 100,
        "highPrice": float(item["highPrice24h"]),
        "lowPrice": float(item["lowPrice24h"]),
        "lastPrice": float(item["lastPrice"]),
    }


def get_funding_rate_pct(pair: str) -> float:
    r = requests.get(
        f"{BASE}/v5/market/funding/history",
        params={"category": "linear", "symbol": pair, "limit": 1},
        timeout=10,
    )
    r.raise_for_status()
    items = r.json()["result"]["list"]
    if not items:
        return 0.0
    return float(items[0]["fundingRate"]) * 100
