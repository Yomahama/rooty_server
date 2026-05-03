## Rules

- After making any changes to the code, run the analyzer and resolve all warnings and errors before considering the task complete.
- Follow a consistent architecture throughout the project. If a block of code belongs in a separate file based on its responsibility, create that file and place the code there. Suggest architectural improvements when you identify them.
- All code, including variable names, function names, and file names, must be written in English. Abbreviations must be widely understood or defined on first use.
- Do not write inline comments or block comments in the code.
- Always add final newline
- Use lazy % formatting in logging functions
- Apply trailing whitespace linter rule
- If new packages are added, make sure to active the enviroment with source .venv/bin/activate and run pip install there

## Project Overview

Rooty Server is a plant monitoring backend system that collects sensor data (moisture, temperature, light) from ESP32 devices via MQTT, performs machine learning-based watering predictions using LSTM neural networks, and provides REST APIs for data access and visualization.

## Development Commands

### Running the Application

```bash
# Local Development
PYTHONPATH=src uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
python src/mqtt_client.py
python test_mqtt.py

# Docker Development
docker-compose up --build

# Docker Production
docker-compose up -d
```

### Code Quality

```bash
# Run pylint (configured in pyproject.toml)
pylint src/

# Install dependencies
pip install -r requirements.txt
```

## Architecture Overview

### Core Components

**Data Pipeline:**

1. **MQTT Client** (`src/mqtt_client.py`) - Receives sensor data from ESP32 devices
2. **Database Layer** (`src/core/database.py`) - SQLite database with measurements and plants tables
3. **API Layer** (`src/api/routes/`) - FastAPI REST endpoints for data access
4. **ML Pipeline** (`src/services/prediction_service.py`) - LSTM-based moisture prediction

**Key Services:**

- `SensorService` - Handles sensor data CRUD operations
- `PredictionService` - ML model training and moisture predictions
- `DliService` - Daily Light Integral calculations
- `PlantService` - Plant profile management

### Database Schema

**measurements table:**

- id, lux, temperature, moisture, battery, timestamp

**plants table:**

- id, name, dli_min/max, temp_min/max, moisture_min/max
- Seeded with default plants: Braškės (Strawberries), Pomidorai (Tomatoes), Salotos (Lettuce)

### Machine Learning Configuration

LSTM model configuration in `src/config/prediction_config.py`:

- Sequence length: 144 steps (2.4 hours at 1-minute intervals)
- Features: moisture, temperature, lux (normalized)
- Prediction horizon: 864 steps (3 days at 5-minute intervals)
- Auto-retraining: Daily at 2 AM via scheduler

Model file: `sensor_lstm.keras` (saved/loaded automatically)

### Data Flow

1. ESP32 → MQTT broker → `mqtt_client.py` → SQLite database
2. FastAPI app serves data via REST endpoints
3. Scheduler triggers daily model retraining
4. ML service provides watering predictions based on historical patterns

### Project Structure

```
src/
├── api/routes/          # FastAPI route handlers
├── core/               # Database and configuration
├── config/            # ML model configuration
├── models/            # Pydantic data models
├── repos/             # Data access layer
├── services/          # Business logic layer
├── shedulers/         # Background task scheduling
└── main.py           # FastAPI application entry point
```

## Deployment

### Docker Compose Setup

The application runs as three services:
- **mosquitto**: MQTT broker (port 1883)
- **fastapi**: REST API server (port 8001)
- **mqtt_client**: Background service for processing sensor data

### Server Requirements

For production deployment:
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com | sh
sudo apt install docker-compose-plugin

# Open MQTT port
sudo ufw allow 1883/tcp

# Deploy
docker-compose up -d
```

### ESP32 Configuration

For server deployment, update ESP32 code:
```cpp
#define MQTT_SERVER "your-server-ip-or-domain"
#define MQTT_PORT 1883
#define MQTT_TOPIC "rooty/sensors"
#define MQTT_CLIENT_ID "rooty_esp32"
```

## Development Notes

- Uses SQLite for data storage (persisted via Docker volumes)
- Python path must include src/ directory for imports
- MQTT broker hostname configurable via MQTT_BROKER_HOST environment variable
- Model retrains automatically when sufficient data available
- Data generation utility (`src/generate_data.py`) creates mock sensor readings for testing
