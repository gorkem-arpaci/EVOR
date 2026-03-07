import json
from geopy.geocoders import Nominatim

# --- AYARLAR ---
INPUT_FILE = "../data/processed/merged_stations.json"
OUTPUT_FILE = "dortgen_istasyonlar.json"
BUFFER = 0.2  # Derece cinsinden esneme payı (Yaklaşık 20km)

geolocator = Nominatim(user_agent="rota_hesaplayici_v3")


def get_coords(city_name):
    """Şehir ismini koordinata çevirir"""
    try:
        loc = geolocator.geocode(city_name)
        if loc:
            return (loc.latitude, loc.longitude)
    except:
        pass
    return None


def filter_with_segmented_boxes(route_cities):
    # 1. Şehirlerin koordinatlarını bul
    waypoints = []
    print("🌍 Koordinatlar alınıyor...")
    for city in route_cities:
        coord = get_coords(city)
        if coord:
            print(f"   📍 {city}: {coord}")
            waypoints.append(coord)

    if len(waypoints) < 2:
        print("❌ Yeterli şehir bilgisi yok.")
        return

    # 2. İstasyonları Yükle
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        all_stations = json.load(f)

    filtered_stations = {}  # Sözlük kullanıyoruz ki aynı istasyonu 2 kere eklemeyelim

    # 3. HER İKİ ŞEHİR ARASINA BİR DÖRTGEN ÇİZ
    for i in range(len(waypoints) - 1):
        # A Şehri ve B Şehri
        lat1, lon1 = waypoints[i]
        lat2, lon2 = waypoints[i + 1]

        # Dörtgenin sınırlarını belirle (Senin mantığın)
        # min() ve max() kullanarak yön fark etmeksizin doğru kutuyu çiziyoruz
        min_lat = min(lat1, lat2) - BUFFER
        max_lat = max(lat1, lat2) + BUFFER
        min_lon = min(lon1, lon2) - BUFFER
        max_lon = max(lon1, lon2) + BUFFER

        print(
            f"📦 Dörtgen {i + 1} taranıyor: {route_cities[i]} -> {route_cities[i + 1]}"
        )

        # 4. KLASİK FİLTRELEME (Senin Kodun)
        for istasyon in all_stations:
            lat = istasyon.get("latitude")
            lon = istasyon.get("longitude")
            name = istasyon.get("name")  # Benzersiz anahtar olarak ismi kullanıyoruz

            if lat is None or lon is None:
                continue

            # Veri string gelebilir diye float çevrimi
            lat = float(lat)
            lon = float(lon)

            # İşte senin sevdiğin basit mantık:
            if (min_lat <= lat <= max_lat) and (min_lon <= lon <= max_lon):
                filtered_stations[name] = istasyon

    # 5. Kaydet
    final_list = list(filtered_stations.values())
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=4)

    print("-" * 30)
    print(f"✅ İŞLEM TAMAM. Toplam {len(final_list)} istasyon bulundu.")
