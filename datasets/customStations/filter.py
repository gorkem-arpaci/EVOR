import json

# Save filtered stations location
input_file = "../merged_stations.json"
output_file = "./isparta-antalya.json"

# Locations of the two cities to be traveled to
MIN_LAT = 36.70
MAX_LAT = 38.00
MIN_LON = 30.10
MAX_LON = 31.60

# coordinates list = (minlon, minlat), (maxlon, minlat), (maxlon, maxlat), (minlon, maxlat), (minlon, minlat)

# Isparta-İzmir
# MIN_LAT = 37.40
# MAX_LAT = 38.80
# MIN_LON = 26.90
# MAX_LON = 31.00

# Isparta - İstanbul
# MIN_LAT = 37.40
# MAX_LAT = 41.60
# MIN_LON = 28.50
# MAX_LON = 31.00

# Isparta - Ankara
# MIN_LAT = 37.40
# MAX_LAT = 40.50
# MIN_LON = 30.00
# MAX_LON = 33.50


def filter_stations():
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        filtered_data = []

        for istasyon in data:
            lat = istasyon.get("latitude")
            lon = istasyon.get("longitude")

            if (MIN_LAT <= lat <= MAX_LAT) and (MIN_LON <= lon <= MAX_LON):
                filtered_data.append(istasyon)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=4)

        print(f"Proccess done! Saved {len(filtered_data)} datas to {output_file}.")

    except FileNotFoundError:
        print("File not found. Check file name.")


if __name__ == "__main__":
    filter_stations()
