from datetime import datetime, timedelta, timezone

from . import alerts, config, data, indicators, llm, tg

CST = timezone(timedelta(hours=8))


def build_snapshot(symbol: str, ticker: dict, funding: float | None) -> dict:
    klines = data.get_klines(symbol, tsym="USDT", limit=210)
    closes = [k["close"] for k in klines]
    return {
        "symbol": symbol,
        "price": ticker["lastPrice"],
        "change_1h_pct": indicators.pct_change(closes[-1], closes[-2]),
        "change_24h_pct": ticker["priceChangePercent"],
        "high_24h": ticker["highPrice"],
        "low_24h": ticker["lowPrice"],
        "rsi_1h": indicators.rsi(closes, 14),
        "ma50_1h": indicators.sma(closes, 50),
        "ma200_1h": indicators.sma(closes, 200),
        "funding_pct": funding,
    }


def format_snapshot_line(s: dict) -> str:
    fund_part = f"  Fund {s['funding_pct']:+.4f}%" if s["funding_pct"] is not None else ""
    return (
        f"<b>{s['symbol']}</b> ${s['price']:,.2f}"
        f"  1h {s['change_1h_pct']:+.2f}%"
        f"  24h {s['change_24h_pct']:+.2f}%"
        f"  RSI {s['rsi_1h']:.0f}"
        f"{fund_part}"
    )


def format_alert_detail(s: dict, alert_msgs: list[str]) -> str:
    return "\n".join([
        f"  H/L 24h: ${s['low_24h']:,.2f} – ${s['high_24h']:,.2f}",
        f"  MA50/MA200 (1h): ${s['ma50_1h']:,.2f} / ${s['ma200_1h']:,.2f}",
        "  ⚠️ " + "  ·  ".join(alert_msgs),
    ])


def build_llm_prompt(snapshots: list[dict], alerts_by_symbol: dict) -> str:
    lines = [
        "你是冷静的加密货币短线分析师。下面是触发告警的标的快照，",
        "请用中文写一段不超过 180 字的解读：",
        "- 重点说**为什么触发**和**接下来要警惕什么**",
        "- 客观、不喊单、不写免责声明",
        "- 多个标的合并成一段，不要分点",
        "",
        "触发标的：",
    ]
    for s in snapshots:
        if s["symbol"] in alerts_by_symbol:
            fund_str = f"  Fund {s['funding_pct']:+.4f}%" if s["funding_pct"] is not None else ""
            lines.append(
                f"- {s['symbol']} ${s['price']:,.2f}  "
                f"1h {s['change_1h_pct']:+.2f}%  "
                f"24h {s['change_24h_pct']:+.2f}%  "
                f"RSI {s['rsi_1h']:.1f}{fund_str}  "
                f"告警: {', '.join(alerts_by_symbol[s['symbol']])}"
            )
    return "\n".join(lines)


def build_message(snapshots: list[dict], alerts_by_symbol: dict, llm_text: str) -> str:
    now = datetime.now(CST).strftime("%m-%d %H:%M")
    out = [f"<b>📊 Crypto Hourly · {now} CST</b>", ""]
    for s in snapshots:
        out.append(format_snapshot_line(s))
        if s["symbol"] in alerts_by_symbol:
            out.append(format_alert_detail(s, alerts_by_symbol[s["symbol"]]))
    if llm_text:
        out.extend(["", "<i>🤖 解读</i>", tg.esc(llm_text)])
    return "\n".join(out)


def main() -> None:
    try:
        tickers = data.get_multi_ticker(config.SYMBOLS, tsym="USDT")
    except Exception as e:
        print(f"ticker fetch failed: {e}")
        return

    funding = data.get_funding_rates_pct(config.SYMBOLS)

    snapshots: list[dict] = []
    alerts_by_symbol: dict[str, list[str]] = {}

    for sym in config.SYMBOLS:
        if sym not in tickers:
            print(f"[{sym}] no ticker data, skip")
            continue
        try:
            s = build_snapshot(sym, tickers[sym], funding.get(sym))
            snapshots.append(s)
            triggered = alerts.evaluate(s)
            if triggered:
                alerts_by_symbol[sym] = triggered
        except Exception as e:
            print(f"[{sym}] error: {e}")

    if not snapshots:
        print("No snapshots, nothing to send.")
        return

    if config.QUIET_MODE and not alerts_by_symbol and not config.FORCE_SEND:
        print("Quiet mode + no alerts; skip send.")
        return

    llm_text = ""
    if alerts_by_symbol:
        llm_text = llm.interpret(build_llm_prompt(snapshots, alerts_by_symbol))

    msg = build_message(snapshots, alerts_by_symbol, llm_text)
    print(msg)
    tg.send(msg)


if __name__ == "__main__":
    main()
