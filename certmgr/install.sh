#!/bin/bash
# installs cert-manager in the cluster and configures PKI
microk8s kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.20.2/cert-manager.yaml
# if you have cmctl installed and configured this checks for the webhook in cert-manager to be ready
# cmctl check api --wait=2m 
# otherwise, let's hope 10s is enough
sleep 10s
microk8s kubectl apply -f ./conf/pki.yaml
helm upgrade trust-manager oci://quay.io/jetstack/charts/trust-manager \
  --install \
  --namespace cert-manager \
  --wait
microk8s kubectl apply -f ./conf/trustbundle.yaml
