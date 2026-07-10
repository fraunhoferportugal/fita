#!/usr/bin/env bash
set -euo pipefail

detect_kubectl() {
	# Environment variable
	if [ -n "${KUBECTL_CMD:-}" ]; then
		echo "$KUBECTL_CMD"
		return
	fi
	
	# this covers an actual kubectl command, or the proper alias for "microk8s kubectl" set with
	# sudo `snap alias microk8s.kubectl kubectl`, but not `alias kubectl=microk8s kubectl`
	if command -v kubectl > /dev/null 2>&1; then
		echo "kubectl"
		return
	fi

	# microk8s installed but no alias set
	if command -v microk8s > /dev/null 2>&1; then
		echo "microk8s kubectl"
		return
	fi

    # others can be added for more compatibility, but ultimately the user can just set $HELM_CMD to whatever they want	
	return 1
}

if ! KUBECTL="$(detect_kubectl)"; then
	echo "error: could not find kubectl installed in your system."
	echo "if you have it installed make sure to set the KUBECTL_CMD env variable to your preferred kubectl binary before running the script"
	exit 1
fi

echo "[1/5] Removing Certificates..."
"$KUBECTL" delete certificates --all -A --ignore-not-found

echo "[2/5] Removing CertificateRequests..."
"$KUBECTL" delete certificaterequests --all -A --ignore-not-found

echo "[3/5] Removing Issuers..."
"$KUBECTL" delete issuers --all -A --ignore-not-found

echo "[4/5] Removing ClusterIssuers..."
"$KUBECTL" delete clusterissuers --all --ignore-not-found

echo "[5/5] Removing trust-manager Bundles..."
"$KUBECTL" delete bundles --all --ignore-not-found

echo "Cleanup complete. Proceed to uninstall."
