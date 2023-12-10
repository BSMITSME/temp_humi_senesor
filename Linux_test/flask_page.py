from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import pymysql
import pandas as pd
from threading import Thread
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import DataFrame
from random import randrange
from sqlalchemy import create_engine
import subprocess

app=Flask(__name__)
socketio=SocketIO(app,cors_allowed_origins="*")

def get_pollution():
    db_host = 'localhost'
    db_user = 'scott'
    db_password = 'tiger'
    db_name = 'DVDB'
    db_connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = db_connection.cursor()

    # 온도와 습도를 가져오기 위한 쿼리 실행
    cursor.execute("SELECT temp, humi FROM temp_humi ORDER BY SID DESC LIMIT 1;")
    result = cursor.fetchone()  # fetchone()을 사용하여 첫 번째 결과 레코드를 가져옴

    # 결과에서 온도와 습도 추출
    if result:
        temp, humi = result  # 결과에서 온도와 습도 값을 얻음
    else:
        temp, humi = 0, 0  # 결과가 없는 경우 None으로 설정

    db_connection.close()
    return temp, humi

@socketio.on('get_pollution_index')
def classify_pollution():
    caution_threshold = 30
    danger_threshold = 60
    
    temperature, humidity = get_pollution()
    
    pollution_index = (0.6 * temperature) + (0.4 * humidity)

    if pollution_index < caution_threshold:
        pollution_status = "주의: 괜찮은 상태입니다."
    elif caution_threshold <= pollution_index < danger_threshold:
        pollution_status = "위험: 주의가 필요한 상태입니다."
    else:
        pollution_status = "위험한 상태입니다. 조심하세요!"
    
    # emit을 사용하여 값을 전달
    socketio.emit('update_pollution', pollution_status)

def get_sensor_data():
    # conn = pymysql.connect(host='localhost',user='scott',password='tiger',database='DVDB')
    engine = create_engine('mysql+pymysql://scott:tiger@localhost/DVDB')
    query="SELECT SID, temp, humi FROM temp_humi ORDER BY SID ASC LIMIT 100"
    df=pd.read_sql(query,con=engine)
    df=df.set_index('SID')
    # conn.close()
    engine.dispose()
    return df

def generate_plot(df):
    return df.plot(use_index=True,y=["temp","humi"],
            kind="line",figsize=(10,5)).legend(loc='upper left')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('update_plot','Connected')

@app.route('/')
def index():
    return render_template("index.html")

@socketio.on('get_plot')
def handle_get_plot():
    sensor_data=get_sensor_data()
    plot=generate_plot(sensor_data)

    plt.savefig('static/plot.png')
    plt.close()
    emit('update_plot','plot.png')

def run_other_file():
    # 실행할 파이썬 파일 경로와 파일명 설정
    file_to_run = 'consumer2.py'  # 실행하려는 다른 파일명으로 변경해주세요

    try:
        # 다른 파일을 실행하는 코드
        with open(file_to_run, 'r') as file:
            code = compile(file.read(), file_to_run, 'exec')
            exec(code, globals())
    except FileNotFoundError:
        print(f"파일 '{file_to_run}'을(를) 찾을 수 없습니다.")
    except Exception as e:
        print(f"파일 실행 중 오류 발생: {e}")
    
    

if __name__ == '__main__':
    external_thread = Thread(target=run_other_file)
    external_thread.start()
    socketio.run(app,port=5001)
    
