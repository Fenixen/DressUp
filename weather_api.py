import requests

class WeatherService:
    """
    trida pro ziskani dat o pocasi (OpenWeatherMap)
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city, settings):
        """
        ziska aktualni pocasi pro dane mesto
        vrati slovnik s teplotou a popisem 
        """
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "cz"
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            temp = data["main"]["temp"]
            condition = data["weather"][0]["description"]

            return {
                "success": True,
                "temp": temp,
                "condition": condition,
                "season_type": self._determine_season(temp, settings)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def _determine_season(self, temp, settings):
        """
        pomocna metoda pro prevod teploty na kategorii
        """
        winter_limit = settings.get("winter_max", 10)
        summer_limit = settings.get("summer_min", 20)

        if temp < winter_limit:
            return "Zima"
        elif winter_limit <= temp < summer_limit:
            return "Jaro/Podzim"
        else:
            return "Leto"
