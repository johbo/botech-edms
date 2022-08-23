
# Development environment as a docker image

# TODO: Can this become a parameter?
FROM debian:11.4-slim as base_image

LABEL org.opencontainers.image.authors="joh@bo-tech.de"

COPY config.env /config.env

ENV LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PROJECT_INSTALL_DIR=/opt/mayan-edms/

ENV MAYAN_MEDIA_ROOT=/var/lib/mayan \
    MAYAN_STATIC_ROOT=${PROJECT_INSTALL_DIR}static

RUN set -x \
    && adduser mayan \
    && DEBIAN_FRONTEND=noninteractive \
        apt-get update \
    && apt-get install --no-install-recommends --yes \
        sudo \
    && echo "mayan ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && sudo -u mayan mkdir /home/mayan/src
# TODO: Decide if purge of apt files should be done here

USER mayan
WORKDIR /home/mayan
