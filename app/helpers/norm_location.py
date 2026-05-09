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
        addr_city = addr.get("city") or addr.get("town") or addr.get("village") or city
        addr_state = addr.get("state")
        if addr_city == "New Delhi" and not addr_state:
            addr_city = "Delhi"
            addr_state = "Delhi"
        elif addr_city == "Delhi" and not addr_state:
            addr_state = "Delhi"
        return {
            "city":     addr_city,
            "state":    addr_state,
            "country":  addr.get("country_code", "").upper(),
            "source":   "geocode"
        }
    except Exception:
        return {"city": city, "state": None, "source": "geocode_error"}


