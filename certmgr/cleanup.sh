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

echo "[1/6] Removing Certificates..."
"$KUBECTL" delete certificate trust-manager -n cert-manager --ignore-not-found
"$KUBECTL" delete certificate fenw-mqtt-client-cert -n fita --ignore-not-found
"$KUBECTL" delete certificate intermediate-ca -n fita --ignore-not-found
"$KUBECTL" delete certificate mqtt-broker-server-cert -n fita --ignore-not-found
"$KUBECTL" delete certificate root-ca -n fita --ignore-not-found

echo "[2/6] Removing CertificateRequests..."
"$KUBECTL" delete certificaterequest fenw-mqtt-client-cert-1 -n fita --ignore-not-found
"$KUBECTL" delete certificaterequest intermediate-ca-1 -n fita --ignore-not-found
"$KUBECTL" delete certificaterequest mqtt-broker-server-cert-1 -n fita --ignore-not-found
"$KUBECTL" delete certificaterequest root-ca-1 -n fita --ignore-not-found

echo "[3/6] Removing Issuers..."
"$KUBECTL" delete issuer trust-manager -n cert-manager --ignore-not-found
"$KUBECTL" delete issuer intermediate-ca-issuer -n fita --ignore-not-found
"$KUBECTL" delete issuer root-ca-issuer -n fita --ignore-not-found

echo "[4/6] Removing ClusterIssuers..."
"$KUBECTL" delete clusterissuer bootstrap-selfsigned --ignore-not-found

echo "[5/6] Removing trust-manager Bundles..."

"$KUBECTL" delete bundle fita-trust-bundle --ignore-not-found

echo "[6/6] Removing Secrets!..."
"$KUBECTL" delete secret fenw-mqtt-client-secret -n fita --ignore-not-found
"$KUBECTL" delete secret intermediate-ca -n fita --ignore-not-found
"$KUBECTL" delete secret mqtt-broker-server-secret -n fita --ignore-not-found
"$KUBECTL" delete secret root-ca -n fita --ignore-not-found

echo "Cleanup complete. Proceed to uninstall."
