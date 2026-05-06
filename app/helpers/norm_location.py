from geopy.geocoders import Nominatim
from functools import lru_cache

geolocator = Nominatim(user_agent="hiremind-rag")

@lru_cache(maxsize=512)   # cache lookups — same city will hit multiple times
def geocode_city(city: str) -> dict:
    try:
        location = geolocator.geocode(
            f"{city}, India",
            addressdetails=True,
            language="en"
        )
        if not location:
            return {"city": city, "state": None, "source": "geocode_miss"}
        
        addr = location.raw["address"]
        return {
            "city":     addr.get("city") or addr.get("town") or city,
            "state":    addr.get("state"),
            "country":  addr.get("country_code", "").upper(),
            "source":   "geocode"
        }
    except Exception:
        return {"city": city, "state": None, "source": "geocode_error"}


# Examples
# print(geocode_city("Dehradun"))     # → {city: "Chennai", state: "Tamil Nadu", ...}
# print(geocode_city("Chattarpur"))     # → {city: "Noida",   state: "Uttar Pradesh", ...}
# print(geocode_city("Trivandrum")) # → {city: "Thiruvananthapuram", state: "Kerala", ...}
# print(geocode_city("Vizag")) # → {city: "Visakhapatnam",      state: "Andhra Pradesh", ...}

# print(geocode_city("Asansol")) # → {city: "UnknownCity", state: None, source: "geocode_miss"}

# print(geocode_city("Hajipur"))
# print(geocode_city("Mira Bhayander")) 