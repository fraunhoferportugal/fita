---
sidebar_position: 2
---
# Multi-platform Images

:::note[TL;DR]
FITA workloads use multi-platform OCI images that include a special platform entry, zephyr/armv7, which stores an embServe service as an OCI artifact instead of a conventional container image.
This lets both FITA-managed devices and Kubernetes-managed devices pull the same image reference, while each device retrieves the format appropriate to its runtime environment.
:::


FITA is designed to work alongside devices other than microcontrollers, not bound by the constrained resources of these devices.
This means that some workloads may need to run both on devices managed by FITA, running embServe workloads,
and on devices directly managed by Kubernetes, capable of executing other container runtimes.

To support transparent workload migration between FITA-managed devices and Kubernetes-managed ones using the same Kubernetes deployment,
we extend Multi-platform Container Images[^1] to include an entry for the `zephyr/armv7` platform storing the embServe workload as an [OCI artifact](https://oras.land/docs/concepts/artifact).
By using this approach we ensure the same reference in a OCI registry can provide container runtimes with the appropriate image for their platform.

This means that if the Multi-platform Image with the reference `example.com/fita/temperature-sensor:0.0.1` supports the embServe platform (`zephyr/armv7`) and a conventional platform such as a x86_64 linux machine running containerd (`linux/amd64`) any of these devices or their proxies can retrieve the workload when using the reference.
When a workload is assigned to a FITA-managed node, the `far-edge-kubelet` component retrieves the embServe workload from the OCI artifact present in the image with platform `zephyr/armv7`, deploying it and enabling it to the device running embServe. When any other device is assigned with it, its `kubelet` will delegate image pulling to the configured container runtime, which will pull and run the appropriate image to the device platform, if one is available.

[^1]: Documentation on Multi-platform Images:
    - [The OpenContainers Image Index Spec](https://specs.opencontainers.org/image-spec/image-index/?v=v1.1.1)
    - [Docker Multi-platform builds](https://docs.docker.com/build/building/multi-platform/)

## Creating a Multi-platform Image with support for embServe workloads
We provide an example script of how you can create Multi-platform images on your own from an embServe service, for the devices supported by FITA, and a conventional `Dockerfile` for other platforms.

### Requirements
- [jq](https://jqlang.org/)
- [ORAS](https://oras.land)
- docker with support for multi-platform image builds and image storage - see [docker documentation](https://docs.docker.com/build/building/multi-platform/#prerequisites)
- An embServe service ready to be pushed to an OCI registry - see [Pushing embServe Service to OCI registry (steps 1-4)](../getting-started/workloads.md#pushing-embserve-service-to-oci-registry)

### Overview
To build a multi-platform image the example script automates the following steps:
1. Build a multi-platform image using `docker` and the `Dockerfile` provided by the workload developer.
2. Unpack the created image to a directory in the OCI Image layout.
3. Use oras to push the artifact containing the embServe service
    - Service in `service.json`
    - Platform configuration provided in `config.json`
4. Backup the service artifact from the image index 
5. Modify the artifact entry in the image index to declare an image manifest for the embServe platform
6. Update the image manifest for the embServe platform with the service artifact
7. Update the index entry of step 5 with the hashes and size of the updated image manifest
8. Repack the OCI image layout into an archive and load it to the docker registry

After these steps, the OCI image layout will have the following entries:
```
example.com/fita/temperature-sensor:0.0.1
│
└── Image Index
    ├── linux/amd64      → container image manifest 
    ├── linux/arm64      → container image manifest
    └┬─ zephyr/armv7     → empty container image manifest
     └── OCI artifact    → embServe service
```

:::note
ORAS has better support for multi-platform images and artifacts since version 1.3.
We plan to revisit how to ease the creation of Multi-platform images with support for embServe workloads in a near future.
:::

### How to use the script
The multi-platform image build script is available as an helper script in the fita repo: ([build-multi-platform-service.sh](https://github.com/fraunhoferportugal/fita/blob/main/helpers/build-multi-platform-service.sh)).

Download it and make it executable:
```bash
wget https://raw.githubusercontent.com/fraunhoferportugal/fita/refs/heads/main/helpers/build-multi-platform-service.sh && chmod +x build-multi-platform-service.sh
```

To use this script, place it in the directory with the context and Dockerfile for your image, update the path for the embServe service `service.json` and `config.json` files, and update the name and tag of the image by setting the following environment variables:
```bash
EMBSERVE_SERVICE=${EMBSERVE_SERVICE?:'Missing embserve service.json path'}
EMBSERVE_SERVICE_CONFIG=${EMBSERVE_SERVICE_CONFIG?:'Missing embserve service config.json'}

TAG=latest
IMAGE_NAME=${IMAGE_NAME?:Missing image name}
# IMAGE_REFERENCE="$IMAGE_NAME:$TAG" # This variable is set in by the script.
```
You can then simply run the script with:
```bash
./build-multi-platform-service.sh
```
After the process has finished, push the image normally:
```bash
docker tag <IMAGE-NAME>:<IMAGE-TAG> <REMOTE-REPOSITORY>/<IMAGE-NAME>:<IMAGE-TAG>
docker push <REMOTE-REPOSITORY>/<IMAGE-NAME>:<IMAGE-TAG>
```
This publishes a unified multi-platform image containing both the conventional container workloads and the embServe artifact.

## Using Multi-platform Images with FITA
To use the images created with the previous steps, use the image reference normally in your Kubernetes workloads, as such:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: temperature-deployment
  labels:
    app: temperature
spec:
  replicas: 2
  selector:
    matchLabels:
      app: temperature
  template:
    metadata:
      labels:
        app: temperature
    spec:
      containers:
      - name: temperature
        image: example.com/fita/temperature-service:0.0.1
        imagePullPolicy: Always
      nodeSelector:
        extra.resources.fhp/temperature_sensor: "true"
      tolerations:
        - key: "fita.fhp.pt/type"
          operator: "Equal"
          value: "far-edge"
          effect: "NoSchedule"
```

:::warning[Node selectors and Tolerations]
Make sure to select devices that report having the desired IoT components with node selectors and to tolerate any taint keeping workloads from executing on embServe nodes (far-edge taint).
:::

:::warning[Communicating transparantly with embServe and container workloads]
Due to the communication constraints of Far-Edge IoT devices, workloads running in these devices may not expose the same APIs as their container conterparts. FITA supports communication adapters to proxy Far-Edge workloads communication through compatible APIs. Check the [Workload Communication Adapter](./workload-communication-adapter) docs.
:::
