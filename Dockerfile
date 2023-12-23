# Builder stage
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache pip wheel --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


# App stage
FROM python:3.11-slim as app

WORKDIR /app

COPY --from=builder /app /app

COPY app app
COPY run.py run.py
COPY requirements.txt requirements.txt
COPY entrypoint.sh entrypoint.sh
COPY message_models message_models

RUN apt-get update
RUN apt-get install -y libtiff5-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev libfribidi-dev tcl8.6-dev tk8.6-dev libjpeg62
COPY --from=builder /usr/src/app/wheels /wheels
RUN --mount=type=cache,target=/root/.cache pip install /wheels/*

RUN chmod 700 entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]