import requests

BASE = "https://min-api.cryptocompare.com"
COINGECKO_BASE = "https://api.coingecko.com/api/v3"
HEADERS = {"User-Agent": "crypto-hourly-watch/1.0"}

# Funding rate sourcing: which exchanges (in priority order) and the perp symbol used there.
FUNDING_MARKET_PRIORITY = ["Binance (Futures)", "Bybit (Futures)", "OKX (Futures)"]
FUNDING_PERP_SYMBOL = {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT"}


def _normalize_ticker(node: dict) -> dict:
    return {
        "lastPrice": float(node["PRICE"]),
        "priceChangePercent": float(node["CHANGEPCT24HOUR"]),
        "highPrice": float(node["HIGH24HOUR"]),
        "lowPrice": float(node["LOW24HOUR"]),
    }


def _fetch_ticker(symbols: list[str], tsym: str) -> dict:
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
    return body.get("RAW", {})


def get_multi_ticker(symbols: list[str], tsym: str = "USDT") -> dict:
    raw = _fetch_ticker(symbols, tsym)
    out: dict = {}
    missing: list[str] = []
    for sym in symbols:
        node = raw.get(sym, {}).get(tsym)
        if node:
            out[sym] = _normalize_ticker(node)
        else:
            missing.append(sym)

    if missing and tsym != "USD":
        try:
            raw_usd = _fetch_ticker(missing, "USD")
            for sym in missing:
                node = raw_usd.get(sym, {}).get("USD")
                if node:
                    out[sym] = _normalize_ticker(node)
        except Exception as e:
            print(f"USD ticker fallback failed: {e}")
    return out


def get_klines(symbol: str, tsym: str = "USDT", limit: int = 210) -> list[dict]:
    last_err: Exception | None = None
    for candidate in [tsym, "USD"]:
        try:
            r = requests.get(
                f"{BASE}/data/v2/histohour",
                params={"fsym": symbol, "tsym": candidate, "limit": limit},
                headers=HEADERS,
                timeout=15,
            )
            r.raise_for_status()
            body = r.json()
            if body.get("Response") == "Error":
                last_err = RuntimeError(body.get("Message", "unknown"))
                continue
            rows = body.get("Data", {}).get("Data", [])
            if not rows:
                continue
            return [
                {
                    "time": int(c["time"]),
                    "open": float(c["open"]),
                    "high": float(c["high"]),
                    "low": float(c["low"]),
                    "close": float(c["close"]),
                    "volume": float(c["volumefrom"]),
                }
                for c in rows
            ]
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"klines fetch failed for {symbol}: {last_err}")


def get_funding_rates_pct(symbols: list[str]) -> dict[str, float]:
    targets = {FUNDING_PERP_SYMBOL[s]: s for s in symbols if s in FUNDING_PERP_SYMBOL}
    if not targets:
        return {}
    try:
        r = requests.get(
            f"{COINGECKO_BASE}/derivatives",
            params={"include_tickers": "unexpired"},
            headers=HEADERS,
            timeout=20,
        )
        r.raise_for_status()
        items = r.json()
    except Exception as e:
        print(f"funding fetch failed: {e}")
        return {}

    found: dict[str, tuple[int, float]] = {}
    for item in items:
        if item.get("contract_type") != "perpetual":
            continue
        market = item.get("market", "")
        if market not in FUNDING_MARKET_PRIORITY:
            continue
        sym = item.get("symbol")
        if sym not in targets:
            continue
        rate = item.get("funding_rate")
        if rate is None:
            continue
        priority = FUNDING_MARKET_PRIORITY.index(market)
        display = targets[sym]
        if display not in found or priority < found[display][0]:
            found[display] = (priority, float(rate))

    return {sym: rate for sym, (_, rate) in found.items()}
