
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
        # TODO: make setup-dev-environment fails without ldap
        libldap2-dev \
        libsasl2-dev \
        # ENDTODO make ...
        make \
        python3-pip \
        python3-venv \
        sudo \
    && echo "mayan ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && sudo -u mayan mkdir /home/mayan/src /home/mayan/venv
# TODO: Decide if purge of apt files should be done here

USER mayan
WORKDIR /home/mayan

COPY --chown=mayan:mayan mayan-edms mayan-edms-make

RUN set -x \
    && DEBIAN_FRONTEND=noninteractive \
    make -C mayan-edms-make setup-dev-operating-system-packages

RUN \
    make -C mayan-edms-make setup-dev-python-libraries

# TODO: Dev installation of botech-edms currently still required manually
#
# source ~/venv/bin/activate
# cd ~/src/botech-edms
# python setup.py develop
# cd ~/src/mayan-edms
# python setup.py develop
#
# Note: This is only required once, since the venv is persistent if a volume is
# mounted on it.
