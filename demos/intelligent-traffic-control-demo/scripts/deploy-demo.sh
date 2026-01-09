#!/bin/bash
set -e

DIR=$(cd "$(dirname "$0")" && pwd)
GRAFANA_ROOT_FOLDER="$DIR/../services/grafana"
EMBSERVE_SERVICE_ROOT_FOLDER="$DIR/../services/embserve"
INTEL_ROOT_FOLDER="$DIR/intel"

REGISTRY_FITA_URL="ghcr.io/fraunhoferportugal/fita"

MY_IP=$(ifconfig enp86s0 | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1')

echo "Adding prometheus repository"
microk8s helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
microk8s helm repo update

# deploy fita
microk8s helm install fita oci://$REGISTRY_FITA_URL --version 0.1.0

# The default pullPolicy is set to Always. Use the following command if you want to avoid pulling images in every installation 
# microk8s helm install fita oci://$REGISTRY_FITA_URL --version 0.1.0 \
#   --set mqttBroker.image.pullPolicy=IfNotPresent \
#   --set nextgengw.image.pullPolicy=IfNotPresent \
#   --set far-edge-node-watcher.image.pullPolicy=IfNotPresent \
#   --set far-edge-node-watcher.farEdgeKubelet.image.pullPolicy=IfNotPresent \
#   --set far-edge-connection-provisioner.image.pullPolicy=IfNotPresent

# deploy tig and external grafana service
microk8s helm install fita-tig oci://$REGISTRY_FITA_URL/demos/common/charts/tig --version 0.1.0
pushd $GRAFANA_ROOT_FOLDER && microk8s kubectl apply -f ./service.yaml && popd

# deploy prometheus
echo "Deploying Prometheus stack..."
microk8s helm install fita-metrics prometheus-community/kube-prometheus-stack --set grafana.enabled=false --set prometheus.prometheusSpec.scrapeInterval=5s

echo "Deploy intel plugin to use GPU in kubernetes"
pushd $INTEL_ROOT_FOLDER
./deploy-intel-gpu-plugin.sh
popd

echo "Deploying Video Component module..."
microk8s helm install video-component oci://$REGISTRY_FITA_URL/demos/intelligent-traffic-control/charts/video-component --version 0.1.0

echo "Deploying Sensor Consumer module..."
microk8s helm install sensor-consumer oci://$REGISTRY_FITA_URL/demos/intelligent-traffic-control/charts/noise-sensor-consumer --version 0.1.0

# add devices
docker container run --name embserve_nodes \
  --privileged \
  --network host \
  -v /dev/pts/:/dev/pts/ \
  -v $EMBSERVE_SERVICE_ROOT_FOLDER/noise_service/workspace:/workspace \
  -d $REGISTRY_FITA_URL/components/iotnetemu:0.1.0 "--workspace /workspace"

# waiting for all services
echo "Waiting for all services to be up... (5s)"
sleep 5

# connect devices to nextgengw
docker exec -d embserve_nodes socat UDP4-LISTEN:5683,fork,so-bindtodevice=lnxbr-0,reuseaddr UDP4:$MY_IP:30009

# Setup Grafana
GRAFANA_PASSWORD=$(microk8s kubectl get secret fita-tig-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo)
pushd $GRAFANA_ROOT_FOLDER
echo "Importing Grafana dashboard..."

# Update IP address of grafana
GRAFANA_FRAME_LINE='\t\t\t\t\t"content": "<p style=\\\"text-align: center\\\"> <iframe width=\\\"889\\\" height=\\\"500\\\" src=http://'$MY_IP':30100/stream.html?src=mystream> </iframe> </p>",'
sed "143c \ $GRAFANA_FRAME_LINE" -i dashboard.json

./import.sh -l http://localhost:30101 -u admin -p $GRAFANA_PASSWORD -t $(microk8s kubectl get secret fita-tig-influxdb2-auth -o jsonpath="{.data.admin-token}" | base64 --decode ; echo)
popd

echo -e "\n\nMLSysOps Use Case Demo deployed"
echo "Grafana URL: http://$MY_IP:30101"
echo "User: admin Password: $GRAFANA_PASSWORD"
echo -e "\nVideo Stream: http://$MY_IP:30100/stream.html?src=mystream"
echo -e "\nFITA Services:"
echo "MQTT Broker: coap://$MY_IP:30010"
echo "NextGenGW COAP: coap://$MY_IP:30009"
echo -e "\nDeploy noise service: microk8s kubectl apply -f $EMBSERVE_SERVICE_ROOT_FOLDER/deployment.yaml"
