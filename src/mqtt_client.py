import json
import logging
import os
from typing import Optional
import paho.mqtt.client as mqtt
from models.sensor import SensorDataIn
from services.sensor_service import SensorService
from core.database import init_db
from shedulers.model_scheduler import model_scheduler

logger = logging.getLogger(__name__)

class MQTTSensorClient:
    def __init__(self, broker_host: str = None, broker_port: int = 1883, topic: str = "rooty/sensors"):
        self.broker_host = broker_host or os.getenv("MQTT_BROKER_HOST", "localhost")
        self.broker_port = broker_port
        self.topic = topic
        self.sensor_service = SensorService()
        self.client: Optional[mqtt.Client] = None

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )


    def on_connect(self, client, _userdata, _flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker at %s:%s", self.broker_host, self.broker_port)
            client.subscribe(self.topic, qos=0)
            logger.info("Subscribed to topic: %s", self.topic)
        else:
            logger.error("Failed to connect to MQTT broker. Return code: %s", rc)

    def on_disconnect(self, _client, _userdata, rc):
        if rc != 0:
            logger.warning("Unexpected disconnection from MQTT broker")
        else:
            logger.info("Disconnected from MQTT broker")

    def on_message(self, _client, _userdata, msg):
        payload = None
        try:
            payload = msg.payload.decode('utf-8')
            logger.info("Received message from %s: %s", msg.topic, payload)

            data = json.loads(payload)
            sensor_data = SensorDataIn(**data)

            result = self.sensor_service.save_reading(sensor_data)
            logger.info("Sensor data saved successfully: %s", result.timestamp)

        except json.JSONDecodeError as e:
            logger.error("Invalid JSON received: %s. Error: %s", payload or "unknown", e)
        except ValueError as e:
            logger.error("Invalid sensor data format: %s. Error: %s", payload or "unknown", e)
        except (UnicodeDecodeError, AttributeError) as e:
            logger.error("Error decoding message payload: %s", e)
        except Exception as e:
            logger.error("Unexpected error processing message: %s", e)

    def on_log(self, _client, _userdata, _level, buf):
        logger.debug("MQTT Log: %s", buf)

    def start(self):
        self.setup_logging()
        logger.info("Starting MQTT sensor client...")

        init_db()
        logger.info("Database initialized")

        model_scheduler.start_scheduler()
        logger.info("Model scheduler started")

        self.client = mqtt.Client(client_id="rooty_server")
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_log = self.on_log

        try:
            logger.info("Connecting to MQTT broker at %s:%s", self.broker_host, self.broker_port)
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_forever()

        except KeyboardInterrupt:
            logger.info("Shutting down MQTT client...")
            self.stop()
        except ConnectionError as e:
            logger.error("Failed to connect to MQTT broker: %s", e)
        except Exception as e:
            logger.error("Error starting MQTT client: %s", e)

    def stop(self):
        if self.client:
            self.client.disconnect()
            logger.info("MQTT client stopped")

        model_scheduler.stop_scheduler()
        logger.info("Model scheduler stopped")

if __name__ == "__main__":
    mqtt_client = MQTTSensorClient()
    mqtt_client.start()
