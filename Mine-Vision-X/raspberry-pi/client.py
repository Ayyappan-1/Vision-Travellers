import json
import time
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

from config import BACKEND_URL, DEVICE_IDENTIFIER, DEVICE_SECRET, TELEMETRY_INTERVAL
from telemetry import Telemetry


def send_telemetry(value: Telemetry) -> None:
    if not DEVICE_IDENTIFIER or not DEVICE_SECRET:
        raise RuntimeError("Set DEVICE_IDENTIFIER and DEVICE_SECRET before starting the client.")
    body = json.dumps(value.as_payload(DEVICE_IDENTIFIER, DEVICE_SECRET)).encode("utf-8")
    request = Request(
        f"{BACKEND_URL}/api/hardware/telemetry",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        print(f"telemetry accepted: {response.status} {response.read().decode('utf-8')}")


def read_sensors() -> Telemetry:
    # Replace this function with GPIO/GPS/camera reads on the physical vehicle.
    # It deliberately does not create connection state or write to the database.
    return Telemetry(speed_kmh=0, lat=21.1458, lng=79.0882)


def main() -> None:
    print(f"Sending telemetry to {BACKEND_URL}; press Ctrl+C to stop.")
    while True:
        try:
            send_telemetry(read_sensors())
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            print(f"network error; retrying in {TELEMETRY_INTERVAL:g}s: {error}")
        except RuntimeError as error:
            print(error)
            return
        time.sleep(TELEMETRY_INTERVAL)


if __name__ == "__main__":
    main()