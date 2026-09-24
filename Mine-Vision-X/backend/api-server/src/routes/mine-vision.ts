import { Router, type IRouter, type Request, type Response } from "express";
import { pool } from "@workspace/db";
import { randomBytes, scryptSync, timingSafeEqual, createHmac } from "node:crypto";
import { broadcastRealtime } from "../realtime/manager";

const router: IRouter = Router();
const JWT_SECRET = process.env["SESSION_SECRET"] ?? process.env["YOUR_JWT_SECRET"] ?? "development-only-change-me";
const CONNECTION_TIMEOUT_MS = Number(process.env["DEVICE_CONNECTION_TIMEOUT_SECONDS"] ?? 60) * 1000;

type Role = "ADMIN" | "CONTROL_ROOM";
type AuthedRequest = Request & { user?: { id: string; role: Role; username: string } };

const id = (prefix: string) => `${prefix}-${randomBytes(5).toString("hex")}`;
const now = () => new Date();
const iso = (value: unknown) => value ? new Date(value as string | Date).toISOString() : null;
const numeric = (value: unknown) => value == null ? null : Number(value);

function passwordHash(password: string, salt = randomBytes(16).toString("hex")) {
  return `${salt}:${scryptSync(password, salt, 64).toString("hex")}`;
}

function passwordMatches(password: string, stored: string) {
  const [salt, hash] = stored.split(":");
  if (!salt || !hash) return false;
  const candidate = scryptSync(password, salt, 64);
  const expected = Buffer.from(hash, "hex");
  return candidate.length === expected.length && timingSafeEqual(candidate, expected);
}

function encodeToken(payload: { id: string; username: string; role: Role }) {
  const header = Buffer.from(JSON.stringify({ alg: "HS256", typ: "JWT" })).toString("base64url");
  const body = Buffer.from(JSON.stringify({ ...payload, exp: Math.floor(Date.now() / 1000) + 60 * 60 * 8 })).toString("base64url");
  const signature = createHmac("sha256", JWT_SECRET).update(`${header}.${body}`).digest("base64url");
  return `${header}.${body}.${signature}`;
}

function decodeToken(token: string) {
  const [header, body, signature] = token.split(".");
  if (!header || !body || !signature) return null;
  const expected = createHmac("sha256", JWT_SECRET).update(`${header}.${body}`).digest("base64url");
  if (signature !== expected) return null;
  const decoded = JSON.parse(Buffer.from(body, "base64url").toString()) as { id: string; username: string; role: Role; exp: number };
  return decoded.exp > Math.floor(Date.now() / 1000) ? decoded : null;
}

function userFromRequest(req: AuthedRequest) {
  const header = req.headers.authorization;
  if (!header?.startsWith("Bearer ")) return null;
  const user = decodeToken(header.slice(7));
  if (user) req.user = user;
  return user;
}

function requireAuth(req: AuthedRequest, res: Response, roles?: Role[]) {
  const user = userFromRequest(req);
  if (!user) {
    res.status(401).json({ error: "Unauthorized" });
    return null;
  }
  if (roles && !roles.includes(user.role)) {
    res.status(403).json({ error: "Forbidden" });
    return null;
  }
  return user;
}

function userResponse(row: Record<string, unknown>) {
  return { id: row.id, username: row.username, role: row.role, displayName: row.display_name };
}

function vehicleResponse(row: Record<string, unknown>) {
  return {
    id: row.id, name: row.name, type: row.type,
    registrationStatus: row.registration_status,
    operationalStatus: row.operational_status,
    connectionStatus: row.connection_status,
    speed: numeric(row.speed) ?? 0, speedLimit: numeric(row.speed_limit) ?? 30,
    lat: numeric(row.lat), lng: numeric(row.lng),
    visibility: row.visibility, completedCycles: row.completed_cycles ?? 0,
    deviceId: row.device_id, updatedAt: iso(row.updated_at),
  };
}

function deviceResponse(row: Record<string, unknown>) {
  return {
    id: row.id, identifier: row.identifier, vehicleId: row.vehicle_id,
    connectionStatus: row.connection_status, lastSeen: iso(row.last_seen),
    gpsHealthy: row.gps_healthy, sensorHealthy: row.sensor_healthy, cameraHealthy: row.camera_healthy,
  };
}

function incidentResponse(row: Record<string, unknown>) {
  return {
    id: row.id, vehicleId: row.vehicle_id, vehicleName: row.vehicle_name ?? row.vehicle_id,
    type: row.type, severity: row.severity, status: row.status, message: row.message,
    createdAt: iso(row.created_at), resolvedAt: iso(row.resolved_at),
  };
}

async function seedAdmin() {
  const result = await pool.query("SELECT username FROM mvx_users WHERE username IN ('admin', 'controlroom')");
  const existing = new Set(result.rows.map((row) => row.username));
  if (!existing.has("admin")) {
    await pool.query(
      "INSERT INTO mvx_users (id, username, password_hash, role, display_name) VALUES ($1, $2, $3, $4, $5)",
      ["usr-admin", "admin", passwordHash("Admin@12345"), "ADMIN", "System Administrator"],
    );
  }
  if (!existing.has("controlroom")) {
    await pool.query(
      "INSERT INTO mvx_users (id, username, password_hash, role, display_name) VALUES ($1, $2, $3, $4, $5)",
      ["usr-controlroom", "controlroom", passwordHash("ControlRoom@12345"), "CONTROL_ROOM", "Control Room Operator"],
    );
  }
}

let initialization: Promise<void> | undefined;
router.use(async (_req, res, next) => {
  try {
    initialization ??= seedAdmin();
    await initialization;
    next();
  } catch {
    res.status(503).json({ error: "Database is unavailable" });
  }
});

router.get("/health", (_req, res) => res.json({ status: "healthy" }));

router.post("/auth/login", async (req, res) => {
  const { username, password, role } = req.body as { username?: string; password?: string; role?: Role };
  if (!username || !password || !role || !["ADMIN", "CONTROL_ROOM"].includes(role)) return res.status(400).json({ error: "Username, password, and role are required" });
  const result = await pool.query("SELECT * FROM mvx_users WHERE username = $1", [username]);
  const row = result.rows[0] as Record<string, unknown> | undefined;
  if (!row || row.role !== role || row.is_active === false || !passwordMatches(password, String(row.password_hash))) {
    return res.status(401).json({ error: "Invalid username or password" });
  }
  const user = { id: String(row.id), username: String(row.username), role: row.role as Role };
  res.json({ accessToken: encodeToken(user), user: userResponse(row) });
});

router.get("/auth/me", (req, res) => {
  const user = requireAuth(req as AuthedRequest, res);
  if (!user) return;
  void pool.query("SELECT * FROM mvx_users WHERE id = $1", [user.id]).then((result) => {
    const row = result.rows[0] as Record<string, unknown> | undefined;
    if (!row) return res.status(401).json({ error: "User no longer exists" });
    res.json(userResponse(row));
  }).catch(() => res.status(500).json({ error: "Unable to load user" }));
});

router.post("/auth/logout", (req, res) => {
  if (!requireAuth(req as AuthedRequest, res)) return;
  res.status(204).send();
});

const webauthnUnavailable = (_req: Request, res: Response) => {
  res.status(501).json({
    error: "WEBAUTHN_NOT_CONFIGURED",
    message: "DEVELOPMENT ONLY — WebAuthn not configured",
  });
};
router.post("/auth/webauthn/register/options", (req, res) => {
  if (!requireAuth(req as AuthedRequest, res, ["ADMIN"])) return;
  webauthnUnavailable(req, res);
});
router.post("/auth/webauthn/register/verify", (req, res) => {
  if (!requireAuth(req as AuthedRequest, res, ["ADMIN"])) return;
  webauthnUnavailable(req, res);
});
router.post("/auth/webauthn/authenticate/options", (req, res) => {
  if (!requireAuth(req as AuthedRequest, res, ["ADMIN"])) return;
  webauthnUnavailable(req, res);
});
router.post("/auth/webauthn/authenticate/verify", (req, res) => {
  if (!requireAuth(req as AuthedRequest, res, ["ADMIN"])) return;
  webauthnUnavailable(req, res);
});

router.get("/system/status", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res, ["ADMIN"])) return;
  try {
    const [vehicles, devices, incidents] = await Promise.all([
      pool.query("SELECT COUNT(*)::int AS count FROM mvx_vehicles"),
      pool.query("SELECT COUNT(*)::int AS count FROM mvx_devices WHERE connection_status = 'CONNECTED'"),
      pool.query("SELECT COUNT(*)::int AS count FROM mvx_incidents WHERE status = 'ACTIVE'"),
    ]);
    res.json({
      backend: "healthy",
      database: "healthy",
      websocket: "ready",
      authentication: "ready",
      registeredVehicles: vehicles.rows[0].count,
      connectedDevices: devices.rows[0].count,
      activeIncidents: incidents.rows[0].count,
    });
  } catch {
    res.status(503).json({ backend: "healthy", database: "unavailable", websocket: "ready", authentication: "ready" });
  }
});

router.get("/auth/users", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res, ["ADMIN"])) return;
  const result = await pool.query("SELECT * FROM mvx_users ORDER BY created_at DESC");
  res.json(result.rows.map((row) => userResponse(row)));
});

router.post("/auth/users", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res, ["ADMIN"])) return;
  const { username, password, role, displayName } = req.body as { username?: string; password?: string; role?: Role; displayName?: string };
  if (!username || !password || !displayName || !["ADMIN", "CONTROL_ROOM"].includes(role ?? "")) {
    return res.status(400).json({ error: "username, password, role, and displayName are required" });
  }
  const newId = id("usr");
  try {
    const result = await pool.query(
      "INSERT INTO mvx_users (id, username, password_hash, role, display_name) VALUES ($1, $2, $3, $4, $5) RETURNING *",
      [newId, username, passwordHash(password), role, displayName],
    );
    res.status(201).json(userResponse(result.rows[0]));
  } catch {
    res.status(409).json({ error: "Username already exists" });
  }
});

router.get("/vehicles", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res)) return;
  const result = await pool.query("SELECT * FROM mvx_vehicles ORDER BY updated_at DESC");
  res.json(result.rows.map(vehicleResponse));
});

router.post("/vehicles", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res, ["ADMIN"])) return;
  const { id: vehicleId, name, type, deviceIdentifier, deviceSecret } = req.body as Record<string, string | undefined>;
  if (!vehicleId || !name || !type || !deviceIdentifier || !deviceSecret || deviceSecret.length < 8) {
    return res.status(400).json({ error: "Vehicle and device details are required; device secret must be at least 8 characters" });
  }
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    await client.query(
      "INSERT INTO mvx_vehicles (id, name, type, registration_status, operational_status, connection_status, speed, speed_limit, visibility) VALUES ($1, $2, $3, 'WAITING_FOR_CONNECTION', 'OFFLINE', 'WAITING_FOR_CONNECTION', 0, 30, 'CLEAR')",
      [vehicleId, name, type],
    );
    const deviceId = id("dev");
    await client.query(
      "INSERT INTO mvx_devices (id, identifier, secret_hash, vehicle_id, connection_status) VALUES ($1, $2, $3, $4, 'WAITING_FOR_CONNECTION')",
      [deviceId, deviceIdentifier, passwordHash(deviceSecret), vehicleId],
    );
    await client.query("UPDATE mvx_vehicles SET device_id = $1 WHERE id = $2", [deviceId, vehicleId]);
    await client.query("COMMIT");
    const result = await client.query("SELECT * FROM mvx_vehicles WHERE id = $1", [vehicleId]);
    const vehicle = vehicleResponse(result.rows[0]);
    broadcastRealtime("vehicle_created", vehicle);
    res.status(201).json(vehicle);
  } catch (error) {
    await client.query("ROLLBACK");
    const message = error instanceof Error && error.message.includes("duplicate") ? "Vehicle ID or device identifier already exists" : "Unable to register vehicle";
    res.status(409).json({ error: message });
  } finally {
    client.release();
  }
});

router.put("/vehicles/:vehicleId/speed-limit", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res)) return;
  const speedLimit = Number(req.body?.speedLimit);
  if (!Number.isFinite(speedLimit) || speedLimit < 1 || speedLimit > 120) return res.status(400).json({ error: "Speed limit must be between 1 and 120 km/h" });
  const result = await pool.query("UPDATE mvx_vehicles SET speed_limit = $1, updated_at = NOW() WHERE id = $2 RETURNING *", [speedLimit, req.params.vehicleId]);
  if (!result.rowCount) return res.status(404).json({ error: "Vehicle not found" });
  const vehicle = vehicleResponse(result.rows[0]);
  broadcastRealtime("speed_limit_updated", vehicle);
  res.json(vehicle);
});

router.get("/devices", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res)) return;
  const result = await pool.query("SELECT * FROM mvx_devices ORDER BY identifier");
  const devices = result.rows.map(deviceResponse);
  res.json(devices);
});

router.get("/devices/:deviceId", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res)) return;
  const result = await pool.query("SELECT * FROM mvx_devices WHERE id = $1", [req.params.deviceId]);
  if (!result.rowCount) return res.status(404).json({ error: "Device not found" });
  res.json(deviceResponse(result.rows[0]));
});

router.post("/hardware/telemetry", async (req, res) => {
  const body = req.body as Record<string, unknown>;
  const required = ["deviceIdentifier", "deviceSecret", "timestamp", "speedKmh", "lat", "lng", "visibilityState", "gpsHealthy", "sensorHealthy", "cameraHealthy"];
  if (required.some((field) => body[field] === undefined || body[field] === null)) return res.status(400).json({ error: "Invalid telemetry payload" });
  const { deviceIdentifier, deviceSecret, timestamp, speedKmh, lat, lng, visibilityState, gpsHealthy, sensorHealthy, cameraHealthy } = body;
  if (Number(speedKmh) < 0 || Number(lat) < -90 || Number(lat) > 90 || Number(lng) < -180 || Number(lng) > 180) return res.status(400).json({ error: "Invalid telemetry values" });
  const deviceResult = await pool.query("SELECT * FROM mvx_devices WHERE identifier = $1", [deviceIdentifier]);
  const device = deviceResult.rows[0] as Record<string, unknown> | undefined;
  if (!device) return res.status(401).json({ error: "Unknown device" });
  if (!passwordMatches(String(deviceSecret), String(device.secret_hash))) return res.status(403).json({ error: "Invalid device credential" });
  const vehicleResult = await pool.query("SELECT * FROM mvx_vehicles WHERE id = $1", [device.vehicle_id]);
  if (!vehicleResult.rowCount) return res.status(409).json({ error: "Device not associated with vehicle" });
  const vehicleBefore = vehicleResult.rows[0] as Record<string, unknown>;
  const timestampDate = new Date(String(timestamp));
  if (Number.isNaN(timestampDate.getTime())) return res.status(400).json({ error: "Invalid telemetry timestamp" });
  const client = await pool.connect();
  const createdIncidents: Record<string, unknown>[] = [];
  try {
    await client.query("BEGIN");
    await client.query(
      "INSERT INTO mvx_telemetry (id, device_id, vehicle_id, timestamp, speed_kmh, lat, lng, visibility_state, gps_healthy, sensor_healthy, camera_healthy) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)",
      [id("tel"), device.id, device.vehicle_id, timestampDate, speedKmh, lat, lng, visibilityState, gpsHealthy, sensorHealthy, cameraHealthy],
    );
    await client.query(
      "UPDATE mvx_devices SET connection_status = 'CONNECTED', last_seen = NOW(), gps_healthy = $1, sensor_healthy = $2, camera_healthy = $3 WHERE id = $4",
      [gpsHealthy, sensorHealthy, cameraHealthy, device.id],
    );
    await client.query(
      "UPDATE mvx_vehicles SET registration_status = 'REGISTERED', operational_status = $1, connection_status = 'CONNECTED', speed = $2, lat = $3, lng = $4, visibility = $5, updated_at = NOW() WHERE id = $6",
      [Number(speedKmh) > 0 ? "RUNNING" : "IDLE", speedKmh, lat, lng, visibilityState, device.vehicle_id],
    );
    const incidentInputs: Array<[string, string, string]> = [];
    if (Number(speedKmh) > Number(vehicleBefore.speed_limit)) incidentInputs.push(["OVERSPEED", "HIGH", `Speed ${Number(speedKmh).toFixed(1)} km/h exceeds limit ${Number(vehicleBefore.speed_limit).toFixed(1)} km/h`]);
    if (!gpsHealthy) incidentInputs.push(["GPS", "HIGH", "GPS health is degraded"]);
    if (!sensorHealthy) incidentInputs.push(["SENSOR", "HIGH", "Vehicle sensor health is degraded"]);
    if (!cameraHealthy) incidentInputs.push(["CAMERA", "MEDIUM", "Camera health is degraded"]);
    if (["LOW", "FOG", "CRITICAL"].includes(String(visibilityState))) incidentInputs.push(["LOW_VISIBILITY", String(visibilityState) === "CRITICAL" ? "CRITICAL" : "MEDIUM", `Visibility state is ${visibilityState}`]);
    for (const [type, severity, message] of incidentInputs) {
      const incidentId = id("inc");
      const inserted = await client.query(
        "INSERT INTO mvx_incidents (id, vehicle_id, type, severity, status, message) VALUES ($1,$2,$3,$4,'ACTIVE',$5) RETURNING *",
        [incidentId, device.vehicle_id, type, severity, message],
      );
      createdIncidents.push(incidentResponse({ ...inserted.rows[0], vehicle_name: vehicleBefore.name }));
    }
    await client.query("COMMIT");
  } catch {
    await client.query("ROLLBACK");
    return res.status(500).json({ error: "Telemetry could not be stored" });
  } finally {
    client.release();
  }
  const updated = await pool.query("SELECT * FROM mvx_vehicles WHERE id = $1", [device.vehicle_id]);
  const vehicle = vehicleResponse(updated.rows[0]);
  broadcastRealtime("telemetry_updated", vehicle);
  for (const incident of createdIncidents) broadcastRealtime("incident_created", incident);
  res.json({ accepted: true, vehicle, incidentsCreated: createdIncidents });
});

router.get("/incidents", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res)) return;
  const result = await pool.query("SELECT i.*, v.name AS vehicle_name FROM mvx_incidents i JOIN mvx_vehicles v ON v.id = i.vehicle_id ORDER BY i.created_at DESC");
  res.json(result.rows.map(incidentResponse));
});

router.get("/incidents/:incidentId", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res)) return;
  const result = await pool.query("SELECT i.*, v.name AS vehicle_name FROM mvx_incidents i JOIN mvx_vehicles v ON v.id = i.vehicle_id WHERE i.id = $1", [req.params.incidentId]);
  if (!result.rowCount) return res.status(404).json({ error: "Incident not found" });
  res.json(incidentResponse(result.rows[0]));
});

router.post("/incidents/:incidentId/claim-resolution", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res)) return;
  const result = await pool.query(
    "SELECT i.*, v.name AS vehicle_name, v.speed, v.speed_limit, v.connection_status, d.gps_healthy, d.sensor_healthy, d.camera_healthy FROM mvx_incidents i JOIN mvx_vehicles v ON v.id = i.vehicle_id LEFT JOIN mvx_devices d ON d.vehicle_id = v.id WHERE i.id = $1",
    [req.params.incidentId],
  );
  const incident = result.rows[0] as Record<string, unknown> | undefined;
  if (!incident) return res.status(404).json({ error: "Incident not found" });
  const safe = Number(incident.speed) <= Number(incident.speed_limit) && incident.connection_status === "CONNECTED" && incident.gps_healthy === true && incident.sensor_healthy === true;
  if (!safe) {
    const rejected = incidentResponse({ ...incident, status: "REJECTED" });
    broadcastRealtime("resolution_rejected", rejected);
    return res.json({ incident: rejected, accepted: false, message: "Resolution Claim Rejected – Issue Still Active." });
  }
  const updated = await pool.query("UPDATE mvx_incidents SET status = 'RESOLVED', resolved_at = NOW() WHERE id = $1 RETURNING *", [req.params.incidentId]);
  const resolved = incidentResponse({ ...updated.rows[0], vehicle_name: incident.vehicle_name });
  broadcastRealtime("incident_resolved", resolved);
  res.json({ incident: resolved, accepted: true, message: "Incident resolved after backend safety verification." });
});

router.get("/trips", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res)) return;
  const result = await pool.query("SELECT t.*, v.name AS vehicle_name FROM mvx_trips t LEFT JOIN mvx_vehicles v ON v.id = t.vehicle_id ORDER BY t.created_at DESC");
  res.json(result.rows.map((row) => ({
    id: row.id, name: row.name, source: row.source, destination: row.destination,
    assignmentStatus: row.assignment_status, vehicleId: row.vehicle_id, vehicleName: row.vehicle_name ?? null,
    completedCycles: row.completed_cycles, createdAt: iso(row.created_at),
  })));
});

router.post("/trips", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res)) return;
  const { name, source, destination } = req.body as Record<string, string | undefined>;
  if (!name || !source || !destination) return res.status(400).json({ error: "Trip name, source, and destination are required" });
  const result = await pool.query(
    "INSERT INTO mvx_trips (id, name, source, destination, assignment_status) VALUES ($1,$2,$3,$4,'FREE') RETURNING *",
    [id("trip"), name, source, destination],
  );
  const trip = { id: result.rows[0].id, name, source, destination, assignmentStatus: "FREE", vehicleId: null, vehicleName: null, completedCycles: 0, createdAt: iso(result.rows[0].created_at) };
  broadcastRealtime("trip_created", trip);
  res.status(201).json(trip);
});

router.post("/trips/:tripId/assign", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res)) return;
  const vehicleResult = await pool.query("SELECT * FROM mvx_vehicles WHERE id = $1", [req.body?.vehicleId]);
  const vehicle = vehicleResult.rows[0] as Record<string, unknown> | undefined;
  if (!vehicle) return res.status(404).json({ error: "Vehicle not found" });
  if (vehicle.registration_status !== "REGISTERED" || vehicle.connection_status !== "CONNECTED") return res.status(409).json({ error: "Only registered and connected vehicles may be assigned" });
  const result = await pool.query("UPDATE mvx_trips SET assignment_status = 'ASSIGNED', vehicle_id = $1 WHERE id = $2 AND assignment_status = 'FREE' RETURNING *", [vehicle.id, req.params.tripId]);
  if (!result.rowCount) return res.status(409).json({ error: "Trip not found or already assigned" });
  const row = result.rows[0];
  const trip = { id: row.id, name: row.name, source: row.source, destination: row.destination, assignmentStatus: "ASSIGNED", vehicleId: vehicle.id, vehicleName: vehicle.name, completedCycles: row.completed_cycles, createdAt: iso(row.created_at) };
  broadcastRealtime("trip_assigned", trip);
  res.json(trip);
});

router.post("/trips/:tripId/unassign", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res)) return;
  const result = await pool.query("UPDATE mvx_trips SET assignment_status = 'FREE', vehicle_id = NULL WHERE id = $1 RETURNING *", [req.params.tripId]);
  if (!result.rowCount) return res.status(404).json({ error: "Trip not found" });
  const row = result.rows[0];
  const trip = { id: row.id, name: row.name, source: row.source, destination: row.destination, assignmentStatus: "FREE", vehicleId: null, vehicleName: null, completedCycles: row.completed_cycles, createdAt: iso(row.created_at) };
  broadcastRealtime("trip_updated", trip);
  res.json(trip);
});

router.get("/dashboard/summary", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res)) return;
  const stale = await pool.query(
    "UPDATE mvx_devices SET connection_status = 'CONNECTION_LOST' WHERE connection_status = 'CONNECTED' AND last_seen < NOW() - ($1 || ' milliseconds')::interval RETURNING vehicle_id",
    [CONNECTION_TIMEOUT_MS],
  );
  const staleVehicleIds = stale.rows.map((row) => row.vehicle_id as string);
  if (staleVehicleIds.length) {
    await pool.query(
      "UPDATE mvx_vehicles SET connection_status = 'CONNECTION_LOST', operational_status = 'OFFLINE', updated_at = NOW() WHERE id = ANY($1::text[])",
      [staleVehicleIds],
    );
    for (const vehicleId of staleVehicleIds) {
      const existing = await pool.query(
        "SELECT id FROM mvx_incidents WHERE vehicle_id = $1 AND type = 'COMMUNICATION' AND status = 'ACTIVE' LIMIT 1",
        [vehicleId],
      );
      if (!existing.rowCount) {
        const incident = await pool.query(
          "INSERT INTO mvx_incidents (id, vehicle_id, type, severity, status, message) VALUES ($1,$2,'COMMUNICATION','HIGH','ACTIVE','No authenticated telemetry received within the configured timeout') RETURNING *",
          [id("inc"), vehicleId],
        );
        broadcastRealtime("incident_created", incidentResponse({ ...incident.rows[0], vehicle_name: vehicleId }));
      }
    }
  }
  const [vehicles, incidents, trips, cycles] = await Promise.all([
    pool.query("SELECT * FROM mvx_vehicles"),
    pool.query("SELECT COUNT(*)::int AS count, COUNT(*) FILTER (WHERE severity = 'CRITICAL')::int AS critical FROM mvx_incidents WHERE status = 'ACTIVE'"),
    pool.query("SELECT COUNT(*)::int AS count FROM mvx_trips"),
    pool.query("SELECT COALESCE(SUM(completed_cycles),0)::int AS count FROM mvx_trips"),
  ]);
  const rows = vehicles.rows as Record<string, unknown>[];
  res.json({
    totalActiveVehicles: rows.filter((v) => v.registration_status === "REGISTERED").length,
    connectedVehicles: rows.filter((v) => v.connection_status === "CONNECTED").length,
    runningVehicles: rows.filter((v) => v.operational_status === "RUNNING").length,
    idleVehicles: rows.filter((v) => v.operational_status === "IDLE").length,
    activeIncidents: incidents.rows[0].count,
    criticalAlerts: incidents.rows[0].critical,
    trips: trips.rows[0].count,
    completedCycles: cycles.rows[0].count,
  });
});

router.get("/safety/overview", async (req, res) => {
  if (!requireAuth(req as AuthedRequest, res)) return;
  const result = await pool.query("SELECT v.*, d.gps_healthy, d.sensor_healthy, d.camera_healthy FROM mvx_vehicles v LEFT JOIN mvx_devices d ON d.vehicle_id = v.id ORDER BY v.id");
  res.json(result.rows.map((row) => ({ vehicle: vehicleResponse(row), gpsHealthy: row.gps_healthy ?? false, sensorHealthy: row.sensor_healthy ?? false, cameraHealthy: row.camera_healthy ?? false, safetyStatus: Number(row.speed) <= Number(row.speed_limit) && row.gps_healthy !== false && row.sensor_healthy !== false && row.connection_status === "CONNECTED" ? "SAFE" : "UNSAFE" })));
});

export default router;