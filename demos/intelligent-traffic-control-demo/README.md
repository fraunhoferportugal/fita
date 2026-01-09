# MLSysOps Project Use Case

## How to setup and deploy demo?

```bash
# Deploy demo
./scripts/deploy-demo.sh

# Deploy noise sensor service
microk8s kubectl apply -f services/embserve/deployment.yaml
```

- Check dashboard
    - http://<HOST_MACHINE_IP>:30101
    - User: admin
    - Password: 
        - microk8s kubectl get secret fita-tig-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
    - Dashboard -> FITA

## How to clean deployed demo?

```bash
# Clean demo
./scripts/unninstall-demo.sh
```

## For the interactive scenario
1. The object detection algorithm is always on - Most of the time no relevant events take place, resulting in wasted energy

2. We implement a solution using a low-powered micro-controller based device equipped with a microphone. When there's no noise indicating relevant events, the object detection algorithm is turned off. 

3. However, the implemented version uses a very high treshold, resulting in many events being lost. To overcome this issue, the solution is updated with a new version of the sensor data consumer, showcasing fast adaptability to changing environments and the ease of application updates using FITA.

4. Mention that, despite other solutions to manage far-edge device applications, no ther offers the same ease of update or is able to manage components accross the computing continuum, using the same configuration model and tools. 

**Future work:** It woukd be nice to implement a version that has the far-edge device publish the detection of events instead of the microphone readings, further crediting our feature set and energy consumption claims.

### Required changes:
- Change the setup script to use the interactive deployment commands of the `video_component` and `sensor_consumer` that set different values in their deployment charts.
    
    The `video_component` will autoplay the video and enable the object detection by default.

    The `sensor_consumer` won't try to start/stop the object detection without data from the microphone.
- Change the `ALARM_THRESHOLD` value in [`./components/sensor_consumer/image/src/mqtt/mqtt_constants.py`](./components/sensor_consumer/image/src/mqtt/mqtt_constants.py) to some value higher than `-16.4`. This seems to be a good threshold for the video3 in this repo (park4, sensor 4 from [StreetAware: A High-Resolution Synchronized Multimodal Urban Scene Dataset](https://ultraviolet.library.nyu.edu/records/q1byv-qc065))

### Commands
2. ```shell
    microk8s kubectl apply -f ./services/embserve/deployment.yaml
    ```
3. ```shell
    microk8s kubectl delete -f ./services/embserve/deployment.yaml
    microk8s helm uninstall mlsysops-use-case-sensor-consumer
    ```
    Update the `ALARM_THRESHOLD` back to `-16.4`

    ```shell
    ./components/sensor_consumer/image/scripts/build-image.sh -v 1.0.0
    ./components/sensor_consumer/image/scripts/deploy-image-local.sh -v 1.0.0
    microk8s helm install mlsysops-use-case-sensor-consumer sensor_consumer/chart/sensor-consumer/ --set mlsysopsUseCaseSensorConsumerImage.setInitialVideoState=false
    sleep 5
    microk8s kubectl apply -f ./services/embserve/deployment.yaml
    ```
