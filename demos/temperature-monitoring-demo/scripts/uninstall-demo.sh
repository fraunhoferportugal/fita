#!/bin/bash

SCRIPT_NAME=$(basename "$0")
DIR=$(cd "$(dirname "$0")" && pwd)
ROOT_FOLDER="$DIR/../../../"

# Remove all deployments
microk8s kubectl delete $(microk8s kubectl get deployments -o name | grep temperature-deployment) > /dev/null 2>&1
microk8s helm uninstall fita-tig
microk8s helm uninstall fita-metrics
microk8s helm uninstall fita
microk8s helm uninstall sensor-data-collector

# Remove services
microk8s kubectl delete service fita-tig-grafana-ext

# Remove persistent volumnes
microk8s kubectl delete persistentvolumeclaims fita-tig-influxdb2

sleep 5

# Remove existing far-edge-kubelets
echo "Removing existing far-edge-kubelets"
for pod in $(microk8s kubectl get pods -A -o name | grep far-edge-kubelet); do
  # Remove the 'pod/' prefix
  pod_name=${pod#pod/}

  # Extract the node name suffix from the pod name
  node_name=$(echo "$pod_name" | sed 's/^far-edge-kubelet-//')

  echo "Deleting pod: $pod_name"
  microk8s kubectl delete pod "$pod_name"

  echo "Deleting node: $node_name"
  microk8s kubectl delete node "$node_name"
done

for deployment in $(microk8s kubectl get deployments -A -o name | grep far-edge-kubelet); do
  microk8s kubectl delete "$deployment"
done

# Stopping embserve_nodes docker container
echo "Removing embserve_nodes docker container"
docker rm $(docker stop embserve_nodes) > /dev/null 2>&1
