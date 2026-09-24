from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Telemetry:
    speed_kmh: float
    lat: float
    lng: float
    visibility_state: str = "CLEAR"
    gps_healthy: bool = True
    sensor_healthy: bool = True
    camera_healthy: bool = True

    def as_payload(self, device_identifier: str, device_secret: str) -> dict:
        return {
            "deviceIdentifier": device_identifier,
            "deviceSecret": device_secret,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "speedKmh": self.speed_kmh,
            "lat": self.lat,
            "lng": self.lng,
            "visibilityState": self.visibility_state,
            "gpsHealthy": self.gps_healthy,
            "sensorHealthy": self.sensor_healthy,
            "cameraHealthy": self.camera_healthy,
        }