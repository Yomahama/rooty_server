#!/usr/bin/env python3
import json
import time
import paho.mqtt.client as mqtt

def test_mqtt_publish():
    """Test script to simulate IoT sensor data via MQTT"""
    
    client = mqtt.Client()
    
    try:
        print("Connecting to MQTT broker...")
        client.connect("localhost", 1883, 60)
        client.loop_start()
        
        # Test data matching your IoT sensor format
        test_data = {
            "lux": 150.2,
            "temperature": 23.1,
            "moisture": 45,
            "battery": 87
        }
        
        print(f"Publishing test data: {test_data}")
        result = client.publish("rooty/sensors", json.dumps(test_data), qos=0)
        
        if result.rc == 0:
            print("✅ Test message published successfully")
        else:
            print("❌ Failed to publish test message")
            
        time.sleep(1)
        client.loop_stop()
        client.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_mqtt_publish()