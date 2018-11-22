FROM alpine:3.8
MAINTAINER Mahmoud Shepero (mahmoud.shepero@angstrom.uu.se)

LABEL date="22112018"
LABEL description="This container runs the EVSpatialChargingModel"

# Install basics and define the repository
RUN apk update && \
    apk add vim && \
    apk add git && \
    apk add curl && \
    echo "@community http://dl-8.alpinelinux.org/alpine/v3.8/community" >> /etc/apk/repositories && \
    echo "http://dl-8.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories

# Install python3 and GDAL
RUN apk --no-cache --update-cache add gcc gfortran libgfortran python3 python3-dev build-base wget freetype-dev libpng-dev openblas-dev@community && \
    apk update python3 && \
    apk add --update libressl2.7-libcrypto && \
    apk add --no-cache gdal gdal-dev --repository http://dl-8.alpinelinux.org/alpine/edge/testing && \
    apk upgrade musl 

# Update pip and install libraries 
RUN pip3 install --upgrade pip && \
    pip3 install --upgrade setuptools && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    pip3 install --no-cache-dir numpy scipy pandas matplotlib jupyter GDAL ipdb scikit-learn twine 

