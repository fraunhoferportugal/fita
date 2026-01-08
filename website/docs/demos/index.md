---
sidebar_position: 1
---

# Introduction

We have prepared some [FITA Demos](https://github.com/fraunhoferportugal/fita/tree/docs/main/demos) that can be easily deployed in your Kubernetes cluster while providing interactive examples of FITA in action. Therefore, you can use these demos to experiment the main FITA features.

```shell
git clone https://github.com/fraunhoferportugal/fita.git
```

Before diving into the example demos, you should make sure that you have all the required frameworks and tools, which are listed in the [requirements](#requirements) section.

## Requirements

The following list present the main requirements for trying any Demo:

- [Kubernetes Distribution](/fita/docs/getting-started/intro#microk8s)
  - We developed and tested FITA demos using [MicroK8s](https://microk8s.io/#install-microk8s).
  - [K3s](https://docs.k3s.io/quick-start), [kind](https://kind.sigs.k8s.io/docs/user/quick-start/), and [k0s](https://docs.k0sproject.io/stable/install/) are possible alternatives.
- [FITA](/fita/docs/getting-started/intro#fita)
- [IoTNetEmu](/fita/docs/getting-started/intro#iotnetemu)
- [Docker Engine](https://docs.docker.com/engine/install/)

## Demos

After installing and preparing all the requirements, you are finally able to easily deploy and experiment any FITA Demo. 

Here you can find a simple description for each available demo:

- [Temperature Monitoring Demo](#temperature-monitoring-demo)

### Temperature Monitoring Demo

This demonstrator showcases FITA by presenting a temperature monitoring setup using two (emulated) Far-Edge nodes built on top of a Kubernetes cluster. A custom component is deployed across the cluster to collect temperature data from the Far-Edge nodes. FITA is the core component of this demonstrator as it is responsible of enabling the connectivity to the Far-Edge devices and allowing the data collection. The goal of this demo is the simulation of a real-world monitoring scenario that collects environment metrics.

[Try Demo 🚀](./temperature-monitoring-demo.mdx)
