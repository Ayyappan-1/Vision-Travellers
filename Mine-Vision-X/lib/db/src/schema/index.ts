import {
  boolean,
  integer,
  numeric,
  pgTable,
  text,
  timestamp,
} from "drizzle-orm/pg-core";

export const users = pgTable("mvx_users", {
  id: text("id").primaryKey(),
  username: text("username").notNull().unique(),
  passwordHash: text("password_hash").notNull(),
  role: text("role").notNull(),
  displayName: text("display_name").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});

export const vehicles = pgTable("mvx_vehicles", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  type: text("type").notNull(),
  registrationStatus: text("registration_status").notNull(),
  operationalStatus: text("operational_status").notNull(),
  connectionStatus: text("connection_status").notNull(),
  speed: numeric("speed").notNull().default("0"),
  speedLimit: numeric("speed_limit").notNull().default("30"),
  lat: numeric("lat"),
  lng: numeric("lng"),
  visibility: text("visibility").notNull().default("CLEAR"),
  completedCycles: integer("completed_cycles").notNull().default(0),
  deviceId: text("device_id"),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});

export const devices = pgTable("mvx_devices", {
  id: text("id").primaryKey(),
  identifier: text("identifier").notNull().unique(),
  secretHash: text("secret_hash").notNull(),
  vehicleId: text("vehicle_id").notNull().unique(),
  connectionStatus: text("connection_status").notNull(),
  lastSeen: timestamp("last_seen", { withTimezone: true }),
  gpsHealthy: boolean("gps_healthy").notNull().default(true),
  sensorHealthy: boolean("sensor_healthy").notNull().default(true),
  cameraHealthy: boolean("camera_healthy").notNull().default(true),
});

export const telemetry = pgTable("mvx_telemetry", {
  id: text("id").primaryKey(),
  deviceId: text("device_id").notNull(),
  vehicleId: text("vehicle_id").notNull(),
  timestamp: timestamp("timestamp", { withTimezone: true }).notNull(),
  speedKmh: numeric("speed_kmh").notNull(),
  lat: numeric("lat").notNull(),
  lng: numeric("lng").notNull(),
  visibilityState: text("visibility_state").notNull(),
  gpsHealthy: boolean("gps_healthy").notNull(),
  sensorHealthy: boolean("sensor_healthy").notNull(),
  cameraHealthy: boolean("camera_healthy").notNull(),
});

export const incidents = pgTable("mvx_incidents", {
  id: text("id").primaryKey(),
  vehicleId: text("vehicle_id").notNull(),
  type: text("type").notNull(),
  severity: text("severity").notNull(),
  status: text("status").notNull(),
  message: text("message").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  resolvedAt: timestamp("resolved_at", { withTimezone: true }),
});

export const trips = pgTable("mvx_trips", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  source: text("source").notNull(),
  destination: text("destination").notNull(),
  assignmentStatus: text("assignment_status").notNull(),
  vehicleId: text("vehicle_id"),
  completedCycles: integer("completed_cycles").notNull().default(0),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});