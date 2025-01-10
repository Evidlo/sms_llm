import paho.mqtt.client as mqtt
import json
import ollama
from datetime import datetime
from datetime import UTC
from importlib import reload

import secretsfile
from database import JSONDatabase


def on_connect(client, userdata, flags, rc, properties):
    """Connected to MQTT broker"""
    print(f"Connected with result code {rc}")
    client.subscribe("sms/received")

def on_message(client, userdata, msg):
    """Receive message from MQTT.  Triggered when new SMS message
    received by android app"""

    # hot-reload secretsfile to allow for live changes
    reload(secretsfile)

    # dict with keys: 'from', 'timestamp', 'message' and 'type'
    msg = json.loads(msg.payload.decode())
    number, text = msg['from'], msg['message']
    # trim millisecond part and convert to datetime
    timestamp = datetime.fromtimestamp(int(msg['timestamp'][:-3]), UTC)

    # only respond if number is in our list
    # or if message starts with 'llm '
    if number in secretsfile.numbers or text.startswith('llm '):
        text = text.removeprefix('llm ')

        print(f"From {number} @ {timestamp}:\n    > {text}")

        if number not in db:
            db[number] = []

        # get a response from the LLM
        response = ollama.chat(
            model=secretsfile.numbers[number],
            # use last N messages for context
            messages=db[number][-10:]
        ).message.content
        # store SMS message in history database
        db[number].append({'role': 'user', 'content': text})
        # store response in history database
        db[number].append({'role': 'assistant', 'content': response})
        db.sync(number)
        # send response back to phone
        client.publish(
            "sms/send",
            s:=json.dumps({
                'to': number,
                'message': response
            })
        )
        print(f"    {response}")

# database for storing chat history
db = JSONDatabase('history')

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(secretsfile.user, secretsfile.password)
client.connect(secretsfile.host, secretsfile.port, 60)
try:
    client.loop_forever()
except KeyboardInterrupt:
    pass
