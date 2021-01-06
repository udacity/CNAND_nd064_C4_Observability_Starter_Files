
import os
import time
import requests

from flask import Flask, jsonify

import logging
from jaeger_client import Config

app = Flask(__name__)


def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()


tracer = init_tracer('test-service')


with tracer.start_span('first-span') as span:
    span.set_tag('first-tag', '100')




@app.route('/')
def hello_world():
    return 'Hello World!'



@app.route('/alpha')
def alpha():
    for i in range(reps):
        do_heavy_work():
        if i % 100 == 99:
            time.sleep(10)
    return 'This is the Alpha Endpoint!'



 
@app.route('/beta')
def beta():
    r = requests.get("https://www.google.com/search?q=python")
    dict = {}
    for key, value in r.headers.items():
        print(key, ":", value)
        dict.update({key: value})
    return jsonify(dict)      




if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))