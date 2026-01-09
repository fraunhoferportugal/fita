#!/bin/bash

set -e

SCRIPT_NAME=$(basename "$0")
DIR=$(cd "$(dirname "$0")" && pwd)

REGISTRY_URL=localhost:30102
SERVICE_NAME=fhp/virtual_noise_sensor
SERVICE_TAG=0.0.1

pushd $DIR
oras push --plain-http $REGISTRY_URL/$SERVICE_NAME:$SERVICE_TAG --config config.json:application/vnd.oci.image.config.v1+json service.json:application/vnd.embserve.v1+json
popd