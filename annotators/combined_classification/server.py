import logging
import os
from flask import Flask, request, jsonify
import sentry_sdk

from sentry_sdk.integrations.flask import FlaskIntegration
from deeppavlov import build_model
logger = logging.getLogger(__name__)
sentry_sdk.init(dsn=os.getenv('SENTRY_DSN'), integrations=[FlaskIntegration()])

try:
    model = build_model("combined_classifier.json", download=False)
    test_res = model(["a"])
    logger.info("model loaded, test query processed")
except Exception as e:
    sentry_sdk.capture_exception(e)
    logger.exception(e)
    raise e

app = Flask(__name__)


def get_result(sentences):
    res = [{} for _ in sentences]
    try:
        res = model(sentences)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.exception(e)
    return res


@app.route("/model", methods=['POST'])
def respond():
    logger.info(request.json)
    sentences = request.json.get("sentences", [" "])
    answer = get_result(sentences)
    return jsonify(answer)


@app.route("/batch_model", methods=['POST'])
def batch_respond():
    logger.info(request.json)
    sentences = request.json.get("sentences", [" "])
    answer = get_result(sentences)
    return jsonify([{"batch": answer}])


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=3000)
