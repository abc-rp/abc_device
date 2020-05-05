#!/bin/sh

gcloud container clusters get-credentials abc-dns --zone europe-west2-c --project sodium-apex-265111

REGISTRY_HOST=registry.abc.re.je:31443
#REGISTRY_IP=$(kubectl get service hono-service-device-registry-ext --output='jsonpath={.status.loadBalancer.ingress[0].ip}' -n hono)
#HTTP_ADAPTER_IP=$(kubectl get service hono-adapter-http-vertx --output='jsonpath={.status.loadBalancer.ingress[0].ip}' -n hono)
#MQTT_ADAPTER_IP=$(kubectl get service hono-adapter-mqtt-vertx --output='jsonpath={.status.loadBalancer.ingress[0].ip}' -n hono)
TOKEN=$(kubectl -n enmasse-infra describe secret $(kubectl -n enmasse-infra get secret | grep default-token | awk '{print $1}') | grep token: | awk '{print $2}')


if [ "$2" != "" ]; then
	echo "device name: " $1 
        echo "tenant name: " $2
        echo "registry host: " $REGISTRY_HOST 
	#echo "registry IP: " $REGISTRY_IP
	#echo "HTTP adapter IP: " $HTTP_ADAPTER_IP
	#echo "MQTT adapter IP: " $HTTP_ADAPTER_IP
	echo "token: " $TOKEN
        curl --insecure -X POST -i -H 'Content-Type: application/json' -H "Authorization: Bearer ${TOKEN}" https://$REGISTRY_HOST/v1/devices/$2/$1
	echo " "
else
	#echo "\n---\ndevices:"
	#curl --insecure -X GET -i -H "Authorization: Bearer ${TOKEN}" https://$REGISTRY_HOST/v1/devices/
	#echo "\n---\ntenants:"
	#curl --insecure -X GET -i -H "Authorization: Bearer ${TOKEN}" https://$REGISTRY_HOST/v1/tenants/
	echo " "
	echo "please provide the name of the device to be registered and a tenant name"
	echo "./register_device.sh device_name tenant_name"
fi
