import requests
import json
import asyncio
import os
import mcp.types as types
from geopy.geocoders import Nominatim
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_FILE = os.path.abspath(
    os.path.join(BASE_DIR, "..", "processed", "all_stations.json")
)


# Find start and end cities coordinates
def get_counrty_coordinates(city_name):
    geolocator = Nominatim(user_agent="ev_charge_stations_filter_v1")
    location = geolocator.geocode(f"{city_name}, Türkiye")
    if location:
        return (location.latitude, location.longitude)
    else:
        return None


def get_route_bbox_from_api(start, end):
    coords_str = f"{start[1]},{start[0]};{end[1]},{end[0]}"

    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson&alternatives=true"

    try:
        response = requests.get(url, timeout=3)
        data = response.json()

        if data["code"] != "Ok":
            return None

        all_points = []
        for route in data["routes"]:
            all_points.extend(route["geometry"]["coordinates"])

        lons = [p[0] for p in all_points]
        lats = [p[1] for p in all_points]

        # Margins to ensure coverage
        lon_margin = 0.172
        lat_margin = 0.135

        # Calculate bounding box with a small margin
        bbox = {
            "min_lon": min(lons) - lon_margin,
            "min_lat": min(lats) - lat_margin,
            "max_lon": max(lons) + lon_margin,
            "max_lat": max(lats) + lat_margin,
        }

        return bbox
    except Exception as e:
        print(f"Error fetching route data: {e}")
        return None


# Check stations and filter
def filter_stations_logic(waypoints: list[str]):
    # Her şehrin koordinatını al
    coords = []
    for city in waypoints:
        coord = get_counrty_coordinates(city)
        if not coord:
            print(f"Bulunamadı: {city}")
            continue
        coords.append((city, coord))

    if len(coords) < 2:
        return json.dumps([])

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        all_stations = json.load(f)

    filtered = {}  # deduplikasyon için dict

    # Her iki şehir arası için ayrı bbox
    for i in range(len(coords) - 1):
        city_a, start = coords[i]
        city_b, end = coords[i + 1]

        bbox = get_route_bbox_from_api(start, end)
        if not bbox:
            print(f"Rota alınamadı: {city_a} → {city_b}")
            continue

        print(f"{city_a} → {city_b} taranıyor...")

        for station in all_stations:
            lat = station.get("latitude")
            lon = station.get("longitude")
            if lat is None or lon is None:
                continue

            if (
                bbox["min_lat"] <= lat <= bbox["max_lat"]
                and bbox["min_lon"] <= lon <= bbox["max_lon"]
            ):
                key = station.get("name") or f"{lat},{lon}"
                filtered[key] = station

    return json.dumps(list(filtered.values()), ensure_ascii=False)


# --- MCP Server to save filtered stations ---

server = Server("ev-route-planner")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_stations_on_route",
            description="Verilen iki şehir arasındaki rotada bulunan şarj istasyonlarını listeler.",
            inputSchema={
                "type": "object",
                "properties": {
                    "waypoints": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Sıralı durak listesi (Örn: ['Isparta', 'Antalya', 'Ankara'])",
                    }
                },
                "required": ["waypoints"],
            },
        )
    ]


@server.call_tool()
async def handle_call_tool(name, arguments):
    if name == "get_stations_on_route":
        waypoints = arguments.get("waypoints", [])

        result_json = filter_stations_logic(waypoints)

        stations = json.loads(result_json)
        print(f"✅ {len(waypoints)} durak, {len(stations)} istasyon bulundu.")

        return [types.TextContent(type="text", text=result_json)]
    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ev-route-planner",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
