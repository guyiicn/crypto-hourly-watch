import math

from . import config


def evaluate(s: dict) -> list[str]:
    triggered: list[str] = []

    p1h = s["change_1h_pct"]
    p24h = s["change_24h_pct"]
    rsi_val = s["rsi_1h"]
    price = s["price"]
    ma200 = s["ma200_1h"]

    if abs(p1h) >= config.ALERT_1H_PCT:
        triggered.append(f"1h {('急涨' if p1h > 0 else '急跌')} {p1h:+.2f}%")

    if abs(p24h) >= config.ALERT_24H_PCT:
        triggered.append(f"24h {('上涨' if p24h > 0 else '下跌')} {p24h:+.2f}%")

    if not math.isnan(rsi_val):
        if rsi_val >= config.ALERT_RSI_HIGH:
            triggered.append(f"RSI 超买 {rsi_val:.1f}")
        elif rsi_val <= config.ALERT_RSI_LOW:
            triggered.append(f"RSI 超卖 {rsi_val:.1f}")

    if not math.isnan(ma200) and ma200 > 0:
        if abs(price - ma200) / ma200 < 0.005:
            relation = "上方" if price > ma200 else "下方"
            triggered.append(f"贴近 MA200 (${ma200:,.2f}) 现处{relation}")

    return triggered
