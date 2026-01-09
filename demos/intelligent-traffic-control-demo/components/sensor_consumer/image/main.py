import time
import sys
import socket
import os

from paho.mqtt.enums import MQTTProtocolVersion
import paho.mqtt.client as mqtt_client

from src.mqtt.mqtt_callbacks import on_connect, on_message 
from src.video import set_video_on, test_connection

def parse_bool_env(var_name, default=False):
    val = os.environ.get(var_name, str(default)).lower()
    return val in ('1', 'true', 't', 'yes', 'y', 'on')


def main():
    if len(sys.argv) != 7:
        print("Usage: 'python3 main.py <mqtt_broker_uri> <mqtt_broker_port> <telegraf_uri> <telegraf_port> <video_uri> <video_port>'")  
        return

    mqtt_broker_uri = sys.argv[1]
    mqtt_broker_port = int(sys.argv[2])

    telegraf_uri = sys.argv[3]
    telegraf_port = int(sys.argv[4])

    video_uri = sys.argv[5]
    video_port = sys.argv[6]

    set_initial_video_state = parse_bool_env('SET_INITIAL_VDEO_STATE') if os.environ.get('SET_INITIAL_VDEO_STATE') != None else True

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, protocol=MQTTProtocolVersion.MQTTv5)
    client.on_connect = on_connect
    client.on_message = on_message
    client.user_data_set({
        'mqtt_broker_uri': mqtt_broker_uri,
        'mqtt_broker_port': mqtt_broker_port,
        'telegraf_uri': telegraf_uri,
        'telegraf_port': telegraf_port,
        'telegraf_sock': socket.socket(socket.AF_INET, socket.SOCK_DGRAM),
        'far_edge_ids': [],
        'video_uri': video_uri,
        'video_port': video_port,
        'noise_timestamp': 0,
        'video_running': True,
        'device_uri': None
    })

    while True:
        try:
            test_connection(video_uri, video_port)

            if set_initial_video_state:
                print(f'Turning video processing on...')
                set_video_on(video_uri, video_port, False, None)
            break
        except Exception as e:
            print(e)
            print("Waiting for 5 seconds... Maybe the video component is not up?")
            time.sleep(5)
            pass
        

    for _ in range(10):
        try:
            print(f"Connecting MQTT broker: {mqtt_broker_uri}:{mqtt_broker_port}")
            client.connect(mqtt_broker_uri, mqtt_broker_port)

            print("Connected!")
            client.loop_forever()  # Start networking daemon
            return

        except ConnectionRefusedError:
            print("MQTT broker not ready. Retrying in 5 seconds...")
            time.sleep(5)

        except Exception as e:
            print(f"Exception: {e}")
            print("MQTT broker: Name does not resolve. Incorrect broker Name or MQTT broker not ready. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()
