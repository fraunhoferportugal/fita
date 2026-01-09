import queue
import uuid
import json

from paho.mqtt.enums import MQTTProtocolVersion
from paho.mqtt import client as mqtt_client
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

msg_queue = queue.Queue()

def get_device_ip(hostname, port, device_id):
    global msg_queue

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, protocol=MQTTProtocolVersion.MQTTv5)
    client.on_message = _on_message
    client.user_data_set({ 'message_queue': msg_queue })

    client.connect(hostname, port)
    client.loop_start()

    ip = _get_device_ip(client, device_id)

    client.disconnect()
    return ip

def _on_message(_client, userdata, message):
    userdata['message_queue'].put(message)

def _get_device_ip(client, device_id):
    global msg_queue

    response_topic = str(uuid.uuid4().hex)
    publish_property = Properties(PacketTypes.PUBLISH)
    publish_property.ResponseTopic = response_topic

    client.subscribe(response_topic)

    try:
        topic = f"{device_id}/Connectivity_Monitoring/0"
        data ='{"operation": "GET"}'
        client.publish(topic=topic, payload=data, properties=publish_property)
        try:
            response = json.loads(msg_queue.get(timeout=1).payload)
            if response['response_code'] == 69:
                for connection in response['sdfObject']['Connectivity_Monitoring']:
                    return connection['sdfProperty']['IP_Addresses']['0']

        except queue.Empty:
            print('Failed to get device connection information')
            pass

    except Exception as e:
        print(e)
        return None

    finally:
        client.unsubscribe(response_topic)

if __name__ == "__main__":
    print(get_device_ip('172.16.5.174', 30010, 'b1_node1'))