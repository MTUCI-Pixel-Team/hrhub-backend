# Этап сборки
FROM python:3.12.2-alpine3.19 as builder

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    /py/bin/pip install clarifai_grpc && \
    if [ "$DEV" = "true" ]; then /py/bin/pip install -r /tmp/requirements.dev.txt; fi && \
    apk del .tmp-build-deps

# Финальный этап
FROM python:3.12.2-alpine3.19

ENV PYTHONUNBUFFERED=1
ENV PATH="/py/bin:$PATH"

COPY --from=builder /py /py
COPY --from=builder /usr/bin/postgresql-client /usr/bin/postgresql-client
COPY ./backend /backend

WORKDIR /backend
EXPOSE 7000

RUN adduser --disabled-password --no-create-home django-user && \
    chmod -R 777 /backend/media

USER django-user
