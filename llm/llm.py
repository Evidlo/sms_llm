import paho.mqtt.client as mqtt
import json
import ollama
from datetime import datetime
from datetime import UTC

from secretsfile import host, port, user, password, model


def llm_response(message: str):
    """Query LLM for response"""
    response = ollama.chat(
        model=model,
        messages=[{
            'role': 'user',
            'content': message
        }]
    ).message.content
    return response

def on_connect(client, userdata, flags, rc):
    """Connected to MQTT broker"""
    print(f"Connected with result code {rc}")
    client.subscribe("sms/received")

def on_message(client, userdata, msg):
    """Receive message from MQTT.  Triggered when new SMS message
    received by android app"""

    # dict with keys: 'from', 'timestamp', 'message' and 'type'
    msg = json.loads(msg.payload.decode())
    if msg['from'] in numbers:

        # get a response from the LLM
        response = llm_response(msg['message'])
        # send response back to phone
        client.publish(
            "sms/send",
            s:=json.dumps({
                'to': msg['from'],
                'message': response
            })
        )
        # trim millisecond part and convert to datetime
        timestamp = datetime.fromtimestamp(int(msg['timestamp'][:-3]), UTC)
        print(f"From {msg['from']} @ {timestamp}:\n    {msg['message']}")
        print(f"    > {response}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(user, password)
client.connect(host, port, 60)
client.loop_forever()