import json
import os

_STATIONS_JSON_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "stations.json"
)
_SOCKET_MAP: dict | None = None


def get_socket_map() -> dict:
    """
    stations.json'ı bir kez okuyup cache'ler.
    Döndürdüğü yapı: { "SKT/9055": { "station_name": "...", "address": "..." }, ... }
    """
    global _SOCKET_MAP
    if _SOCKET_MAP is not None:
        return _SOCKET_MAP

    try:
        with open(_STATIONS_JSON_PATH, encoding="utf-8") as f:
            stations: list = json.load(f)
    except FileNotFoundError:
        print(f"⚠️  stations.json bulunamadı: {_STATIONS_JSON_PATH}")
        _SOCKET_MAP = {}
        return _SOCKET_MAP

    _SOCKET_MAP = {}
    for station in stations:
        for socket in station.get("soketler", []):
            socket_no = socket.get("no", "")
            if socket_no:
                _SOCKET_MAP[socket_no] = {
                    "station_name": station.get("İstasyon Adı", "Bilinmeyen İstasyon"),
                    "address": station.get("Adres", ""),
                }

    print(f"✅ {len(_SOCKET_MAP)} soket yüklendi (stations.json)")
    return _SOCKET_MAP


def get_station_info(socket_no: str) -> dict:
    """
    Tek bir soket için istasyon adı ve adres döner.
    Bulunamazsa varsayılan değerler döner.
    """
    return get_socket_map().get(
        socket_no,
        {
            "station_name": "Bilinmeyen İstasyon",
            "address": "",
        },
    )
