"""
Gemini ile prompt -> yapılandırılmış JSON (parse katmanı)
==========================================================

Bu script, kullanıcının serbest metin gezi isteğini (Türkçe) alıp
backend'in rota motoru için ihtiyaç duyduğu sabit şemaya çevirir.

ÖNEMLİ: Bu adım HESAPLAMA yapmaz — rota, süre, istasyon, sıra gibi
hiçbir şey burada üretilmez. Sadece "kullanıcı ne istedi" bilgisini
ayrıştırır. Rota hesaplama (A*/route_optimizer), istasyon seçimi,
şarj planlaması vb. bu çıktıyı girdi olarak alan sonraki adımlarda
yapılacak.

Kullanım:
    export GEMINI_API_KEY="senin-key-in"
    pip install requests python-dotenv
    python test_gemini_parse.py
"""

import os
import sys
import json
import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = "gemini-3.1-flash-lite"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

if not API_KEY:
    print("HATA: GEMINI_API_KEY ortam değişkeni tanımlı değil.")
    print('Şunu çalıştır: export GEMINI_API_KEY="senin-key-in"')
    sys.exit(1)


# ---------------------------------------------------------------------------
# 1) Sistem talimatı — modelin rolünü ve sınırlarını net çiziyoruz
# ---------------------------------------------------------------------------
SYSTEM_INSTRUCTION = """
Sen bir elektrikli araç yolculuk planlama uygulamasının GİRDİ AYRIŞTIRMA
katmanısın. Kullanıcının Türkçe serbest metin gezi isteğini alıp, verilen
JSON şemasına uygun yapılandırılmış veri üreteceksin.

KURALLAR:
1. SADECE ayrıştır, HESAPLAMA YAPMA. Mesafe, süre, rota, istasyon, sıra
   gibi hiçbir şey üretme veya tahmin etme — bunlar senin işin değil.
2. start_location ve end_location için üç durum var:
   a) "Ev", "evim", "evden", "eve" gibi ifadeler geçerse:
      type="home_profile" — adres uygulama içi kayıtlı profilden
      çekilecek, sen adres ÜRETME. raw_text'e kullanıcının kullandığı
      ifadeyi yaz.
   b) Açık bir adres/şehir/POI ismi verilmişse: type="explicit",
      raw_text'e o ifadeyi yaz.
   c) Ne "ev" ifadesi ne açık bir yer belirtilmemişse: type="missing",
      raw_text="". Bu durumda prompt eksik/geçersiz sayılır.
3. waypoints listesindeki her yer için SADECE kullanıcının yazdığı ismi
   raw_text'e koy. Koordinat, adres tamamlama, POI doğrulama YAPMA —
   bu ayrı bir geocoding adımında yapılacak.
4. Kullanıcı waypoint'leri hangi sırada gezeceğini AÇIKÇA belirtmediyse
   (örn. "önce X sonra Y" gibi bir sıralama ifadesi yoksa)
   waypoint_order_fixed = false yap. Sıra netse true yap.
5. Araç modeli/markası prompt içinde AÇIKÇA geçmiyorsa vehicle_ref = null
   bırak — "kullanıcının profildeki aracı" gibi bir varsayım YAPMA.
6. requested_departure_time yalnızca kullanıcı açık bir zaman/tarih
   belirtmişse doldurulur, aksi halde null.
6b. requested_arrival_deadline: kullanıcı "en geç saat X'te orada
   olmalıyım", "saat X'e kadar yetişmem lazım" gibi bir varış zaman
   kısıtı belirtirse doldur (örn. "09:00"). Belirtilmemişse null.
   Bunu requested_departure_time ile karıştırma — biri kalkış, diğeri
   zorunlu varış sınırı.
7. preferences.optimize_for SADECE kullanıcı açıkça bir öncelik
   belirtmişse ("en hızlı", "en kısa sürede", "en ucuz", "en az durak"
   gibi) time/distance/cost olarak doldurulur. Kullanıcı sadece
   "en optimize rotayı hesapla" gibi genel bir ifade kullandıysa
   (spesifik bir kritere işaret etmiyorsa) optimize_for="unspecified"
   yap — bu genel ifadeyi "time" ile eş tutma, uydurma.
8. is_valid ve missing_fields alanlarını doldur: start_location.type
   veya end_location.type "missing" ise is_valid=false yap ve
   missing_fields listesine "start_location" ve/veya "end_location"
   ekle. Her şey tamamsa is_valid=true, missing_fields=[].
9. Emin olmadığın ya da metinde açıkça yer almayan hiçbir alanı
   uydurma — null/boş bırak.
"""

# ---------------------------------------------------------------------------
# 2) Yanıt şeması — Gemini bu şemaya token seviyesinde uymak zorunda
# ---------------------------------------------------------------------------
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "trip_type": {
            "type": "STRING",
            "enum": ["one_way", "round_trip"],
        },
        "start_location": {
            "type": "OBJECT",
            "properties": {
                "type": {
                    "type": "STRING",
                    "enum": ["home_profile", "explicit", "missing"],
                },
                "raw_text": {"type": "STRING"},
            },
            "required": ["type", "raw_text"],
        },
        "end_location": {
            "type": "OBJECT",
            "properties": {
                "type": {
                    "type": "STRING",
                    "enum": ["home_profile", "explicit", "missing"],
                },
                "raw_text": {"type": "STRING"},
            },
            "required": ["type", "raw_text"],
        },
        "is_valid": {"type": "BOOLEAN"},
        "missing_fields": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
        },
        "city_context": {"type": "STRING", "nullable": True},
        "waypoints": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {"raw_text": {"type": "STRING"}},
                "required": ["raw_text"],
            },
        },
        "waypoint_order_fixed": {"type": "BOOLEAN"},
        "vehicle_ref": {"type": "STRING", "nullable": True},
        "requested_departure_time": {"type": "STRING", "nullable": True},
        "requested_arrival_deadline": {"type": "STRING", "nullable": True},
        "preferences": {
            "type": "OBJECT",
            "properties": {
                "optimize_for": {
                    "type": "STRING",
                    "enum": ["time", "distance", "unspecified"],
                },
            },
            "required": ["optimize_for"],
        },
    },
    "required": [
        "trip_type",
        "start_location",
        "end_location",
        "waypoints",
        "waypoint_order_fixed",
        "preferences",
        "is_valid",
        "missing_fields",
    ],
}


# ---------------------------------------------------------------------------
# 3) Gemini'yi çağıran fonksiyon
# ---------------------------------------------------------------------------
def parse_trip_prompt(user_prompt: str) -> dict:
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
            "temperature": 0.1,  # ayrıştırma görevi, yaratıcılık istemiyoruz
        },
    }

    resp = requests.post(
        URL,
        params={"key": API_KEY},
        json=body,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text)


# ---------------------------------------------------------------------------
# 4) Test
# ---------------------------------------------------------------------------
TEST_PROMPTS = [
    "Ev adresinden yola çıkan araç Antalya'ya gidicektir. Şehir içinde ise "
    "Deepo AVM, Ikea AVM, kaleiçi ve lara sahil tarafını gezecektir. Gezi "
    "sonrası tekrardan eve geri dönecektir. Bu yolculuk için en optimize "
    "rotayı hesaplar mısın?",
    # Eksik bilgi testi: başlangıç noktası ne "ev" ne açık bir adres —
    # is_valid=false, missing_fields=["start_location"] dönmesi beklenir.
    "Antalya'da Kaleiçi ve Lara sahiline gitmek istiyorum, en hızlı rotayı "
    "bulur musun?",
    # Varış deadline testi: requested_arrival_deadline="09:00" dönmesi beklenir.
    "Işıkkent mahallesi 5742 sokak Isparta'dan yola çıkmaya başlayan araç "
    "İzmir Adalet Sarayı'na gidecektir. Gece saat 03.00'da yola çıkacaktır "
    "ve en geç saat sabah 09.00'da adreste olması gerekmektedir. Bu "
    "yolculuk için en optimize rotayı hesaplar mısın?",
]


def main():
    for i, prompt in enumerate(TEST_PROMPTS, 1):
        print(f"\n{'=' * 70}\nPROMPT {i}: {prompt}\n{'=' * 70}")
        result = parse_trip_prompt(prompt)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
