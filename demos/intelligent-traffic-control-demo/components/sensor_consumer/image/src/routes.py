import queue
import uuid
import json

from paho.mqtt.enums import MQTTProtocolVersion
from paho.mqtt import client as mqtt_client
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

msg_queue = queue.Queue()

def create_route(hostname, port, device_id, origin_uri, destination_uri):
    global msg_queue

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, protocol=MQTTProtocolVersion.MQTTv5)
    client.on_message = _on_message
    client.user_data_set({ 'message_queue': msg_queue })

    client.connect(hostname, port)
    client.loop_start()

    _create_route(client, device_id, origin_uri, destination_uri)

    client.disconnect()

def _on_message(_client, userdata, message):
    userdata['message_queue'].put(message)

def _create_route(client, device_id, origin_uri, destination_uri):
    global msg_queue

    route_id = 1000

    response_topic = str(uuid.uuid4().hex)
    publish_property = Properties(PacketTypes.PUBLISH)
    publish_property.ResponseTopic = response_topic

    client.subscribe(response_topic)

    try:
        # Get routes
        topic = device_id + "/Data_Route"
        data ='{"operation": "GET"}'
        client.publish(topic=topic, payload=data, properties=publish_property)
        try:
            response = json.loads(msg_queue.get(timeout=1).payload)
            if response['response_code'] == 69:
                route_ids = []

                for route in response['sdfObject']['Data_Route']:
                    route_ids.append(int(route['label']))
                    route_origin_uri = route['sdfProperty']['Origin_URI']
                    route_destination_uri = route['sdfProperty']['Destination_URI']

                    if route_origin_uri == origin_uri and route_destination_uri == destination_uri:
                        # Route already exists
                        print("Route already exists")
                        return True

                # Increment ID if needed
                while route_id in route_ids:
                    route_id += 1
        except queue.Empty:
            print('Failed to get routes, empty?')
            pass

        # Create Instance
        data ='{"operation": "POST", "data": "{\\"label\\": \\"' + str(route_id) + '\\"}"}'
        client.publish(topic=topic, payload=data, properties=publish_property)
        response = json.loads(msg_queue.get(timeout=10).payload)
        if response['response_code'] != 65:
            raise RuntimeError('Failed to create instance')

        # Set data in Instance
        topic = device_id + "/Data_Route/" + str(route_id)

        data ='{"operation": "POST", "data": "{\\"sdfProperty\\":{\\"Origin_URI\\": \\"' + origin_uri + '\\",\\"Destination_URI\\": \\"' + destination_uri + '\\"}}"}'

        client.publish(topic=topic, payload=data, properties=publish_property)
        response = json.loads(msg_queue.get(timeout=10).payload)
        if response['response_code'] != 68:
            raise RuntimeError('Failed to create instance')

    except Exception as e:
        print(e)
        return False

    finally:
        client.unsubscribe(response_topic)
        return True

if __name__ == "__main__":
    create_route('172.16.5.174', 30010, 'b1_node1', 'coap://k8s/input', 'local://0/value')
