# Mine Vision-X

Mine Vision-X is a control platform for mine vehicles and their Raspberry Pi hardware. It gives two kinds of people a shared operational view:

- **Admin** provisions vehicles, creates hardware identities, inspects Raspberry Pi health, and manages software users.
- **Control Room** monitors the live fleet, sets speed limits, manages trips, watches incidents, and reviews safety.

There is no Driver login and no separate Fleet Manager login. The Raspberry Pi is a hardware client, not an application user.

## What is built

The project includes:

- Express API with PostgreSQL/Drizzle schema
- JWT login with hashed passwords and role authorization
- Backend-owned vehicle registration and device connection states
- One-to-one vehicle/device provisioning
- Authenticated hardware telemetry ingestion
- Overspeed, GPS, sensor, camera, low-visibility, and stale-communication safety incidents
- Backend Claim Resolution with safe/unsafe verification
- Trip creation, assignment, and unassignment
- WebSocket broadcasts on `/ws`
- Responsive React/Vite Admin and Control Room surfaces
- Python Raspberry Pi client and Python simulator using the same telemetry endpoint

## Start the app in this workspace

The Replit preview runs the API and frontend workflows automatically. For local terminal work:

```bash
pnpm install
pnpm --filter @workspace/db run push
pnpm --filter @workspace/api-server run dev
```

In another terminal:

```bash
pnpm --filter @workspace/mine-vision-x run dev
```

The browser app is served at the preview root. The API is available through `/api`, and the WebSocket endpoint is `/ws`.

## Development login

The API seeds this development-only account when the database is empty:

```text
Username: admin
Password: Admin@12345
Role: ADMIN
```

The development Control Room account is:

```text
Username: controlroom
Password: ControlRoom@12345
Role: CONTROL_ROOM
```

The selected role is sent to the backend and must match the user's stored role.

Change this account or create a proper Admin account before real use.

Admin WebAuthn/Windows Hello endpoints are present as a service boundary, but browser biometric verification is not configured in this development environment. The login page labels this explicitly as:

```text
DEVELOPMENT ONLY — WebAuthn / Windows Hello is not configured in this environment.
```

## Admin vehicle registration

1. Sign in as Admin.
2. Open **Vehicles** and choose **Register vehicle**.
3. Enter a vehicle ID, name, type, device identifier, and a device secret of at least 8 characters.
4. The vehicle will remain `WAITING_FOR_CONNECTION`; it is not operational yet.
5. Put the device identifier and secret into the Raspberry Pi client or simulator.
6. Send the first valid telemetry message.
7. Only then will the backend set the device to `CONNECTED` and the vehicle to `REGISTERED`.

Creating a row, generating a credential, or pressing a frontend button never fakes a connection.

## Run the simulator

The simulator only communicates with the backend over HTTP. It never touches the database:

```bash
python simulator/simulator.py \
  --backend-url http://localhost:5000 \
  --device-identifier RP-101 \
  --device-secret YOUR_DEVICE_SECRET \
  --mode safe
```

Useful modes:

```bash
python simulator/simulator.py --device-identifier RP-101 --device-secret YOUR_DEVICE_SECRET --mode overspeed
python simulator/simulator.py --device-identifier RP-101 --device-secret YOUR_DEVICE_SECRET --mode low-visibility
python simulator/simulator.py --device-identifier RP-101 --device-secret YOUR_DEVICE_SECRET --mode gps-fault
python simulator/simulator.py --device-identifier RP-101 --device-secret YOUR_DEVICE_SECRET --mode sensor-fault
```

Stop it with Ctrl+C. After `DEVICE_CONNECTION_TIMEOUT_SECONDS`, the backend marks the device `CONNECTION_LOST`, the vehicle `OFFLINE`, and creates a communication incident.

## Raspberry Pi client

Copy `raspberry-pi/.env.example` to `.env` and set:

| Variable | Meaning | Example |
| --- | --- | --- |
| `BACKEND_URL` | Network address of the backend | `http://192.168.1.100:5000` |
| `DEVICE_IDENTIFIER` | Provisioned hardware identity | `RP-101` |
| `DEVICE_SECRET` | Provisioned device credential | never commit this |
| `TELEMETRY_INTERVAL` | Seconds between messages | `5` |

Run it with `python raspberry-pi/client.py`. Do not use `localhost` on the Pi when the backend is on a laptop; use the laptop's LAN IP.

## Important API routes

| Method | Route | User |
| --- | --- | --- |
| POST | `/api/auth/login` | Admin or Control Room |
| POST | `/api/auth/logout` | Admin or Control Room |
| POST | `/api/auth/webauthn/*` | Admin |
| POST | `/api/auth/users` | Admin |
| GET/POST | `/api/vehicles` | View: both; create: Admin |
| PUT | `/api/vehicles/{id}/speed-limit` | Admin or Control Room |
| GET | `/api/devices` | Admin or Control Room |
| POST | `/api/hardware/telemetry` | Raspberry Pi only |
| GET | `/api/incidents` | Admin or Control Room |
| POST | `/api/incidents/{id}/claim-resolution` | Admin or Control Room |
| GET/POST | `/api/trips` | Admin or Control Room |
| POST | `/api/trips/{id}/assign` | Admin or Control Room |
| POST | `/api/trips/{id}/unassign` | Admin or Control Room |
| GET | `/api/dashboard/summary` | Admin or Control Room |
| GET | `/api/safety/overview` | Admin or Control Room |
| GET | `/api/system/status` | Admin |
| WS | `/ws` | Browser Control Room clients |

Hardware telemetry is authenticated with `deviceIdentifier` and `deviceSecret`; it does not accept a client-supplied vehicle ID.

## Verification performed

The following were exercised against the running services:

- API health response
- Development Admin login
- Vehicle/device registration remains waiting for hardware
- Backend speed limit update
- Valid hardware telemetry authenticates the device and activates the vehicle
- Overspeed incident creation
- Claim Resolution rejection while the issue remains active
- Safe telemetry followed by successful Claim Resolution
- Trip creation and assignment to a connected vehicle
- React typecheck and production build
- Login screen rendered through the preview

## Current limitation

Trip records currently store source and destination as operational names. The end-to-end geofence cycle counter needs source/destination coordinate capture and a migration for those fields before `SOURCE → DESTINATION → SOURCE` can increment `completedCycles`. The rest of the trip assignment flow is live and backend-authoritative.