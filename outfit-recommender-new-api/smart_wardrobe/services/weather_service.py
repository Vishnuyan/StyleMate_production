import requests

API_KEY = "c55dc9ca73704ce2d059fef558961d66"

def get_location_by_ip():
    """Auto-detect user location using IP"""
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        if data["status"] == "success":
            return data["lat"], data["lon"], data["city"]
    except:
        pass
    return None, None, "Unknown"

def get_weather_by_coords(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    return response.json()

def get_weather_by_city(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    return response.json()

def get_weather_context(city=None):
    """Returns a string describing the weather for AI context"""
    if city:
        data = get_weather_by_city(city)
    else:
        lat, lon, city = get_location_by_ip()
        if lat and lon:
            data = get_weather_by_coords(lat, lon)
        else:
            return "mild weather"

    try:
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        
        if temp < 10:
            status = "cold"
        elif temp > 25:
            status = "hot"
        else:
            status = "moderate"
            
        return f"{status} weather, {temp} degrees, {desc}"
    except:
        return "mild weather"