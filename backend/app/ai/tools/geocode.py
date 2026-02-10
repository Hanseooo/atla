from langchain.tools import tool
import httpx
from app.config import settings


@tool
async def geocode(query: str) -> str:
    """
    Geocode a location to get its latitude and longitude.

    Args:
        query (str): Location to geocode - can be a city, address,
                    place name, or landmark (e.g., "Manila",
                    "SM Mall of Asia", "Rizal Park", "123 Rizal St, Cebu").

    Returns:
        str: Coordinates in "latitude,longitude" format, or error message.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.geoapify.com/v1/geocode/search",
                params={
                    "text": query,
                    "format": "json",
                    "limit": 1,
                    "apiKey": settings.GEOAPIFY_API_KEY,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("features"):
                coords = data["features"][0]["geometry"]["coordinates"]
                return f"{coords[1]},{coords[0]}"
            return "error: location not found"

        except httpx.HTTPError as e:
            return f"error: HTTP request failed - {str(e)}"
        except (KeyError, IndexError) as e:
            return f"error: invalid response format - {str(e)}"
        except Exception as e:
            return f"error: {str(e)}"