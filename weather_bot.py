import requests

# --- ВАЖНО: ЗАМЕНИТЕ ЭТО НА ВАШ ТОПИК ИЗ NTFY ---
NTFY_TOPIC = "pogoda_kurgan_7m_2024" 
# ------------------------------------------------

LAT, LON = 55.4490, 65.3434  # Координаты Кургана
TIMEZONE = "Asia/Yekaterinburg"  # Часовой пояс Кургана (UTC+5)

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": LAT,
    "longitude": LON,
    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
    "timezone": TIMEZONE,
    "forecast_days": 1
}

try:
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    current = data["current"]
    
    weather_codes = {
        0: "Ясно", 1: "Преимущественно ясно", 2: "Переменная облачность", 3: "Пасмурно",
        45: "Туман", 48: "Изморозь", 51: "Легкая морось", 53: "Морось", 55: "Сильная морось",
        61: "Небольшой дождь", 63: "Дождь", 65: "Сильный дождь",
        71: "Небольшой снег", 73: "Снег", 75: "Сильный снег",
        80: "Ливень", 81: "Сильный ливень", 82: "Очень сильный ливень",
        95: "Гроза", 96: "Гроза с градом", 99: "Сильная гроза с градом"
    }
    weather_desc = weather_codes.get(current["weather_code"], "Неизвестно")
    
    message = (
        f"🌤 Погода в Кургане\n"
        f"🌡 Температура: {current['temperature_2m']}°C (ощущается как {current['apparent_temperature']}°C)\n"
        f"💧 Влажность: {current['relative_humidity_2m']}%\n"
        f"💨 Ветер: {current['wind_speed_10m']} м/с\n"
        f"☁️ {weather_desc}\n"
        f"🌧 Осадки: {current['precipitation']} мм"
    )
    
    ntfy_url = f"https://ntfy.sh/{NTFY_TOPIC}"
    headers = {
        "Title": "Погода в Кургане",
        "Priority": "default",
        "Tags": "cloud"
    }
    ntfy_response = requests.post(ntfy_url, data=message.encode('utf-8'), headers=headers, timeout=15)
    ntfy_response.raise_for_status()
    print("Уведомление отправлено успешно!")

except Exception as e:
    print(f"Ошибка: {e}")
