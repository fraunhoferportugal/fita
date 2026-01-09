import json
import time

from .mqtt_constants import *
from .mqtt_utils import subscribe, unsubscribe

from ..video import set_video_on, set_video_off
from ..telegraf import send_to_telegraf
from ..routes import create_route
from ..device_ip import get_device_ip

ROUTE_ORIGIN_URI='coap://k8s/input'
ROUTE_DESTINATION_URI='local://0/value'

def on_announce_message(client, userdata, message):
    try:
        announce_payload_json = json.loads(message.payload.decode("utf-8"))
    except Exception as e:
        print(f"Exception in decoding message: {e}")
        print(f'{message.topic}: {message.payload}')
        return

    far_edge_id = list(announce_payload_json.keys())[0]

    far_edge_node = announce_payload_json.get(far_edge_id, None)
    sdf_object = far_edge_node.get('sdfObject', None) if far_edge_node else None
    lwm2m_object = sdf_object.get(LWM2M_OBJECT, None) if sdf_object else None

    # FIXME: This may break for more than 1 service on embServe
    if (lwm2m_object is None or len(lwm2m_object) == 0) and far_edge_id not in userdata["far_edge_ids"]:
        print(f'Node {far_edge_id} has a {LWM2M_OBJECT}! Subscribing...')

        # Create route to device
        try:
            create_route(userdata['mqtt_broker_uri'], userdata['mqtt_broker_port'], far_edge_id, ROUTE_ORIGIN_URI, ROUTE_DESTINATION_URI)
            ip = get_device_ip(userdata['mqtt_broker_uri'], userdata['mqtt_broker_port'], far_edge_id)
        except Exception as e:
            print(f"Exception in creating route: {e}")
            print(f'{message.topic}: {message.payload}')
            return
        
        userdata['device_uri'] = f'coap://{ip}:12345/k8s/input'
        print(f'Route on {far_edge_id} created: coap://{ip}:12345/k8s/input')

        # Subscribe to device
        try:
            subscribe(client, f"{far_edge_id}/{LWM2M_OBJECT}/0", START_OBSERVE_PAYLOAD, on_object_update)
        except Exception as e:
            print(f"Exception in subscribing to device: {e}")
            print(f'{message.topic}: {message.payload}')
            return
        userdata['noise_timestamp'] = time.time()
            
        # Append to list
        userdata["far_edge_ids"].append(far_edge_id)
        print(f'Node {far_edge_id} subscribed')

        # Start video knowing device uri
        try:
            set_video_on(userdata['video_uri'], userdata['video_port'], False, userdata['device_uri'])
        except Exception as e:
            print(f"Exception in setting video with the device URI: {e}")
            print(f'{message.topic}: {message.payload}')
            return
        userdata['video_running'] = False

def on_unregister_message(client, userdata, message):
    far_edge_id = (message.payload).decode("utf-8")

    if far_edge_id not in userdata["far_edge_ids"]:
        return

    print(f'Node {far_edge_id} disconnected, cleaning up...')

    # Unsubscribe from device
    unsubscribe(client, far_edge_id)

    # Remove from list
    userdata["far_edge_ids"].remove(far_edge_id)
    print(f'Node {far_edge_id} unsubscribed')
    userdata['device_uri'] = None

    if len(userdata["far_edge_ids"]) == 0:
        print(f'Noise data not available, turning video processing on...')
        set_video_on(userdata['video_uri'], userdata['video_port'], True, None)
        userdata['video_running'] = True

def on_object_update(_client, userdata, message):
    global COUNTER, ALARM
    try:
        payload_json = json.loads(message.payload.decode("utf-8"))

        far_edge_id = list(payload_json.keys())[0]
        noise = float(payload_json[far_edge_id]['sdfObject'][LWM2M_OBJECT][0]['sdfProperty'][PROPERTY])
        # On start, node can send 0. Ignore it since it is an impossible value
        if noise > -1:
            return

        send_to_telegraf(userdata["telegraf_sock"], userdata["telegraf_uri"], userdata["telegraf_port"], f"{TELEGRAF_TOPIC},id={far_edge_id},unit=dBFs value={noise}")

        if userdata['video_running']:
            if noise < ALARM_THRESHOLD:
                if time.time() - userdata['noise_timestamp'] > ALARM_UNSET_TIME:
                    print("Turning Processing Video Off")
                    set_video_on(userdata['video_uri'], userdata['video_port'], False, userdata['device_uri'])
                    userdata['video_running'] = False
            else:
                userdata['noise_timestamp'] = time.time()
        else:
            if noise > ALARM_THRESHOLD:
                if time.time() - userdata['noise_timestamp'] > ALARM_SET_TIME:
                    print("Turning Video On")
                    set_video_on(userdata['video_uri'], userdata['video_port'], True, userdata['device_uri'])
                    userdata['video_running'] = True
            else:
                userdata['noise_timestamp'] = time.time()

        print(f'noise: {noise} noise_timestamp: {userdata['noise_timestamp']} video_running: {userdata['video_running']}')

    except Exception as e:
        print(f'Exception on object update: {e}')
