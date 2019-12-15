import urllib.parse
import urllib.request
from datetime import datetime

def post_bme():
    time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    values = {
        'user': 'Lukas Brennauer', 
        'password': 'a',
        'time': time,
        'temperature': 1,
        'humidity': 2,
        'pressure': 3
    }

    data = urllib.parse.urlencode(values).replace('+', '%20')
    url = 'http://127.0.0.1:5000/admin/post_bme?' + data
    with urllib.request.urlopen(url) as response:
        print(response.read().decode('utf-8'))

post_bme()

def post_mpu():
    time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    values = {
        'user': 'Lukas Brennauer', 
        'password': 'a',
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

    data = urllib.parse.urlencode(values).replace('+', '%20')
    url = 'http://127.0.0.1:5000/admin/post_mpu?' + data
    with urllib.request.urlopen(url) as response:
        print(response.read().decode('utf-8'))

post_mpu()




