FROM debian:bullseye

RUN apt-get update -y && \
    apt-get install -y \
    python3.9 \
    python3-pip \
    python3.9-dev \
    libpq-dev \
    git

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN python3 -m pip install -U pip && \
    python3 -m pip install -r requirements.txt && \
    python3 -m pip install gunicorn

COPY jwnlp jwnlp
COPY assets assets
#COPY data data
COPY temp temp
COPY db db
COPY app.py build_wt_json_library.py build_database_prefect.py boot.sh wsgi.py /app/
RUN chmod +x /app/boot.sh

ENV FLASK_APP /app/wsgi.py

EXPOSE 5000

RUN ls -la /app/ 

#ENTRYPOINT [ "/app/boot.sh" ]
