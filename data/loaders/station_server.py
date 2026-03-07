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
    os.path.join(BASE_DIR, "..", "processed", "merged_stations.json")
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
def filter_stations_logic(start_city, end_city):
    start = get_counrty_coordinates(start_city)
    end = get_counrty_coordinates(end_city)
    print(f"Json dosyası aranıyor: {INPUT_FILE}")
    print(f"Dosya mevcut mu? {'Evet' if os.path.exists(INPUT_FILE) else 'Hayır'}")

    if not start or not end:
        print("Could not find coordinates for the specified cities.")
        return

    bbox = get_route_bbox_from_api(start, end)

    if not bbox:
        print("Could not retrieve route data.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        stations = json.load(f)

    filtered_stations = []

    for station in stations:
        lat = station.get("latitude")
        lon = station.get("longitude")

        if lat is None or lon is None:
            continue

        if (
            bbox["min_lat"] <= lat <= bbox["max_lat"]
            and bbox["min_lon"] <= lon <= bbox["max_lon"]
        ):
            filtered_stations.append(station)

    return json.dumps(filtered_stations, ensure_ascii=False)


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
                    "start_city": {
                        "type": "string",
                        "description": "Başlangıç şehri (Örn: Isparta)",
                    },
                    "end_city": {
                        "type": "string",
                        "description": "Bitiş şehri (Örn: İzmir)",
                    },
                },
                "required": ["start_city", "end_city"],
            },
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if name == "get_stations_on_route":
        start = arguments.get("start_city")
        end = arguments.get("end_city")

        result_json = filter_stations_logic(start, end)

        # Log
        stations = json.loads(result_json)
        print(f"Found {len(stations)} stations between {start} and {end}.")

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
