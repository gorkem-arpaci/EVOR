import json
from pathlib import Path

# Dosya yolları (gerekirse değiştir)
ESARJ_PATH = "./datasets/esarj_stations.json"
TRUGO_PATH = "./datasets/trugo_stations.json"
ZES_PATH = "./datasets/zes_stations.json"
OUT_PATH = "./datasets/merged_stations.json"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_esarj(esarj):
    results = []
    for item in esarj.get("data", []):
        results.append(
            {
                "provider": "ESARJ",
                "name": item.get("storeName"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "acConnectors": item.get("acConnectors", 0),
                "dcConnectors": item.get("dcConnectors", 0),
                "hpcConnectors": 0,
            }
        )
    return results


def normalize_trugo(trugo):
    results = []
    features = trugo.get("data", {}).get("stationList", {}).get("features", [])
    for feat in features:
        props = feat.get("properties", {})
        geom = feat.get("geometry", {})
        coords = geom.get("coordinates", [None, None])

        type_val = props.get("type", "")
        dc = 1 if isinstance(type_val, str) and type_val.upper().startswith("DC") else 0

        results.append(
            {
                "provider": "TRUGO",
                "name": props.get("locationName"),
                "latitude": coords[1],
                "longitude": coords[0],
                "acConnectors": 0,
                "dcConnectors": dc,
                "hpcConnectors": 0,
            }
        )
    return results


def normalize_zes(zes):
    results = []
    # Yeni format: { "totalCount": ..., "stationLocations": [ ... ] }
    station_list = zes.get("stationLocations", [])

    for item in station_list:
        results.append(
            {
                "provider": "ZES",
                "name": item.get("name"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "acConnectors": item.get("acConnectorCount", 0),
                "dcConnectors": item.get("dcConnectorCount", 0),
                "hpcConnectors": item.get("hpcConnectorCount", 0),
            }
        )
    return results


def main():
    esarj = load_json(ESARJ_PATH)
    trugo = load_json(TRUGO_PATH)
    zes = load_json(ZES_PATH)

    merged = normalize_esarj(esarj) + normalize_trugo(trugo) + normalize_zes(zes)

    Path(OUT_PATH).write_text(
        json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"✅ Toplam {len(merged)} istasyon birleştirildi ve '{OUT_PATH}' dosyasına kaydedildi."
    )


if __name__ == "__main__":
    main()
