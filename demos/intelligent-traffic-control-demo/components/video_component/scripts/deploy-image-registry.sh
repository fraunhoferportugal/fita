#!/bin/bash

set -e

SCRIPT_NAME=$(basename "$0")
DIR=$(cd "$(dirname "$0")" && pwd)
ROOT_FOLDER="$DIR/../../"
IMAGE_NAME=fhp/video-component
IMAGE_VERSION=latest

REGISTRY_URL=127.0.0.1:5000
REGISTRY_USERNAME=username
REGISTRY_PASSWORD=password

usage()
{
    echo "$SCRIPT_NAME [options]"
    echo "Note: You might have to run this as root or sudo."
    echo ""
    echo "options"
    echo " -i, --image-name     Image name (default: $IMAGE_NAME)"
    echo " -v, --image-version  Docker Image Version (default: $IMAGE_VERSION)"
    echo " -r, --registry-url  Registry URL (default: $REGISTRY_URL)"
    echo " -u, --registry-username  Registry username (default: $REGISTRY_USERNAME)"
    echo " -p, --registry-password  Registry password (default: $REGISTRY_PASSWORD)"
    exit 1;
}

process_args()
{
    save_next_arg=0
    for arg in "$@"
    do
        if [ $save_next_arg -eq 1 ]; then
            IMAGE_NAME="$arg"
            save_next_arg=0
        elif [ $save_next_arg -eq 2 ]; then
            IMAGE_VERSION="$arg"
            save_next_arg=0
        elif [ $save_next_arg -eq 3 ]; then
            REGISTRY_URL="$arg"
            save_next_arg=0
        elif [ $save_next_arg -eq 4 ]; then
            REGISTRY_USERNAME="$arg"
            save_next_arg=0
        elif [ $save_next_arg -eq 5 ]; then
            REGISTRY_USERNAME="$arg"
            save_next_arg=0
        else
            case "$arg" in
                "-h" | "--help" ) usage;;
                "-i" | "--image-name" ) save_next_arg=1;;
                "-v" | "--image-version" ) save_next_arg=2;;
                "-r" | "--registry-url" ) save_next_arg=3;;
                "-u" | "--registry-username" ) save_next_arg=4;;
                "-p" | "--registry-password" ) save_next_arg=5;;
                * ) usage;;
            esac
        fi
    done
}

# process command line args
process_args "$@"

# push the Docker image
pushd "$ROOT_FOLDER"
docker login -u "$REGISTRY_USERNAME" -p "$REGISTRY_PASSWORD" "$REGISTRY_URL"
docker push "$REGISTRY_URL/$IMAGE_NAME:$IMAGE_VERSION"
popd
