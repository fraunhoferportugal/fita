#!/bin/bash
# uninstalls cert-manager from the cluster, be sure to remove lingering resources you created first, be sure to remove lingering resources you created first
microk8s kubectl delete -f https://github.com/cert-manager/cert-manager/releases/download/v1.20.2/cert-manager.yaml
microk8s helm uninstall trust-manager -n cert-manager # warning, this removes all trust bundles in the cluster
