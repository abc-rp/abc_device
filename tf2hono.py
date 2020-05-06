#!/usr/bin/env python3

# Tinkerforge to Hono
# Capture data from Tinkerforge devices and publish it to Hono

## Setup devices inc. gateway
# hat device create gateway_name
# hat creds add-password gateway_name gateway_name password
# hat device create sensor_name
# hat device set-via sensor_name gateway_name
## Setup container (host on which the script is run)
# podman --runtime crun run --rm -it registry.fedoraproject.org/fedora-minimal
# microdnf -y install tinkerforge python3-paho-mqtt
# wget https://letsencrypt.org/certs/fakelerootx1.pem
# <copy over script>

# Gateway HOUSE-gw
# Temperature sensor TPS-1
# Humidity sensor HMS-1
# Lighting photocell sensor LPS-1

# import sched
import time
import paho.mqtt.client as mqtt
import json
import ssl
import os
import udmi
from datetime import datetime as dt
import dateutil.parser
from pandas.io.json import json_normalize

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_ambient_light_v2 import BrickletAmbientLightV2
from tinkerforge.bricklet_temperature import BrickletTemperature
from tinkerforge.bricklet_humidity import BrickletHumidity
from tinkerforge.bricklet_sound_intensity import BrickletSoundIntensity
from tf_device_ids import deviceIdentifiersList
from tf_device_ids import deviceIdentifiersDict

GATEWAY = "HOUSE-gw"
TENANT = "myapp.iot"
USERNAME = "%s@%s" % (GATEWAY, TENANT)
PASSWORD = "password"
CA_CERTS = "fakelerootx1.pem"
MQTT_ADAPTER_IP = "mqtt.abc.re.je"
MQTT_ADAPTER_PORT = 30883
TF_CONNECT = True
TF_HOST = "192.168.1.113"
TF_PORT = 4223
INTERVAL = 5
DEBUG = True
PUBLISH = True

TPS1_UID = 'zEo'
HMS1_UID = 'xB2'
LPS1_UID = 'yAd'

if TF_CONNECT:
    tfIDs = []

#deviceIDs = [i[0] for i in deviceIdentifiersList]
deviceIDs = [item for item in deviceIdentifiersDict]

if DEBUG:
    print(deviceIDs)
    for dID in deviceIDs:
        print(deviceIdentifiersDict[dID])

def getIdentifier(ID):
    deviceType = ""
    # for t in deviceIdentifiers:
        # if ID[1]==t[0]:
        #     #print(ID,t[0])
        #     deviceType = t[1]
    for t in deviceIDs:
        if ID[1]==t:
            #print(ID,t[0])
            deviceType = deviceIdentifiersDict[t]["type"]
    return(deviceType)

# Tinkerforge sensors enumeration
def cb_enumerate(uid, connected_uid, position, hardware_version, firmware_version,
                 device_identifier, enumeration_type):
    global tfIDs
    tfIDs.append([uid, device_identifier])

def main():
    global tfIDs
    mqttc = mqtt.Client("")
    mqttc.username_pw_set(USERNAME, password=PASSWORD)
    mqttc.tls_set(ca_certs="{}/fakelerootx1.pem".format(os.getcwd()), certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
    mqttc.connect(MQTT_ADAPTER_IP, MQTT_ADAPTER_PORT) # mqtt.abc.re.je == 35.242.131.248:30883
    mqttc.loop_start()

    if TF_CONNECT:
        # Create connection and connect to brickd
        ipcon = IPConnection()

        TPS1_bricklet = BrickletTemperature(TPS1_UID, ipcon)
        HMS1_bricklet = BrickletHumidity(HMS1_UID, ipcon) 
        LPS1_bricklet = BrickletAmbientLightV2(LPS1_UID, ipcon)

        ipcon.connect(TF_HOST, TF_PORT)

        # Register Enumerate Callback
        ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE, cb_enumerate)

        # Trigger Enumerate
        ipcon.enumerate()

        time.sleep(2)
    
    if DEBUG:
        print(tfIDs)
        
    if PUBLISH:

        # Get current temperature
        TPS1 = TPS1_bricklet.get_temperature()/100.0
        HMS1 = HMS1_bricklet.get_humidity()/10.0
        LPS1 = LPS1_bricklet.get_illuminance()/100.0

        today = dt.now().strftime("%Y-%m-%d %H:%M")
        today_0 = dt.now().strftime("%Y-%m-%d 00:00")
        t = dt.now().strftime("%H:%M")
        # dtt = dateutil.parser.parse(today)
        dtt = dt.utcnow()

        points_TPS1 = {}
        points_TPS1["temperature"] = {"present_value": TPS1}

        points_HMS1 = {}
        points_HMS1["humidity"] = {"present_value": HMS1}

        points_LPS1 = {}
        points_LPS1["illuminance"] = {"present_value": LPS1}
        
        udmi_payload_TPS1 = str(udmi.Pointset(dtt, points_TPS1))
        # print(udmi_payload_TPS1)
        udmi_payload_HMS1 = str(udmi.Pointset(dtt, points_HMS1))
        # print(udmi_payload_HMS1)
        udmi_payload_LPS1 = str(udmi.Pointset(dtt, points_LPS1))
        # print(udmi_payload_LPS1)

        payload_norm_TPS1 = json_normalize(json.loads(udmi_payload_TPS1)).to_json(orient='records').strip('[]')
        print(payload_norm_TPS1)
        payload_norm_HMS1 = json_normalize(json.loads(udmi_payload_HMS1)).to_json(orient='records').strip('[]')
        print(payload_norm_HMS1)
        payload_norm_LPS1 = json_normalize(json.loads(udmi_payload_LPS1)).to_json(orient='records').strip('[]')
        print(payload_norm_LPS1)

        # msg = json.dumps({"wind": wind, "humidity": humidity, "temperature": temperature})
        

        # infot = mqttc.publish("telemetry", udmi_payload, qos=1)
        # print("Sending {}".format(udmi_payload_TPS1))
        infot = mqttc.publish("telemetry/myapp.iot/{}".format("TPS-1"), payload_norm_TPS1, qos=1) 
        # print("Sending {}".format(udmi_payload_HMS1))
        infot = mqttc.publish("telemetry/myapp.iot/{}".format("HMS-1"), payload_norm_HMS1, qos=1) 
        # print("Sending {}".format(udmi_payload_LPS1))
        infot = mqttc.publish("telemetry/myapp.iot/{}".format("LPS-1"), payload_norm_LPS1, qos=1) 

        infot.wait_for_publish()

        # time.sleep(INTERVAL)

if __name__ == "__main__":
    main()


# import json
# import paho.mqtt.client as mqtt  # import the MQTT client
# from datetime import datetime as dt
# import os
# from time import sleep
# import ssl
# import dateutil.parser

# import udmi
# from pandas.io.json import json_normalize
# import requests
# import urllib3
# import subprocess
# import csv

# urllib3.disable_warnings()
# DEBUG = False
# VERBOSE = True

# registry_host =  os.environ.get("REGISTRY_HOST", "registry.abc.re.je:31443")
# token = os.environ['TOKEN']
# url = 'https://{}/v1'.format(registry_host)

# auth_header={'Content-Type': 'application/json','Authorization': 'Bearer {}'.format(token)}

# POINT_NAME_LOOKUP = {"LightOutput": "light_output",
#                      "LightLevelLimit": "light_level_limit",
#                      "LightOutputHours": "light_output_hours",
#                      "BinaryInput1": "binary_input_1",
#                      "BinaryInput2": "binary_input_2",
#                      "BinaryInput3": "binary_input_3",
#                      "BinaryInput4": "binary_input_4",
#                      "BinaryInputAlarm": "binary_input_alarm",
#                      "LightLevel": "light_level",
#                      "Presence": "presence"
#                      }

# def get_udmi_pointset(data):
#     device = json.loads(data)['LightingDevice']
#     if device["AssetClass"] in ('AreaController', 'ControlModule'):
#         return None
#     elif device["AssetClass"] in ("Luminaire", "Sensor"):
#         dt = dateutil.parser.parse(device["Timestamp"])
#         points = {}
#         for point_name in POINT_NAME_LOOKUP.keys():
#             point = device.get(point_name)
#             if point is not None:
#                 value = point.get("State") if point.get("State") is not None else point["Value"]
#                 points[POINT_NAME_LOOKUP[point_name]] = {"present_value": value}
#         return udmi.Pointset(dt, points)
#     else:
#         return None

# def register_device_to_gtw(device_id):
#     os.system("hat device create {}  &> /dev/null".format(str(device_id)))
#     os.system("hat device set-via {} simmtronic-gtw2 &> /dev/null".format(str(device_id)))
#     return print('{} registered and connected to simmtronic-gtw2'.format(str(device_id)))

# # The callback for when the client receives a CONNACK response from the server.
# def on_connect(client, userdata, flags, rc):
#     print("Connected to %s with result code: %s" % (client._host, str(rc)))
#     sleep(2)
#     # Subscribing in on_connect() means that if we lose the connection and
#     # reconnect then subscriptions will be renewed.
#     client.subscribe("LightingControl/#")

# # The callback for when a PUBLISH message is received from the server.
# def on_message(client, userdata, msg):
#     pl = msg.payload.decode("utf-8")
#     if DEBUG:
#         # pl = json.load(str(msg.payload))
#         print()
#         t = dt.fromtimestamp(msg.timestamp).strftime('%Y-%m-%d %H:%M:%S')
#         print(t + " - " + str(msg.timestamp) + " - " + str(msg.info) + " - " + msg.topic + "\n")
#     d = json.loads(pl)
#     asset_name = d['LightingDevice']['AssetInstance']
#     register_device_to_gtw(asset_name)
#     payload_tel = str(get_udmi_pointset(pl))
#     # print(msg.topic + "-" + str(payload_tel) + "-")
#     payload_norm = json_normalize(json.loads(payload_tel)).to_json(orient='records').strip('[]')
#     print(payload_norm)
#     ext_client.publish("telemetry/myapp.iot/{}".format(str(asset_name)), payload_norm, qos=1)  # publish MQTT topic to pi.arupiot.com

# def main():
#     global ext_client
#     print('Creating external client...')
#     ext_client = mqtt.Client("8fs-lighting-republish") # create a new MQTT client instance
#     ext_client.username_pw_set("simmtronic-gtw2@myapp.iot", password="simmtronicpass")
#     ext_client.tls_set(ca_certs="./fakelerootx1.pem", cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
#     ext_client.connect("mqtt.abc.re.je", 30883)
#     print('Creating internal client...')
#     int_client = mqtt.Client("republish-lighting") # create a new MQTT client instance
#     int_client.on_connect = on_connect
#     int_client.on_message = on_message
#     int_client.connect("iot.arup.com")
#     int_client.loop_start()
#     ext_client.loop_start()
#     sleep(2*60)
#     int_client.loop_stop()
#     ext_client.loop_stop()

# if __name__ == "__main__":
#     main()


# wind_msg = json.dumps({"wind": wind})
# print("Wind: {}".format(wind_msg))
# humidity_msg = json.dumps({"humidity": humidity})
# print("Humidity: {}".format(humidity_msg))
# temperature_msg = json.dumps({"temperature": temperature})
# print("Temperature: {}".format(temperature_msg))
# wind_pub = mqttc.publish("telemetry/myapp.iot/WEATHER-wind", wind_msg, qos=1)
# wind_pub.wait_for_publish()
# humidity_pub = mqttc.publish("telemetry/myapp.iot/WEATHER-humidity", humidity_msg, qos=1)
# humidity_pub.wait_for_publish()
# temperature_pub = mqttc.publish("telemetry/myapp.iot/WEATHER-temperature", temperature_msg, qos=1)
# temperature_pub.wait_for_publish()