from .mqtt_constants import *
from .mqtt import on_announce_message, on_unregister_message

def on_connect(client, _userdata, _flags, rc, _props):
    print(f"Connected with result code {rc}")
    
    client.subscribe(ANNOUNCE_TOPIC)
    client.subscribe(UNREGISTER_TOPIC)

    print(f"Subscribed {ANNOUNCE_TOPIC} and {UNREGISTER_TOPIC} topics")

def on_message(client, userdata, message):
    if (message.topic == ANNOUNCE_TOPIC):
        on_announce_message(client, userdata, message)
    elif (message.topic == UNREGISTER_TOPIC):
        on_unregister_message(client, userdata, message)
    else:
        print("Unknown topic.")
