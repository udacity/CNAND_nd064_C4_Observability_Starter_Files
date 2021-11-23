import os
import requests
from flask import Flask, render_template, request, jsonify
from jaeger_client import Config
from flask_opentracing import FlaskTracing

app = Flask(__name__)
config = Config(
    config={
        "sampler": {"type": "const", "param": 1},
        "logging": True,
        "reporter_batch_size": 1,
    },
    service_name="service",
)
jaeger_tracer = config.initialize_tracer()
tracing = FlaskTracing(jaeger_tracer, True, app)


@app.route("/")
def hello_world():

    return """Hello, World!

Thank you for visiting the site!\n\n"""


@app.route("/api/second", methods=["GET", "POST"])
def jobs():
    if request.method == "GET":
        response = requests.get("http://second-sample-app.default.svc.cluster.local:8000")
        return str(type(response))
    elif request.method == "POST":
        response = requests.get("http://second-sample-app.default.svc.cluster.local:8000")
        return str(type(response))
