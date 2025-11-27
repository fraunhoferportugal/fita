#!/bin/bash

set -e

# include constants and functions
source $(cd "$(dirname "$0")" && pwd)/utils.sh

# main
main () {
  # Build and deploy Far Edge Kubelet
  pushd $FAR_EDGE_KUBELET_DIR
  echo "Building and deploying Far Edge Kubelet image..."
  build-component-image fhp/far-edge-kubelet
  popd

  # Build and deploy Far Edge Node Watcher
  pushd $FAR_EDGE_NODE_WATCHER_DIR
  echo "Building and deploying Far Edge Node Watcher image..."
  build-component-image fhp/far-edge-node-watcher
  popd

  # Build and deploy Far Edge Connection Provisioner
  pushd $FAR_EDGE_CONNECTION_PROVISIONER_DIR
  echo "Building and deploying Far Edge Connection Provisioner image..."
  build-component-image fhp/far-edge-connection-provisioner
  popd

  echo "Done!"
}

main
