import datetime
import random
import time
import paho.mqtt.client as mqtt

def simulate_and_send(client):
    while True:
        current_time = datetime.datetime.now()
        temperature = random.uniform(20,30)
        humidity = random.uniform(40,60)
        S_ID = 1
        data = {'time': current_time.strftime('%Y-%m-%d %H:%M:%S'), 
                'S_ID' : S_ID,
                'temperature': temperature,
                'humidity': humidity
                }
        client.publish(topic,str(data))

        print(f"Time:{current_time}, S_ID:{S_ID}, Temp:{temperature:.2f}'C, humidity: {humidity}")
        time.sleep(1)
        
broker_address = 'localhost'
broker_port = 1883
topic = 'temp_humi'


mqtt_client = mqtt.Client()
mqtt_client.connect(broker_address, broker_port)
mqtt_client.loop_start()

simulate_and_send(mqtt_client)