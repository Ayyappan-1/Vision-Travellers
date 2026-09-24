import argparse
import json
import math
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def send(base_url: str, identifier: str, secret: str, speed: float, lat: float, lng: float, visibility: str, gps: bool, sensor: bool) -> None:
    payload = {
        "deviceIdentifier": identifier,
        "deviceSecret": secret,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "speedKmh": speed,
        "lat": lat,
        "lng": lng,
        "visibilityState": visibility,
        "gpsHealthy": gps,
        "sensorHealthy": sensor,
        "cameraHealthy": True,
    }
    request = Request(
        f"{base_url.rstrip('/')}/api/hardware/telemetry",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        print(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Mine Vision-X authenticated Raspberry Pi simulator")
    parser.add_argument("--backend-url", default="http://localhost:5000")
    parser.add_argument("--device-identifier", required=True)
    parser.add_argument("--device-secret", required=True)
    parser.add_argument("--mode", choices=["safe", "overspeed", "low-visibility", "gps-fault", "sensor-fault"], default="safe")
    parser.add_argument("--interval", type=float, default=5)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    print(f"Sending authenticated telemetry to {args.backend_url}; mode={args.mode}")
    tick = 0
    while True:
        tick += 1
        mode = args.mode
        speed = 24 if mode == "safe" else 37 if mode == "overspeed" else 18
        visibility = "LOW" if mode == "low-visibility" else "CLEAR"
        gps_healthy = mode != "gps-fault"
        sensor_healthy = mode != "sensor-fault"
        try:
            send(args.backend_url, args.device_identifier, args.device_secret, speed, 21.1458 + math.sin(tick / 8) * 0.001, 79.0882 + math.cos(tick / 8) * 0.001, visibility, gps_healthy, sensor_healthy)
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            print(f"telemetry error: {error}")
        if args.once:
            return
        time.sleep(args.interval)


if __name__ == "__main__":
    main()