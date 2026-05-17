import requests

# CryptoCompare public REST. CDN-fronted, reliably reachable from GitHub Actions.
BASE = "https://min-api.cryptocompare.com"
HEADERS = {"User-Agent": "crypto-hourly-watch/1.0"}


def get_klines(symbol: str, tsym: str = "USDT", limit: int = 210) -> list[dict]:
    r = requests.get(
        f"{BASE}/data/v2/histohour",
        params={"fsym": symbol, "tsym": tsym, "limit": limit},
        headers=HEADERS,
        timeout=15,
    )
    r.raise_for_status()
    body = r.json()
    if body.get("Response") == "Error":
        raise RuntimeError(f"CryptoCompare error: {body.get('Message')}")
    return [
        {
            "time": int(c["time"]),
            "open": float(c["open"]),
            "high": float(c["high"]),
            "low": float(c["low"]),
            "close": float(c["close"]),
            "volume": float(c["volumefrom"]),
        }
        for c in body["Data"]["Data"]
    ]


def get_multi_ticker(symbols: list[str], tsym: str = "USDT") -> dict:
    r = requests.get(
        f"{BASE}/data/pricemultifull",
        params={"fsyms": ",".join(symbols), "tsyms": tsym},
        headers=HEADERS,
        timeout=15,
    )
    r.raise_for_status()
    body = r.json()
    if body.get("Response") == "Error":
        raise RuntimeError(f"CryptoCompare error: {body.get('Message')}")
    raw = body.get("RAW", {})
    out = {}
    for sym in symbols:
        node = raw.get(sym, {}).get(tsym)
        if not node:
            continue
        out[sym] = {
            "lastPrice": float(node["PRICE"]),
            "priceChangePercent": float(node["CHANGEPCT24HOUR"]),
            "highPrice": float(node["HIGH24HOUR"]),
            "lowPrice": float(node["LOW24HOUR"]),
        }
    return out
