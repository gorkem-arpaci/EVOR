DO $$
DECLARE
    usr_ali    UUID := '33333333-0000-0000-0000-000000000001';
    usr_ayse   UUID := '33333333-0000-0000-0000-000000000002';
    usr_mehmet UUID := '33333333-0000-0000-0000-000000000003';
BEGIN

INSERT INTO profile (id, name, surname, email, password, address, phone, home_lat, home_lng) VALUES
(usr_ali,    'Ali',    'Yılmaz', 'ali@example.com',    '$2b$12$mHwHtYwPr/6Iy7WuCbXCleGYkbMZdFx0mspqMBtXknpsHV.QRKpCO', 'Kadıköy, İstanbul',  '555-123-4567', 40.9927,  29.0277),
(usr_ayse,   'Ayşe',  'Kaya',   'ayse@example.com',   '$2b$12$d6nMh2.jVNZPvFCBgApMr.PK3Px6uME2q2KzaWJHmtz9fFVftfQNu', 'Çankaya, Ankara',    '555-987-6543', 39.9032,  32.8597),
(usr_mehmet, 'Mehmet','Demir',  'mehmet@example.com', '$2b$12$3KsewXPgweKBjIpj24oqSeX6pk9rtdD6mCwsU.x1O6bJL9UErADqO', 'Bornova, İzmir',     NULL,           38.4611,  27.2183);

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

-- Ali şarj geçmişi
INSERT INTO charging_detail (id, profile_id, station_key, price, total_time) VALUES
(uuid_generate_v4(), usr_ali, 'SRJ9055', 45.50, '2024-11-10 09:15:00'),
(uuid_generate_v4(), usr_ali, 'SRJ9055', 82.00, '2024-12-03 14:30:00');

-- Ayşe şarj geçmişi
INSERT INTO charging_detail (id, profile_id, station_key, price, total_time) VALUES
(uuid_generate_v4(), usr_ayse, 'SRJ9055', 38.00, '2024-09-05 08:00:00'),
(uuid_generate_v4(), usr_ayse, 'SRJ9055', 95.50, '2024-09-18 13:45:00'),
(uuid_generate_v4(), usr_ayse, 'SRJ9055', 71.00, '2024-10-02 17:20:00'),
(uuid_generate_v4(), usr_ayse, 'SRJ9055', 42.00, '2024-10-15 10:10:00'),
(uuid_generate_v4(), usr_ayse, 'SRJ9055', 88.50, '2024-11-01 09:30:00'),
(uuid_generate_v4(), usr_ayse, 'SRJ9055', 65.00, '2024-11-20 16:00:00'),
(uuid_generate_v4(), usr_ayse, 'SRJ9055', 50.00, '2024-12-10 11:45:00');

-- Mehmet şarj geçmişi
INSERT INTO charging_detail (id, profile_id, station_key, price, total_time) VALUES
(uuid_generate_v4(), usr_mehmet, 'SRJ9055', 60.00, '2024-10-08 12:00:00'),
(uuid_generate_v4(), usr_mehmet, 'SRJ9055', 75.50, '2024-10-25 15:30:00'),
(uuid_generate_v4(), usr_mehmet, 'SRJ9055', 90.00, '2024-11-12 08:45:00'),
(uuid_generate_v4(), usr_mehmet, 'SRJ9055', 48.00, '2024-12-01 14:00:00');

END $$;
