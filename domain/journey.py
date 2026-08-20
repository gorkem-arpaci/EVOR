from dataclasses import dataclass
from typing import Optional, List


@dataclass
class JourneyStop:
    stop_number: int
    station_name: str
    provider: str
    connector_type: str
    estimated_power_kw: Optional[float]
    energy_added_kwh: Optional[float]
    charge_time_min: Optional[int]
    arrival_soc_percent: Optional[int]
    charge_to_percent: Optional[int]
    arrival_time: Optional[str]
    departure_time: Optional[str]
    reason: Optional[str]


@dataclass
class Journey:
    id: int
    start_location: str
    end_location: str
    start_time: Optional[str]
    total_distance_km: Optional[float]
    total_trip_time_min: Optional[int]
    stops: List[JourneyStop]
