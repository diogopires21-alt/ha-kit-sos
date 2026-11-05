# https://contributors.home-assistant.io/apps/guides/dockerfile/
ARG BUILD_FROM=ghcr.io/home-assistant/base-python:3.14-alpine3.24
FROM ${BUILD_FROM}

ARG BUILD_VERSION=dev
ENV KIT_SOS_VERSION=${BUILD_VERSION} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# A app só usa a biblioteca padrão do Python: nada para instalar.
COPY app /app
WORKDIR /app

# Com o S6 overlay (imagens base do HA) o comando só vê as variáveis do
# contentor (ex.: SUPERVISOR_TOKEN) se correr através do with-contenv.
CMD [ "/command/with-contenv", "python3", "/app/server.py" ]

LABEL \
    org.opencontainers.image.title="Home Assistant App: Kit SOS" \
    org.opencontainers.image.description="Emergency-kit and expiry-date tracker for Home Assistant." \
    org.opencontainers.image.licenses="MIT"
