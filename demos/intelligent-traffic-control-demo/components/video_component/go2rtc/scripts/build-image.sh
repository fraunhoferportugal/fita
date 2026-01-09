#!/bin/bash

set -e

SCRIPT_NAME=$(basename "$0")
DIR=$(cd "$(dirname "$0")" && pwd)
ROOT_FOLDER="$DIR/../"
PUBLISH_DIR=$ROOT_FOLDER/bin
IMAGE_NAME=fhp/go2rtc
IMAGE_VERSION=0.1.0

usage()
{
    echo "$SCRIPT_NAME [options]"
    echo "Note: You might have to run this as root or sudo."
    echo ""
    echo "options"
    echo " -i, --image-name     Image name (default: $IMAGE_NAME)"
    echo " -v, --image-version  Docker Image Version (default: $IMAGE_VERSION)"
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
        else
            case "$arg" in
                "-h" | "--help" ) usage;;
                "-i" | "--image-name" ) save_next_arg=1;;
                "-v" | "--image-version" ) save_next_arg=2;;
                * ) usage;;
            esac
        fi
    done
}

# process command line args
process_args "$@"

# build the Docker image
pushd "$ROOT_FOLDER"
# add --platform linux/arm64/v8 for RPI4
docker build -t "$IMAGE_NAME":"$IMAGE_VERSION" .
popd
