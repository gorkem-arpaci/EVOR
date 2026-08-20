"""Initial schema migration generated from init.sql

This migration executes the project's `init.sql` to create required tables.
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    sql = '''
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
    energy_kwh FLOAT,
    duration_min INTEGER,
    connector_type TEXT,
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

CREATE TABLE journey (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES profile(id) ON DELETE CASCADE,
    vehicle_id  UUID,
    start_location          TEXT NOT NULL,
    end_location            TEXT NOT NULL,
    start_time              VARCHAR(50),
    season                  VARCHAR(50),
    weather_conditions      VARCHAR(100),
    total_distance_km       INTEGER,
    total_driving_time_min  INTEGER,
    total_charging_time_min INTEGER,
    total_trip_time_min     INTEGER,
    total_energy_needed_kwh DOUBLE PRECISION,
    starting_soc_percent    INTEGER,
    ending_soc_percent      INTEGER,
    created_at              TIMESTAMP DEFAULT NOW()
);

CREATE TABLE journey_stop (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    journey_id      UUID NOT NULL REFERENCES journey(id) ON DELETE CASCADE,
    stop_number     INTEGER NOT NULL,
    station_name    VARCHAR(255),
    provider        VARCHAR(100),
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    connector_type  VARCHAR(50),
    estimated_power_kw DOUBLE PRECISION,
    distance_from_start_km DOUBLE PRECISION,
    arrival_time    VARCHAR(50),
    arrival_soc_percent INTEGER,
    charge_to_percent INTEGER,
    energy_added_kwh DOUBLE PRECISION,
    charge_time_min INTEGER,
    departure_time  VARCHAR(50),
    reason          TEXT
);
'''
    op.execute(sql)


def downgrade() -> None:
    # drop in reverse dependency order
    op.execute('DROP TABLE IF EXISTS journey_stop CASCADE;')
    op.execute('DROP TABLE IF EXISTS journey CASCADE;')
    op.execute('DROP TABLE IF EXISTS favorite_stations CASCADE;')
    op.execute('DROP TABLE IF EXISTS charging_detail CASCADE;')
    op.execute('DROP TABLE IF EXISTS user_cars CASCADE;')
    op.execute('DROP TABLE IF EXISTS email_verifications CASCADE;')
    op.execute('DROP TABLE IF EXISTS profile CASCADE;')
    # extension left as-is; dropping extension may require superuser