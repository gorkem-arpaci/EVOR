"""
XLS Dosyalarını Birleştirip Düzelten Script
============================================
- 31 adet .xls dosyasını okur
- Her istasyonu tek satıra dönüştürür (soketler yatayda genişler)
- Hepsini tek bir .xlsx dosyasında birleştirir

Kurulum:
  pip install xlrd openpyxl pandas

Kullanım:
  - Bu scripti tüm .xls dosyalarıyla aynı klasöre koy
  - python birlestir.py

Çıktı: tum_istasyonlar_temiz.xlsx
"""

import xlrd
import pandas as pd
import glob
import os

OUTPUT_FILE = "tum_istasyonlar_temiz.xlsx"

# Ana sütunlar (soket öncesi)
ANA_SUTUNLAR = [
    "Sıra No",
    "İstasyon No",
    "İstasyon Adı",
    "Hizmet Şekli",
    "Marka",
    "Şarj Ağı İşletmecisi",
    "Şarj İstasyonu İşletmecisi",
    "Yeşil Şarj İstasyonu mu",
    "Adres",
]


def xls_oku(dosya_yolu):
    wb = xlrd.open_workbook(dosya_yolu)
    ws = wb.sheet_by_index(0)

    istasyonlar = []
    mevcut_istasyon = None
    soketler = []

    def istasyon_kaydet():
        if mevcut_istasyon is None:
            return
        kayit = dict(mevcut_istasyon)
        for idx, soket in enumerate(soketler, 1):
            kayit[f"Soket{idx}_No"] = soket.get("no", "")
            kayit[f"Soket{idx}_Tipi"] = soket.get("tipi", "")
            kayit[f"Soket{idx}_Turu"] = soket.get("turu", "")
            kayit[f"Soket{idx}_Guc"] = soket.get("guc", "")
        istasyonlar.append(kayit)

    for i in range(1, ws.nrows):
        row = [ws.cell_value(i, j) for j in range(ws.ncols)]
        sira_no = str(row[0]).strip()
        soket_no = str(row[9]).strip() if ws.ncols > 9 else ""

        # Yeni istasyon satırı
        if sira_no not in ("", "nan"):
            istasyon_kaydet()
            mevcut_istasyon = {
                "Sıra No": sira_no,
                "İstasyon No": str(row[1]).strip(),
                "İstasyon Adı": str(row[2]).strip(),
                "Hizmet Şekli": str(row[3]).strip(),
                "Marka": str(row[4]).strip(),
                "Şarj Ağı İşletmecisi": str(row[5]).strip(),
                "Şarj İstasyonu İşletmecisi": str(row[6]).strip(),
                "Yeşil Şarj İstasyonu mu": str(row[7]).strip(),
                "Adres": str(row[8]).strip(),
                "Kaynak Dosya": os.path.basename(dosya_yolu),
            }
            soketler = []

        # Soket verisi satırı (başlık satırını atla)
        elif soket_no not in ("", "Soket No"):
            soketler.append(
                {
                    "no": soket_no,
                    "tipi": str(row[10]).strip() if ws.ncols > 10 else "",
                    "turu": str(row[11]).strip() if ws.ncols > 11 else "",
                    "guc": str(row[12]).strip() if ws.ncols > 12 else "",
                }
            )

    # Son istasyonu kaydet
    istasyon_kaydet()
    return istasyonlar


def main():
    xls_dosyalar = sorted(glob.glob("*.xls") + glob.glob("*.XLS"))
    if not xls_dosyalar:
        print("HATA: Hiç .xls dosyası bulunamadı!")
        return

    print(f"{len(xls_dosyalar)} adet .xls dosyası bulundu.")

    tum_istasyonlar = []
    for dosya in xls_dosyalar:
        istasyonlar = xls_oku(dosya)
        print(f"  {dosya}: {len(istasyonlar)} istasyon")
        tum_istasyonlar.extend(istasyonlar)

    df = pd.DataFrame(tum_istasyonlar)

    # Sıra No'yu düzelt (1.0 -> 1)
    df["Sıra No"] = pd.to_numeric(df["Sıra No"], errors="coerce").fillna(0).astype(int)

    # Sütun sırasını düzenle: önce ana sütunlar, sonra soketler
    soket_sutunlar = sorted(
        [c for c in df.columns if c.startswith("Soket")],
        key=lambda x: (int(x.split("_")[0].replace("Soket", "")), x.split("_")[1]),
    )
    diger = [
        c
        for c in df.columns
        if c not in ANA_SUTUNLAR + soket_sutunlar + ["Kaynak Dosya"]
    ]
    sutun_sirasi = ANA_SUTUNLAR + soket_sutunlar + ["Kaynak Dosya"] + diger
    sutun_sirasi = [c for c in sutun_sirasi if c in df.columns]
    df = df[sutun_sirasi]

    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\nToplam {len(df)} istasyon kaydedildi -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
