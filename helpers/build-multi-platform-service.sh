#!/bin/bash

SCRIPT_DIR=$(dirname $(realpath $0))

set -e
# Create a clean working environment
WORK_DIR="$SCRIPT_DIR/build"
OCI_IMAGE_DIR="$WORK_DIR/oci_image_modified"
OCI_IMAGE_TAR="$WORK_DIR/oci_image.tar"
FITA_IMAGE_TAR="$WORK_DIR/fita_service.tar"

EMBSERVE_SERVICE=${EMBSERVE_SERVICE?:'Missing embserve service.json path'}
EMBSERVE_SERVICE_CONFIG=${EMBSERVE_SERVICE_CONFIG?:'Missing embserve service config.json'}

TAG=latest
IMAGE_NAME=${IMAGE_NAME?:Missing image name}
IMAGE_REFERENCE="$IMAGE_NAME:$TAG"

# Ensure the working directory exists
mkdir -p $WORK_DIR

# Step 1: Build multi-platform image with docker buildx
echo "Building multi-platform Docker image..."
docker buildx build \
    -t $IMAGE_REFERENCE \
    --output type=oci,dest=$OCI_IMAGE_TAR \
    --platform linux/amd64,linux/arm64,linux/arm/v7,linux/arm/v5 \
    .

# Step 2: Prepare the OCI image for editing
pushd $WORK_DIR > /dev/null

# Copy necessary artifacts (service.json and config.json)
echo "Copying artifacts..."
cp $EMBSERVE_SERVICE .
cp $EMBSERVE_SERVICE_CONFIG .

# Unpack the OCI image
rm -rf $OCI_IMAGE_DIR
mkdir -p $OCI_IMAGE_DIR
echo "Extracting OCI image..."
tar -xf $OCI_IMAGE_TAR -C $OCI_IMAGE_DIR

# Step 3: Modify the image using ORAS (push new artifacts)
echo "Modifying OCI image with ORAS..."
oras push --oci-layout $OCI_IMAGE_DIR:$TAG \
    --config config.json:application/vnd.oci.image.config.v1+json \
    service.json:application/vnd.embserve.v1+json

# Clean up the artifacts (service.json and config.json)
rm service.json config.json

# Step 4: Handle index.json modifications
echo "Updating OCI image index..."
chmod -R +w $OCI_IMAGE_DIR
OUTER_INDEX_PATH="$OCI_IMAGE_DIR/index.json"
oras_entry=$(jq ".manifests[] | select(.artifactType == \"application/vnd.oci.image.config.v1+json\")" $OUTER_INDEX_PATH)
cp $OUTER_INDEX_PATH $OUTER_INDEX_PATH.tmp
jq "del(.manifests[] | select(.artifactType == \"application/vnd.oci.image.config.v1+json\"))" $OUTER_INDEX_PATH.tmp > $OUTER_INDEX_PATH
cp $OUTER_INDEX_PATH $OUTER_INDEX_PATH.tmp
tag=$(jq -r ".annotations[\"org.opencontainers.image.ref.name\"]" <<< $oras_entry)
jq ".manifests[].annotations[\"org.opencontainers.image.ref.name\"] = \"$tag\"" $OUTER_INDEX_PATH.tmp > $OUTER_INDEX_PATH
rm $OUTER_INDEX_PATH.tmp

echo "Move the embserve service artifact to the inner index and update annotations..."
image_index=$(jq ".manifests[] | select(.mediaType == \"application/vnd.oci.image.index.v1+json\")" $OUTER_INDEX_PATH)
sha256_hash=$(jq -r ".digest" <<< $image_index) 
hash_value=$(echo $sha256_hash | cut -d: -f2)
INNER_INDEX_PATH="$OCI_IMAGE_DIR/blobs/sha256/$hash_value"

#I need to add oras_entry to the manifests array in the inner index, removing any annotations and adding the platform details for zephyr/arm/v7
oras_entry=$(jq 'del(.annotations)' <<< $oras_entry | jq '.platform = {"architecture": "arm", "os": "zephyr", "variant": "v7"}')
cp $INNER_INDEX_PATH $INNER_INDEX_PATH.tmp
chmod +w $INNER_INDEX_PATH
jq --argjson entry "$oras_entry" '.manifests += [$entry]' $INNER_INDEX_PATH.tmp > $INNER_INDEX_PATH
rm $INNER_INDEX_PATH.tmp

# The I need to calculate the digest of the inner index with the updated changes and modify the outer index to reflect them, updating both size and digest
new_digest=$(sha256sum $INNER_INDEX_PATH | cut -d " " -f 1)
new_size=$(stat -c %s $INNER_INDEX_PATH)
mv $INNER_INDEX_PATH "$OCI_IMAGE_DIR/blobs/sha256/$new_digest"
cp $OUTER_INDEX_PATH $OUTER_INDEX_PATH.tmp
jq --arg old_digest "$sha256_hash" --arg new_digest "sha256:$new_digest" '.manifests |= map(if .digest == $old_digest then .digest = $new_digest else . end)' "$OUTER_INDEX_PATH.tmp" > "$OUTER_INDEX_PATH"
cp $OUTER_INDEX_PATH $OUTER_INDEX_PATH.tmp
jq --arg digest "sha256:$new_digest" --argjson new_size "$new_size" '.manifests |= map(if .digest == $digest then .size = $new_size else . end)' "$OUTER_INDEX_PATH.tmp" > "$OUTER_INDEX_PATH"
rm $OUTER_INDEX_PATH.tmp

# This is a placeholder for your specific implementation of manipulating the index.json
# Use sha256sum and other required steps to adjust your index as needed.
# Be sure to replace the 'index.json' manipulation with actual commands.

# Step 5: Repack the modified OCI image and prepare for Docker load
echo "Repacking OCI image..."
tar -cf $FITA_IMAGE_TAR -C $OCI_IMAGE_DIR .

# Clean up the extracted OCI image directory
rm -rf $OCI_IMAGE_DIR

# Step 6: Load the image into Docker
echo "Loading image into Docker..."
docker load -i $FITA_IMAGE_TAR

# Clean up temporary files
popd > /dev/null
rm -rf $WORK_DIR
set +e

echo "Process complete!"
