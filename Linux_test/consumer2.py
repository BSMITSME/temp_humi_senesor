import datetime
import random
import time
import paho.mqtt.client as mqtt
import pymysql

def on_message(client, userdata, message):
    try:
        global mmmmmhh
        payload = message.payload.decode()
        data = eval(payload)

        # print(f'data topic : {message.topic}, data type : {type(data)}, data : {data}')
        db_connection = pymysql.connect(host=db_host,user=db_user,password=db_password,database=db_name)
        cursor = db_connection.cursor()
        
        timestamp = datetime.datetime.strptime(data['time'], '%Y-%m-%d %H:%M:%S')
        humi = int(data['humidity'])
        temperature = int(data['temperature'])

        query=f"INSERT INTO {table_name} (temp, humi) VALUES (%s,%s)"
        cursor.execute(query,(temperature, humi))
        db_connection.commit()

        db_connection.close()
        print(f"Received and stored: Time:{timestamp}, Temp:{temperature}'C, Humi:{humi}%")
    except Exception as e:
        print(f"Error:{e}")
        
broker_address = 'localhost'
broker_port = 1883
topic_temp = 'temperature'
topic_humi = 'humidity'
topic = 'temp_humi'

db_host = 'localhost'
db_user = 'scott'
db_password = 'tiger'
db_name = 'DVDB'
table_name = 'temp_humi'

# 함수 설정
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe(topic)

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address, broker_port)
client.loop_forever()