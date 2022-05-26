FROM python:3.9

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y \
        gosu \
        wait-for-it && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -o -u 1000 -U -m user

ADD ./requirements.txt /tmp/requirements.txt
RUN gosu user pip3 install --no-cache-dir -r /tmp/requirements.txt

ADD ./amzmusicplaylistdumper /opt/amzmusicplaylistdumper

WORKDIR /opt/amzmusicplaylistdumper
CMD [ "gosu", "user", "python3", "main.py" ]
