#!/bin/sh

# prerequisite: hat

gcloud container clusters get-credentials abc-dns --zone europe-west2-c --project sodium-apex-265111

REGISTRY_HOST=registry.abc.re.je:31443
#REGISTRY_IP=$(kubectl get service hono-service-device-registry-ext --output='jsonpath={.status.loadBalancer.ingress[0].ip}' -n hono)
#HTTP_ADAPTER_IP=$(kubectl get service hono-adapter-http-vertx --output='jsonpath={.status.loadBalancer.ingress[0].ip}' -n hono)
#MQTT_ADAPTER_IP=$(kubectl get service hono-adapter-mqtt-vertx --output='jsonpath={.status.loadBalancer.ingress[0].ip}' -n hono)
TOKEN=$(kubectl -n enmasse-infra describe secret $(kubectl -n enmasse-infra get secret | grep default-token | awk '{print $1}') | grep token: | awk '{print $2}')

if [ "$4" != "" ]; then
	echo "gateway name: " $1 
    echo "tenant name: " $2
	echo "context name: " $3
    echo "registry host: " $REGISTRY_HOST 
	#echo "registry IP: " $REGISTRY_IP
	#echo "HTTP adapter IP: " $HTTP_ADAPTER_IP
	#echo "MQTT adapter IP: " $HTTP_ADAPTER_IP
	echo "token: " $TOKEN
	#curl --insecure -X POST -i -H 'Content-Type: application/json' -H "Authorization: Bearer ${TOKEN}" https://$REGISTRY_HOST/v1/devices/$2/$1
    hat context create $3 https://$REGISTRY_HOST/v1 --insecure --tenant $2 --token $TOKEN
    hat device create $1
    hat creds add-password $1 $1 $4
    #hat device create WEATHER-wind
    #hat device set-via WEATHER-wind WEATHER-gw
    #hat device create WEATHER-humidity
    #hat device set-via WEATHER-humidity WEATHER-gw
    #hat device create WEATHER-temperature
    #hat device set-via WEATHER-temperature WEATHER-gw
	echo " "
else
	#echo "\n---\ndevices:"
	#curl --insecure -X GET -i -H "Authorization: Bearer ${TOKEN}" https://$REGISTRY_HOST/v1/devices/
	#echo "\n---\ntenants:"
	#curl --insecure -X GET -i -H "Authorization: Bearer ${TOKEN}" https://$REGISTRY_HOST/v1/tenants/
	echo " "
	echo "please provide the name of the device to be registered, a tenant name, a context name and a password"
	echo "./register_device.sh gateway_name tenant_name context_name password"
fi
