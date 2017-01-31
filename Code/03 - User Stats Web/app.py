
from flask import Flask, render_template
import json

from monitor import collect_stats

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', name='Romac')

@app.route('/<username>')
def user(username):
    (log, stats) = collect_stats(username)
    return render_template('user.html', name=username, log='<br>'.join(log), stats=json.dumps(stats))

if __name__ == '__main__':
    app.run()

