# SMS LLM

<img src="out2.png" height="500px"/>
<img src="out.png"/>

This is a guide for connecting Android SMS chats to an LLM for fun and chaos.

LLM-generated messages appear in the default SMS app as if they were sent by the user.

This uses a simple Android application which forwards all SMS messages to Ollama via MQTT and some glue logic.  Only phone numbers in the whitelist or messages which begin with `llm ` generate an LLM response.

Thanks to [ibnux](https://github.com/ibnux/Android-SMS-Gateway-MQTT) for the application which I have modified for 2-way communication over MQTT.

``` text
                      ANDROID PHONE                  LLM SERVER    
                                                                   
                    +---------------+      |                         
                    | SMS Messaging |      |                        
 Your Victims ------|     App       |                              
                    +---------------+      |                        
                            |              |                        
                    +---------------+              +---------------+
                    |  Forward App  |--------------|  MQTT Broker  |
                    +---------------+              +---------------+
                                           |               |        
                                           |       +---------------+
                                                   |    llm.py     |
                                           |       +---------------+
                                           |               |        
                                                   +---------------+
                                           |       | Ollama Server |
                                           |       +---------------+
```

# Setup

### MQTT Broker

Here is how I've set up my MQTT broker.  It should be accessible from the Android phone and computer running the LLM.

    sudo apt install mosquitto
    # generate mosquitto credentials
    mosquitto_passwd -c /var/lib/mosquitto/pass [USERNAME]
    # edit /etc/mosquitto/mosquitto.conf and add credentials file
    
And my mosquitto config `/etc/mosquitto/mosquitto.conf`

    # Place your local configuration in /etc/mosquitto/conf.d/
    #
    # A full description of the configuration file is at
    # /usr/share/doc/mosquitto/examples/mosquitto.conf.example

    pid_file /run/mosquitto/mosquitto.pid

    persistence true
    persistence_location /var/lib/mosquitto/

    #log_dest file /var/log/mosquitto/mosquitto.log
    log_dest syslog
    log_type debug

    include_dir /etc/mosquitto/conf.d

    allow_anonymous false
    password_file /var/lib/mosquitto/pass

    listener 1883 0.0.0.0

### Android App

Install the apk from the [Releases page](https://github.com/Evidlo/sms_llm/releases/) or build it yourself using the steps below.

Configuring the application:

- `Menu > Set MQTT Server`, set your MQTT host and credentials
- `Menu > Disable Battery optimization`
- **fully restart the application**.


<details>
<summary>
Building the application from source:
</summary>

You must have the Android SDK [installed somewhere](https://developer.android.com/tools).

    export ANDROID_HOME=[ANDROID ROOT DIR]
    cd android
    # build
    ./gradlew build -x lint
    # install the apk at android/app/build/outputs/apk/debug/app-debug.apk

</details>


### LLM

Ollama setup.  Install [ollama](https://ollama.com/) before this section

    # start the Ollama server
    ollama serve
    # set up a model in Ollama
    ollama pull llama3.3
    # launch the model and experiment with different system prompts
    ollama run llama3.3
    >>> /set system "you are a millenial who is texting on SMS.  you only respond with single sentences and everything you write is in lowercase"
    >>> /save llama3.3
    
Glue logic setup
    
    # glue logic dependencies
    pip install -r llm/requirements.txt
    # edit llm/secretsfile.py with your MQTT broker host and credentials, and phone number whitelist
    # run the glue logic script
    python llm/llm.py
