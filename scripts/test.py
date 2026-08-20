"""
GraphHopper ile rota bulma testi
==================================

YENİ YÖNTEM: Tüm waypoint'ler (şehir/istasyon konumları) tek bir HTTP
isteğinde gönderiliyor, elevation=true ile yükseklik profili de aynı
cevapta geliyor.

ESKİ YÖNTEM (karşılaştırma için): Ardışık her nokta çifti için ayrı ayrı
istek atılıyor (station_server.py'deki eski OSRM mantığının simülasyonu).

"""

import os
import sys
import json
import time
import math
import requests

try:
    from dotenv import load_dotenv

    load_dotenv()  # proje kökündeki .env dosyasını okur
except ImportError:
    pass  # python-dotenv kurulu değilse export edilmiş env var'a düşer

API_KEY = os.environ.get("GRAPHHOPPER_API_KEY")
BASE_URL = "https://graphhopper.com/api/1/route"

if not API_KEY:
    print("HATA: GRAPHHOPPER_API_KEY ortam değişkeni tanımlı değil.")
    print('Şunu çalıştır: export GRAPHHOPPER_API_KEY="senin-key-in"')
    sys.exit(1)

# ---------------------------------------------------------------------------
# 1) TEST VERİSİ — kendi istasyon JSON'undan yükleniyor
# ---------------------------------------------------------------------------
# İstasyon JSON dosyanın yolu. Proje kökünden çalıştırıyorsan göreli yol
# yeterli, ya da tam yol ver.
STATIONS_JSON_PATH = "data/stations.json"  # <-- kendi dosya yoluna göre düzelt

# Rota üzerinde sırayla kullanmak istediğin istasyonların "İstasyon No"
# değerleri. Sıra önemli: ilk eleman başlangıç, son eleman hedef kabul edilir.
WAYPOINT_STATION_IDS = [
    "ŞRJ/9055",
    "ŞRJ/9056",
    "ŞRJ/2796",
    "ŞRJ/2957",
    # ... rota üzerinde geçmek istediğin diğer istasyon no'larını ekle
]


def load_waypoints_from_json(json_path, station_ids):
    """İstasyon JSON'unu okuyup, verilen 'İstasyon No' sırasına göre
    (lat, lon) tuple listesi döndürür."""
    with open(json_path, "r", encoding="utf-8") as f:
        stations = json.load(f)

    by_id = {s["İstasyon No"]: s for s in stations}

    waypoints = []
    for sid in station_ids:
        station = by_id.get(sid)
        if station is None:
            raise KeyError(
                f"'{sid}' JSON içinde bulunamadı — İstasyon No'yu kontrol et."
            )
        lat = station["Enlem"]
        lon = station["Boylam"]
        waypoints.append((lat, lon))

    return waypoints


WAYPOINTS = load_waypoints_from_json(STATIONS_JSON_PATH, WAYPOINT_STATION_IDS)


# ---------------------------------------------------------------------------
# 2) YENİ YÖNTEM: tek istek, çoklu waypoint, elevation dahil
# ---------------------------------------------------------------------------
def get_route_single_request(waypoints):
    """Tüm noktaları tek seferde GraphHopper /route'a gönderir."""
    params = [("point", f"{lat},{lon}") for lat, lon in waypoints]
    params += [
        ("profile", "car"),
        ("elevation", "true"),
        ("points_encoded", "false"),
        ("key", API_KEY),
    ]

    t0 = time.perf_counter()
    resp = requests.get(BASE_URL, params=params, timeout=30)
    elapsed = time.perf_counter() - t0

    resp.raise_for_status()
    data = resp.json()

    path = data["paths"][0]
    points = path["points"]["coordinates"]  # [lon, lat, elevation] listesi

    return {
        "distance_m": path["distance"],
        "time_ms": path["time"],
        "points": points,  # [ [lon, lat, elev], ... ]
        "request_count": 1,
        "wall_time_s": elapsed,
    }


# ---------------------------------------------------------------------------
# 3) ESKİ YÖNTEM (kıyaslama): her ardışık çift için ayrı istek
# ---------------------------------------------------------------------------
def get_route_pairwise(waypoints):
    """Eski mantığın simülasyonu: her komşu çift ayrı sorgu."""
    total_distance = 0.0
    total_time_ms = 0
    all_points = []
    request_count = 0

    t0 = time.perf_counter()
    for i in range(len(waypoints) - 1):
        a, b = waypoints[i], waypoints[i + 1]
        params = [
            ("point", f"{a[0]},{a[1]}"),
            ("point", f"{b[0]},{b[1]}"),
            ("profile", "car"),
            ("elevation", "true"),
            ("points_encoded", "false"),
            ("key", API_KEY),
        ]
        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        path = data["paths"][0]

        total_distance += path["distance"]
        total_time_ms += path["time"]
        all_points.extend(path["points"]["coordinates"])
        request_count += 1
    elapsed = time.perf_counter() - t0

    return {
        "distance_m": total_distance,
        "time_ms": total_time_ms,
        "points": all_points,
        "request_count": request_count,
        "wall_time_s": elapsed,
    }


# ---------------------------------------------------------------------------
# 4) Elevation profilinden eğim (segment) hesabı
# ---------------------------------------------------------------------------
def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(a))


def build_segments(points, step_km=1.0):
    """[lon, lat, elev] noktalarından yaklaşık step_km aralıklarla
    segment listesi çıkarır: mesafe (m), yükseklik farkı (m), eğim açısı (derece)."""
    segments = []
    acc_dist = 0.0
    last_lon, last_lat, last_elev = points[0]
    seg_start_elev = last_elev

    for lon, lat, elev in points[1:]:
        d = haversine_m(last_lat, last_lon, lat, lon)
        acc_dist += d
        last_lon, last_lat = lon, lat

        if acc_dist >= step_km * 1000:
            dh = elev - seg_start_elev
            theta_deg = math.degrees(math.atan2(dh, acc_dist)) if acc_dist > 0 else 0.0
            segments.append(
                {
                    "distance_m": acc_dist,
                    "delta_elev_m": dh,
                    "grade_deg": theta_deg,
                }
            )
            acc_dist = 0.0
            seg_start_elev = elev

    return segments


# ---------------------------------------------------------------------------
# 5) Çalıştır ve kıyasla
# ---------------------------------------------------------------------------
def main():
    print("== YENİ YÖNTEM: tek istek, çoklu waypoint ==")
    new_result = get_route_single_request(WAYPOINTS)
    print(f"  İstek sayısı : {new_result['request_count']}")
    print(f"  Toplam süre  : {new_result['wall_time_s']:.3f} sn (network dahil)")
    print(f"  Mesafe       : {new_result['distance_m'] / 1000:.1f} km")
    print(f"  Tahmini süre : {new_result['time_ms'] / 60000:.1f} dk")
    print(f"  Nokta sayısı : {len(new_result['points'])}")

    segments = build_segments(new_result["points"], step_km=1.0)
    print(f"  Segment sayısı (1km aralık): {len(segments)}")
    if segments:
        print("  İlk 3 segment örneği:")
        for s in segments[:3]:
            print(
                f"    mesafe={s['distance_m']:.0f}m  "
                f"Δh={s['delta_elev_m']:.1f}m  "
                f"eğim={s['grade_deg']:.2f}°"
            )

    print("\n== ESKİ YÖNTEM: her çift için ayrı istek ==")
    old_result = get_route_pairwise(WAYPOINTS)
    print(f"  İstek sayısı : {old_result['request_count']}")
    print(f"  Toplam süre  : {old_result['wall_time_s']:.3f} sn (network dahil)")
    print(f"  Mesafe       : {old_result['distance_m'] / 1000:.1f} km")

    print("\n== KIYAS ==")
    print(
        f"  İstek sayısı farkı : {old_result['request_count']} -> {new_result['request_count']}"
    )
    speedup = (
        old_result["wall_time_s"] / new_result["wall_time_s"]
        if new_result["wall_time_s"]
        else float("inf")
    )
    print(f"  Hız kazancı         : {speedup:.2f}x")
    dist_diff = abs(old_result["distance_m"] - new_result["distance_m"])
    print(
        f"  Mesafe tutarlılığı  : fark {dist_diff:.0f} m "
        f"({'aynı rota' if dist_diff < 100 else 'rotalar farklı olabilir'})"
    )


if __name__ == "__main__":
    main()
