FROM deeppavlov/base-gpu:0.12.0

ARG CONFIG
ARG DATA_URL=http://files.deeppavlov.ai/alexaprize_data/cobot_bert_6task.tar.gz
ARG PORT
ENV CONFIG=$CONFIG
ENV PORT=$PORT

ADD $DATA_URL /tmp

RUN tar -xvzf /tmp/*.tar.gz -C /tmp/

WORKDIR /src
RUN mkdir common

COPY annotators/combined_classification/requirements.txt .
RUN pip install -r requirements.txt

COPY annotators/combined_classification/ ./
COPY common/ common/

RUN python -m deeppavlov install $CONFIG
CMD gunicorn --workers=1 --bind 0.0.0.0:8087 --timeout=300 server:app
