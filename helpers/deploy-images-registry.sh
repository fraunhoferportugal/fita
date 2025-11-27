#!/bin/bash

set -e

# include constants and functions
DIR=$(cd "$(dirname "$0")" && pwd)
source $DIR/.config
source $DIR/utils.sh

# main
main () {
  # Build and deploy Far Edge Kubelet
  pushd $FAR_EDGE_KUBELET_DIR
  echo "Building and deploying Far Edge Kubelet image..."
  deploy-component-registry fhp/far-edge-kubelet
  popd

  # Build and deploy Far Edge Node Watcher
  pushd $FAR_EDGE_NODE_WATCHER_DIR
  echo "Building and deploying Far Edge Node Watcher image..."
  deploy-component-registry fhp/far-edge-node-watcher
  popd

  # Build and deploy Far Edge Connection Provisioner
  pushd $FAR_EDGE_CONNECTION_PROVISIONER_DIR
  echo "Building and deploying Far Edge Connection Provisioner image..."
  deploy-component-registry fhp/far-edge-connection-provisioner
  popd

  echo "Done!"
}

main
