FROM python:3.9 AS base

ADD . /opt/project

WORKDIR /opt/project

RUN python3.9 -m pip install --upgrade -r /opt/project/requirements.txt

RUN set -e && apt-get update && \
    apt-get install -y pkg-config git yasm nasm doxygen ffmpeg && \
    cd vmaf/libvmaf && meson build --buildtype release && ninja -vC build install
