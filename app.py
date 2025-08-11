from flask_cors import CORS
from flask import Flask

app = Flask(__name__)
CORS(app)

@app.route('/')
def f_home():
    return 'hellow RVX task dl bot',200


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=8000)
