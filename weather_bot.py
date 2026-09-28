import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# --- НАСТРОЙКИ TELEGRAM ---
TELEGRAM_TOKEN = "8847922404:AAGfmnFQXE-0S3uhOCr17HUVqnY2GM4njeI"
TELEGRAM_CHAT_ID = "444451877"
# --------------------------

LAT, LON = 55.4490, 65.3434  # Координаты Кургана
TIMEZONE = "Asia/Yekaterinburg"

# 1. Определяем текущее время в Кургане
tz = ZoneInfo(TIMEZONE)
now_local = datetime.now(tz)
current_hour = now_local.hour
current_date_str = now_local.strftime("%Y-%m-%d")

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": LAT,
    "longitude": LON,
    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
    "hourly": "temperature_2m,precipitation_probability,weather_code",
    "timezone": TIMEZONE,
    "forecast_days": 3
}

try:
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    current = data["current"]
    hourly = data["hourly"]

    weather_codes = {
        0: "Ясно", 1: "Преимущественно ясно", 2: "Переменная облачность", 3: "Пасмурно",
        45: "Туман", 48: "Изморозь", 51: "Легкая морось", 53: "Морось", 55: "Сильная морось",
        61: "Небольшой дождь", 63: "Дождь", 65: "Сильный дождь",
        71: "Небольшой снег", 73: "Снег", 75: "Сильный снег",
        80: "Ливень", 81: "Сильный ливень", 82: "Очень сильный ливень",
        95: "Гроза", 96: "Гроза с градом", 99: "Сильная гроза с градом"
    }

    # 2. Формируем блок текущей погоды
    weather_desc_now = weather_codes.get(current["weather_code"], "Неизвестно")
    message = (
        f"🌤 Погода в Кургане сейчас:\n"
        f"🌡 {current['temperature_2m']}°C (ощущается как {current['apparent_temperature']}°C)\n"
        f"💧 Влажность: {current['relative_humidity_2m']}%\n"
        f"💨 Ветер: {current['wind_speed_10m']} м/с\n"
        f"☁️ {weather_desc_now}\n\n"
    )

    # 3. Динамический блок прогноза
    forecast_lines = []

    if current_hour < 16:
        forecast_lines.append("⏳ Прогноз на сегодня:")
        for i, t in enumerate(hourly["time"]):
            if t.startswith(current_date_str):
                parts = t.split("T")
                if len(parts) > 1:
                    time_str = parts[1]
                    hour = int(time_str.split(":")[0])
                    if hour > current_hour:
                        temp = hourly["temperature_2m"][i]
                        precip_prob = hourly["precipitation_probability"][i]
                        code = hourly["weather_code"][i]
                        desc = weather_codes.get(code, "")
                        forecast_lines.append(f"{time_str}: {temp}°C, {desc} (осадки {precip_prob}%)")
    else:
        forecast_lines.append("🌅 Прогноз на ЗАВТРАШНЕЕ УТРО:")
        for i, t in enumerate(hourly["time"]):
            if not t.startswith(current_date_str):
                parts = t.split("T")
                if len(parts) > 1:
                    time_str = parts[1]
                    hour = int(time_str.split(":")[0])
                    if 6 <= hour <= 12:
                        temp = hourly["temperature_2m"][i]
                        precip_prob = hourly["precipitation_probability"][i]
                        code = hourly["weather_code"][i]
                        desc = weather_codes.get(code, "")
                        forecast_lines.append(f"{time_str}: {temp}°C, {desc} (осадки {precip_prob}%)")

    if len(forecast_lines) > 1:
        message += "\n".join(forecast_lines)
    else:
        message += "Не удалось загрузить детальный прогноз."

    # 4. Отправка в Telegram
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    tg_response = requests.post(tg_url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=15)
    tg_response.raise_for_status()
    print("Уведомление отправлено успешно!")

except Exception as e:
    print(f"Произошла ошибка: {e}")
    raise e



