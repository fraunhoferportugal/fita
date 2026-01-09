FROM python:3.12.0-alpine

ENV PT=Europe/Lisbon
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

LABEL maintainer="Fernando Rego <fernando.rego@fraunhofer.pt>"
LABEL version="1.0"

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN pip install paho.mqtt==2.1.0 requests

ADD main.py /
ADD src /src

CMD [ "python3","-u", "main.py", "127.0.0.1", "1883", "127.0.0.1", "8126", "video-component-video", "6013"]
