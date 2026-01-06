---
sidebar_position: 1
---

# Getting Started with FITA

This section explains how to use FITA to add a Far-Edge device to the Kubernetes cluster and how to deploy workloads on them. Before detailing this procedures you need to install [FITA](#fita) and [IoTNetEMU](#iotnetemu).

<!-- , the Far-edge device emulator we use in the remainder of this documentation.  -->

<!-- You can use any Kubernetes distribution to run FITA. However, in the examples and demos used in this documentation, we used microK8S version XXXX. In section [Install and Configure microK8S](#microk8s), we explain how to install and configure microK8S. Similar procedures should be done for the Kubernetes distribution of your choice. -->

## Requirements

Before running FITA, you need to ensure some dependencies are available. These are:

- [Docker](https://docs.docker.com/engine/install/)
- Kubernetes Cluster

### Kubernetes Cluster

FITA does not have any direct dependency on any Kubernetes distribution, requiring only a working cluster with at least one node. There are several options you can used to ease the setup of a cluster:

- [minikube](https://minikube.sigs.k8s.io/docs/)
- [MicroK8s](https://microk8s.io/)
- [k3s](https://k3s.io/)
- Others

Additionally, we require DNS support in the cluster and a working metrics-server.

While any of the options meet the requirements for FITA, the guides on this page are built and tested with MicroK8s. A small configuration guide for MicroK8s can be found [here](#microk8s).

For other distributions or solutions, refer to their documentation. 

#### Install and Configure MicroK8S {#microk8s}

Here we show a quick guide highlighting the minimal MicroK8s configurations to support FITA.

1. Install MicroK8s following [this](https://microk8s.io/docs/getting-started) guide
2. Enable DNS addon
```shell
microk8s enable dns
```
3. Enable metrics-server
```shell
microk8s metrics-server
```
4. Enable the built-in registry
```shell
microk8s registry
```
5. Create an alias for kubectl
```shell
alias kubectl='microk8s kubectl'
```

:::warning

IoTNetEMU modifies the network interfaces of the host. If it is launched in the same node as the one running MicroK8s, additional configurations are need to ensure the network changes do not interfere with the cluster. 

To disable MicroK8s network change monitoring, add the ```--advertise-address 0.0.0.0``` option to ```/var/snap/microk8s/current/args/kube-apiserver``` and restart MicroK8s. Refer to [this](https://github.com/canonical/microk8s/issues/2790) page for more information.

Other Kubernetes distributions might have similar issues. Refer to their documentation.

:::

## Installing FITA {#fita}

FITA is deployed using [Helm](https://helm.sh/). Depending on your setup, it may already be available in your system. If not, refer to [this](https://helm.sh/docs/intro/install/) guide.

To install FITA:

1. Create Kubernetes namespace for FITA
```shell
kubectl create namespace fita
```
2. Deploy FITA to the ```fita``` namespace
```shell
microk8s helm install fita oci://harbor.nbfc.io/mlsysops/fita --version 0.2.0 -n fita
```
3. Wait for all container images to be deployed
4. Validate that the FITA pod is running correctly
```shell
kubectl get pods -n fita
```
Which should output:
```shell
NAME                         READY   STATUS    RESTARTS   AGE
fita-fita-5cfd8bd5ff-5tcz5   4/4     Running   0          37s
```

## Installing IoTNetEMU {#iotnetemu}

IoTNetEMU is a Python framework that integrates several open-source emulation and simulation tools to create a more realistic testing and development scenario for IoT applications. It allows developers to easily validate and test an application using simple configurations and actual code with minimal adaptations.

FITA leverages IoTNetEMU to emulate Far-Edge devices running the embServe runtime, removing the need for real devices and allowing large scale testing with minimal effort.

IoTNetEMU is distributed as a Docker image and hosted in a public registry. To install IoTNetEMU:

- Create a folder to store IoTNetEMU configuration files:
```shell
mkdir ~/.iotnetemu
```

- Create the IoTNetEMU Docker container:
```shell
docker container create --name iotnetemu --network host --privileged -v /dev/pts/:/dev/pts/ -v ~/.iotnetemu:/iotnetemu/workspace -it harbor.nbfc.io/mlsysops/iotnetemu:1.0.1
```

- Start the container:
```shell
docker container start -a -i iotnetemu
```


- Validate that the container is working properly with the built-in sample:
```shell
root@<host>:/# iotnetemu --workspace /iotnetemu/samples/embserve-linux-bridge
```

- You should get the following output, where 5 nodes are started:
```shell
2025-09-09 15:47:30,004 [INFO] Setting up node node1
2025-09-09 15:47:30,005 [INFO] Setting up node node2
2025-09-09 15:47:30,005 [INFO] Setting up node node3
2025-09-09 15:47:30,006 [INFO] Setting up node node4
2025-09-09 15:47:30,008 [INFO] Setting up node node5
2025-09-09 15:47:30,012 [INFO] Skipping build for node1
2025-09-09 15:47:30,013 [INFO] Creating interfaces for node node1
2025-09-09 15:47:30,017 [INFO] Skipping build for node2
2025-09-09 15:47:30,018 [INFO] Creating interfaces for node node2
2025-09-09 15:47:30,019 [INFO] Skipping build for node3
2025-09-09 15:47:30,019 [INFO] Creating interfaces for node node3
2025-09-09 15:47:30,023 [INFO] Skipping build for node4
2025-09-09 15:47:30,025 [INFO] Creating interfaces for node node4
2025-09-09 15:47:30,029 [INFO] Skipping build for node5
2025-09-09 15:47:30,029 [INFO] Creating interfaces for node node5
2025-09-09 15:47:30,030 [INFO] Setup done, starting...
2025-09-09 15:47:30,031 [INFO] Starting node node1
2025-09-09 15:47:30,031 [INFO] Starting node node2
2025-09-09 15:47:30,031 [INFO] Starting node node3
2025-09-09 15:47:30,032 [INFO] Starting node node4
2025-09-09 15:47:30,032 [INFO] Starting node node5
2025-09-09 15:47:30,136 [INFO] Saved /dev/pts/14 path on /iotnetemu/samples/embserve-linux-bridge/build/node1/pts for node node1
2025-09-09 15:47:30,138 [INFO] Saved /dev/pts/17 path on /iotnetemu/samples/embserve-linux-bridge/build/node2/pts for node node2
2025-09-09 15:47:30,140 [INFO] Saved /dev/pts/15 path on /iotnetemu/samples/embserve-linux-bridge/build/node4/pts for node node4
2025-09-09 15:47:30,140 [INFO] Saved /dev/pts/18 path on /iotnetemu/samples/embserve-linux-bridge/build/node3/pts for node node3
2025-09-09 15:47:30,142 [INFO] Saved /dev/pts/16 path on /iotnetemu/samples/embserve-linux-bridge/build/node5/pts for node node5
2025-09-09 15:47:33,062 [INFO] Creating interfaces using linux network
2025-09-09 15:47:33,155 [INFO] linux network setup done
2025-09-09 15:47:33,155 [INFO] All done, sleeping...
```

:::info

IoTNetEMU creates networks interfaces dynamically, which requires access to the host network to ensure the emulated devices can communicate with external hosts.  

:::

For more details regarding IoTNetEMU and its configurations, refer to [here](../advanced-usage/iotnetemu.md).

<br/>
<br/>
<br/>

Now that FITA and the Far-edge device emulator is setup, we can go to [Add Far-edge Device in Kubernetes Cluster](./nodes.md), which explains with an hands-on example how are Far-edge devices added and represented in the Kubernetes cluster. [Deploy Workload on Far-edge Devices](./workloads.md) continues the hands-on example for the deployment of Far-edge device workloads.

Advanced usage, such as the implementation of custom Far-edge workloads and the integration of Far-edge workloads with workloads running on other nodes of the cluster is explained in [Create embServe Workload](../advanced-usage/create-workload.md) and [Interact with Far-edge Workload](../advanced-usage/interact-workload.md), respectively.

You can further explore FITA using the examples provided in the [demo section](../../demos/index.md).
