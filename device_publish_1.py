#!/usr/bin/python3
"""
Test paho <-> hono comms
"""
# import context
import paho.mqtt.client as mqtt
import json
import ssl
import random

DEVICE = "test_device"
#DEVICE = "sensor1"
TENANT = "myapp.iot"
USERNAME = "%s@%s" % (DEVICE, TENANT)
PASSWORD = ""
#PASSWORD = "hono-secret"
CA_CERTS = "fakelerootx1.pem"
MQTT_ADAPTER_IP = "mqtt.abc.re.je"
MQTT_ADAPTER_PORT = 30883
METRIC_NAME = "test"


mqttc = mqtt.Client("")
mqttc.username_pw_set(USERNAME, password=PASSWORD)

mqttc.tls_set(ca_certs=CA_CERTS, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
mqttc.connect(MQTT_ADAPTER_IP, MQTT_ADAPTER_PORT) # mqtt.abc.re.je == 35.242.131.248:30883  
mqttc.loop_start()
msg = json.dumps({METRIC_NAME: random.random()*100})
print(msg)
infot = mqttc.publish("telemetry", msg, qos=1)
infot.wait_for_publish()

# mosquitto_pub -h $MQTT_ADAPTER_IP -u $MY_DEVICE@$MY_TENANT -P $MY_PWD -t telemetry -m '{"temp": 5}'
