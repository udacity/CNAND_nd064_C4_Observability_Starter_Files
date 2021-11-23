import logging
import re
import requests


from flask import Flask, jsonify, render_template
from flask_opentracing import FlaskTracing
from jaeger_client import Config
from jaeger_client.metrics.prometheus import PrometheusMetricsFactory
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from prometheus_flask_exporter import PrometheusMetrics


app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

metrics = PrometheusMetrics(app)
# static information as metric
metrics.info("app_info", "Application info", version="1.0.3")

logging.getLogger("").handlers = []
logging.basicConfig(format="%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


def init_tracer(service):

    config = Config(
        config={
            "sampler": {"type": "const", "param": 1},
            "logging": True,
            "reporter_batch_size": 1,
        },
        service_name=service,
        validate=True,
        metrics_factory=PrometheusMetricsFactory(service_name_label=service),
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()


tracer = init_tracer("trial")
flask_tracer = FlaskTracing(tracer, True, app)


@app.route("/")
def homepage():
    return render_template("main.html")


@app.route("/trace")
def trace():
    def remove_tags(text):
        tag = re.compile(r"<[^>]+>")
        return tag.sub("", text)

    with tracer.start_span("get-python-jobs") as span:
        res = requests.get("https://jobs.github.com/positions.json?description=python")
        span.log_kv({"event": "get jobs count", "count": len(res.json())})
        span.set_tag("jobs-count", len(res.json()))

        jobs_info = []
        for result in res.json():
            jobs = {}
            with tracer.start_span("request-site") as site_span:
                logger.info(f"Getting website for {result['company']}")
                try:
                    jobs["description"] = remove_tags(result["description"])
                    jobs["company"] = result["company"]
                    jobs["company_url"] = result["company_url"]
                    jobs["created_at"] = result["created_at"]
                    jobs["how_to_apply"] = result["how_to_apply"]
                    jobs["location"] = result["location"]
                    jobs["title"] = result["title"]
                    jobs["type"] = result["type"]
                    jobs["url"] = result["url"]

                    jobs_info.append(jobs)
                    site_span.set_tag("http.status_code", res.status_code)
                    site_span.set_tag("company-site", result["company"])
                except Exception:
                    logger.error(f"Unable to get site for {result['company']}")
                    site_span.set_tag("http.status_code", res.status_code)
                    site_span.set_tag("company-site", result["company"])

    return jsonify(jobs_info)


if __name__ == "__main__":
    app.run(debug=True,)
