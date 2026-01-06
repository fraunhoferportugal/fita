---
sidebar_position: 1
---

# Introducing FITA

**FITA** (Far-edge IoT device mAnagement) is a framework that **integrates Far-edge IoT device in Kubernetes**, allowing them to be part of the Kubernetes orchestration and lifecycle monitoring procedures. **Far-edge IoT devices** in the context of FITA **are** the devices **equipped with sensors and actuators** that sense and act in the environment in which they are installed. Additionally, these devices are composed of microcontrollers, which **do not have enough resources to run the Kubernetes Kubelet**.

The Figure below details FITA's architecture, highlighting the main components that allow integrating Far-edge IoT devices in the Kubernetes cluster.

![FITA Architecture](/img/CompleteSolution.png)

* **embServe** is the runtime of Far-edge IoT devices. It implements a service-oriented architecture, allowing the deployment and update of services (or workloads) independently of the base firmware using standard protocols and data models. Thus, when installed in Far-edge IoT devices, embServe removes the need for full-flash updates by enabling the dynamic modification of the device behaviour through the deployment and update of different workloads that can run simultaneously on the device.

* **NextGenGW** is the gateway that addresses the heterogeneity of Far-edge IoT devices regarding communication protocols and data models. It exposes Far-edge devices following the IETF SDF semantic definition format, bound with MQTT. It homogenises communication with heterogeneous Far-edge devices using a single communication protocol and data model. 

* **Far-edge Node Watcher** is responsible for monitoring the installation and removal of Far-edge devices. When a new Far-edge device is connected, NextGenGW publishes the details of this device in the "announce" topic. When a Far-edge device is disconnected, NextGenGW publishes such an event in the "unregister" topic. The Far-edge Node Watcher subscribes to these topics and creates or deletes the digital representations of Far-edge devices in the Kubernetes cluster by creating or deleting the Far-edge Kubelet associated with them.

* **Far-edge Kubelet** bridges Kubernetes with the Far-edge devices. It instantiates a virtual node in the Kubernetes cluster that is associated with the Far-edge device it is responsible for, and connects to the Kubernetes control plane through the Kubernetes API as a standard Kubelet. Following this strategy allows the Kuberentes control plane to look at the virtual nodes associated with Far-edge devices as regular nodes in the cluster and consider them for scheduling. The workload deployment commands are received by the Far-edge Kubelet, which downloads the Far-edge Kubelet workload from an OCI-compliant registry and deploys it in the Far-edge device by interacting with the NextGenGW. 

In [Getting Started](./getting-started/intro.md), we use an hands-on example to further explains how are Far-edge devices added and represented in the Kubernetes cluster, as well as how to deploy workloads on Far-edge devices.