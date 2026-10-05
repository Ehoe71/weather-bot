import requests

# ==============================================================
# НАСТРОЙКИ TELEGRAM
# ==============================================================
TELEGRAM_TOKEN = "8847922404:AAFIsHxn6QDgfF6ZqWdPNZC7_Jm5sZZLcII"
TELEGRAM_CHAT_ID = "444451877"

# ==============================================================
# МОНЕТЫ
# ==============================================================
COINS = [
    ("BTC", "Bitcoin"),
    ("ETH", "Ethereum"),
    ("SOL", "Solana"),
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
        print(f"⚠️ USD/RUB: {e}")
        return 95.0

# ==============================================================
# ИСТОЧНИК 1: KRAKEN (работает из GitHub Actions)
# ==============================================================
def get_prices_kraken():
    result = {}
    for symbol, name in COINS:
        pair = f"{symbol}USD"
        url = "https://api.kraken.com/0/public/Ticker"
        r = requests.get(url, params={"pair": pair}, timeout=15)
        r.raise_for_status()
        data = r.json()
        if data.get("error"):
            raise RuntimeError(f"Kraken: {data['error']}")
        # Ключ в результате может быть "XXBTZUSD" или "XBTUSD" — берём первый
        key = list(data["result"].keys())[0]
        price = float(data["result"][key]["c"][0])
        result[symbol] = {
            "name": name,
            "usd": price,
            "change": 0.0,  # Kraken Ticker не даёт % за 24ч напрямую
        }
    return result

# ==============================================================
# ИСТОЧНИК 2: COINCAP
# ==============================================================
def get_prices_coincap():
    result = {}
    mapping = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana"}
    for symbol, name in COINS:
        cid = mapping[symbol]
        url = f"https://api.coincap.io/v2/assets/{cid}"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        d = r.json()["data"]
        result[symbol] = {
            "name": name,
            "usd": float(d["priceUsd"]),
            "change": float(d.get("changePercent24Hr", 0)),
        }
    return result

# ==============================================================
# ИСТОЧНИК 3: COINGECKO (резерв)
# ==============================================================
def get_prices_coingecko():
    ids = ",".join({"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana"}[s]
                   for s, _ in COINS)
    url = "https://api.coingecko.com/api/v3/simple/price"
    r = requests.get(url, params={
        "ids": ids,
        "vs_currencies": "usd",
        "include_24hr_change": "true",
    }, timeout=15)
    r.raise_for_status()
    data = r.json()
    mapping = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana"}
    result = {}
    for symbol, name in COINS:
        cg_id = mapping[symbol]
        if cg_id in data:
            result[symbol] = {
                "name": name,
                "usd": float(data[cg_id]["usd"]),
                "change": float(data[cg_id].get("usd_24h_change", 0)),
            }
    return result

# ==============================================================
# ОСНОВНАЯ ЛОГИКА
# ==============================================================
def main():
    usd_rub = get_usd_rub()
    print(f"Курс USD/RUB: {usd_rub:.2f}")

    prices = None
    source = None

    for func, name in [(get_prices_kraken,    "Kraken"),
                       (get_prices_coincap,   "CoinCap"),
                       (get_prices_coingecko, "CoinGecko")]:
        try:
            print(f"[Crypto] Пробую {name}...")
            prices = func()
            source = name
            print(f"[Crypto] {name} OK")
            break
        except Exception as e:
            print(f"[Crypto] {name} упал: {e}")

    if not prices:
        raise RuntimeError("Все источники недоступны")

    message = f"📊 Курс криптовалют (источник: {source}):\n\n"
    for symbol, _ in COINS:
        if symbol not in prices:
            continue
        p = prices[symbol]
        usd = p["usd"]
        rub = usd * usd_rub
        change = p["change"]

        if change > 0:
            emoji, sign = "📈", "+"
        elif change < 0:
            emoji, sign = "📉", ""
        else:
            emoji, sign = "▪️", ""

        message += (
            f"{emoji} {p['name']}:\n"
            f"   ${usd:,.2f} | {rub:,.0f} ₽\n"
        )
        if change != 0:
            message += f"   Изм. за 24ч: {sign}{change:.2f}%\n"
        message += "\n"

    # Отправка
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    r = requests.post(tg_url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }, timeout=15)
    print(f"[TG] HTTP: {r.status_code}, ответ: {r.text[:200]}")
    r.raise_for_status()
    if not r.json().get("ok"):
        raise RuntimeError(f"Telegram: {r.json().get('description')}")
    print("✅ Курс отправлен!")

if __name__ == "__main__":
    main()
