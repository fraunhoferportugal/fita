# folders
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)/.."
FAR_EDGE_KUBELET_DIR="$ROOT_DIR/components/far-edge-kubelet"
FAR_EDGE_NODE_WATCHER_DIR="$ROOT_DIR/components/far-edge-node-watcher"
FAR_EDGE_CONNECTION_PROVISIONER_DIR="$ROOT_DIR/components/far-edge-connection-provisioner"

# helper functions
pushd () {
  command pushd "$@" > /dev/null
}

popd () {
  command popd "$@" > /dev/null
}

get-latest-tag () {
  echo $(git describe --tags --abbrev=0)
}

build-component-image () {
  # $1 - image name
  make build-image image-name=$1 image-version=$(get-latest-tag)
}

deploy-component-registry () {
  # $1 - image name
  if [[ ! -n $REGISTRY_URL ]] || [[ ! -n $REGISTRY_REPOSITORY ]] || [[ ! -n $REGISTRY_USERNAME ]] || [[ ! -n $REGISTRY_PASSWORD ]]; then
    echo Please set REGISTRY_URL, REGISTRY_REPOSITORY, REGISTRY_USERNAME and REGISTRY_PASSWORD environmental values;
    exit;
  fi
  
  IMAGE="$1:$(get-latest-tag)"

  if [[ -z "$(docker images -q $IMAGE 2> /dev/null)" ]]; then
    build-component-image $1;
  fi

  docker login -u "$REGISTRY_USERNAME" -p "$REGISTRY_PASSWORD" $REGISTRY_URL
  docker tag "$IMAGE" "$REGISTRY_URL/$REGISTRY_REPOSITORY/$IMAGE"
  docker push "$REGISTRY_URL/$REGISTRY_REPOSITORY/$IMAGE"
}
