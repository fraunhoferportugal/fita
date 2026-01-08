# Temperature Monitoring Demo

## How to setup?

- Deploy demo
    - cd scripts/
    - ./deploy-demo.sh
- If everything went as expected, the Kallisto should connect to FITA and appear as k8s nodes

- Check dashboard
    - http://<IP>:30101
    - User: admin
    - Password: 
        - microk8s kubectl get secret fita-tig-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
    - Dashboard -> FITA
    - Edit -> Settings -> Variables
    - Configure each variable with the correct name of the device
        - The name will be the one used in the Kallisto setup!
    - Save dashboard

- Deploy temperature sensors
    - cd embserve/deployments
    - microk8s kubectl apply -f deployment.yaml

- Check if nodes, pods and data appears in the Dashboard