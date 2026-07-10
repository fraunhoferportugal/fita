#!/bin/bash
set -euo pipefail

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

# uninstalls cert-manager from the cluster, be sure to remove lingering resources you created first, be sure to remove lingering resources you created first
"$HELM" uninstall trust-manager -n cert-manager # warning, this removes all trust bundles in the cluster
"$HELM" uninstall cert-manager -n cert-manager
