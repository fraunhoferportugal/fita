---
sidebar_position: 1
---

# FITA Demos

We have prepared some [FITA Demos](https://github.com/fraunhoferportugal/fita-demos.git) that can be easily deployed in your Kubernetes cluster while providing interactive examples of FITA in action. Therefore, you can use these demos to experiment the main FITA features.

```shell
git clone https://github.com/fraunhoferportugal/fita-demos.git
```

Before diving into the example demos, you should make sure that you have all the required frameworks and tools, which are listed in the [requirements](#requirements) section.

## Requirements

The following list present the main requirements for trying any Demo:

- [Kubernetes Distribution](/docs/getting-started/intro#microk8s)
  - We developed and tested FITA demos using [MicroK8s](https://microk8s.io/#install-microk8s).
  - [K3s](https://docs.k3s.io/quick-start), [kind](https://kind.sigs.k8s.io/docs/user/quick-start/), and [k0s](https://docs.k0sproject.io/stable/install/) are possible alternatives.
- [FITA](/docs/getting-started/intro#fita)
- [IoTNetEmu](/docs/getting-started/intro#iotnetemu)
- [Docker Engine](https://docs.docker.com/engine/install/)

## Demos

After installing and preparing all the requirements, you are finally able to easily deploy and experiment any FITA Demo. 

Here you can find a simple description for each available demo:

- [Temperature Monitoring Demo](#temperature-monitoring-demo)
- [Intelligent Traffic Control Demo](#intelligent-traffic-control-demo)

### Temperature Monitoring Demo

This demonstrator showcases FITA by presenting a temperature monitoring setup using two (emulated) Far-Edge nodes built on top of a Kubernetes cluster. A custom component is deployed across the cluster to collect temperature data from the Far-Edge nodes. FITA is the core component of this demonstrator as it is responsible of enabling the connectivity to the Far-Edge devices and allowing the data collection. The goal of this demo is the simulation of a real-world monitoring scenario that collects environment metrics.

[Try Demo 🚀](./temperature_monitoring-demo)

### Intelligent Traffic Control Demo

This demonstrator showcases a traffic monitoring system on a Kubernetes cluster equipped with a device featuring a noise sensor and a camera. The captured video is transmitted to a web-based streaming application, making it easily accessible for real-time monitoring. Similarly to the [Temperature Monitoring Demo](#temperature-monitoring-demo), FITA enables a custom component to collect noise data and visualize it in Grafana dashboards. To enable traffic image processing, when the noise surpasses a predefined threshold, the system triggers an AI model that processes the collected images for object detection. In a real-world scenario, this approach increases the energy efficiency by limiting image processing to noisy situations while enabling real-time traffic monitoring.

[Try Demo 🚀](./intelligent-traffic-control-demo)
