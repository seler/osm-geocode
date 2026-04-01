FROM ghcr.io/home-assistant/home-assistant:stable

# Install HACS (Alpine-based image)
RUN set -ex \
    && apk add --no-cache unzip wget \
    && mkdir -p /config/custom_components/hacs \
    && wget -q https://github.com/hacs/integration/releases/latest/download/hacs.zip \
    && unzip -o hacs.zip -d /config/custom_components/hacs \
    && rm hacs.zip \
    && apk del unzip wget

# Copy our component
COPY custom_components/osm_geocode /config/custom_components/osm_geocode

# Copy test HA configuration
COPY tests/integration/configuration.yaml /config/configuration.yaml

EXPOSE 8123
