def rsi(closes: list[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return float("nan")
    gains: list[float] = []
    losses: list[float] = []
    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


def sma(values: list[float], period: int) -> float:
    if len(values) < period:
        return float("nan")
    return sum(values[-period:]) / period


def pct_change(now: float, then: float) -> float:
    if then == 0:
        return 0.0
    return (now - then) / then * 100
