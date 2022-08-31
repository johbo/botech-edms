
# Development environment as a docker image

# TODO: Can this become a parameter?
FROM debian:11.4-slim as base_image

LABEL org.opencontainers.image.authors="joh@bo-tech.de"

COPY config.env /config.env

ENV LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1

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
        python3-ipdb \
        python3-pip \
        python3-venv \
        sudo \
        tesseract-ocr-deu \
    # TODO: copy of the dockerfile from EDMS, consider to use their image as base
    && apt-get install --no-install-recommends --yes \
        ca-certificates \
        exiftool \
        file \
        fonts-arphic-uming \
        fonts-arphic-ukai \
        fonts-unfonts-core \
        fuse \
        ghostscript \
        git-core \
        gpgv \
        gnupg1 \
        graphviz \
        libarchive-zip-perl \
        libfile-mimeinfo-perl \
        libfuse2 \
        libldap-2.4-2 \
        libmagic1 \
        libmariadb3 \
        libpq5 \
        libreoffice-calc-nogui \
        libreoffice-draw-nogui \
        libreoffice-impress-nogui \
        libreoffice-math-nogui \
        libreoffice-writer-nogui \
        libsasl2-2 \
        poppler-utils \
        python3-distutils \
        sane-utils \
        sudo \
        supervisor \
        tesseract-ocr \
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

EXPOSE 8000

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
