FROM python:3.9 AS base

ADD . /opt/project

WORKDIR /opt/project

RUN python3.9 -m pip install --upgrade -r /opt/project/requirements.txt

RUN set -e && apt-get update && \
    apt-get install -y pkg-config git yasm nasm doxygen xxd && \
    cd vmaf && make clean && make && make install

RUN python3.9 -m pip install --upgrade -r /opt/project/vmaf/python/requirements.txt

RUN mkdir -p /tools && \
    cd /tools && \
    wget -O ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz && \
    tar -xf ffmpeg.tar.xz && \
    mv ffmpeg-git-20220622-amd64-static ffmpeg && \
    rm -f ffmpeg.tar.xz
