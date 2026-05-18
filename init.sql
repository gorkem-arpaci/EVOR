CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE profile (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT,
    surname TEXT,
    email VARCHAR(255) UNIQUE,
    password TEXT,
    address TEXT,
    phone VARCHAR(20) NULL,
    home_lat DOUBLE PRECISION NULL,
    home_lng DOUBLE PRECISION NULL
);

CREATE TABLE user_cars (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID REFERENCES profile(id),
    car_key TEXT,
    plate VARCHAR(20) NULL,
    is_default BOOLEAN DEFAULT FALSE,
    added_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE charging_detail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID REFERENCES profile(id),
    station_key TEXT,
    price FLOAT,
    total_time TIMESTAMP
);

CREATE TABLE email_verifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) NOT NULL,
  code VARCHAR(6) NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  used BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE favorite_stations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID REFERENCES profile(id) ON DELETE CASCADE,
    station_key TEXT NOT NULL,
    added_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(profile_id, station_key)
);
