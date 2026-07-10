#!/bin/bash
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

detect_helm() {
	# Environment variable
	if [ -n "${HELM_CMD:-}" ]; then
		echo "$HELM_CMD"
		return
	fi 
	
	# this covers an actual helm command, or the proper alias for "microk8s helm" set with
	# sudo `snap alias microk8s.helm helm`, but not `alias helm=microk8s helm`
	if command -v helm > /dev/null 2>&1; then
		echo "helm"
		return
	fi
	
	# microk8s installed but no alias set
	if command -v microk8s > /dev/null 2>&1; then
		echo "microk8s helm"
		return
	fi
    # others can be added for more compatibility, but ultimately the user can just set $HELM_CMD to whatever they want	
	return 1
}

if ! HELM="$(detect_helm)"; then
	echo "error: could not find helm installed in your system."
	echo "if you have it installed make sure to set the HELM_CMD env variable to your preferred helm binary before running the script"
	exit 1
fi

# installs cert-manager in the cluster and configures PKI
curl -LO https://cert-manager.io/public-keys/cert-manager-keyring-2021-09-20-1020CF3C033D4F35BAE1C19E1226061C665DF13E.gpg
helm install \
  cert-manager oci://quay.io/jetstack/charts/cert-manager \
  --version v1.21.0 \
  --namespace cert-manager \
  --create-namespace \
  --verify \
  --keyring ./cert-manager-keyring-2021-09-20-1020CF3C033D4F35BAE1C19E1226061C665DF13E.gpg \
  --set crds.enabled=true

rm cert-manager-keyring-2021-09-20-1020CF3C033D4F35BAE1C19E1226061C665DF13E.gpg
# if you have cmctl installed and configured this checks for the webhook in cert-manager to be ready
# cmctl check api --wait=2m 
# otherwise, let's hope 10s is enough
sleep 10s
"$KUBECTL" apply -f ./conf/pki.yaml
"$KUBECTL" apply -f ./conf/fenw.yaml
"$KUBECTL" apply -f ./conf/mqttbroker.yaml
"$KUBECTL" label namespaces fita trust=enabled --overwrite=true
"$HELM" upgrade trust-manager oci://quay.io/jetstack/charts/trust-manager \
  --install \
  --namespace cert-manager \
  --set app.trust.namespace=fita \
  --wait
"$KUBECTL" apply -f ./conf/trustbundle.yaml
