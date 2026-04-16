# Rooty Server

## Getting Started

To launch project locally:

```bash
PYTHONPATH=src uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

## Project Overview

This project consists of 3 smaller projects:

### 1. Data Gathering

A small DIY device that gathers data about the soil and environment the plants grow in. The data that is being collected currently:

- Soil moisture
- Temperature
- Light intensity

Ideally, we would also want to measure pH and integrate it into our circuit board. However, we will leave it for the future.

The device utilizes the ESP32 microcontroller which gathers the data from sensors (C++ code) and via WiFi sends data to the home server which then exposes data via API.

### 2. Home Server and Python Backend

That is this project. It serves as the middleware between the data gathering board and visualization in the app.

#### Current Functions:

**Daily Light Integral (DLI) calculation:**

It measures how much light the plant gets over the course of a day, which is often used across communities who grow plants.

**Main feature - Watering prediction with ML:**

Based on historical data, ML predicts when the soil will reach the minimum moisture limit for a specific plant. We can use this data to estimate how often we need to water our plants.

### 3. App (Not yet connected)

The interface with which users interact. In the app we display all the data visually, receive notifications, and provide the ability to see how our plants perform. Currently we do not have this implemented, therefore for this project we will rely on AI to generate us an interface for our currently implemented logic just for the purpose of demonstrating the data visualization and testing.
