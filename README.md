# Mine Vision-X
# Intelligent Driver Assistance & Fleet Safety System for Low-Visibility Mining

> **Smart India Hackathon 2026 --- Problem Statement SIH26007**\
> **Safe and Efficient Operation of Mine Vehicles in Fog and Low-Visibility Conditions in Opencast Iron Ore Mines**

# Team
Team Name: Vision Travellers  
Team ID: 152231  
Problem Statement: SIH26007  
Theme: Smart Automation  
Category: Hardware

# PROJECT OVERVIEW:
Mine Vision-X is a driver-assistance and fleet-safety system designed for heavy mine vehicles operating in fog, dust, darkness and
other low-visibility conditions in open-cast iron-ore mines. The system combines mmWave radar, thermal/IR sensing, GNSS/GPS and IMU
data to detect nearby hazards, estimate risk and provide timely driver warnings. Vehicle safety events, location and system-health information are also sent to a central fleet-monitoring dashboard for the control room. The solution is designed as a modular retrofit system that can be developed first as a low-cost prototype and then scaled toward an industrial deployment using rugged edge-AI hardware.

# PROBLEM:

Low visibility on mine haul roads can reduce a driver's ability to identify:

#Nearby vehicles and moving equipment
#People and obstacles.
#Changes in road conditions.
#Safe following and stopping distances.
#Hazards appearing ahead or in blind areas.
This creates a need for continuous vehicle-level hazard awareness together with fleet-level monitoring.

# PROPOSED SOLUTION:

Mine Vision-X uses a multi-layer approach:
Sensors → Edge Processing → Risk Detection → Driver Alerts → Communication → Fleet Dashboard On the Vehicle

77 GHz mmWave Radar --- distance and relative-motion information.
Thermal/IR Camera --- heat-based perception in darkness and degraded visibility.
GNSS/GPS --- vehicle position, speed and heading.
6-axis IMU --- motion, acceleration and orientation information.
Edge Computer --- sensor processing, fusion and risk evaluation.
Driver HMI --- visual and audio warnings.

# At the Control Room

The fleet dashboard provides:
^Live vehicle positions
^Vehicle speed and movement status
^Safety/risk events
^Vehicle and hardware health
^Risk hotspots and haul-road awareness
^Historical reports and analytics

# SYSTEM ARCHITECTURE:

<img width="1326" height="684" alt="image" src="https://github.com/user-attachments/assets/675069f7-8737-45bf-b94a-8e8a1987b375" />

# How It Works
^Sensors continuously collect vehicle, position and surrounding-object information.
^The edge system processes the sensor inputs.
^Sensor information is combined to improve hazard awareness under poor visibility.
^The risk engine evaluates factors such as distance, relative motion, visibility and Time-to-Collision (TTC).
^The vehicle receives a graded warning through the in-cab HMI when a risk condition is detected.
^Important safety events and vehicle telemetry are sent to the central server.
^The control-room dashboard displays the vehicle state, location and safety events.
^When communication is temporarily unavailable, the edge system can continue local safety processing and buffer important events for later synchronization.


# Risk Detection
A key part of Mine Vision-X is converting sensor information into an understandable risk level.
A simplified Time-to-Collision concept is:
TTC = Distance / Relative Speed

The system can combine TTC with visibility and object information to produce graded states such as:

LOW       → Normal monitoring
MEDIUM    → Caution / warning
HIGH      → Immediate driver warning
CRITICAL  → Urgent safety alert

The exact thresholds are configurable for the vehicle, road segment and deployment environment.

# Prototype vs Industrial Deployment

# The prototype can use cost-effective components such as:
Laptop/PC or Raspberry Pi as the local compute platform
24 GHz mmWave radar such as HLK-LD2450
MLX90640 or AMG8833 thermal/IR sensor
NEO-M8N GPS
MPU6050/ICM-class IMU
LoRa modules for communication experiments
Buzzer/display for driver alerts

The prototype is intended to demonstrate the complete concept:
Sensor acquisition → processing → risk logic → alert → telemetry → dashboard.

# Industrial Target

For an industrial deployment, the architecture can move to:
#Ruggedized NVIDIA Jetson Orin-class edge computing
#Industrial 77 GHz mmWave radar
#Industrial LWIR thermal camera
#High-precision RTK-GNSS
#Industrial IMU
#4G/LTE + LoRa communication
#Rugged IP66/IP67 enclosure
#Industrial in-cab HMI
#Central server and fleet-monitoring infrastructure
# The final proposal estimates an indicative industrial cost ofapproximately ₹1.97--₹3.46 lakh per vehicle, excluding shared site infrastructure.

# Technology Stack:

Layer                    Technologies / Components

Vehicle Sensors          mmWave Radar, Thermal/IR, GNSS/GPS, IMU
Prototype Compute        Laptop / Raspberry Pi / ESP32
Industrial Edge Target   NVIDIA Jetson Orin-class hardware
Communication            Wi-Fi, 4G/LTE, LoRa
Backend                  Python, FastAPI, APIs, WebSocket/real-time communication
Database                 Relational/time-series storage as required
Frontend                 React-based web dashboard
Mapping                  Live GPS/map integration
Safety Logic             Sensor fusion, TTC, configurable risk thresholds
Security                 Authentication and role-based access

# Prototype Hardware

Component                           Prototype Role

mmWave Radar                        Distance, target position and
relative movement
Thermal / IR Sensor                 Heat-based perception in low
visibility
GPS / GNSS                          Location, speed and heading
IMU                                 Acceleration, orientation and
motion
ESP32 / Raspberry Pi / Laptop       Sensor aggregation and prototype
processing
LoRa Module                         V2V/V2I communication experiment
Buzzer / Display                    Local driver warning
Wi-Fi / Network                     Prototype telemetry communication

An indicative low-cost prototype BOM described in the supporting design is approximately ₹5,100--₹12,100 per vehicle node, depending on the
selected thermal sensor and excluding an already-available laptop used as the prototype edge computer.

# Software Architecture

#Vehicle / Edge Layer
#Sensor drivers and data acquisition
#Radar processing
#Thermal/IR processing
#GNSS/GPS processing
#IMU processing
#Sensor fusion
#Visibility estimation
#Risk and TTC calculation
#Local alert generation
#Telemetry buffering and communication
#Central Layer
#Backend API / telemetry ingestion
#Vehicle and device management
#Safety-event processing
#Database storage
#Real-time communication
#Authentication and role-based access
#Dashboard Layer

The web dashboard is intended for fleet and control-room operations and provides:
#Total / running / idle / stopped / offline vehicles
#Active and critical alerts
#Live vehicle map
#Vehicle details and status
#Trip and route information
#Safety-event history
#Hardware/system health
#Reports and analytics
---
# Fleet Monitoring
Each physical vehicle is treated as an independent vehicle system with
its own sensing and edge-processing unit.

Vehicle
   ↓
Vehicle Hardware / Device
   ↓
Telemetry & Safety Events
   ↓
Central Backend
   ↓
Fleet / Control-Room Dashboard
# Communication
The proposed architecture supports hybrid communication:

Primary Communication
4G/LTE → MQTT/HTTP → Central Server
Used for regular telemetry, safety events and system health when network coverage is available.
Fallback / Safety Communication
LoRa Mesh → Gateway → Central System
Used for compact safety messages and communication in areas where cellular connectivity may be weak.
The edge system is designed to continue local safety processing even when the central connection is temporarily unavailable.
---
# Key Features

Multi-sensor hazard detection
Fog/dust/darkness-oriented perception
Distance and relative-motion monitoring
Visibility-aware risk evaluation
Time-to-Collision estimation
Graded driver warnings
Live vehicle tracking
Central safety-event monitoring
Vehicle and hardware health monitoring
Hybrid communication
Local operation during temporary connectivity loss
Scalable multi-vehicle architecture
Retrofit-oriented deployment
---
# Current Prototype Focus
The prototype focuses on validating the core safety workflow rather than
reproducing the complete industrial hardware stack.
Demonstration Flow

The prototype is intended to demonstrate that the same architecture can be extended toward industrial-grade hardware and mine deployment.
---
# Expected Impact
#Drivers
#Earlier awareness of nearby hazards
#Visual/audio warnings
#Better situational awareness in poor visibility
#Control Room
#Real-time fleet visibility
#Faster awareness of safety events
#Vehicle and communication-health monitoring
#Mine Operations
#Better haul-road traffic awareness
#Reduced disruption from avoidable incidents
#Improved support for safer and more efficient vehicle movement
#Scalable monitoring across the mining fleet
---
# Scalability
The architecture is modular and can be expanded from:
Prototype → Pilot Vehicle → Multi-Vehicle Fleet → Mine-Wide Deployment.
The same platform can also be extended to additional mining-safety use cases such as:
^Blind-spot assistance
^Hazard-zone monitoring
^PPE-related safety functions
^Reverse assistance
^Additional fleet analytics
^Expanded digital-twin capabilities
---
# Repository Structure
│
├── README.md
├── .gitignore
├── .npmrc
├── package.json
├── pnpm-lock.yaml
├── pnpm-workspace.yaml
├── tsconfig.json
├── tsconfig.base.json
│
├── frontend/
│   ├── .env.example
│   └── artifacts/
│       ├── mine-vision-x/
│       │   ├── public/
│       │   ├── src/
│       │   ├── components.json
│       │   ├── index.html
│       │   ├── package.json
│       │   ├── tsconfig.json
│       │   └── vite.config.ts
│       │
│       └── mockup-sandbox/
│
├── backend/
│   ├── .env.example
│   ├── server.py
│   └── api-server/
│       ├── src/
│       ├── build.mjs
│       ├── package.json
│       └── tsconfig.json
│
├── lib/
│   ├── api-client-react/
│   ├── api-spec/
│   ├── api-zod/
│   └── db/
│
├── raspberry-pi/
│   ├── .env.example
│   ├── client.py
│   ├── config.py
│   ├── driver_dashboard.py
│   ├── telemetry.py
│   ├── requirements.txt
│   └── README.md
│
├── simulator/
│   ├── simulator.py
│   ├── requirements.txt
│   └── README.md
│
└── scripts/
    ├── src/
    ├── package.json
    ├── post-merge.sh
    └── tsconfig.json   





