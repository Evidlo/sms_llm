import paho.mqtt.client as mqtt
import shelve
import json
import ollama
from datetime import datetime
from datetime import UTC

from secretsfile import host, port, user, password, model, numbers


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

#def on_connect(client, userdata, flags, rc):
def on_connect(client, userdata, flags, rc, properties):
    """Connected to MQTT broker"""
    print(f"Connected with result code {rc}")
    client.subscribe("sms/received")

def on_message(client, userdata, msg):
    """Receive message from MQTT.  Triggered when new SMS message
    received by android app"""

    # dict with keys: 'from', 'timestamp', 'message' and 'type'
    msg = json.loads(msg.payload.decode())
    number, text = msg['from'], msg['message']
    # trim millisecond part and convert to datetime
    timestamp = datetime.fromtimestamp(int(msg['timestamp'][:-3]), UTC)

    # only respond if number is in our list
    # or if message starts with 'llm '
    if number in numbers or text.startswith('llm '):
        text = text.removeprefix('llm ')
        if number not in db:
            db[number] = []

        # store SMS content in history database
        db[number].append({'role': 'user', 'content': text})
        # get a response from the LLM
        # print(db[number][-10:])
        response = ollama.chat(
            model=model,
            # use a single message for context
            # messages=[{
            #     'role': 'user',
            #     'content': text
            # }]
            # use last N messages for context
            messages=db[number][-10:]
        ).message.content
        # store response in history database
        db[number].append({'role': 'assistant', 'content': response})
        # send response back to phone
        client.publish(
            "sms/send",
            s:=json.dumps({
                'to': number,
                'message': response
            })
        )
        print(f"From {number} @ {timestamp}:\n    > {text}")
        print(f"    {response}")

# database for storing chat history
db = shelve.open('history.sql', 'c', writeback=True)

#client = mqtt.Client()
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(user, password)
client.connect(host, port, 60)
client.loop_forever()
