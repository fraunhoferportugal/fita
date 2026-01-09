from paho.mqtt.subscribeoptions import SubscribeOptions

def subscribe(client, topic, pub_payload, callback):
    client.publish(topic, payload=pub_payload)
    client.subscribe(topic, options=SubscribeOptions(noLocal=True))
    client.message_callback_add(topic, callback)

def unsubscribe(client, topic):
    client.unsubscribe(topic)
    client.message_callback_remove(topic)
