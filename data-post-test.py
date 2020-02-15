from datetime import datetime
import requests

def post_bme():
    time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    url = 'http://127.0.0.1:5000/api/raspi/bme'
    data = {
        'time': time,
        'temperature': 1,
        'humidity': 2,
        'pressure': 3
    }
    r = requests.put(url, params=data, auth=('Lukas Brennauer', 'a'))
    print('PUT: STATUS:', r.status_code ,'\nURL:', r.url, '\n', r.json())

def post_mpu():
    time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    url = 'http://127.0.0.1:5000/api/raspi/mpu'
    data = {
        'time': time,
        'gyroscope_x': 1,
        'gyroscope_y': 2,
        'gyroscope_z': 3,
        'acceleration_x': 4,
        'acceleration_y': 5,
        'acceleration_z': 6,
        'rot_x': 7,
        'rot_y': 8
    }
    r = requests.put(url, params=data, auth=('Lukas Brennauer', 'a'))
    print('PUT: STATUS:', r.status_code ,'\nURL:', r.url, '\n', r.json())

def post_neo():
    time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    url = 'http://127.0.0.1:5000/api/raspi/neo'
    data = {
        'time': time,
        'data': "1"
    }
    r = requests.put(url, params=data, auth=('Lukas Brennauer', 'a'))
    print('PUT: STATUS:', r.status_code, '\nURL:', r.url, '\n', r.json())


if __name__ == '__main__':
    post_bme()
    post_mpu()
    post_neo()