import pandas as pd
import json
import re

INPUT_FILE = "birlesik_final.xlsx"
OUTPUT_FILE = "istasyonlar.json"

df = pd.read_excel(INPUT_FILE)

ana_sutunlar = [
    "İstasyon No",
    "İstasyon Adı",
    "Hizmet Şekli",
    "Marka",
    "Şarj Ağı İşletmecisi",
    "Şarj İstasyonu İşletmecisi",
    "Yeşil Şarj İstasyonu mu",
    "Adres",
    "Enlem",
    "Boylam",
]

soket_nos = sorted(
    set(int(re.search(r"\d+", c).group()) for c in df.columns if c.startswith("Soket"))
)

sonuc = []

for _, row in df.iterrows():
    istasyon = {col: (None if pd.isna(row[col]) else row[col]) for col in ana_sutunlar}

    soketler = []
    for n in soket_nos:
        no = row.get(f"Soket{n}_No")
        tipi = row.get(f"Soket{n}_Tipi")
        turu = row.get(f"Soket{n}_Türü", row.get(f"Soket{n}_Turu"))
        guc = row.get(f"Soket{n}_Güç", row.get(f"Soket{n}_Guc"))

        if pd.isna(no):
            break

        soket = {}
        if not pd.isna(no):
            soket["no"] = no
        if not pd.isna(tipi):
            soket["tipi"] = tipi
        if not pd.isna(turu):
            soket["turu"] = turu
        if not pd.isna(guc):
            soket["guc"] = guc
        soketler.append(soket)

    istasyon["soketler"] = soketler
    sonuc.append(istasyon)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(sonuc, f, ensure_ascii=False, indent=2)

print(f"Tamamlandı! {len(sonuc)} istasyon -> {OUTPUT_FILE}")
