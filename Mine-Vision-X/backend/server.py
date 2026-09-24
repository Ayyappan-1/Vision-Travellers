from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Mine Vision-X Telemetry Server")


# ============================================================
# LATEST TELEMETRY STATE
# ============================================================

latest_state = {
    "device_id": "HEMM_01",

    "speed": None,

    "distance": None,

    "acceleration": {
        "x": None,
        "y": None,
        "z": None
    },

    "latitude": None,
    "longitude": None,
    "altitude": None,

    "satellites": None,
    "hdop": None,
    "fix_type": None,

    "speed_knots": None,
    "course": None,

    "last_update": None
}


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Mine Vision-X Telemetry Server is running",
        "status": "online"
    }


# ============================================================
# RECEIVE TELEMETRY FROM RASPBERRY PI
# ============================================================

@app.post("/api/telemetry")
def receive_telemetry(data: dict):

    global latest_state

    latest_state = data.copy()

    latest_state["last_update"] = datetime.now().isoformat()

    print()
    print("=" * 70)
    print("TELEMETRY RECEIVED FROM RASPBERRY PI")
    print("=" * 70)

    print("Device ID :", latest_state.get("device_id"))
    print("Speed     :", latest_state.get("speed"))
    print("Distance  :", latest_state.get("distance"))

    acceleration = latest_state.get("acceleration", {})

    print(
        "IMU       : X={:.3f}  Y={:.3f}  Z={:.3f}".format(
            acceleration.get("x") or 0,
            acceleration.get("y") or 0,
            acceleration.get("z") or 0
        )
    )

    print("Latitude  :", latest_state.get("latitude"))
    print("Longitude :", latest_state.get("longitude"))

    print("Updated   :", latest_state.get("last_update"))

    print("=" * 70)

    return {
        "status": "received",
        "message": "Telemetry received successfully"
    }


# ============================================================
# DRIVER DASHBOARD STATE
# ============================================================

@app.get("/api/state")
def get_state():

    return latest_state