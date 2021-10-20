FROM 557762406065.dkr.ecr.us-west-2.amazonaws.com/fr/ubuntu:20.04__py3.8.11 AS base

ARG DEBIAN_FRONTEND="noninteractive"

RUN apt-get update && apt-get install -y gfortran libexpat-dev \
    m4 libcurl4-openssl-dev zlib1g-dev python3-setuptools python3-pip \
    libeccodes-tools unzip \
    git wget \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN cd /root \
    && wget https://github.com/alcf-lidar/alcf/archive/refs/tags/v1.1.0.tar.gz \
    && tar zxvf v1.1.0.tar.gz 

# WORKDIR /root/alcf

RUN cd /root/alcf-1.1.0 \
    && ./download_dep \
    && ./build_dep \
    && make

RUN cd /root/alcf-1.1.0 \
    && python3 setup.py install
