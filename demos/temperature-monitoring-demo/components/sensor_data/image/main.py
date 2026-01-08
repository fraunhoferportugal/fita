from paho.mqtt import client as mqtt_client
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.subscribeoptions import SubscribeOptions

import time
import json
import sys
import socket

def send_to_telegraf(sock, telegraf_uri, telegraf_port, data):
    print(f"Sending to Telegraf: {data}")
    sock.sendto(data.encode(), (telegraf_uri, telegraf_port))

def on_connect(client, userdata, flags, rc):
  # This will be called once the client connects
  print(f"Connected with result code {rc}")

  # Subscribe here!
  client.subscribe("announce")
  client.subscribe("unregister")

def on_temperature_message(client, userdata, message):
  # print(message.payload)
  try:
    payload_json = json.loads(message.payload.decode("utf-8"))
    far_edge_id = list(payload_json.keys())[0]
    temperature = float(payload_json[far_edge_id]['sdfObject']['Temperature'][0]['sdfProperty']['Sensor_Value'])

    send_to_telegraf(userdata["telegraf_sock"], userdata["telegraf_uri"], userdata["telegraf_port"], f"temperature,id={far_edge_id},unit=ºC value={temperature}")
    print(f"Device: {far_edge_id} Value: {temperature} ºC")

  except Exception as e:
    print(f'Exception!: {e}')

def subscribe(client, far_edge_id):
  # This should work but we don't receive any callback...
  # client.publish(f"{far_edge_id}/Temperature/0/sdfProperty/Sensor_Value", payload='{"operation":"START_OBSERVE"}')
  # client.subscribe(f"{far_edge_id}/Temperature/0/sdfProperty/Sensor_Value", options=SubscribeOptions(noLocal=True))
  # client.message_callback_add(f"{far_edge_id}/Temperature/0/sdfProperty/Sensor_Value", on_temperature_message)

  client.publish(f"{far_edge_id}/Temperature/0", payload='{"operation":"START_OBSERVE"}')
  client.subscribe(f"{far_edge_id}/Temperature/0", options=SubscribeOptions(noLocal=True))
  client.message_callback_add(f"{far_edge_id}/Temperature/0", on_temperature_message)

def unsubscribe(client, far_edge_id):
  client.unsubscribe(f"{far_edge_id}/Temperature/0")
  client.message_callback_remove(f"{far_edge_id}/Temperature/0")

def on_message(client, userdata, message):
  print(f'{message.topic}: {message.payload}')

  if (message.topic == "announce"):
    try:
      announce_payload_json = json.loads(message.payload.decode("utf-8"))
      far_edge_id = list(announce_payload_json.keys())[0]

      # Device has Temperature Sensor and we are not subscribed
      if len(announce_payload_json[far_edge_id]['sdfObject']['Temperature']) != 0 and far_edge_id not in userdata["far_edge_ids"]:
        print(f'Node {far_edge_id} has a temperature sensor! Subscribing...')

        # Subscribe to device
        subscribe(client, far_edge_id)

        # Append to list
        userdata["far_edge_ids"].append(far_edge_id)
        print(f'Node {far_edge_id} subscribed')

      # Device had Temperature Sensor and we are subscribed
      elif len(announce_payload_json[far_edge_id]['sdfObject']['Temperature']) == 0 and far_edge_id in userdata["far_edge_ids"]:
        print(f'Node {far_edge_id} had a temperature sensor! Unsubscribing...')

        # Unsubscribe from device
        unsubscribe(client, far_edge_id)

        # Remove from list
        userdata["far_edge_ids"].remove(far_edge_id)
        print(f'Node {far_edge_id} unsubscribed')

    except Exception as e:
      print(f'Exception!: {e}')
      print(f'{message.topic}: {message.payload}')

  elif (message.topic == "unregister"):
    far_edge_id = (message.payload).decode("utf-8")

    if far_edge_id not in userdata["far_edge_ids"]:
      return

    print(f'Node {far_edge_id} disconnected, cleaning up...')

    # Unsubscribe from device
    unsubscribe(client, far_edge_id)

    # Remove from list
    userdata["far_edge_ids"].remove(far_edge_id)
    print(f'Node {far_edge_id} unsubscribed')

  else:
    print("Unknown topic.") 

def main():
  if len(sys.argv) != 6:
    print("Usage: 'python3 main.py <mqtt_broker_uri> <mqtt_broker_port> <mqtt_client_id> <telegraf_uri> <telegraf_port>'")  
    return

  mqtt_broker_uri = sys.argv[1]
  mqtt_broker_port = int(sys.argv[2])
  mqtt_client_id = sys.argv[3]

  telegraf_uri = sys.argv[4]
  telegraf_port = int(sys.argv[5])

  client = mqtt_client.Client(mqtt_client_id)
  client.on_connect = on_connect
  client.on_message = on_message
  client.user_data_set({
    'mqtt_broker_uri': mqtt_broker_uri,
    'mqtt_broker_port': mqtt_broker_port,
    'telegraf_uri': telegraf_uri,
    'telegraf_port': telegraf_port,
    'telegraf_sock': socket.socket(socket.AF_INET, socket.SOCK_DGRAM),
    'far_edge_ids': [],
  })

  for i in range(10):
    try:
      print(f"Connecting MQTT broker: {mqtt_broker_uri}:{mqtt_broker_port}")
      client.connect(mqtt_broker_uri, mqtt_broker_port)

      print("Connected!")
      client.loop_forever()  # Start networking daemon
      return

    except ConnectionRefusedError:
        print("MQTT broker not ready. Retrying in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
  main()