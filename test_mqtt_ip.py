#!/usr/bin/env python3
import json
import time
import paho.mqtt.client as mqtt

def test_mqtt_publish_ip():
    """Test MQTT connection using IP address instead of localhost"""
    
    client = mqtt.Client()
    
    try:
        print("Connecting to MQTT broker at 192.168.0.141...")
        client.connect("192.168.0.141", 1883, 60)
        client.loop_start()
        
        # Test data matching ESP32 sensor format
        test_data = {
            "lux": 200.5,
            "temperature": 24.3,
            "moisture": 52,
            "battery": 91
        }
        
        print(f"Publishing test data: {test_data}")
        result = client.publish("rooty/sensors", json.dumps(test_data), qos=0)
        
        if result.rc == 0:
            print("✅ Test message published successfully to IP address")
        else:
            print("❌ Failed to publish test message")
            
        time.sleep(1)
        client.loop_stop()
        client.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_mqtt_publish_ip()