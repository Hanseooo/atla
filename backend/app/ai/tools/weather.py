from langchain.tools import tool
import httpx
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings


# OpenWeather API base URL
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"


def format_weather_description(weather_code: str) -> str:
    """Get text icon for weather condition."""
    weather_icons = {
        "clear sky": "[SUN]",
        "few clouds": "[CLOUDY]",
        "scattered clouds": "[CLOUDY]",
        "broken clouds": "[CLOUDY]",
        "shower rain": "[RAIN]",
        "rain": "[RAIN]",
        "thunderstorm": "[STORM]",
        "snow": "[SNOW]",
        "mist": "[FOG]",
        "fog": "[FOG]",
        "haze": "[FOG]",
    }
    
    code_lower = weather_code.lower()
    for key, icon in weather_icons.items():
        if key in code_lower:
            return icon
    return "[TEMP]"


def get_travel_recommendations(weather_data: dict) -> str:
    """Generate travel recommendations based on weather."""
    temp = weather_data.get("main", {}).get("temp", 0)
    weather_desc = weather_data.get("weather", [{}])[0].get("description", "").lower()
    
    recommendations = []
    
    # Temperature-based recommendations
    if temp > 35:
        recommendations.append("[HOT] Very hot - stay hydrated, use sunscreen, avoid midday sun")
    elif temp > 30:
        recommendations.append("[WARM] Warm weather - perfect for beach activities, bring sunscreen")
    elif temp > 25:
        recommendations.append("[PLEASANT] Pleasant temperature - great for outdoor activities")
    elif temp > 20:
        recommendations.append("[MILD] Mild weather - comfortable for sightseeing")
    else:
        recommendations.append("[COOL] Cool weather - bring a light jacket")
    
    # Weather condition recommendations
    if "rain" in weather_desc or "shower" in weather_desc:
        recommendations.append("[RAIN] Rain expected - pack an umbrella, consider indoor activities")
    elif "thunderstorm" in weather_desc:
        recommendations.append("[STORM] Thunderstorms - stay indoors, avoid water activities")
    elif "clear" in weather_desc or "sun" in weather_desc:
        recommendations.append("[CLEAR] Clear skies - excellent for outdoor adventures and photography")
    elif "cloud" in weather_desc:
        recommendations.append("[CLOUDY] Cloudy - good for sightseeing without harsh sun")
    elif "fog" in weather_desc or "mist" in weather_desc or "haze" in weather_desc:
        recommendations.append("[FOG] Reduced visibility - drive carefully, check flight schedules")
    
    return "\n".join(recommendations)


@tool
async def get_weather(
    location: str,
    date: Optional[str] = None,
    units: str = "metric",
) -> str:
    """
    Get weather forecast for a location using OpenWeather API.
    
    Only provides forecast data if the requested date is within 5 days from now.
    For dates beyond 5 days, returns current weather only.

    Args:
        location: City name (e.g., "Cebu", "Manila", "Boracay")
        date: Target date in YYYY-MM-DD format (optional). If not provided, returns current weather.
        units: Temperature units - "metric" (Celsius) or "imperial" (Fahrenheit). Default: "metric"

    Returns:
        Formatted markdown string with weather information including temperature, conditions,
        humidity, wind speed, and travel recommendations.
    """
    api_key = settings.OPENWEATHER_API_KEY
    
    if not api_key:
        return "[ERROR] Weather API key not configured"
    
    try:
        # Parse date if provided
        target_date = None
        if date:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return f"[ERROR] Invalid date format. Use YYYY-MM-DD (e.g., 2024-12-25)"
        
        # Calculate if date is within 5 days
        today = datetime.now()
        use_forecast = False
        
        if target_date:
            days_diff = (target_date - today).days
            if 0 <= days_diff <= 5:
                use_forecast = True
            elif days_diff < 0:
                return f"[ERROR] Cannot get weather for past dates: {date}"
        
        async with httpx.AsyncClient() as client:
            if use_forecast:
                # Get 5-day forecast
                response = await client.get(
                    f"{OPENWEATHER_BASE_URL}/forecast",
                    params={
                        "q": location,
                        "appid": api_key,
                        "units": units,
                        "cnt": 40,  # 5 days * 8 intervals per day
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                
                # Find forecast for target date
                target_forecasts = [
                    item for item in data.get("list", [])
                    if datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d") == date
                ]
                
                if not target_forecasts:
                    return f"[ERROR] No forecast data available for {date} in {location}"
                
                # Use midday forecast (around 12:00)
                midday_forecast = target_forecasts[len(target_forecasts) // 2]
                
                # Extract data
                weather = midday_forecast.get("weather", [{}])[0]
                main = midday_forecast.get("main", {})
                wind = midday_forecast.get("wind", {})
                
                temp_unit = "°C" if units == "metric" else "°F"
                wind_unit = "m/s" if units == "metric" else "mph"
                
                weather_icon = format_weather_description(weather.get("description", ""))
                
                lines = [
                    f"## {weather_icon} Weather Forecast for {location}",
                    f"**Date:** {date}",
                    "",
                    f"**Condition:** {weather.get('main', 'Unknown')} - {weather.get('description', 'No description')}",
                    f"**Temperature:** {main.get('temp', 'N/A')}{temp_unit}",
                    f"**Feels Like:** {main.get('feels_like', 'N/A')}{temp_unit}",
                    f"**High:** {main.get('temp_max', 'N/A')}{temp_unit} | **Low:** {main.get('temp_min', 'N/A')}{temp_unit}",
                    f"**Humidity:** {main.get('humidity', 'N/A')}%",
                    f"**Wind:** {wind.get('speed', 'N/A')} {wind_unit}",
                    "",
                    "### Travel Recommendations",
                    get_travel_recommendations(midday_forecast),
                    "",
                    f"Data from OpenWeather (forecast for {date})",
                ]
                
                return "\n".join(lines)
            
            else:
                # Get current weather
                response = await client.get(
                    f"{OPENWEATHER_BASE_URL}/weather",
                    params={
                        "q": location,
                        "appid": api_key,
                        "units": units,
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract data
                weather = data.get("weather", [{}])[0]
                main = data.get("main", {})
                wind = data.get("wind", {})
                
                temp_unit = "°C" if units == "metric" else "°F"
                wind_unit = "m/s" if units == "metric" else "mph"
                
                weather_icon = format_weather_description(weather.get("description", ""))
                
                lines = [
                    f"## {weather_icon} Current Weather in {location}",
                    "",
                    f"**Condition:** {weather.get('main', 'Unknown')} - {weather.get('description', 'No description')}",
                    f"**Temperature:** {main.get('temp', 'N/A')}{temp_unit}",
                    f"**Feels Like:** {main.get('feels_like', 'N/A')}{temp_unit}",
                    f"**High:** {main.get('temp_max', 'N/A')}{temp_unit} | **Low:** {main.get('temp_min', 'N/A')}{temp_unit}",
                    f"**Humidity:** {main.get('humidity', 'N/A')}%",
                    f"**Wind:** {wind.get('speed', 'N/A')} {wind_unit}",
                    "",
                    "### Travel Recommendations",
                    get_travel_recommendations(data),
                ]
                
                if target_date and (target_date - today).days > 5:
                    lines.append("")
                    lines.append(f"[NOTE] Forecast only available up to 5 days. Showing current weather.")
                    lines.append(f"   For {date}, check closer to your travel date.")
                
                lines.append("")
                lines.append("Data from OpenWeather")
                
                return "\n".join(lines)
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"[ERROR] Location not found: '{location}'"
        elif e.response.status_code == 401:
            return "[ERROR] Invalid weather API key"
        else:
            return f"[ERROR] Weather API error: {e.response.status_code}"
    except httpx.TimeoutException:
        return "[ERROR] Weather request timed out. Please try again."
    except Exception as e:
        return f"[ERROR] Weather error: {str(e)}"
