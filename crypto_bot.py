import requests

# ==============================================================
# НАСТРОЙКИ TELEGRAM
# ==============================================================
TELEGRAM_TOKEN = "8847922404:AAFIsHxn6QDgfF6ZqWdPNZC7_Jm5sZZLcII"
TELEGRAM_CHAT_ID = "444451877"

# ==============================================================
# СПИСОК МОНЕТ
# ==============================================================
COINS = [
    ("BTCUSDT", "Bitcoin"),
    ("ETHUSDT", "Ethereum"),
    ("SOLUSDT", "Solana"),
]

# ==============================================================
# КУРС USD/RUB от ЦБ РФ
# ==============================================================
def get_usd_rub():
    try:
        r = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=15)
        r.raise_for_status()
        return float(r.json()["Valute"]["USD"]["Value"])
    except Exception as e:
        print(f"⚠️ Не удалось получить курс USD/RUB: {e}")
        return 95.0

# ==============================================================
# ЦЕНЫ С BINANCE (работает из GitHub Actions)
# ==============================================================
def get_prices_binance():
    result = {}
    url = "https://api.binance.com/api/v3/ticker/24hr"
    for symbol, name in COINS:
        r = requests.get(url, params={"symbol": symbol}, timeout=15)
        r.raise_for_status()
        d = r.json()
        result[symbol] = {
            "name": name,
            "usd": float(d["lastPrice"]),
            "change": float(d["priceChangePercent"]),
        }
    return result

# ==============================================================
# ОСНОВНАЯ ЛОГИКА
# ==============================================================
def main():
    usd_rub = get_usd_rub()
    print(f"Курс USD/RUB: {usd_rub:.2f}")

    prices = get_prices_binance()
    print(f"Получены цены: {list(prices.keys())}")

    message = "📊 Курс криптовалют:\n\n"
    for symbol, _ in COINS:
        if symbol not in prices:
            continue
        p = prices[symbol]
        usd = p["usd"]
        rub = usd * usd_rub
        change = p["change"]

        emoji = "📈" if change > 0 else "📉"
        sign = "+" if change > 0 else ""

        message += (
            f"{emoji} {p['name']}:\n"
            f"   ${usd:,.2f} | {rub:,.0f} ₽\n"
            f"   Изм. за 24ч: {sign}{change:.2f}%\n\n"
        )

    # Отправка в Telegram
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    r = requests.post(tg_url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }, timeout=15)
    r.raise_for_status()
    print("✅ Курс отправлен!")

if __name__ == "__main__":
    main()
