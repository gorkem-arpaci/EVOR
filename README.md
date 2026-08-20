<div align="center">
  # EVOR: Electric Vehicle Optimized Routing

  **Grok 4.1 AI Destekli Elektrikli Araç Rota Optimizasyon Asistanı**

  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
  [![Platform](https://img.shields.io/badge/platform-iOS%20(SwiftUI)-lightgrey)](https://developer.apple.com/xcode/swiftui/)
  [![Python](https://img.shields.io/badge/backend-Python%20%7C%20TypeScript-yellow)]()
  [![Status](https://img.shields.io/badge/status-Geliştirme%20Aşamasında-orange)]()
</div>

---

## 📖 Proje Hakkında

**EVOR**, elektrikli araç (EV) kullanıcılarının "menzil kaygısını" (range anxiety) ortadan kaldırmak için tasarlanmış, yapay zeka destekli bir mobil uygulamadır.

Klasik navigasyon servislerinin aksine EVOR, rota optimizasyonunu **Grok 4.1 API** gücünü kullanarak gerçekleştirir. Araç verilerini ve yol koşullarını analiz eden yapay zeka, sürücüye en enerji verimli rotayı önerir.

### 🎯 Temel Amaçlar
* Sürüş menzilini maksimize eden AI tabanlı rotalar oluşturmak.
* Karmaşık rota hesaplamalarını yapay zeka ile basitleştirmek.
* Sürücüye geçmiş sürüşlerine dair kolay erişim sağlamak.

---

## ✨ Özellikler

* **🧠 Grok 4.1 ile Rota Optimizasyonu:** Standart algoritmalar yerine, Grok 4.1 yapay zeka modelini kullanarak elektrikli aracınız için en verimli rotayı oluşturur.
* **📜 Rota Geçmişi:** Favori sistemi yerine, oluşturduğunuz tüm rotalar otomatik olarak cihaz hafızasına (Local) kaydedilir; böylece internetiniz olmasa bile eski rotalarınıza bakabilirsiniz.
* **📱 SwiftUI Modern Arayüz:** Kullanıcı deneyimini en üst düzeye çıkaran, hızlı ve akıcı bir iOS tasarımı sunar.
* **⚡ Özelleştirilmiş Tüketim Analizi:** Python ve TypeScript tabanlı arka plan servisleri ile aracın enerji tüketimini yol şartlarına göre analiz eder.
* **🔋 Akıllı Menzil Yönetimi:** A noktasından B noktasına giderken şarj durumunuzu dikkate alarak sizi yolda bırakmayacak optimizasyonlar yapar.

---

## 📱 Ekran Görüntüleri

*(Ekran görüntüleri geliştirme süreci ilerledikçe eklenecektir.)*

---

## 🛠️ Kullanılan Teknolojiler

Bu proje, modern iOS geliştirme standartları ve yeni nesil yapay zeka entegrasyonu üzerine kuruludur.

### Mobil Uygulama (Client)
* **Dil:** Swift
* **Framework:** SwiftUI
* **Mimari:** MVVM
* **Veri Saklama:** Local Storage (Cihaz içi kayıt)

### Backend & Logic
* **Diller:** Python, TypeScript
* **AI Engine:** Grok 4.1 API (Rota Optimizasyon Motoru)
* **Veri İşleme:** JSON tabanlı veri akışı

---

## Database & Migrations

This project uses Alembic for schema and seed migrations. Prefer the Alembic-first workflow in development and CI/CD.

Quick setup:

```bash
# create venv if needed
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

# set your DATABASE_URL e.g. postgres with psycopg2
export DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/evor"

# run migrations
alembic upgrade head
```

Fallback: raw SQL files were archived to `data/sql-backups/`. Use `psql` only for manual/one-off setups:

```bash
psql "$DATABASE_URL" -f data/sql-backups/init.sql
psql "$DATABASE_URL" -f data/sql-backups/mock_data.sql
```

