"""Technical indicators as pure functions over close prices (newest last).

Deliberately small: SMA / EMA / RSI only, ~30 lines of math, no TA-Lib.
All functions return None when there isn't enough data, never raise.
"""


def sma(closes: list[float], window: int) -> float | None:
    """Simple moving average of the last `window` closes."""
    if len(closes) < window or window <= 0:
        return None
    return sum(closes[-window:]) / window


def ema(closes: list[float], window: int) -> float | None:
    """Exponential moving average, seeded with the SMA of the first `window` closes."""
    if len(closes) < window or window <= 0:
        return None
    value = sum(closes[:window]) / window
    k = 2 / (window + 1)
    for close in closes[window:]:
        value = close * k + value * (1 - k)
    return value


def rsi(closes: list[float], period: int = 14) -> float | None:
    """Relative Strength Index (Wilder's smoothing). 100 when there are no losses."""
    if len(closes) < period + 1 or period <= 0:
        return None
    gains: list[float] = []
    losses: list[float] = []
    for prev, curr in zip(closes[:-1], closes[1:]):
        delta = curr - prev
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for gain, loss in zip(gains[period:], losses[period:]):
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)
