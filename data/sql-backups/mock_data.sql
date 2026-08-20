DO $$
DECLARE
    usr_ali    UUID := '33333333-0000-0000-0000-000000000001';
    usr_ayse   UUID := '33333333-0000-0000-0000-000000000002';
    usr_mehmet UUID := '33333333-0000-0000-0000-000000000003';
BEGIN

INSERT INTO profile (id, name, surname, email, password, address, phone, home_lat, home_lng) VALUES
-- Ali şifre: EvorAdmin2026!
(usr_ali,    'Ali',    'Yılmaz', 'ali@example.com',    '$2b$12$X1WkJ82zITiNu0yT0VGlGuGSd3HaNUcF3GckXkEw0I9dhnf3.dKUa', 'Kadıköy, İstanbul',  '555-123-4567', 40.9927,  29.0277),
-- Ayşe şifre: EvorTestUser1*
(usr_ayse,   'Ayşe',  'Kaya',   'ayse@example.com',   '$2b$12$t7FpZ1aw5H5Ay.dfPxK.0eewl7b9EOyIpfRLdV4KExrG1aKAMFlgm', 'Çankaya, Ankara',    '555-987-6543', 39.9032,  32.8597),
-- Mehmet şifre: MockAccount2026#
(usr_mehmet, 'Mehmet','Demir',  'mehmet@example.com', '$2b$12$3OqYFi7OjNnISBWEIz9J9.e6Qv2ii7fJAFp7l2an.1TF5ZkkQUEOS', 'Bornova, İzmir',     NULL,           38.4611,  27.2183);

-- Ali: Tesla Model 3 (varsayılan)
INSERT INTO user_cars (id, profile_id, car_key, plate, is_default) VALUES
(uuid_generate_v4(), usr_ali, 'tesla_model_3_rwd_highland', '34ABC123', TRUE);

-- Ayşe: TOGG T10X (varsayılan) + BMW i4
INSERT INTO user_cars (id, profile_id, car_key, plate, is_default) VALUES
(uuid_generate_v4(), usr_ayse, 'togg_t10x_rwd',    '06XYZ789', TRUE),
(uuid_generate_v4(), usr_ayse, 'bmw_ix3_50_xdrive_my26', '06DEF456', FALSE);

-- Mehmet: Audi e-tron (varsayılan)
INSERT INTO user_cars (id, profile_id, car_key, plate, is_default) VALUES
(uuid_generate_v4(), usr_mehmet, 'audi_q8_e-tron_55', '35GHI321', TRUE);

INSERT INTO charging_detail (id, profile_id, station_key, price, energy_kwh, duration_min, connector_type, total_time) VALUES
(uuid_generate_v4(), usr_ali,    'SKT/9055', 45.50, 12.5, 35, 'AC', '2026-01-10 09:15:00'),
(uuid_generate_v4(), usr_ali,    'SKT/9055', 82.00, 22.8, 48, 'DC', '2026-04-03 14:30:00'),

(uuid_generate_v4(), usr_ayse,   'SKT/9051', 38.00, 10.2, 28, 'AC', '2026-01-05 08:00:00'),
(uuid_generate_v4(), usr_ayse,   'SKT/9055', 95.50, 26.4, 52, 'DC', '2026-01-18 13:45:00'),
(uuid_generate_v4(), usr_ayse,   'SKT/9041', 71.00, 19.6, 40, 'DC', '2026-03-02 17:20:00'),
(uuid_generate_v4(), usr_ayse,   'SKT/9051', 42.00, 11.8, 30, 'AC', '2026-03-15 10:10:00'),
(uuid_generate_v4(), usr_ayse,   'SKT/9055', 88.50, 24.5, 45, 'DC', '2026-04-01 09:30:00'),
(uuid_generate_v4(), usr_ayse,   'SKT/9041', 65.00, 18.0, 38, 'AC', '2026-04-20 16:00:00'),
(uuid_generate_v4(), usr_ayse,   'SKT/9051', 50.00, 14.2, 32, 'AC', '2026-04-10 11:45:00'),

(uuid_generate_v4(), usr_mehmet, 'SKT/9055', 60.00, 16.8, 36, 'DC', '2026-02-08 12:00:00'),
(uuid_generate_v4(), usr_mehmet, 'SKT/9041', 75.50, 21.0, 44, 'DC', '2026-02-25 15:30:00'),
(uuid_generate_v4(), usr_mehmet, 'SKT/9055', 90.00, 25.2, 50, 'DC', '2026-02-12 08:45:00'),
(uuid_generate_v4(), usr_mehmet, 'SKT/9051', 48.00, 13.5, 29, 'AC', '2026-04-01 14:00:00');

-- Ali: 2 yolculuk
INSERT INTO journey (id, user_id, vehicle_id, start_location, end_location, start_time, season, weather_conditions, total_distance_km, total_driving_time_min, total_charging_time_min, total_trip_time_min, total_energy_needed_kwh, starting_soc_percent, ending_soc_percent, created_at) VALUES
('aaaaaaaa-0000-0000-0000-000000000001', usr_ali, NULL, 'Kadıköy, İstanbul', 'Bursa Merkez',   '2026-01-10 08:00', 'Kış',      'Karlı', 245, 180, 35, 215, 48.2, 85, 22, '2026-01-10 15:00:00'),
('aaaaaaaa-0000-0000-0000-000000000002', usr_ali, NULL, 'Kadıköy, İstanbul', 'Ankara Çankaya', '2026-04-03 07:30', 'İlkbahar', 'Açık',  450, 310, 48, 358, 87.5, 90, 18, '2026-04-03 20:00:00');

-- Ayşe: 4 yolculuk
INSERT INTO journey (id, user_id, vehicle_id, start_location, end_location, start_time, season, weather_conditions, total_distance_km, total_driving_time_min, total_charging_time_min, total_trip_time_min, total_energy_needed_kwh, starting_soc_percent, ending_soc_percent, created_at) VALUES
('bbbbbbbb-0000-0000-0000-000000000001', usr_ayse, NULL, 'Çankaya, Ankara', 'Konya Merkez',      '2026-01-05 09:00', 'Kış',      'Bulutlu',  260, 195, 28, 223, 52.1, 80, 25, '2026-01-05 16:30:00'),
('bbbbbbbb-0000-0000-0000-000000000002', usr_ayse, NULL, 'Çankaya, Ankara', 'İstanbul Kadıköy',  '2026-01-18 07:00', 'Kış',      'Soğuk',    450, 315, 52, 367, 91.0, 88, 15, '2026-01-18 20:00:00'),
('bbbbbbbb-0000-0000-0000-000000000003', usr_ayse, NULL, 'Çankaya, Ankara', 'Antalya Merkez',    '2026-03-02 08:30', 'İlkbahar', 'Açık',     480, 335, 40, 375, 95.4, 92, 20, '2026-03-02 22:00:00'),
('bbbbbbbb-0000-0000-0000-000000000004', usr_ayse, NULL, 'Çankaya, Ankara', 'Eskişehir Merkez',  '2026-04-20 10:00', 'İlkbahar', 'Rüzgarlı', 235, 170, 38, 208, 47.8, 78, 28, '2026-04-20 17:30:00');

-- Mehmet: 3 yolculuk
INSERT INTO journey (id, user_id, vehicle_id, start_location, end_location, start_time, season, weather_conditions, total_distance_km, total_driving_time_min, total_charging_time_min, total_trip_time_min, total_energy_needed_kwh, starting_soc_percent, ending_soc_percent, created_at) VALUES
('cccccccc-0000-0000-0000-000000000001', usr_mehmet, NULL, 'Bornova, İzmir', 'Antalya Merkez',  '2026-02-08 08:00', 'Kış',      'Açık',     320, 230, 36, 266, 64.5, 85, 22, '2026-02-08 18:30:00'),
('cccccccc-0000-0000-0000-000000000002', usr_mehmet, NULL, 'Bornova, İzmir', 'Bodrum Merkez',   '2026-02-25 09:00', 'Kış',      'Açık',     290, 210, 44, 254, 59.8, 90, 30, '2026-02-25 17:30:00'),
('cccccccc-0000-0000-0000-000000000003', usr_mehmet, NULL, 'Bornova, İzmir', 'İstanbul Avrupa', '2026-04-01 07:00', 'İlkbahar', 'Yağmurlu', 490, 345, 50, 395, 98.2, 87, 12, '2026-04-01 21:30:00');

END $$;

-- Ali yolculuk 1: Kadıköy → Bursa (1 durak)
INSERT INTO journey_stop (journey_id, stop_number, station_name, provider, latitude, longitude, connector_type, estimated_power_kw, distance_from_start_km, arrival_time, arrival_soc_percent, charge_to_percent, energy_added_kwh, charge_time_min, departure_time, reason) VALUES
('aaaaaaaa-0000-0000-0000-000000000001', 1, 'Gebze ZES HPC', 'ZES', 40.8026, 29.4313, 'CCS2', 180, 65, '2026-01-10 09:05', 42, 80, 22.1, 18, '2026-01-10 09:23', 'Menzil güvenliği');

-- Ali yolculuk 2: Kadıköy → Ankara (2 durak)
INSERT INTO journey_stop (journey_id, stop_number, station_name, provider, latitude, longitude, connector_type, estimated_power_kw, distance_from_start_km, arrival_time, arrival_soc_percent, charge_to_percent, energy_added_kwh, charge_time_min, departure_time, reason) VALUES
('aaaaaaaa-0000-0000-0000-000000000002', 1, 'Düzce TRUGO HPC', 'TRUGO', 40.8376, 31.1563, 'CCS2', 180, 195, '2026-04-03 10:15', 38, 80, 26.4, 20, '2026-04-03 10:35', 'Menzil güvenliği'),
('aaaaaaaa-0000-0000-0000-000000000002', 2, 'Bolu Dağı Opet HPC', 'TRUGO', 40.6923, 31.5731, 'CCS2', 150, 280, '2026-04-03 11:40', 35, 75, 23.8, 22, '2026-04-03 12:02', 'Dağ geçişi öncesi şarj');

-- Ayşe yolculuk 1: Ankara → Konya (1 durak)
INSERT INTO journey_stop (journey_id, stop_number, station_name, provider, latitude, longitude, connector_type, estimated_power_kw, distance_from_start_km, arrival_time, arrival_soc_percent, charge_to_percent, energy_added_kwh, charge_time_min, departure_time, reason) VALUES
('bbbbbbbb-0000-0000-0000-000000000001', 1, 'Cihanbeyli ZES DC', 'ZES', 38.6567, 32.9246, 'CCS2', 60, 145, '2026-01-05 11:25', 35, 75, 20.8, 28, '2026-01-05 11:53', 'Rota optimizasyonu');

-- Ayşe yolculuk 2: Ankara → İstanbul (2 durak)
INSERT INTO journey_stop (journey_id, stop_number, station_name, provider, latitude, longitude, connector_type, estimated_power_kw, distance_from_start_km, arrival_time, arrival_soc_percent, charge_to_percent, energy_added_kwh, charge_time_min, departure_time, reason) VALUES
('bbbbbbbb-0000-0000-0000-000000000002', 1, 'Bolu Dağı Opet HPC', 'TRUGO', 40.6923, 31.5731, 'CCS2', 150, 185, '2026-01-18 10:05', 32, 80, 29.5, 26, '2026-01-18 10:31', 'Menzil güvenliği'),
('bbbbbbbb-0000-0000-0000-000000000002', 2, 'Düzce TRUGO HPC', 'TRUGO', 40.8376, 31.1563, 'CCS2', 180, 280, '2026-01-18 11:45', 40, 75, 21.8, 18, '2026-01-18 12:03', 'İstanbul girişi öncesi');

-- Ayşe yolculuk 3: Ankara → Antalya (2 durak)
INSERT INTO journey_stop (journey_id, stop_number, station_name, provider, latitude, longitude, connector_type, estimated_power_kw, distance_from_start_km, arrival_time, arrival_soc_percent, charge_to_percent, energy_added_kwh, charge_time_min, departure_time, reason) VALUES
('bbbbbbbb-0000-0000-0000-000000000003', 1, 'Konya ZES HPC', 'ZES', 37.8713, 32.4846, 'CCS2', 120, 260, '2026-03-02 11:50', 38, 80, 24.6, 20, '2026-03-02 12:10', 'Toros geçişi öncesi'),
('bbbbbbbb-0000-0000-0000-000000000003', 2, 'Serik EŞARJ DC', 'EŞARJ', 36.9236, 31.1046, 'CCS2', 60, 420, '2026-03-02 14:30', 22, 70, 27.8, 40, '2026-03-02 15:10', 'Varışa güvenli ulaşım');

-- Ayşe yolculuk 4: Ankara → Eskişehir (1 durak)
INSERT INTO journey_stop (journey_id, stop_number, station_name, provider, latitude, longitude, connector_type, estimated_power_kw, distance_from_start_km, arrival_time, arrival_soc_percent, charge_to_percent, energy_added_kwh, charge_time_min, departure_time, reason) VALUES
('bbbbbbbb-0000-0000-0000-000000000004', 1, 'Polatlı ZES AC', 'ZES', 39.5838, 32.1464, 'CCS2', 60, 110, '2026-04-20 11:50', 45, 75, 16.2, 22, '2026-04-20 12:12', 'Rota optimizasyonu');

-- Mehmet yolculuk 1: İzmir → Antalya (1 durak)
INSERT INTO journey_stop (journey_id, stop_number, station_name, provider, latitude, longitude, connector_type, estimated_power_kw, distance_from_start_km, arrival_time, arrival_soc_percent, charge_to_percent, energy_added_kwh, charge_time_min, departure_time, reason) VALUES
('cccccccc-0000-0000-0000-000000000001', 1, 'Kumluca TRUGO DC', 'TRUGO', 36.3726, 30.2847, 'CCS2', 90, 190, '2026-02-08 11:10', 30, 78, 27.8, 30, '2026-02-08 11:40', 'Menzil güvenliği');

-- Mehmet yolculuk 2: İzmir → Bodrum (1 durak)
INSERT INTO journey_stop (journey_id, stop_number, station_name, provider, latitude, longitude, connector_type, estimated_power_kw, distance_from_start_km, arrival_time, arrival_soc_percent, charge_to_percent, energy_added_kwh, charge_time_min, departure_time, reason) VALUES
('cccccccc-0000-0000-0000-000000000002', 1, 'Söke ZES DC', 'ZES', 37.7479, 27.4162, 'CCS2', 60, 150, '2026-02-25 11:30', 40, 78, 21.8, 28, '2026-02-25 11:58', 'Rota optimizasyonu');

-- Mehmet yolculuk 3: İzmir → İstanbul (3 durak)
INSERT INTO journey_stop (journey_id, stop_number, station_name, provider, latitude, longitude, connector_type, estimated_power_kw, distance_from_start_km, arrival_time, arrival_soc_percent, charge_to_percent, energy_added_kwh, charge_time_min, departure_time, reason) VALUES
('cccccccc-0000-0000-0000-000000000003', 1, 'Bursa TRUGO HPC', 'TRUGO', 40.1885, 29.0610, 'CCS2', 180, 280, '2026-04-01 11:20', 28, 80, 30.2, 22, '2026-04-01 11:42', 'Menzil güvenliği'),
('cccccccc-0000-0000-0000-000000000003', 2, 'Gebze ZES HPC',   'ZES',   40.8026, 29.4313, 'CCS2', 180, 390, '2026-04-01 13:10', 32, 78, 27.4, 20, '2026-04-01 13:30', 'İstanbul girişi öncesi'),
('cccccccc-0000-0000-0000-000000000003', 3, 'Kadıköy EŞARJ DC','EŞARJ', 40.9833, 29.0333, 'CCS2',  60, 480, '2026-04-01 15:00', 20, 60, 22.6, 35, '2026-04-01 15:35', 'Final şarj');
