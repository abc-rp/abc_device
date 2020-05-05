import paho.mqtt.client as mqtt
import json
import ssl
from datetime import datetime as dt
from udmi import Pointset
import csv
from pandas.io.json import json_normalize
import subprocess

# method to convert the timestamp found in the csv to the format we prefer
def format_timestamp(timestamp):
    datetime_timestamp = dt.strptime(timestamp[:19], "%Y-%m-%d %H:%M:%S")
    return datetime_timestamp

print("creating the connection ")
mqttc = mqtt.Client("")
mqttc.username_pw_set("DB_T1_L_1_TotalUseage/arup@myapp.iot", password="password")
mqttc.tls_set(ca_certs="./fakelerootx1.pem", cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
mqttc.connect("mqtt.abc.re.je", 30883)
mqttc.loop_start()
i=1

with open('./projectscene_weatherdata.csv') as f:
    reader = csv.reader(f)
    csv_headings = next(reader)
    tps_col = csv_headings.index('outdoorTemperature')
    hms_col = csv_headings.index('outdoorHumidity')
    raingauge_col = csv_headings.index('rainGauge')
    windspeed_col = csv_headings.index('windSpeed')
    windvane_col = csv_headings.index('windVane')
    timestamp_col = csv_headings.index('readingTime')
    # sensor_col = [tps_col, hms_col, raingauge_col, windspeed_col, windvane_col]
    sensor_col = [tps_col]
    # subprocess.call(["hat", "device", "create", "DB_T1_L_2_TotalUseage/arup"])
    # subprocess.call(["hat", "creds", "add-password", "DB_T1_L_2_TotalUseage/arup", "DB_T1_L_2_TotalUseage/arup", "password"])
    # hat device create DB_T1_L_1_TotalUseage/arup
    while True:
        row = next(reader)
        timestamp = row[timestamp_col]
        for j in sensor_col:
            value = float(row[j])
            points = {
                "reading_value": {
                    "present_value": value
                }
            }
            asset_name = csv_headings[j] + '-%06i' % i
            topic = asset_name
            print(4 * "-" + " " + topic + 4 * "-")
            payload = str(Pointset(format_timestamp(timestamp), points))
            payload_norm = json_normalize(json.loads(payload)).to_json(orient='records').strip('[]')
            print(payload_norm)
            i=i+1
            infot = mqttc.publish("telemetry", payload_norm, qos=1)
            infot.wait_for_publish()
# time.sleep(30)
# mqttc.loop_stop()
