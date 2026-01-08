---
sidebar_position: 4
---
# Workload Communication Adapter
Far-Edge devices are highly heterogeneous regarding their communication protocols and data models. To address this heterogeneity, NextGenGW abstracts Far-Edge devices heterogeneity with MQTT and IETF SDF (see [Introducing FITA](../index.md) for details). However, the resulting communication interface may not match the interface expected by consumer applications or be consistent with the interfaces exposed by workload versions targeting different platforms (check [Multi-platform Images](multi-platform-images.md) docs). FITA provides the Workload Communication Adapter mechanism to enable transparent communication with Far-Edge workload versions. 

Suppose we want to create a Far-Edge version of a previously existing workload, but, because of the underlying communication stack with LWM2M over COAP and BLE, the device cannot effectively support the existing HTTP API. NextGenGW acts as a bridge between the device and the rest of the cluster, translating device communication into MQTT messages following the IETF SDF data model. However, these protocols and data formats are still not compatible with the HTTP API the workload consumers expect. A Workload Communication Adapter can be used to translate between the two protocols and APIs.

The Workload Communication Adapter mechanism should guarantee that:
- Workloads running on different platforms are not distinguishable by components outside the deployment system.
- The communication interface is the same regardless of the platform the workload is running on and the underlying network stack. 

The Far-Edge workload developer is responsible for implementing the Communication Adapter. which is deployed and has its lifecycle managed by the `far-edge-kubelet`. With this approach, the workloads or clients that were interacting with a workload with Far-Edge and non-Far-Edge versions are not aware of the particularities of the Far-Edge version and continue interacting with it independently of where it is deployed.

## Implementation Details
The Workload Communication Adapter is specified through annotations in the PodTemplate of workloads that can be deployed to a Far-Edge Node. 
These annotations are processed by the `far-edge-kubelet` during workload deployment.

The Communication Adapter is deployed **after** the Far-Edge device reports the workload is running successfully, but **before** the Pod status is reported to the Kubernetes API.
It runs as a standalone Pod controlled by a Kubernetes deployment with a single replica. It should be scheduled to a node capable of exposing the desired interface.
The IP of the Pod representing the workload in the Far-Edge node is set to the IP of its Communication Adapter, effectively routing all traffic destined for the workload through the Adapter.

When the workload Pod is removed, so is the deployment controlling the Communication Adapter, completing its lifecycle.

The configuration annotations available are:
| Annotation | Description | Type | Default | Example |
| --- | --- | --- | --- | --- |
| `communication-adapter.fita/image` | Image to be used as the Communication Adapter | string | - |  `"example.com/fita/temperature-service-adapter:0.0.1"` |
| `communication-adapter.fita/ports` | Ports exposed by the “Adapter” Pod | json string | - |  `"[{\"name\":\"http\", \"port:\" 80, \"protocol\": \"TCP\"}]"` |
| `communication-adapter.fita/service-name` | Name of the property exposed by the Far-Edge service in the node’s SDF representation | string | - |  `"Temperature"` |
| `communication-adapter.fita/pull-policy` | Image pull policy to be used in the “Adapter” deployment  | string | `"IfNotPresent"` |  `"Always"` |

## Using the Workload Communication Adapter
Below is an example of how to configure FITA to deploy a Workload Communication Adapter.

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
      annotations:
        "communication-adapter.fita/image": "example.com/fita/temperature-service-adapter:0.0.1"
        "communication-adapter.fita/pull-policy": "Always"
        "communication-adapter.fita/ports": "[{\"name\":\"http\",\"port:\"80,\"protocol\":\"TCP\"}]"
        "communication-adapter.fita/service-name": "Temperature"
      labels:
        app: temperature
    spec:
      containers:
      - name: temperature
        image: example.com/fita/temperature_service:0.0.1
        imagePullPolicy: Always
      nodeSelector:
          extra.resources.fhp/temperature_sensor: "true"
      tolerations:
        - key: "fita.fhp.pt/type"
          operator: "Equal"
          value: "far-edge"
          effect: "NoSchedule"
```