FROM python:3.8-alpine
RUN apk add build-base zlib-dev jpeg-dev freetype-dev lcms2-dev tiff-dev \
            openjpeg-dev tk-dev tcl-dev harfbuzz-dev fribidi-dev openssl-dev \
            yaml-dev
WORKDIR /keypunch_bot

COPY ./requirements.txt .
RUN pip install -r ./requirements.txt

COPY ./requirements.build.txt .
RUN pip install -r ./requirements.build.txt

COPY ./keypunch_bot ./keypunch_bot
COPY ./tests ./tests
COPY ./.pylintrc ./mypy.ini ./

ENV PYTHONPATH ${PYTHONPATH}:/keypunch_bot
RUN pytest && \
    pylint keypunch_bot && \
    mypy -m keypunch_bot


FROM python:3.8-alpine
RUN apk add build-base zlib-dev jpeg-dev freetype-dev lcms2-dev tiff-dev \
            openjpeg-dev tk-dev tcl-dev harfbuzz-dev fribidi-dev openssl-dev \
            yaml-dev
WORKDIR /keypunch_bot

COPY ./requirements.txt .
RUN pip install -r ./requirements.txt
COPY ./keypunch_bot ./keypunch_bot

ENV PYTHONPATH ${PYTHONPATH}:/keypunch_bot

CMD ["sh", "-c", "python -m keypunch_bot --api-key \"$API_KEY\" --mongo \"mongodb://${MONGO_USER}:${MONGO_PASSWORD}@${MONGO_SERVER}/${MONGO_DATABASE}?retryWrites=false\" webhook --port $PORT --url \"$URL\""]
