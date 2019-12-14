from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

@app.route('/post_bme')
def post_bme():
    return render_template('post_bme.html', now=datetime.now())

@app.route('/post_mpu')
def post_mpu():
    return render_template('post_mpu.html', now=datetime.now())

# TODO: Use real time and data in production version

if __name__ == '__main__':
    app.run(port=5001)