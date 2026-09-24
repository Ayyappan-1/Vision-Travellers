import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://192.168.1.100:5000").rstrip("/")
DEVICE_IDENTIFIER = os.getenv("DEVICE_IDENTIFIER", "")
DEVICE_SECRET = os.getenv("DEVICE_SECRET", "")
TELEMETRY_INTERVAL = float(os.getenv("TELEMETRY_INTERVAL", "5"))