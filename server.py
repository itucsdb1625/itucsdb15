import datetime
import os

from flask import Flask
from flask import render_template


app = Flask(__name__)


@app.route('/')
def home_page():
    now = datetime.datetime.now()
    return render_template('home.html', current_time=now.ctime())

@app.route('/samplecommit')
def movies_page():
    return render_template('samplecommit.html')

@app.route('/samplecommit2')
def berkay_page():
    return render_template('samplecommit2.html')

@app.route('/samplecommit3')
def efe_page():
    return render_template('samplecommit3.html')

@app.route('/samplecommit4')
def emre_page():
    return render_template('samplecommit4.html')

@app.route('/samplecommit5')
def kursat_page():
    return render_template('samplecommit5.html')

if __name__ == '__main__':
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True
    app.run(host='0.0.0.0', port=port, debug=debug)
