---
sidebar_position: 3
---

# Deploy Workloads on Far-Edge Devices

Far-Edge services follow the same flow as normal Kubernetes nodes services. Before deployment the Far-Edge service must be uploaded to a OCI registry. 

## Pushing embServe Service to OCI registry

To push an service to a registry:

1. Create a new folder:
```shell
mkdir service
```

2. Install the oras library:

```shell
cd service
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install oras
```

3. Create a `config.json`:
```json
{
    "architecture": "arm",
    "os": "zephyr",
    "variant": "v7"
}
```

4. Copy the service manifest to the same folder. Folder should have this structure:
```shell
(.venv) user@LABWS:~/Workspace/embserve-sdk/sample$ ls -la
total 20
drwxrwxr-x 2 user user 4096 Sep 26 16:16 .
drwxrwxr-x 8 user user 4096 Sep 26 13:15 ..
-rw-rw-r-- 1 user user   71 Sep 26 16:16 config.json
-rw-rw-r-- 1 user user 2399 Sep 26 16:12 service.json
```

5. Upload the device to an OCI registry:
```shell
oras push harbor.nbfc.io/mlsysops/fita/services/temperature_sensor:1.0.0 --config config.json:application/vnd.oci.image.config.v1+json service.json:application/vnd.embserve.v1+json 
```
:::note
You may need to adapt the command above to match your registry. Also, you must ensure the registry matches the one configured during the FITA deployment. By default, it uses `harbor.nbfc.io`.
:::

:::tip
If you want the same reference OCI registry reference to provide both an `embServe workload` and a `Container image`, check out the [Multi-platform Artifacts](../advanced-usage/multi-platform-images) documentation.
:::


## Creating a Kubernetes deployment for a Far-Edge device

Creating a deployment targeting a Far-Edge device follows the same logic as a normal Kubernetes deployment. Let's create a deployment for the service uploaded in the previous section.

1. Create a file `pod.yaml` with:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: temperature
spec:
  containers:
  - name: temperature
    image: mlsysops/fita/services/temperature_sensor:1.0.0
    imagePullPolicy: IfNotPresent
  nodeSelector:
    extra.resources.fhp/embserve: "true"
    extra.resources.fhp/temperature_sensor: "true"
  tolerations:
    - key: "fita.fhp.pt/type"
      operator: "Equal"
      value: "far-edge"
      effect: "NoSchedule"
```
:::note
Far-Edge node Kubelet contains a taint which prevents scheduling of Pods. Ensure you add the toleration shown above and filter nodes by using `extra.resources.fhp/embserve: "true"` as the `nodeSelector`.

Other labels are available that allows to filter by device capability. Inspect a Far-Edge node to understand what labels are available.
:::

2. Deploy the Pod:

```shell
microk8s kubectl apply -f pod.yaml -n fita
```

3. Observe that the Pod was deployed successfully:

```shell
kubectl get pods -n fita --output wide
```
Which should output:
```shell
NAME          READY   STATUS    RESTARTS   AGE   IP            NODE
temperature   1/1     Running   0          37s   10.1.42.190   labnuc05-b1-node1
```