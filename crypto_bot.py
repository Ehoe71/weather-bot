import requests

# --- НАСТРОЙКИ TELEGRAM ---
TELEGRAM_TOKEN = "8847922404:AAGfmnFQXE-0S3uhOCr17HUVqnY2GM4njeI"        # <-- вставьте свой токен
TELEGRAM_CHAT_ID = "444451877"    # <-- вставьте свой Chat ID
# --------------------------

url = "https://api.coingecko.com/api/v3/simple/price"
params = {
    "ids": "bitcoin,ethereum,solana,dash",
    "vs_currencies": "usd"   # <-- только USD, чтобы API не капризничал
}

try:
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    btc = data["bitcoin"]["usd"]
    eth = data["ethereum"]["usd"]
    sol = data["solana"]["usd"]
    dash = data["dash"]["usd"]

    message = (
        f"💰 Курс криптовалют (USDT):\n\n"
        f"🟡 Bitcoin (BTC):  ${btc:,.0f}\n\n"
        f"🔵 Ethereum (ETH):  ${eth:,.0f}\n\n"
        f"🟣 Solana (SOL):  ${sol:,.2f}\n\n"
        f"🔷 Dash (DASH):  ${dash:,.2f}"
    )

    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(tg_url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=15)
    print("Уведомление отправлено успешно!")

except Exception as e:
    print(f"Ошибка: {e}")
    raise e
import requests


