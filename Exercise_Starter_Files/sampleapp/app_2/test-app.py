import os
import requests
from flask import Flask, request

from jaeger_client import Config
from flask_opentracing import FlaskTracer
from opentracing import tracer

app = Flask(__name__)


@app.route("/")
def homepage():
    gh_jobs = "https://jobs.github.com/positions.json?description=python"

    parent_span = flask_tracer.get_span()
    with tracer.start_span("get-python-jobs", child_of=parent_span) as span:
        span.set_tag("http.url", gh_jobs)
        res = requests.get(gh_jobs)
        span.set_tag("http.status_code", res.status_code)

    with tracer.start_span("get-json", child_of=parent_span) as span:
        myjson = res.json()

        span.set_tag("python_jobs", len(myjson))
        pull_python_jobs = map(lambda item: item["title"], myjson)

    return "Tracing Results: " + ", ".join(pull_python_jobs)


def initialize_trace():
    config = Config(
        config={"sampler": {"type": "const", "param": 1},}, service_name="service",
    )
    return config.initialize_tracer()  # also sets opentracing.tracer


flask_tracer = FlaskTracer(initialize_trace, True, app)
# https://github.com/jaegertracing/jaeger/tree/master/monitoring/jaeger-mixin
