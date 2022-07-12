FROM python:3.9 AS base

ADD . /opt/project

WORKDIR /opt/project

RUN python3.9 -m pip install --upgrade -r /opt/project/requirements.txt

RUN set -e && apt-get update && \
    apt-get install -y pkg-config git yasm nasm doxygen && \
    cd vmaf && make clean && make && make install

RUN python3.9 -m pip install --upgrade -r /opt/project/vmaf/python/requirements.txt

RUN set -e && apt-get update && apt-get install -y ffmpeg