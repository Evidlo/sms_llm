#!/usr/bin/env python3

# inject a message into the LLM as if it were a received text.
# this is useful for handling missed messages, e.g. if the forwarding
# app crashes or a number wasn't whitelisted
#
# Usage:
#       ./inject.py +12340000000 "sms message here"

import json
import paho.mqtt.client as mqtt
import secretsfile
import sys
import time

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.username_pw_set(secretsfile.user, secretsfile.password)
client.connect(secretsfile.host, secretsfile.port, 60)

client.publish(
    "sms/received",
    s:=json.dumps({
        'from': sys.argv[1],
        'message': sys.argv[2],
        'timestamp': str(int(time.time())) + '000',
        'type': '1',
    })
)