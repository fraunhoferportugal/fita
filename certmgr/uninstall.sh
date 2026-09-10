#!/bin/bash
set -u

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

resources=$(for res in $(microk8s kubectl api-resources --verbs=list --namespaced -o name); do
  case "$res" in
    configmaps)
	  "$KUBECTL" get "$res" -n fita --show-kind --ignore-not-found \
        --field-selector metadata.name!=kube-root-ca.crt 2>&1 \
		| grep -v 'Endpoints is deprecated'
      ;;
    serviceaccounts)
      "$KUBECTL" get "$res" -n fita --show-kind --ignore-not-found 2>&1 \
        --field-selector metadata.name!=default \
		| grep -v 'Endpoints is deprecated'
      ;;
    *)
      "$KUBECTL" get "$res" -n fita --show-kind --ignore-not-found 2>&1 \
		| grep -v 'Endpoints is deprecated'
      ;;
  esac
done)

# uninstalls cert-manager from the cluster, be sure to remove lingering resources you created first, be sure to remove lingering resources you created first
"$HELM" uninstall trust-manager -n cert-manager # warning, this removes all trust bundles in the cluster
"$HELM" uninstall cert-manager -n cert-manager

if [ -z "$resources" ]; then
	echo "Namespace fita has no resources. Deleting."
	"$KUBECTL" delete namespace fita
else
	echo "Namespace fita still has resources. Note that all secrets have been deleted and cert-manager and trust-manager have been uninstalled."
fi
