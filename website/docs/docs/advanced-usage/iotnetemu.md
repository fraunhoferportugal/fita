---
label: "What is it?"
---

# IoTNetEMU Configurations

## Nodes

In IoTNetEMU, Nodes refer IoT nodes that connect to Networks and communicate with Applications. Such Nodes are end-nodes, edge devices or even gateways and are used to emulate a complete device running real code.

To configure a Node, the configuration file shall define a node, ```node1```:

```shell
nodes:
  node1:
    type: 'zephyr'
    image: 'images/embserve-1.0.1.elf'
    bootstrap:
      - 'embserve connector lwm2m server_add coap://10.10.12.254:30009 node1'
    networks:
      linux-br:
        ipv4_address: 10.10.12.1
        ipv4_gateway: 10.10.12.254
```

- node1: defines an unique key for the node
- type: defines the node type. In the example, ```zephyr``` refers to a node based on the [Zephyr RTOS](https://www.zephyrproject.org/), which the only type of node currently supported. It is emulated using QEMU, using an ARM Cortex-M3 ```mps2-an385``` machine.
- image: defines the firmware image for the node. In the case of a ```zephyr``` node, it is the full firmware image of the device. For FITA, we provide ready-to-run embServe images. 
- bootstrap: configures a set of commands to be ran in the device using the Zephyr shell 
- networks: maps the network configurations to a network ```linux-br```.

To add additional nodes, just create a new node with a different name and IP address.

## Applications

Applications define IoT workloads deployed in a gateway or cloud server. This component can be used to run native or containerized software components.

The configuration block for a native application is:

```shell
applications:
  proxy:
    type: 'native'
    image: 'socat UDP4-LISTEN:30009,fork,so-bindtodevice=lnxbr-0,reuseaddr UDP4:<IP ADDRESS>:30009'
```
- proxy: defines an unique key for the application
- type: defines the type of workload. Currently supported workloads are ```native``` which runs a native binary, and ```docker``` that launches a container.
- image: defines the command to launch the native workload or the container image

For a Docker based workload the configuration is:

```shell
applications:
  leshan-server:
    type: 'docker'
    image: 'altshiftcreative/leshan-server:1.0.4'
    bootstrap:
      - 'docker exec --privileged leshan-server apt-get update'
      - 'docker exec --privileged leshan-server apt-get install -y iproute2'
      - 'docker exec --privileged leshan-server ip route add 10.10.12.0/24 via 10.10.11.254'
    networks:
      linux-br:
        ipv4_address: 10.10.11.1
        ipv4_gateway: 10.10.11.254
```
A Docker container requires additional configurations to ensure Nodes can communicate with containers. A route between subnets is added using the bootstrap key, which run the configured commands inside the Docker container. More information is provided in the Network section.

## Networks

Networks define the communication linkes that connect Nodes to Nodes, Nodes to Applications or Applications to Applications. Multiple Networks can exist in an IoT application scenario.

To define a network:

```shell
networks:
  linux-br:
    type: 'linux-br'
    host_address: 10.10.12.254
```
- linux-br: defines an unique key for the network
- type: also defines the type of network. Currently two different types are supported: Linux Bridges (```linux-br```) and [NS3](https://www.nsnam.org/) (```ns3```). Only the first is detailed here.
- host_address: defines the IP address of the host Linux bridge.

Each Node and Application that must be connected to the Linux Bridge must provide some information to ensure correct configuration:

```shell
nodes:
  node1:
    (...)
    networks:
      linux-br:
        ipv4_address: 10.10.12.1
        ipv4_gateway: 10.10.12.254
```

The network is linked by using its unique key. The provided information defines the IP address of the device itself. It is up to the user to correctly define addresses to ensure correct communication (e.g., no duplicated IP address, gateway match host_address). In the case of Docker containers, an extra bridge is created by Docker. To ensure communication between networks in different bridges, a route needs to be added to the Docker container. 

:::warning

While [ns3](https://www.nsnam.org/) is supported by IoTNetEMU, the Docker image does not currently support it. 

:::
