import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather_by_location(city: str, state: str = None, country: str = "IN") -> dict:
    """Fetch current weather for a given location"""
    location_query = f"{city},{country}"
    if state:
        location_query = f"{city},{state},{country}"
    
    params = {
        "q": location_query,
        "appid": API_KEY,
        "units": "metric"  # Celsius
    }
    
    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        raise Exception(f"Weather API failed: {response.text}")
    
    data = response.json()
    
    # Extract precipitation data (rain volume in mm for the last hour)
    rain_data = data.get("rain", {})
    rain_1h = rain_data.get("1h", 0)  # Rain in mm for last 1 hour
    
    weather_info = {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_speed": data["wind"]["speed"],
        "description": data["weather"][0]["description"],
        "rain_1h": rain_1h,  # Recent rainfall in mm
        "rain_3h": rain_data.get("3h", 0),  # Rain in mm for last 3 hours
        "clouds": data["clouds"]["all"]  # Cloud coverage percentage
    }
    
    return weather_info

def get_weather(city: str, state: str = None, country: str = "IN") -> dict:
    """Legacy function for backward compatibility"""
    return get_weather_by_location(city, state, country)

def generate_farm_alerts(weather_info: dict, farm: dict) -> dict:
    """
    Generate comprehensive farm management alerts based on weather data.

    Parameters:
        weather_info: dict with keys temperature, humidity, pressure, wind_speed, description
        farm: dict with keys soil_moisture (0-100%), crop_type, farm_size, recent_rainfall

    Returns:
        dict: {"irrigation": str, "pest_alert": str, "general_tips": str, "harvest_tips": str, "fertilizer_tips": str, "crop_health": str}
    """
    alerts = {
        "irrigation": None, 
        "pest_alert": None, 
        "general_tips": None,
        "harvest_tips": None,
        "fertilizer_tips": None,
        "crop_health": None
    }

    temp = weather_info.get("temperature")
    humidity = weather_info.get("humidity")
    pressure = weather_info.get("pressure", 1013)
    wind_speed = weather_info.get("wind_speed")
    description = weather_info.get("description", "").lower()
    
    # Use actual rainfall data from weather API
    rain_1h = weather_info.get("rain_1h", 0)  # Rain in last 1 hour
    rain_3h = weather_info.get("rain_3h", 0)  # Rain in last 3 hours
    clouds = weather_info.get("clouds", 0)    # Cloud coverage

    soil_moisture = farm.get("soil_moisture", 50)
    crop_type = farm.get("crop_type", "generic")
    # Use actual rainfall data instead of manual input
    recent_rainfall = max(rain_1h, rain_3h)  # Use the higher of 1h or 3h rainfall
    farm_size = farm.get("farm_size", "medium")

    # -------- IRRIGATION ALERTS --------
    if temp > 40 and humidity < 30:
        alerts["irrigation"] = "🔥 Extreme heat & drought: Emergency irrigation needed! Water twice daily."
    elif temp > 35 and humidity < 35:
        alerts["irrigation"] = "⚠️ Hot & dry: Irrigation highly recommended! Water in early morning."
    elif soil_moisture < 20:
        alerts["irrigation"] = "🚨 Critical: Soil moisture extremely low! Irrigate immediately."
    elif soil_moisture < 30:
        alerts["irrigation"] = "💧 Soil moisture low: Start irrigation within 2 hours."
    elif recent_rainfall < 2 and humidity < 40 and temp > 30:
        alerts["irrigation"] = f"🌱 No recent rain ({recent_rainfall}mm) + high temp: Irrigation recommended."
    elif recent_rainfall > 15 and soil_moisture > 80:
        alerts["irrigation"] = f"⛔ Stop irrigation: Heavy rain ({recent_rainfall}mm) has waterlogged soil."
    elif recent_rainfall > 10:
        alerts["irrigation"] = f"🌧 Recent rain ({recent_rainfall}mm): Skip irrigation today, soil is moist."
    elif humidity > 90 and soil_moisture > 70:
        alerts["irrigation"] = "⛔ Skip irrigation: High humidity + adequate soil moisture."
    elif temp < 5:
        alerts["irrigation"] = "❄️ Cold weather: Delay irrigation to prevent root damage."
    elif rain_1h > 5:
        alerts["irrigation"] = f"🌧 Currently raining ({rain_1h}mm/h): No irrigation needed."
    else:
        alerts["irrigation"] = "💧 Irrigation not needed currently."

    # -------- PEST & DISEASE ALERTS --------
    if humidity > 85 and temp > 28:
        alerts["pest_alert"] = f"🐛 High pest activity for {crop_type}: Apply organic pesticides, inspect daily."
    elif humidity > 90 and temp < 22:
        alerts["pest_alert"] = "🦠 High fungal/bacterial risk: Apply fungicide, improve air circulation."
    elif recent_rainfall > 20 and humidity > 85:
        alerts["pest_alert"] = f"🌧 Heavy rain ({recent_rainfall}mm) + humidity: Perfect for fungal outbreak - preventive treatment needed."
    elif rain_1h > 10:
        alerts["pest_alert"] = f"🌧 Heavy current rain ({rain_1h}mm/h): High disease risk, check for waterlogging."
    elif temp > 35 and humidity > 70:
        alerts["pest_alert"] = "🔥 Heat stress + humidity: Monitor for pest damage, provide shade."
    elif wind_speed > 20 and humidity > 80:
        alerts["pest_alert"] = "💨 Wind + humidity: Check for wind-borne diseases, secure plants."
    elif temp < 15 and humidity > 85:
        alerts["pest_alert"] = "❄️ Cold + damp: Watch for root rot, improve drainage."
    elif crop_type.lower() in ["grapevine", "grapes"] and humidity > 70 and temp > 20:
        alerts["pest_alert"] = "🍇 Powdery mildew risk on grapevine: Consider fungicide applications."
    elif crop_type.lower() in ["rice", "paddy"] and humidity > 80 and temp > 25:
        alerts["pest_alert"] = "🌾 Rice blast risk: Monitor for leaf spots, apply preventive fungicide."
    elif recent_rainfall > 5 and clouds > 80:
        alerts["pest_alert"] = f"🌧 Rainy conditions ({recent_rainfall}mm): Monitor for water-borne diseases."
    else:
        alerts["pest_alert"] = "✅ Low pest risk today."

    # -------- HARVEST TIPS --------
    if temp > 30 and humidity < 40 and recent_rainfall < 2:
        alerts["harvest_tips"] = "🌾 Perfect harvest weather: Dry conditions ideal for grain crops."
    elif rain_1h > 5 or recent_rainfall > 10:
        alerts["harvest_tips"] = f"⛔ Avoid harvesting: Recent rain ({recent_rainfall}mm) can damage crops and reduce quality."
    elif "rain" in description or humidity > 80:
        alerts["harvest_tips"] = "⛔ Avoid harvesting: Wet conditions can damage crops and reduce quality."
    elif wind_speed > 15:
        alerts["harvest_tips"] = "💨 Windy conditions: Harvest carefully, secure equipment and crops."
    elif temp < 10:
        alerts["harvest_tips"] = "❄️ Cold weather: Harvest early morning, protect crops from frost."
    elif temp > 35:
        alerts["harvest_tips"] = "🔥 Hot weather: Harvest early morning or evening to avoid heat damage."
    elif pressure < 1000 and clouds > 70:
        alerts["harvest_tips"] = "🌪️ Low pressure + cloudy: Weather may change, consider delaying harvest."
    elif recent_rainfall > 5:
        alerts["harvest_tips"] = f"🌧 Recent rain ({recent_rainfall}mm): Wait for crops to dry before harvesting."
    else:
        alerts["harvest_tips"] = "🌱 Good conditions for harvesting today."

    # -------- FERTILIZER TIPS --------
    if recent_rainfall > 20:
        alerts["fertilizer_tips"] = f"🌧 Recent heavy rain ({recent_rainfall}mm): Wait 2-3 days before applying fertilizer to prevent runoff."
    elif rain_1h > 5:
        alerts["fertilizer_tips"] = f"🌧 Currently raining ({rain_1h}mm/h): Avoid fertilizer application, wait for rain to stop."
    elif temp > 35 and humidity < 40:
        alerts["fertilizer_tips"] = "🔥 Hot & dry: Avoid fertilizer application, focus on irrigation first."
    elif humidity > 85 and temp > 25:
        alerts["fertilizer_tips"] = "💧 High humidity: Good conditions for liquid fertilizer application."
    elif wind_speed > 15:
        alerts["fertilizer_tips"] = "💨 Windy conditions: Avoid fertilizer application to prevent drift."
    elif temp < 15:
        alerts["fertilizer_tips"] = "❄️ Cold weather: Fertilizer absorption will be slow, consider waiting."
    elif soil_moisture < 30:
        alerts["fertilizer_tips"] = "💧 Low soil moisture: Irrigate before applying fertilizer."
    elif recent_rainfall > 5 and recent_rainfall < 15:
        alerts["fertilizer_tips"] = f"🌧 Light rain ({recent_rainfall}mm): Good conditions for fertilizer application."
    else:
        alerts["fertilizer_tips"] = "🌱 Good conditions for fertilizer application today."

    # -------- CROP HEALTH MONITORING --------
    if temp > 40:
        alerts["crop_health"] = "🔥 Extreme heat stress: Provide shade, increase irrigation, monitor wilting."
    elif temp < 5:
        alerts["crop_health"] = "❄️ Frost risk: Cover sensitive crops, consider frost protection measures."
    elif humidity > 95:
        alerts["crop_health"] = "💧 Excessive humidity: Risk of mold, improve ventilation, check for diseases."
    elif pressure < 1000 and "storm" in description:
        alerts["crop_health"] = "⛈ Storm approaching: Secure crops, check drainage, prepare for damage."
    elif wind_speed > 25:
        alerts["crop_health"] = "💨 Strong winds: Check for wind damage, secure tall crops, protect young plants."
    elif temp > 30 and humidity < 30:
        alerts["crop_health"] = "🌵 Drought stress: Monitor leaf wilting, increase watering frequency."
    elif temp > 35 and humidity > 70:
        alerts["crop_health"] = "🔥 Heat + humidity stress: Provide shade, improve air circulation."
    else:
        alerts["crop_health"] = "🌱 Crops are healthy under current conditions."

    # -------- GENERAL FARMING TIPS --------
    if "storm" in description or "heavy rain" in description:
        alerts["general_tips"] = "⛈ Severe weather: Secure equipment, check drainage, protect sensitive crops."
    elif wind_speed > 20:
        alerts["general_tips"] = "💨 Strong winds: Secure irrigation systems, check for wind damage."
    elif temp > 35 and humidity > 70:
        alerts["general_tips"] = "🔥 Hot & humid: Work early morning/evening, stay hydrated, provide crop shade."
    elif temp < 10:
        alerts["general_tips"] = "❄️ Cold weather: Protect sensitive crops, check for frost damage."
    elif pressure < 1000:
        alerts["general_tips"] = "🌪️ Low pressure system: Weather may change rapidly, monitor conditions."
    elif humidity > 90:
        alerts["general_tips"] = "💧 High humidity: Good for seed germination, but watch for diseases."
    elif temp > 30 and humidity < 40:
        alerts["general_tips"] = "🌵 Dry conditions: Focus on irrigation, consider mulching to retain moisture."
    else:
        alerts["general_tips"] = "🌱 Good farming conditions today."

    return alerts

