#!/usr/bin/env bash
set -euo pipefail

echo "[1/5] Removing Certificates..."
microk8s kubectl delete certificates --all -A --ignore-not-found

echo "[2/5] Removing CertificateRequests..."
microk8s kubectl delete certificaterequests --all -A --ignore-not-found

echo "[3/5] Removing Issuers..."
microk8s kubectl delete issuers --all -A --ignore-not-found

echo "[4/5] Removing ClusterIssuers..."
microk8s kubectl delete clusterissuers --all --ignore-not-found

echo "[5/5] Removing trust-manager Bundles..."
microk8s kubectl delete bundles --all --ignore-not-found

echo "Cleanup complete. Proceed to uninstall."
