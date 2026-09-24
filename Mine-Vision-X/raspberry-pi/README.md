# Mine Vision-X Raspberry Pi client

This client is the vehicle-side hardware process. It authenticates with the device identifier and secret created during Admin vehicle registration, then sends telemetry to the backend.

## Important network rule

`localhost` on the Raspberry Pi means the Raspberry Pi itself. It does not mean the laptop running Mine Vision-X. If the backend runs on a laptop, set `BACKEND_URL` to the laptop's LAN address, for example:

```text
BACKEND_URL=http://192.168.1.100:5000
```

## Setup

1. Install Raspberry Pi OS, connect it to the same network as the backend, and install Python 3.10 or newer.
2. Copy this folder to the Pi.
3. Copy `.env.example` to `.env` and set `BACKEND_URL`, `DEVICE_IDENTIFIER`, `DEVICE_SECRET`, and `TELEMETRY_INTERVAL`.
4. Replace `read_sensors()` in `client.py` with real GPS, speed, sensor, and camera reads.
5. Run `python client.py`.

The backend determines connection status. The client cannot mark a vehicle connected or update vehicle records directly.