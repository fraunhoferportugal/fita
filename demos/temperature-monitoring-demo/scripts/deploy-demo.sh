#!/bin/bash
set -e

DIR=$(cd "$(dirname "$0")" && pwd)
EMBSERVE_ROOT_FOLDER="$DIR/../services/embserve"
GRAFANA_ROOT_FOLDER="$DIR/../services/grafana"

REGISTRY_FITA_URL="harbor.nbfc.io/mlsysops/fita"

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
microk8s helm install fita-tig oci://$REGISTRY_FITA_URL/tig --version 0.1.0
pushd $GRAFANA_ROOT_FOLDER && microk8s kubectl apply -f ./service.yaml && popd

# build and deploy sensor data image
microk8s helm install sensor-data-collector oci://$REGISTRY_FITA_URL/charts/simple-sensor-data-collector --version 0.1.0

# deploy prometheus
echo "Deploying Prometheus stack..."
microk8s helm install fita-metrics prometheus-community/kube-prometheus-stack --set grafana.enabled=false

# add devices
docker container run --name embserve_nodes \
  --privileged \
  --network host \
  -v /dev/pts/:/dev/pts/ \
  -v $EMBSERVE_ROOT_FOLDER/temperature_sensor/workspace:/workspace \
  -d $REGISTRY_FITA_URL/iotnetemu:0.1.0 "--workspace /workspace"

# waiting for all services
echo "Waiting for all services to be up..."
sleep 5

# connect devices to nextgengw
docker exec -d embserve_nodes socat UDP4-LISTEN:5683,fork,so-bindtodevice=lnxbr-0,reuseaddr UDP4:$MY_IP:30009

# setup Grafana
GRAFANA_PASSWORD=$(microk8s kubectl get secret fita-tig-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo)
pushd $GRAFANA_ROOT_FOLDER
echo "Importing Grafana dashboard..."
./import.sh -l http://localhost:30101 -u admin -p $GRAFANA_PASSWORD -t $(microk8s kubectl get secret fita-tig-influxdb2-auth -o jsonpath="{.data.admin-token}" | base64 --decode ; echo)
popd

echo -e "\n\nTemperature Monitoring Demo deployed successfully"
echo "Grafana URL: http://$MY_IP:30101"
echo "User: admin Password: $GRAFANA_PASSWORD"
echo -e "\nDeploy temperature monitoring service: microk8s kubectl apply -f $EMBSERVE_ROOT_FOLDER/deployment.yaml"
