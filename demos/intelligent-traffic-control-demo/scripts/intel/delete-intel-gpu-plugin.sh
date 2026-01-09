#!/bin/bash
set -e

GIT_EXEC_PATH=/snap/microk8s/current/usr/lib/git-core microk8s kubectl delete -k 'https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd?ref=main'
GIT_EXEC_PATH=/snap/microk8s/current/usr/lib/git-core microk8s kubectl delete -k 'https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd/overlays/node-feature-rules?ref=main'
GIT_EXEC_PATH=/snap/microk8s/current/usr/lib/git-core microk8s kubectl delete -k 'https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/gpu_plugin/overlays/nfd_labeled_nodes?ref=main'
