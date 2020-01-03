from flask import Flask
from flask import request
import json
import requests
app = Flask(__name__)
@app.route('/test/', methods=["GET"])
def get_api():
    getstr = request.args['str']
    info = json.loads(getstr)
    print(info)
    return json.dumps({
        'code':'0'
        })
if __name__ == '__main__':
    app.run()
