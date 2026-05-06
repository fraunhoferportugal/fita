#!/bin/bash
# checks for lingering cert-manager resources in the cluster

microk8s kubectl get Issuers,ClusterIssuers,Certificates,CertificateRequests,Orders,Challenges --all-namespaces
